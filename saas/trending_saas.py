"""
GitHub Trending SaaS - API 服务
用户无需安装，直接调用 API 即可获取 GitHub 热门项目推送
"""
from flask import Flask, request, jsonify, render_template, send_file
import requests
import os
from datetime import datetime
import threading
import json

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "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")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")

# 订阅用户列表
subscribers = {}


def fetch_github_trending(language=None, limit=8):
    """获取 GitHub 热门项目"""
    query = "stars:>500+created:>2026-06-01"
    if language:
        query += f"+language:{language}"
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={limit}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        return None
    return resp.json().get("items", [])


def format_report(repos, language=None):
    """格式化报告"""
    today = datetime.now().strftime("%Y年%m月%d日")
    lang_tag = f"[{language}] " if language else ""
    lines = []
    for i, repo in enumerate(repos, 1):
        stars = repo.get("stargazers_count", 0)
        stars_str = f"{stars/1000:.1f}k" if stars >= 1000 else str(stars)
        lines.append(
            f"{i}. {lang_tag}{repo['full_name']}\n"
            f"   ⭐ {stars_str} | 🍴 {repo.get('forks_count', 0)} | {repo.get('language', 'Other')}\n"
            f"   📝 {repo.get('description') or '无描述'}\n"
            f"   🔗 {repo['html_url']}"
        )
    top = repos[0] if repos else None
    top_stars = top.get("stargazers_count", 0) if top else 0
    top_stars_str = f"{top_stars/1000:.1f}k" if top_stars >= 1000 else str(top_stars)
    header = f"🔥 GitHub 热门 · {today}"
    if language:
        header += f" · {language}"
    report = f"{header}\n\n" + "\n\n".join(lines)
    report += f"\n\n━━━━━━━━━━━━━━━━━\n📊 共 {len(repos)} 个项目"
    if top:
        report += f" | 🏆 最热: {top['full_name']} ⭐{top_stars_str}"
    report += "\n🤖 by 灵犀 SaaS"
    return report


def send_telegram(text, chat_id):
    """发送 Telegram 消息"""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
    return resp.status_code == 200


@app.route("/")
def index():
    import os
    path = os.path.join(os.path.dirname(__file__), "index.html")
    return send_file(path) if os.path.exists(path) else "index.html not found"

@app.route("/api/info")
def api_info():
    return jsonify({
        "service": "GitHub Trending SaaS",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "/": "Web 订阅页面",
            "/api/trending": "GET - 获取今日 GitHub 热门",
            "/api/trending?language=Python&limit=5": "GET - 指定语言",
            "/api/push?chat_id=xxx": "POST - 推送到 Telegram",
            "/api/subscribe?chat_id=xxx": "GET - 订阅每日推送"
        }
    })


@app.route("/api/trending")
def api_trending():
    language = request.args.get("language")
    limit = int(request.args.get("limit", 8))
    repos = fetch_github_trending(language=language, limit=limit)
    if repos is None:
        return jsonify({"error": "GitHub API 请求失败，请稍后重试"}), 502
    report = format_report(repos, language=language)
    return jsonify({
        "success": True,
        "count": len(repos),
        "report": report
    })


@app.route("/api/push", methods=["POST"])
def api_push():
    data = request.get_json() or {}
    chat_id = data.get("chat_id") or request.args.get("chat_id")
    language = data.get("language")
    limit = int(data.get("limit", 8))
    if not chat_id:
        return jsonify({"error": "缺少 chat_id 参数"}), 400
    repos = fetch_github_trending(language=language, limit=limit)
    if repos is None:
        return jsonify({"error": "GitHub API 请求失败"}), 502
    report = format_report(repos, language=language)
    ok = send_telegram(report, chat_id)
    if ok:
        return jsonify({"success": True, "message": "推送成功", "count": len(repos)})
    else:
        return jsonify({"success": False, "error": "Telegram 推送失败，请检查 Bot Token"}), 500


@app.route("/api/subscribe", methods=["GET", "POST"])
def api_subscribe():
    chat_id = request.args.get("chat_id") or (request.get_json() or {}).get("chat_id")
    if not chat_id:
        return jsonify({"error": "缺少 chat_id"}), 400
    subscribers[chat_id] = {
        "chat_id": chat_id,
        "subscribed_at": datetime.now().isoformat()
    }
    # 发测试消息
    repos = fetch_github_trending(limit=3)
    if repos:
        report = format_report(repos)
        send_telegram("✅ 订阅成功！每天早9点自动推送 GitHub 热门项目", chat_id)
    return jsonify({"success": True, "subscribers_count": len(subscribers)})


@app.route("/api/daily-push", methods=["POST"])
def api_daily_push():
    """定时推送，给管理员用"""
    # 简单密码保护
    token = request.headers.get("X-Admin-Token", "")
    if token != os.environ.get("ADMIN_TOKEN", "lingxi2025"):
        return jsonify({"error": "Unauthorized"}), 401
    count = 0
    for chat_id in list(subscribers.keys()):
        repos = fetch_github_trending(limit=8)
        if repos:
            report = format_report(repos)
            if send_telegram(report, chat_id):
                count += 1
    return jsonify({"success": True, "pushed": count, "total_subscribers": len(subscribers)})


@app.route("/webhook/telegram", methods=["POST"])
def telegram_webhook():
    """Telegram 机器人 webhook"""
    data = request.get_json()
    if not data.get("message"):
        return "ok"
    chat_id = str(data["message"]["chat"]["id"])
    text = data["message"].get("text", "")
    if text == "/start" or text == "/subscribe":
        repos = fetch_github_trending(limit=5)
        if repos:
            report = format_report(repos)
            send_telegram("🔥 欢迎！这是今日 GitHub 热门：\n\n" + report, chat_id)
            send_telegram("✅ 已自动订阅，每天早9点推送", chat_id)
        subscribers[chat_id] = {"chat_id": chat_id, "subscribed_at": datetime.now().isoformat()}
    elif text == "/trending":
        repos = fetch_github_trending(limit=8)
        if repos:
            report = format_report(repos)
            send_telegram(report, chat_id)
    elif text == "/help":
        send_telegram("📖 命令列表：\n/start - 订阅并获取今日热门\n/trending - 获取最新热门\n/help - 显示帮助", chat_id)
    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
