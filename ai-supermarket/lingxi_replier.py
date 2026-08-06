#!/usr/bin/env python3
"""
灵犀客服引擎 v5（纯轮询版）
架构：客户 → GitHub inbox.json → lingxi_replier 轮询 → 自动回复 → customer_messages.json（GitHub Pages）
网站：写 inbox.json + 读 customer_messages.json
"""
import time, json, os, random, threading, urllib.request, base64
from http.server import HTTPServer, BaseHTTPRequestHandler

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "nima54851/ai-supermarket"
GIST_ID = "3fda3818530c065953da3f2257bc05d1"
INBOX_FILE = "customer_inbox.json"
MSG_FILE = "customer_messages.json"
PENDING_FILE = "/root/.openclaw/workspace/ai-supermarket/pending_deliveries.json"
POLL_INTERVAL = 8   # 轮询间隔（秒）

CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

PRODUCT_DOWNLOADS = {
    "telegram-bot":      "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/telegram-bot.zip",
    "github-automation": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/github-automation.zip",
    "content-promoter":  "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/content-promoter.zip",
    "n8n-workflow":      "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/n8n-workflow.zip",
    "web-scraper":       "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/web-scraper.zip",
    "ecloudsign-panel":  "https://github.com/nima54851/ai-supermarket/releases/download/ecloudsign-panel-v1.0/ecloudsign-panel-v1.0-linux.tar.gz",
}
PRODUCT_NAMES = {
    "telegram-bot":      "📱 Telegram号码查询机器人",
    "github-automation": "⚡ GitHub Agent自动化系统",
    "content-promoter":  "📣 AI内容推流系统",
    "n8n-workflow":      "🔗 n8n工作流自动化系统",
    "web-scraper":       "🕷️ AI智能网页爬虫",
    "ecloudsign-panel":  "🖊️ 易云章 API 控制面板",
}

# ══════════════════════════════════════════════════════════════
#  GitHub API 工具
# ══════════════════════════════════════════════════════════════

def gh_api(path, method="GET", data=None):
    url = f"https://api.github.com/repos/{REPO}/{path}"
    hdrs = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def get_sha(path):
    try:
        return gh_api(f"contents/{path}")["sha"]
    except:
        return None

def write_file(path, content, msg="update"):
    sha = get_sha(path)
    data = {"message": msg, "content": base64.b64encode(content.encode()).decode(), "sha": sha}
    r = gh_api(f"contents/{path}", method="PUT", data=data)
    print(f"  ✅ 写入 {path} (SHA: {r['content']['sha'][:8]})")
    return r

def read_raw(url, default=None):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except:
        return default

def read_messages():
    """读取 GitHub 上的 inbox.json"""
    try:
        sha_info = gh_api(f"contents/{INBOX_FILE}")
        raw = urllib.request.urlopen(sha_info["download_url"], timeout=10)
        return json.loads(raw.read()), sha_info["sha"]
    except:
        return {}, None

def read_customer_messages():
    """读取现有的 customer_messages.json"""
    try:
        sha_info = gh_api(f"contents/{MSG_FILE}")
        raw = urllib.request.urlopen(sha_info["download_url"], timeout=10)
        return json.loads(raw.read()), sha_info["sha"]
    except:
        return {}, None

def save_customer_messages(msgs):
    """保存完整的 customer_messages.json"""
    write_file(MSG_FILE, json.dumps(msgs, ensure_ascii=False, indent=2),
               msg="chat: 更新客户消息")

# ══════════════════════════════════════════════════════════════
#  自动回复
# ══════════════════════════════════════════════════════════════

def generate_reply(c):
    c = c.strip().lower()
    if any(k in c for k in ["价格", "多少", "费用", "怎么买", "购买", "多少钱", "收费"]):
        return f"""您好！灵犀集市商品列表：

📱 Telegram号码查询机器人 — ¥29/月
⚡ GitHub Agent自动化系统 — ¥99/月
📣 AI内容推流系统 — ¥199/月
🔗 n8n工作流自动化系统 — ¥149/月
🕷️ AI智能网页爬虫 — ¥49/月
🖊️ 易云章 API 控制面板 — ¥199/月

💳 付款：USDT TRC20 `TFfwcPBSF2t5pruoRfN1McxnuStFNkX3Cy`
   PayPal：paypalyinanzo@hotmail.com
   Telegram：@diquchaxun78_bot

付款后5分钟内秘钥自动发到本窗口 ✅"""

    if any(k in c for k in ["试", "测试", "hello", "你好", "hi", "在", "嗨"]):
        return "您好！我是灵犀 🤖 灵犀集市的AI客服。请问您想购买哪个工具？"

    if any(k in c for k in ["退款", "骗子", "不行", "不能用", "坏", "问题"]):
        return "抱歉给您带来不好的体验！请描述具体问题，我来帮您解决。也可以联系 Telegram：@diquchaxun78_bot"

    if any(k in c for k in ["下载", "激活", "秘钥", "key", "license"]):
        return "💡 购买后秘钥自动发送到本对话框。您也可以访问「秘钥激活」标签页手动激活。如有问题请联系客服。"

    return f"""收到！我来帮您 😊

目前您可以直接在网站上购买，付款后秘钥自动推送到本对话框 ✅

💬 有任何问题请描述，我可以帮您解答。
📩 或联系 Telegram：@diquchaxun78_bot"""

# ══════════════════════════════════════════════════════════════
#  核心处理：轮询 inbox → 生成回复 → 写入 customer_messages
# ══════════════════════════════════════════════════════════════

# 记录已处理的 visitor_id（内存缓存，防止重复处理）
_processed = set()

def process_inbox():
    inbox, _ = read_messages()
    if not inbox:
        return

    msgs_db, msgs_sha = read_customer_messages()
    changed = False

    for vid, item in inbox.items():
        if vid in _processed:
            continue
        _processed.add(vid)

        # 初始化访客消息库
        if vid not in msgs_db:
            msgs_db[vid] = {"messages": []}

        # 客户消息
        msgs_db[vid]["messages"].append({
            "role": "user",
            "content": item.get("content", ""),
            "time": item.get("time", time.time()),
        })

        # 生成自动回复
        reply = generate_reply(item.get("content", ""))
        msgs_db[vid]["messages"].append({
            "role": "agent",
            "content": reply,
            "agent": "灵犀",
            "time": time.time(),
        })
        changed = True
        print(f"[{time.strftime('%H:%M:%S')}] 💬 {vid}: {item.get('content','')[:40]}")

    if changed:
        save_customer_messages(msgs_db)
        # 清空 inbox（已处理）
        write_file(INBOX_FILE, "{}", msg="chat: 清空已处理的 inbox")

def load_pending():
    if os.path.exists(PENDING_FILE):
        try:
            return json.load(open(PENDING_FILE))
        except:
            return []
    return []

def save_pending(pending):
    open(PENDING_FILE, 'w').write(json.dumps(pending, ensure_ascii=False, indent=2))

def gen_key():
    p = lambda: ''.join(random.choices(CHARS, k=4))
    return f"LING-{p()}-{p()}"

def add_secret_to_gist(key, product_id):
    try:
        req = urllib.request.Request(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            gist = json.loads(r.read())
        raw_url = gist["files"]["secrets.json"]["raw_url"]
        secrets = json.loads(urllib.request.urlopen(raw_url, timeout=10).read())
        secrets.append({"key": key, "productId": product_id, "used": False, "created": time.strftime("%Y-%m-%d")})
        body = json.dumps({
            "description": "灵犀集市 - 秘钥数据库",
            "files": {"secrets.json": {"content": json.dumps(secrets, ensure_ascii=False, indent=2)}}
        }).encode()
        req2 = urllib.request.Request(f"https://api.github.com/gists/{GIST_ID}", data=body,
            headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}, method="PATCH")
        with urllib.request.urlopen(req2, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"  Gist 写入失败: {e}")
        return False

def deliver_secret(vid, secret_key, product_id):
    download = PRODUCT_DOWNLOADS.get(product_id, "https://github.com/nima54851/ai-supermarket/releases")
    pname = PRODUCT_NAMES.get(product_id, product_id)
    content = f"""🔑 *您的秘钥已到！*

商品：{pname}
秘钥：`{secret_key}`

━━━━━━━━━━━━━━━━━

📥 *下载地址：*
`{download}`

━━━━━━━━━━━━━━━━━

💡 *激活方法：*
① 打开网站 → 秘钥激活
② 粘贴上方秘钥 → 点激活
③ 自动解锁下载权限

⏰ 秘钥永久有效，禁止转让。"""

    # 写入 customer_messages
    msgs_db, _ = read_customer_messages()
    if vid not in msgs_db:
        msgs_db[vid] = {"messages": []}
    msgs_db[vid]["messages"].append({
        "role": "agent", "content": content, "agent": "灵犀", "time": time.time()
    })
    save_customer_messages(msgs_db)
    print(f"  ✅ 秘钥已送达 {vid[:12]} → {secret_key}")

def process_pending_deliveries():
    pending = load_pending()
    active = [p for p in pending if not p.get("delivered") and p.get("visitor_id")]
    if not active:
        return
    print(f"\n[{time.strftime('%H:%M:%S')}] 📦 待发货: {len(active)} 条")
    changed = False
    for item in active:
        vid, pid = item.get("visitor_id", ""), item.get("product_id", "unknown")
        key = gen_key()
        if add_secret_to_gist(key, pid):
            deliver_secret(vid, key, pid)
            item["delivered"] = True
            item["delivered_at"] = time.strftime("%Y-%m-%d %H:%M")
            item["secret_key"] = key
            changed = True
    if changed:
        save_pending(pending)

# ══════════════════════════════════════════════════════════════
#  本地 HTTP 服务（可选，用于本地测试）
# ══════════════════════════════════════════════════════════════

class ChatHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_POST(self):
        if self.path != "/api/chat/send":
            self.send_error(404)
            return
        import urllib.parse
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="ignore")
        params = {}
        for pair in body.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[urllib.parse.unquote(k)] = urllib.parse.unquote(v)
        vid = params.get("visitor_id", "")
        content = params.get("content", "")
        if not vid or not content:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok":false}')
            return

        # 写入 GitHub inbox.json
        inbox, sha = read_messages()
        inbox[vid] = {"content": content, "time": time.time()}
        write_file(INBOX_FILE, json.dumps(inbox, ensure_ascii=False, indent=2), msg="chat: 客户新消息")
        print(f"[{time.strftime('%H:%M:%S')}] 💬 {vid[:12]}: {content[:40]}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

def run_http(port=6061):
    server = HTTPServer(("0.0.0.0", port), ChatHandler)
    print(f"🌐 本地测试 HTTP: http://localhost:{port}/api/chat/send")
    server.serve_forever()

# ══════════════════════════════════════════════════════════════
#  启动
# ══════════════════════════════════════════════════════════════

def main():
    print("🚀 灵犀客服引擎 v5 启动（纯轮询版）")
    print(f"   轮询 GitHub inbox.json 每 {POLL_INTERVAL} 秒")
    print(f"   待发货队列处理每 {POLL_INTERVAL} 秒")
    print(f"   本地 HTTP: http://localhost:6061/api/chat/send（测试用）\n")

    # 本地 HTTP 线程（仅测试用，外部访问走 GitHub API）
    t = threading.Thread(target=run_http, daemon=True)
    t.start()

    while True:
        try:
            process_inbox()
        except Exception as e:
            print(f"  ⚠️ inbox 处理异常: {e}")
        try:
            process_pending_deliveries()
        except Exception as e:
            print(f"  ⚠️ 发货处理异常: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
