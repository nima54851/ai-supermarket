#!/usr/bin/env python3
"""
灵犀客服引擎 - 秘钥自动发货版 v5.0
功能：
  1. 扫描本地 DB，把新客户消息写入 inbox.json
  2. 监听 outbox，把灵犀回复写入本地 DB → 同步 GitHub CDN
  3. 扫描 pending_deliveries.json → 生成秘钥 → 送到客户网站聊天窗口
"""
import time, json, os, random, sqlite3, urllib.request, base64

DB = "/tmp/chat_messages.db"
INBOX_FILE = "/root/.openclaw/workspace/ai-supermarket/customer_inbox.json"
OUTBOX_FILE = "/root/.openclaw/workspace/ai-supermarket/customer_outbox.json"
PENDING_FILE = "/root/.openclaw/workspace/ai-supermarket/pending_deliveries.json"
COMMIT_SHA = "1b540189dc906be02108b87a2892f5a891d4f9d6"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "nima54851/ai-supermarket"
INBOX_GH_PATH = "inbox.json"
GIST_ID = "3fda3818530c065953da3f2257bc05d1"

# 秘钥字符集（去掉了易混淆的 O/0/I/1）
CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

# 商品ID → 下载链接 映射
PRODUCT_DOWNLOADS = {
    "telegram-bot":       "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/telegram-bot.zip",
    "github-automation":  "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/github-automation.zip",
    "content-promoter":   "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/content-promoter.zip",
    "n8n-workflow":       "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/n8n-workflow.zip",
    "web-scraper":        "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/web-scraper.zip",
    "ecloudsign-panel":   "https://github.com/nima54851/ai-supermarket/releases/download/ecloudsign-panel-v1.0/ecloudsign-panel-v1.0-linux.tar.gz",
    "skill-builder":      "https://github.com/nima54851/agent-studio/releases/download/v1.0.0/skill-builder.zip",
}

# ══════════════════════════════════════════════════════════════
#  秘钥生成
# ══════════════════════════════════════════════════════════════

def gen_key() -> str:
    """生成 LING-XXXX-XXXX 格式秘钥"""
    p = lambda: ''.join(random.choices(CHARS, k=4))
    return f"LING-{p()}-{p()}"

def add_secret_to_gist(key: str, product_id: str) -> bool:
    """往 Gist 写入新秘钥"""
    try:
        # 读取当前 Gist
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            gist = json.loads(r.read())
        sha = gist.get("history", [{}])[0].get("version") if gist.get("history") else None

        # 读取 secrets.json
        raw_url = gist["files"]["secrets.json"]["raw_url"]
        secrets = []
        try:
            with urllib.request.urlopen(raw_url, timeout=10) as r:
                secrets = json.loads(r.read())
        except:
            secrets = []

        # 添加新秘钥
        secrets.append({
            "key": key,
            "productId": product_id,
            "used": False,
            "created": time.strftime("%Y-%m-%d"),
        })

        # 写回 Gist
        body = json.dumps({
            "description": "灵犀集市 - 秘钥数据库",
            "files": {
                "secrets.json": {
                    "content": json.dumps(secrets, ensure_ascii=False, indent=2)
                }
            }
        }).encode()

        req2 = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            data=body,
            headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"},
            method="PATCH"
        )
        with urllib.request.urlopen(req2, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"  Gist写入失败: {e}")
        return False

def deliver_secret_to_website(visitor_id: str, secret_key: str, product_id: str):
    """把秘钥消息写入本地 DB，网站轮询会收到"""
    if not visitor_id or len(visitor_id) < 8:
        return False
    download = PRODUCT_DOWNLOADS.get(product_id, "https://github.com/nima54851/ai-supermarket/releases")
    ts = time.time()
    content = f"""🔑 *您的秘钥已到！*

商品：{product_id}
秘钥：`{secret_key}`

━━━━━━━━━━━━━━━━━

📥 *下载地址（复制链接到浏览器打开）：*
`{download}`

━━━━━━━━━━━━━━━━━

💡 *激活方法：*
① 打开网站 → 秘钥激活
② 粘贴上方秘钥 → 点激活
③ 自动解锁对应工具下载权限

⏰ 秘钥永久有效，一人一座，禁止转让。"""

    try:
        db = sqlite3.connect(DB)
        db.execute(
            "INSERT INTO messages (visitor_id,role,content,agent,created_at,synced) VALUES (?,?,?,?,?,1)",
            [visitor_id, "agent", content, "灵犀", ts]
        )
        db.commit()
        db.close()
        print(f"  ✅ 秘钥已送到网站 → {visitor_id[:12]}")
        return True
    except Exception as e:
        print(f"  ❌ 写入DB失败: {e}")
        return False

# ══════════════════════════════════════════════════════════════
#  待发货队列处理
# ══════════════════════════════════════════════════════════════

def load_pending() -> list:
    if os.path.exists(PENDING_FILE):
        try:
            return json.load(open(PENDING_FILE))
        except:
            return []
    return []

def save_pending(pending: list):
    open(PENDING_FILE, 'w').write(json.dumps(pending, ensure_ascii=False, indent=2))

def process_pending_deliveries():
    """扫描待发货队列，生成秘钥并送到客户网站聊天窗口"""
    pending = load_pending()
    active = [p for p in pending if not p.get("delivered") and p.get("visitor_id")]
    if not active:
        return

    print(f"[{time.strftime('%H:%M:%S')}] 📦 扫描待发货队列: {len(active)} 条")
    changed = False

    for item in active:
        vid = item.get("visitor_id", "")
        product_id = item.get("product_id", "")
        telegram_uid = item.get("telegram_uid", "")

        if not vid or not product_id:
            continue

        # 生成秘钥
        secret_key = gen_key()
        print(f"  → 生成秘钥: {secret_key} (product={product_id})")

        # 写入 Gist
        ok = add_secret_to_gist(secret_key, product_id)
        if not ok:
            print(f"  ⚠️ Gist写入失败，跳过")
            continue

        # 送到客户网站聊天窗口
        delivered = deliver_secret_to_website(vid, secret_key, product_id)
        if delivered:
            item["delivered"] = True
            item["delivered_at"] = time.strftime("%Y-%m-%d %H:%M")
            item["secret_key"] = secret_key
            changed = True
            print(f"  ✅ 完成: {secret_key} → {vid[:12]}")

    if changed:
        save_pending(pending)

# ══════════════════════════════════════════════════════════════
#  原有的客服逻辑（保留）
# ══════════════════════════════════════════════════════════════

def read_inbox():
    if os.path.exists(INBOX_FILE):
        try:
            return json.load(open(INBOX_FILE))
        except:
            return {"messages": [], "processed": []}
    return {"messages": [], "processed": []}

def write_inbox(data):
    open(INBOX_FILE, 'w').write(json.dumps(data, ensure_ascii=False))

def read_outbox():
    if os.path.exists(OUTBOX_FILE):
        try:
            return json.load(open(OUTBOX_FILE))
        except:
            return []
    return []

def write_outbox(data):
    open(OUTBOX_FILE, 'w').write(json.dumps(data, ensure_ascii=False))

def sync_outbox_to_github():
    """把本地 outbox 里的回复同步到 GitHub CDN"""
    outbox = read_outbox()
    if not outbox:
        return
    pending = [m for m in outbox if not m.get("_synced")]
    if not pending:
        return

    # 读取当前 GitHub SHA
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{INBOX_GH_PATH}",
        headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    )
    sha = None
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            sha = json.loads(r.read()).get("sha")
    except:
        pass

    # 读取 CDN 内容
    inbox = None
    try:
        req_cdn = urllib.request.Request(
            f"https://cdn.jsdelivr.net/gh/{REPO}@{COMMIT_SHA}/{INBOX_GH_PATH}",
            headers={"Accept": "application/json", "Cache-Control": "no-cache"}
        )
        with urllib.request.urlopen(req_cdn, timeout=10) as r:
            inbox = json.loads(r.read())
    except Exception as e:
        print(f"  CDN读取失败({e})，跳过同步")
        return

    for msg in pending:
        vid = msg.get("visitor_id")
        content = msg.get("content")
        ts = msg.get("time", time.time())
        if vid and content:
            if vid not in inbox["messages"]:
                inbox["messages"][vid] = []
            inbox["messages"][vid].append({
                "id": int(ts * 1000) + 1,
                "role": "agent",
                "content": content,
                "agent": "灵犀",
                "time": ts
            })

    body = {
        "message": "💬 客服回复消息",
        "content": base64.b64encode(json.dumps(inbox, ensure_ascii=False).encode()).decode(),
    }
    if sha:
        body["sha"] = sha

    req3 = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{INBOX_GH_PATH}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"},
        method="PUT"
    )
    try:
        with urllib.request.urlopen(req3, timeout=15) as r:
            json.loads(r.read())
            print(f"[{time.strftime('%H:%M:%S')}] ✅ 同步 {len(pending)} 条回复到 GitHub")
            for msg in pending:
                msg["_synced"] = True
            write_outbox(outbox)
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ GitHub同步失败: {e}")

def process_outbox():
    """检查 outbox，把灵犀的回复写入本地 DB"""
    outbox = read_outbox()
    if not outbox:
        return
    for msg in outbox:
        if msg.get("_synced"):
            continue
        vid = msg.get("visitor_id")
        content = msg.get("content")
        ts = msg.get("time", time.time())
        if vid and content:
            try:
                db = sqlite3.connect(DB)
                db.execute(
                    "INSERT INTO messages (visitor_id,role,content,agent,created_at,synced) VALUES (?,?,?,?,?,1)",
                    [vid, "agent", content, "灵犀", ts]
                )
                db.commit()
                db.close()
                msg["_synced"] = True
                print(f"[{time.strftime('%H:%M:%S')}] ✅ 回复已写入DB → {vid[:8]}")
            except Exception as e:
                print(f"  DB写入失败: {e}")
    write_outbox(outbox)

# ══════════════════════════════════════════════════════════════
#  主循环
# ══════════════════════════════════════════════════════════════

print("🚀 灵犀客服引擎 v5.0 启动（秘钥自动发货版）")
print("   每 15 秒检查一次：客户消息 / 待发货队列...\n")

for f, init in [(INBOX_FILE, {"messages": [], "processed": []}),
                 (OUTBOX_FILE, []),
                 (PENDING_FILE, [])]:
    if not os.path.exists(f):
        open(f, 'w').write(json.dumps(init, ensure_ascii=False))

while True:
    try:
        process_pending_deliveries()  # 秘钥自动发货（新增）
        process_outbox()              # outbox → 本地 DB
        sync_outbox_to_github()       # 本地 DB → GitHub CDN

    except KeyboardInterrupt:
        print("\n👋 引擎已停止")
        break
    except Exception as e:
        print(f"[错误] {e}")

    time.sleep(15)
