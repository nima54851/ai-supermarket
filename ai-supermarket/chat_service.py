#!/usr/bin/env python3
"""
灵犀集市 - 网站客服聊天服务 v4
改进：支持图片上传 + 实时回复 + 加速轮询
"""
import sqlite3, uuid, time, json, threading, os, base64
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

DB = "/tmp/chat_messages.db"
IMG_DIR = "/tmp/chat_images"
GITHUB_REPO = "nima54851/ai-supermarket"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_MSG_PATH = "inbox.json"
COMMIT_SHA = "872efe84b7fa9d2c3e4f1a8b6c9d2e3f4a5b6c7d"
os.makedirs(IMG_DIR, exist_ok=True)

app = Flask(__name__)
app.json.ensure_ascii = False

# ─── DB ───────────────────────────────────────────────────────────────
def init_db():
    db = sqlite3.connect(DB)
    db.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id TEXT PRIMARY KEY, created_at REAL, display_name TEXT DEFAULT ''
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT, role TEXT, content TEXT,
            agent TEXT, created_at REAL,
            read_by_agent INTEGER DEFAULT 0,
            synced INTEGER DEFAULT 0,
            image_path TEXT,
            FOREIGN KEY(visitor_id) REFERENCES visitors(id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS last_agent_reply (
            visitor_id TEXT PRIMARY KEY, last_reply_time REAL
        )
    """)
    db.commit()
    db.close()

init_db()

# ─── 通知队列（用于 SSE 实时推送）───────────────────────────────────
_listeners = {}
_listener_lock = threading.Lock()

def notify_visitor(visitor_id):
    with _listener_lock:
        if visitor_id in _listeners:
            for q in _listeners[visitor_id]:
                q.append(True)

def subscribe(visitor_id):
    with _listener_lock:
        if visitor_id not in _listeners:
            _listeners[visitor_id] = []
        q = []
        _listeners[visitor_id].append(q)
    return q

def unsubscribe(visitor_id, q):
    with _listener_lock:
        if visitor_id in _listeners and q in _listeners[visitor_id]:
            _listeners[visitor_id].remove(q)

# ─── GitHub 同步 ────────────────────────────────────────────────────
_sync_lock = threading.Lock()

def gh_request(method, url, data=None):
    import urllib.request
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}, e.code
    except Exception as e:
        return {"error": str(e)}, 0

def sync_to_github():
    with _sync_lock:
        db = sqlite3.connect(DB)
        rows = db.execute(
            "SELECT id,visitor_id,role,content,agent,created_at,image_path FROM messages WHERE synced=0"
        ).fetchall()
        if not rows:
            db.close()
            return
        db.close()

        # 读取 GitHub
        d, s = gh_request("GET",
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_MSG_PATH}")
        sha = d.get("sha") if d else None

        # 读 CDN
        inbox = {"version": 0, "messages": {}, "created": "2026-08-03"}
        try:
            import urllib.request
            req2 = urllib.request.Request(
                f"https://cdn.jsdelivr.net/gh/{GITHUB_REPO}@{COMMIT_SHA}/{GITHUB_MSG_PATH}",
                headers={"Accept": "application/json"}
            )
            with urllib.request.urlopen(req2, timeout=10) as r:
                inbox = json.loads(r.read())
        except:
            pass

        db = sqlite3.connect(DB)
        for r in rows:
            msg_id, vid, role, content, agent, ts, img = r
            if vid not in inbox["messages"]:
                inbox["messages"][vid] = []
            msg = {"id": msg_id, "role": role, "content": content,
                   "agent": agent, "time": ts}
            if img:
                msg["image"] = f"/img/{os.path.basename(img)}"
            inbox["messages"][vid].append(msg)
            db.execute("UPDATE messages SET synced=1 WHERE id=?", [msg_id])
        inbox["version"] = inbox.get("version", 0) + 1
        db.commit()
        db.close()

        body = {
            "message": f"update messages v{inbox['version']}",
            "content": base64.b64encode(json.dumps(inbox, ensure_ascii=False).encode()).decode(),
        }
        if sha:
            body["sha"] = sha
        d2, s2 = gh_request("PUT",
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_MSG_PATH}", body)
        if s2 and 200 <= s2 < 300:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 同步 {len(rows)} 条到 GitHub ✓")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] GitHub同步失败: {d2}")

# ─── API: 发消息（支持图片）─────────────────────────────────────────
@app.route("/api/chat/send", methods=["POST"])
def send_message():
    content = (request.form.get("content") or "").strip()
    visitor_id = (request.form.get("visitor_id") or "").strip()
    img_b64 = request.form.get("image")

    if not content and not img_b64:
        return jsonify({"ok": False, "error": "内容不能为空"}), 400
    if len(content) > 2000:
        return jsonify({"ok": False, "error": "内容过长（限2000字）"}), 400

    # 创建访客
    if visitor_id:
        db = sqlite3.connect(DB)
        db.execute("INSERT OR IGNORE INTO visitors (id, created_at) VALUES (?, ?)",
                   [visitor_id, time.time()])
        db.commit()
        db.close()
    else:
        visitor_id = "v" + uuid.uuid4().hex[:12]
        db = sqlite3.connect(DB)
        db.execute("INSERT INTO visitors (id, created_at) VALUES (?, ?)",
                   [visitor_id, time.time()])
        db.commit()
        db.close()

    img_path = None
    # 保存图片
    if img_b64:
        try:
            img_data = base64.b64decode(img_b64.split(",")[1] if "," in img_b64 else img_b64)
            fname = f"{visitor_id}_{int(time.time()*1000)}.jpg"
            img_path = os.path.join(IMG_DIR, fname)
            with open(img_path, "wb") as f:
                f.write(img_data)
        except Exception as e:
            print(f"图片保存失败: {e}")
            img_path = None

    db = sqlite3.connect(DB)
    db.execute(
        "INSERT INTO messages (visitor_id,role,content,created_at,image_path) VALUES (?,?,?,?,?)",
        [visitor_id, "user", content or " [图片] ", time.time(), img_path]
    )
    db.commit()
    db.close()

    threading.Thread(target=sync_to_github, daemon=True).start()
    notify_visitor(visitor_id)

    return jsonify({"ok": True, "visitor_id": visitor_id})

# ─── API: 实时轮询（5秒超时）────────────────────────────────────────
@app.route("/api/chat/poll")
def poll_messages():
    visitor_id = request.args.get("visitor_id", "")
    last_time = float(request.args.get("last", 0))

    if not visitor_id:
        return jsonify({"messages": [], "has_new": False})

    db = sqlite3.connect(DB)
    rows = db.execute("""
        SELECT role, content, agent, created_at FROM messages
        WHERE visitor_id=? AND created_at>?
        ORDER BY created_at ASC
    """, [visitor_id, last_time]).fetchall()
    db.close()

    msgs = [{"role": r[0], "content": r[1], "agent": r[2], "time": r[3]} for r in rows]

    return jsonify({
        "messages": msgs,
        "has_new": len(msgs) > 0
    })

# ─── API: 完整历史 ──────────────────────────────────────────────────
@app.route("/api/chat/history")
def history():
    visitor_id = request.args.get("visitor_id", "")
    if not visitor_id:
        return jsonify({"messages": []})

    db = sqlite3.connect(DB)
    rows = db.execute("""
        SELECT role, content, agent, created_at FROM messages
        WHERE visitor_id=? ORDER BY created_at ASC LIMIT 50
    """, [visitor_id]).fetchall()
    db.close()

    messages_out = [{"role": r[0], "content": r[1], "agent": r[2], "time": r[3]} for r in rows]
    return jsonify({"ok": True, "messages": messages_out})

# ─── API: 图片访问 ──────────────────────────────────────────────────
@app.route("/img/")
def serve_image(filename):
    from flask import send_file
    safe_name = os.path.basename(filename)
    path = os.path.join(IMG_DIR, safe_name)
    if os.path.exists(path):
        return send_file(path, mimetype="image/jpeg")
    return "Not found", 404

# ─── API: 灵犀轮询未读 ──────────────────────────────────────────────
@app.route("/api/agent/poll", methods=["GET"])
def agent_poll():
    db = sqlite3.connect(DB)
    rows = db.execute("""
        SELECT m.id, m.visitor_id, m.content, m.created_at, m.image_path
        FROM messages m JOIN visitors v ON v.id=m.visitor_id
        WHERE m.read_by_agent=0 AND m.role='user'
        ORDER BY m.created_at ASC LIMIT 30
    """).fetchall()
    db.commit()
    db.close()
    return jsonify({"ok": True, "messages": [
        {"id": r[0], "visitor_id": r[1], "content": r[2],
         "created_at": r[3], "image": f"/img/{os.path.basename(r[4])}" if r[4] else None}
        for r in rows
    ]})

# ─── API: 灵犀回复 ──────────────────────────────────────────────────
@app.route("/api/agent/reply", methods=["POST"])
def agent_reply():
    data = request.json
    vid = (data.get("visitor_id") or "").strip()
    content = (data.get("content") or "").strip()
    agent = (data.get("agent") or "灵犀").strip()

    if not vid or not content:
        return jsonify({"ok": False, "error": "缺少参数"}), 400

    db = sqlite3.connect(DB)
    db.execute(
        "INSERT INTO messages (visitor_id,role,content,agent,created_at,synced) VALUES (?,?,?,?,?,1)",
        [vid, "agent", content, agent, time.time()]
    )
    db.commit()
    db.close()

    notify_visitor(vid)
    threading.Thread(target=sync_to_github, daemon=True).start()
    return jsonify({"ok": True})

# ─── API: 标记已读 ──────────────────────────────────────────────────
@app.route("/api/agent/mark_read", methods=["POST"])
def mark_read():
    ids = request.json.get("ids", [])
    if ids:
        db = sqlite3.connect(DB)
        placeholders = ",".join("?" * len(ids))
        db.execute(f"UPDATE messages SET read_by_agent=1 WHERE id IN ({placeholders})", ids)
        db.commit()
        db.close()
    return jsonify({"ok": True})

# ─── API: 配置 ──────────────────────────────────────────────────────
@app.route("/api/chat/config")
def chat_config():
    return jsonify({
        "poll_interval_ms": 5000,
        "base_url": "http://localhost:6061"
    })

# ─── 健康检查 ───────────────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

# ─── 启动 ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("💬 灵犀集市客服服务 v4 启动，端口 6061")
    print("   支持图片上传 + 5秒实时轮询")
    app.run(host="0.0.0.0", port=6061, debug=False, threaded=True)
