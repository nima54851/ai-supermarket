#!/usr/bin/env python3
"""
AI超市 自动发货系统
- 接收 PayPal IPN 通知
- 验证支付真实性
- 自动发送下载链接

环境变量:
  SMTP_HOST     SMTP服务器地址
  SMTP_PORT     SMTP端口 (默认 587)
  SMTP_USER     SMTP用户名
  SMTP_PASS     SMTP密码
  SMTP_FROM     发件人邮箱
  WEBHOOK_URL   本服务对外URL（用于日志显示）

依赖: pip install flask pyyaml
运行: python3 paypal-webhook.py
"""

import os
import sys
import json
import time
import logging
import threading
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime
from collections import defaultdict

from flask import Flask, request, jsonify

# ── 配置 ──
PAYPAL_EMAIL = "yinanzo@hotmail.com"
PAYPAL_API_VERIFY = "https://ipnpb.paypal.com/cgi-bin/webscr"
# 测试用沙箱地址（正式环境用上面的）
PAYPAL_API_VERIFY_TEST = "https://ipnpb.sandbox.paypal.com/cgi-bin/webscr"

# 商品ID → 下载链接映射
PRODUCT_DOWNLOADS = {
    "telegram-bot":       "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/telegram-bot.zip",
    "github-automation":   "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/github-automation.zip",
    "content-promoter":   "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/content-promoter.zip",
    "n8n-workflow":       "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/n8n-workflow.zip",
    "video-gen":          "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/video-gen.zip",
    "ai-manga":           "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/ai-manga.zip",
    "idea-generator":     "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/idea-generator.zip",
    "ppt-generator":      "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/ppt-generator.zip",
    "ai-writing":         "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/ai-writing.zip",
    "cross-border-ai":     "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/cross-border-ai.zip",
    "ai-agent":           "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/ai-agent.zip",
    "3d-generator":       "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/3d-generator.zip",
    "web-scraper":        "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/web-scraper.zip",
    "database-toolkit":   "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/database-toolkit.zip",
    "security-scanner":   "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/security-scanner.zip",
    "design-toolkit":     "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/design-toolkit.zip",
    "game-dev-kit":       "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/game-dev-kit.zip",
}

# 商品名称 → ID 映射（用于从 item_name 解析）
PRODUCT_NAME_MAP = {
    "telegram号码查询机器人": "telegram-bot",
    "telegram-bot": "telegram-bot",
    "github agent自动化系统": "github-automation",
    "github-automation": "github-automation",
    "ai内容推流系统": "content-promoter",
    "content-promoter": "content-promoter",
    "n8n工作流自动化系统": "n8n-workflow",
    "n8n-workflow": "n8n-workflow",
    "ai视频生成助手": "video-gen",
    "video-gen": "video-gen",
    "ai漫剧生成系统": "ai-manga",
    "ai-manga": "ai-manga",
    "脑洞助手": "idea-generator",
    "创意生成器": "idea-generator",
    "idea-generator": "idea-generator",
    "ppt智能生成器": "ppt-generator",
    "ppt-generator": "ppt-generator",
    "ai代写定制服务系统": "ai-writing",
    "ai-writing": "ai-writing",
    "跨境电商ai助手": "cross-border-ai",
    "cross-border-ai": "cross-border-ai",
    "多平台ai agent助手": "ai-agent",
    "ai-agent": "ai-agent",
    "3d模型生成系统": "3d-generator",
    "3d-generator": "3d-generator",
    "ai智能网页爬虫": "web-scraper",
    "web-scraper": "web-scraper",
    "ai数据库管理工具包": "database-toolkit",
    "database-toolkit": "database-toolkit",
    "ai代码安全审计系统": "security-scanner",
    "security-scanner": "security-scanner",
    "ai设计素材生成器": "design-toolkit",
    "design-toolkit": "design-toolkit",
    "ai游戏开发工具包": "game-dev-kit",
    "game-dev-kit": "game-dev-kit",
}

# 商品中文名（用于邮件显示）
PRODUCT_DISPLAY = {
    "telegram-bot": "📱 Telegram号码查询机器人",
    "github-automation": "⚡ GitHub Agent自动化系统",
    "content-promoter": "📣 AI内容推流系统",
    "n8n-workflow": "🔗 n8n工作流自动化系统",
    "video-gen": "🎬 AI视频生成助手",
    "ai-manga": "🎭 AI漫剧生成系统",
    "idea-generator": "🧠 脑洞助手/创意生成器",
    "ppt-generator": "📊 PPT智能生成器",
    "ai-writing": "✍️ AI代写定制服务系统",
    "cross-border-ai": "🌐 跨境电商AI助手",
    "ai-agent": "🤖 多平台AI Agent助手",
    "3d-generator": "🎨 3D模型生成系统",
    "web-scraper": "🕷️ AI智能网页爬虫",
    "database-toolkit": "🗄️ AI数据库管理工具包",
    "security-scanner": "🔒 AI代码安全审计系统",
    "design-toolkit": "🖌️ AI设计素材生成器",
    "game-dev-kit": "🎮 AI游戏开发工具包",
}

# SMTP 配置（环境变量）
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "yinanzo@hotmail.com")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://YOUR_IP:5000")

# 订单存储文件
ORDERS_FILE = "orders.json"
PROCESSED_FILE = "processed_ipns.txt"  # 防重复处理

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ── 工具函数 ──

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return defaultdict(list)

def save_orders(orders):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(dict(orders), f, ensure_ascii=False, indent=2)

def mark_processed(txn_id):
    with open(PROCESSED_FILE, "a") as f:
        f.write(txn_id + "\n")

def is_processed(txn_id):
    if not os.path.exists(PROCESSED_FILE):
        return False
    with open(PROCESSED_FILE) as f:
        return txn_id in f.read()

def parse_product_from_item_name(item_name):
    """从 PayPal item_name 解析商品ID"""
    if not item_name:
        return None
    item = item_name.strip()
    # 去掉 "AI超市 - " 前缀
    if item.startswith("AI超市 - ") or item.startswith("AI超市 -"):
        item = item.replace("AI超市 - ", "").replace("AI超市 -", "").strip()
    # 直接匹配
    if item in PRODUCT_NAME_MAP:
        return PRODUCT_NAME_MAP[item]
    # 模糊匹配
    for key, pid in PRODUCT_NAME_MAP.items():
        if key in item or item in key:
            return pid
    # 尝试从商品ID直接匹配
    for pid in PRODUCT_DOWNLOADS:
        if pid in item.lower() or item.lower() in pid:
            return pid
    logger.warning(f"无法识别商品: {item_name}")
    return None

def send_email(to_email, subject, html_body, text_body):
    """发送邮件"""
    if not SMTP_HOST:
        logger.warning("SMTP未配置，跳过邮件发送")
        return False
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to_email

        part1 = MIMEText(text_body, "plain", "utf-8")
        part2 = MIMEText(html_body, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [to_email], msg.as_string())

        logger.info(f"✅ 邮件已发送至 {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ 邮件发送失败: {e}")
        return False

def send_download_link_buyer(email, product_id, txn_id, amount, payer_email):
    """发送下载链接给买家"""
    product_name = PRODUCT_DISPLAY.get(product_id, product_id)
    download_url = PRODUCT_DOWNLOADS.get(product_id, "")

    subject = f"📦 AI超市 - 您的 {product_name} 下载链接"

    text_body = f"""
您好！

感谢您的购买！以下是您的下载链接：

商品: {product_name}
订单号: {txn_id}
金额: ¥{amount}

🔗 下载链接:
{download_url}

⚠️ 链接永久有效，请及时下载保存！

如有问题，欢迎联系客服: @diquchaxun78_bot

—— AI超市
"""

    html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;margin:0;padding:20px;">
  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
    <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:30px;text-align:center;">
      <h1 style="color:#fff;margin:0;font-size:24px;">🛒 AI超市</h1>
      <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;">购买成功！您的下载链接来了 🎉</p>
    </div>
    <div style="padding:30px;">
      <div style="background:#f8f9ff;border-radius:10px;padding:20px;margin-bottom:20px;border:1px solid #e0e7ff;">
        <h3 style="margin:0 0 10px;color:#4f46e5;">📦 订单详情</h3>
        <table style="width:100%;font-size:14px;">
          <tr><td style="padding:4px 0;color:#666;">商品</td><td style="text-align:right;font-weight:bold;">{product_name}</td></tr>
          <tr><td style="padding:4px 0;color:#666;">订单号</td><td style="text-align:right;font-size:12px;color:#888;">{txn_id}</td></tr>
          <tr><td style="padding:4px 0;color:#666;">金额</td><td style="text-align:right;font-weight:bold;color:#059669;">¥{amount}</td></tr>
        </table>
      </div>
      <a href="{download_url}" style="display:block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;text-align:center;padding:16px;border-radius:10px;font-size:16px;font-weight:bold;text-decoration:none;margin-bottom:16px;box-shadow:0 4px 15px rgba(99,102,241,0.4);">
        🔗 点击下载 {product_name}
      </a>
      <p style="font-size:13px;color:#888;text-align:center;">
        ⚠️ 链接永久有效，请及时下载保存<br>
        如有问题联系客服: <strong>@diquchaxun78_bot</strong>
      </p>
    </div>
    <div style="background:#f9fafb;padding:15px;text-align:center;font-size:12px;color:#aaa;border-top:1px solid #eee;">
      AI超市 · 购买AI能力，像买菜一样简单
    </div>
  </div>
</body>
</html>
"""

    success = send_email(email, subject, html_body, text_body)

    # 同时记录到订单
    orders = load_orders()
    orders[email].append({
        "txn_id": txn_id,
        "product_id": product_id,
        "product_name": product_name,
        "amount": amount,
        "payer_email": payer_email,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "email_sent": success,
    })
    save_orders(orders)

    logger.info(f"📋 订单已记录: {email} -> {product_id}")
    return True

def verify_paypal_ipn(post_data):
    """向 PayPal 验证 IPN"""
    # 添加验证命令
    verify_data = b"cmd=_notify-validate&" + post_data
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "AI-Supermarket-Python/1.0",
    }
    try:
        # 优先用正式环境
        for api_url in [PAYPAL_API_VERIFY, PAYPAL_API_VERIFY_TEST]:
            try:
                req = urllib.request.Request(api_url, data=verify_data, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    result = resp.read().decode()
                    if result == "VERIFIED":
                        logger.info(f"✅ IPN 验证通过 ({api_url})")
                        return True
                    elif result == "INVALID":
                        logger.warning(f"⚠️ IPN 验证失败 (INVALID): {api_url}")
                        return False
            except Exception as e:
                logger.warning(f"⚠️ 验证请求失败 ({api_url}): {e}")
                continue
        return False
    except Exception as e:
        logger.error(f"❌ IPN 验证异常: {e}")
        return False

# ── Flask 路由 ──

@app.route("/webhook/paypal", methods=["POST"])
def paypal_webhook():
    """PayPal IPN 回调"""
    logger.info("=" * 50)
    logger.info(f"📩 收到 PayPal IPN 请求")

    # 解析 POST 数据
    post_data = request.get_data()
    params = urllib.parse.parse_qs(post_data.decode("utf-8"))
    # 处理同键多值
    data = {}
    for k, v in params.items():
        data[k] = v[0] if len(v) == 1 else v

    # 提取关键字段
    payment_status = data.get("payment_status", "")
    txn_id = data.get("txn_id", "")
    item_name = data.get("item_name", "")
    receiver_email = data.get("receiver_email", "")
    mc_gross = data.get("mc_gross", "")
    payer_email = data.get("payer_email", "")
    payer_id = data.get("payer_id", "")
    mc_currency = data.get("mc_currency", "")

    logger.info(f"  txn_id: {txn_id}")
    logger.info(f"  status: {payment_status}")
    logger.info(f"  item: {item_name}")
    logger.info(f"  amount: {mc_gross} {mc_currency}")
    logger.info(f"  receiver: {receiver_email}")
    logger.info(f"  payer: {payer_email}")

    # 1. 基础校验：收款人必须是商家邮箱
    if receiver_email.lower() != PAYPAL_EMAIL.lower():
        logger.warning(f"⚠️ 收款邮箱不匹配: {receiver_email} != {PAYPAL_EMAIL}")
        return jsonify({"error": "not our payment"}), 400

    # 2. 校验支付状态
    if payment_status != "Completed":
        logger.info(f"⏳ 非完成状态，跳过: {payment_status}")
        return jsonify({"status": "ignored", "reason": payment_status}), 200

    # 3. 防重复
    if txn_id and is_processed(txn_id):
        logger.info(f"⏭️ 已处理过的交易，跳过: {txn_id}")
        return jsonify({"status": "duplicate"}), 200

    # 4. 验证 IPN 真实性（向 PayPal 确认）
    if not verify_paypal_ipn(post_data):
        logger.warning(f"❌ IPN 验证失败: {txn_id}")
        return jsonify({"error": "verification failed"}), 400

    # 5. 解析商品
    product_id = parse_product_from_item_name(item_name)
    if not product_id:
        logger.error(f"❌ 无法识别商品: {item_name}")
        # 仍记录订单，但不发下载链接
        orders = load_orders()
        orders[payer_email].append({
            "txn_id": txn_id,
            "item_name": item_name,
            "amount": mc_gross,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "product_unknown",
        })
        save_orders(orders)
        return jsonify({"status": "recorded", "product": "unknown"}), 200

    # 6. 发货！
    download_url = PRODUCT_DOWNLOADS.get(product_id, "")
    logger.info(f"🚀 开始发货: {product_id} -> {payer_email}")

    # 发送下载链接
    email_sent = False
    if payer_email:
        email_sent = send_download_link_buyer(payer_email, product_id, txn_id, mc_gross, payer_email)
    else:
        logger.warning("⚠️ 没有买家邮箱，无法发送邮件")

    # 标记已处理
    if txn_id:
        mark_processed(txn_id)

    logger.info(f"✅ 发货完成: {txn_id} | 邮件: {'✅' if email_sent else '⚠️ 未配置'}")
    logger.info("=" * 50)

    return jsonify({
        "status": "success",
        "txn_id": txn_id,
        "product_id": product_id,
        "email_sent": email_sent,
    }), 200

@app.route("/webhook/test", methods=["POST", "GET"])
def test_webhook():
    """测试端点"""
    logger.info(f"🧪 测试请求: {request.get_json() or request.args}")
    return jsonify({
        "status": "ok",
        "message": "AI超市 Webhook 运行正常",
        "time": datetime.now().isoformat(),
        "smtp_configured": bool(SMTP_HOST),
        "products_loaded": len(PRODUCT_DOWNLOADS),
    })

@app.route("/orders", methods=["GET"])
def view_orders():
    """查看订单（简单密码保护）"""
    auth = request.authorization
    if auth and auth.username == "admin" and auth.password == os.environ.get("ADMIN_PASS", "ai-market-2026"):
        orders = load_orders()
        return jsonify({"orders": dict(orders), "count": len(orders)})
    return jsonify({"error": "unauthorized"}), 401

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "uptime": "ok"})

# ── 启动 ──
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║       🛒 AI超市 自动发货系统  v1.0              ║
╠══════════════════════════════════════════════════╣
║  📡 Webhook 端点: http://0.0.0.0:5000           ║
║     → /webhook/paypal  (PayPal IPN 回调)        ║
║     → /webhook/test    (健康检查)               ║
║     → /orders          (查看订单)               ║
╠══════════════════════════════════════════════════╣
║  📧 SMTP: {}            ║
║  📦 商品数: {}                              ║
╚══════════════════════════════════════════════════╝
    """.strip().format(
        "已配置" if SMTP_HOST else "❌ 未配置（需设置环境变量）",
        len(PRODUCT_DOWNLOADS)
    ))
    print()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
