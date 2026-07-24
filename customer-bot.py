#!/usr/bin/env python3
"""
AI超市 客服机器人
用法: python3 customer-bot.py
依赖: pip install python-telegram-bot

环境变量（可选）:
  TELEGRAM_PROXY  — 例如 socks5://127.0.0.1:1080
  TELEGRAM_API_ID  — Telegram API ID（从 https://my.telegram.org 获取）
"""

import os
import sys
import json
import logging
from datetime import datetime
from functools import lru_cache

# Telegram Bot Token
BOT_TOKEN = "8979991426:AAEtgWjhF1KV_pJZVwzjk-ZE2_Yf1-W4RDU"

# ── 代理配置 ──
#   服务器无法直连 Telegram，在此填入你的 MTProxy 地址
#   万提供的代理: socks5://ee29044830465c5171f152ab7d07ccfc89617a7572652e6d6963726f736f66742e636f6d@18.139.137.172:443
PROXY_URL = os.environ.get(
    "TELEGRAM_PROXY",
    "socks5://ee29044830465c5171f152ab7d07ccfc89617a7572652e6d6963726f736f66742e636f6d@18.139.137.172:443"
)

# Admin User IDs (你的 Telegram User ID，设置后只有你能用管理命令)
ADMIN_IDS = [7668716558]

# 商品数据
PRODUCTS = {
    "telegram-bot":    {"name": "📱 Telegram号码查询机器人", "price": 29, "period": "月", "desc": "实时手机号码归属地查询"},
    "github-automation": {"name": "⚡ GitHub Agent自动化系统", "price": 99, "period": "月", "desc": "全自动GitHub运营"},
    "content-promoter": {"name": "📣 AI内容推流系统", "price": 199, "period": "月", "desc": "一键生成多平台推广文案"},
    "n8n-workflow":    {"name": "🔗 n8n工作流自动化系统", "price": 149, "period": "月", "desc": "拖拽式n8n工作流"},
    "video-gen":       {"name": "🎬 AI视频生成助手", "price": 99, "period": "月", "desc": "AI驱动的视频批量生成"},
    "ai-manga":        {"name": "🎭 AI漫剧生成系统", "price": 149, "period": "月", "desc": "AI自动生成漫画/漫剧"},
    "idea-generator":  {"name": "🧠 脑洞助手/创意生成器", "price": 39, "period": "月", "desc": "AI创意头脑风暴工具"},
    "ppt-generator":   {"name": "📊 PPT智能生成器", "price": 79, "period": "月", "desc": "AI一键生成PPT"},
    "ai-writing":      {"name": "✍️ AI代写定制服务系统", "price": 59, "period": "月", "desc": "AI文章/文案/报告代写"},
    "cross-border-ai":{"name": "🌐 跨境电商AI助手", "price": 199, "period": "月", "desc": "AI驱动的跨境电商运营助手"},
    "ai-agent":        {"name": "🤖 多平台AI Agent助手", "price": 129, "period": "月", "desc": "通用AI Agent框架"},
    "3d-generator":    {"name": "🎨 3D模型生成系统", "price": 129, "period": "月", "desc": "AI文本→3D模型生成"},
    "web-scraper":     {"name": "🕷️ AI智能网页爬虫", "price": 69, "period": "月", "desc": "AI驱动的智能网页数据采集"},
    "database-toolkit":{"name": "🗄️ AI数据库管理工具包", "price": 89, "period": "月", "desc": "AI辅助的数据库管理"},
    "security-scanner":{"name": "🔒 AI代码安全审计系统", "price": 149, "period": "月", "desc": "AI驱动的代码安全审计"},
    "design-toolkit":  {"name": "🖌️ AI设计素材生成器", "price": 79, "period": "月", "desc": "AI生成Logo、UI设计素材"},
    "game-dev-kit":    {"name": "🎮 AI游戏开发工具包", "price": 199, "period": "月", "desc": "AI辅助游戏开发"},
}

# 订单记录文件
ORDERS_FILE = "orders.json"

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_orders(orders):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

# ── 消息模板 ──
WELCOME = """
🛒 *AI超市 - 智能客服*

您好！欢迎来到AI超市 👋

我是这里的自动客服，可以帮您：

📋 *商品列表* — 查看所有AI技能
💰 *价格说明* — 了解收费方式
💳 *购买流程* — 如何付款获取下载链接
📦 *下载帮助* — 购买后如何下载

直接输入商品名称或编号即可下单！

————————————
💳 支付方式：PayPal
📧 paypalyinanzo@hotmail.com
"""

PRODUCT_LIST = """
🛍️ *AI超市 - 商品列表*

"""

def get_product_list():
    text = PRODUCT_LIST
    for i, (pid, p) in enumerate(PRODUCTS.items(), 1):
        text += f"*{i}. {p['name']}*\n   💰 ¥{p['price']}/{p['period']}\n   {p['desc']}\n\n"
    text += "————————————\n回复商品编号或名称即可下单！\n"
    return text

BUY_GUIDE = """
💳 *购买流程*

1️⃣ 告诉我您想要的商品
2️⃣ 我给您 PayPal 付款链接
3️⃣ 扫码付款后发我截图
4️⃣ 我确认后发送下载链接

📧 PayPal: paypalyinanzo@hotmail.com
💬 付款后联系本机器人发送截图即可
"""

ORDER_CONFIRM = """
✅ *订单已确认！*

商品: {name}
价格: ¥{price}/{period}

⏳ 正在处理您的下载链接...
请稍等片刻，链接将自动发送给您。
"""

DOWNLOAD_SENT = """
📦 *下载链接已发送！*

商品: {name}
购买时间: {time}

🔗 请点击以下链接下载：
{link}

⚠️ 链接有效期：永久
💾 下载后请妥善保存
"""

ADMIN_HELP = """
🛠️ *管理命令*

`/orders` — 查看所有订单
`/order <user_id>` — 查看指定用户订单
`/sendlink <user_id> <product_id>` — 发送下载链接给用户
`/broadcast <消息>` — 广播消息给所有用户
`/stats` — 查看统计数据
`/addadmin <user_id>` — 添加管理员
"""

def is_admin(user_id):
    return str(user_id) in [str(a) for a in ADMIN_IDS]

def make_order_keyboard():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = []
    row = []
    for i, pid in enumerate(PRODUCTS.keys()):
        row.append(InlineKeyboardButton(str(i+1), callback_data=f"buy:{pid}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("📋 商品列表", callback_data="list")])
    keyboard.append([InlineKeyboardButton("💳 购买指南", callback_data="guide")])
    return InlineKeyboardMarkup(keyboard)

def main():
    import asyncio
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        CallbackQueryHandler, filters, ContextTypes,
    )

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    orders = load_orders()
    user_sessions = {}  # user_id -> {"state": "...", "data": {...}}

    async def start_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        if user_id not in orders:
            orders[user_id] = {"history": [], "purchases": []}
            save_orders(orders)
        await update.message.reply_text(WELCOME, parse_mode="Markdown", reply_markup=make_order_keyboard())

    async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(WELCOME, parse_mode="Markdown", reply_markup=make_order_keyboard())

    async def list_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(get_product_list(), parse_mode="Markdown")

    async def buy_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(get_product_list(), parse_mode="Markdown")

    async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = str(query.from_user.id)
        data = query.data

        if data.startswith("buy:"):
            pid = data.split(":", 1)[1]
            if pid not in PRODUCTS:
                await query.edit_message_text("❌ 商品不存在")
                return
            p = PRODUCTS[pid]
            pay_url = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=paypalyinanzo@hotmail.com&item_name=AI超市 - {p['name']}&amount={p['price']}&currency_code=USD"
            text = f"""💳 *确认购买*

商品: {p['name']}
价格: ¥{p['price']}/{p['period']}

点击下方按钮打开 PayPal 付款：
[👉 立即付款]({pay_url})

付款后 *截图* 发给我，我确认后立刻发送下载链接！

⚠️ 务必先付款再发截图，否则无法处理
"""
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 去 PayPal 付款", url=pay_url)],
                [InlineKeyboardButton("✅ 我已付款，发截图", callback_data=f"paid:{pid}")],
            ])
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

        elif data.startswith("paid:"):
            pid = data.split(":", 1)[1]
            p = PRODUCTS[pid]
            if user_id not in user_sessions:
                user_sessions[user_id] = {}
            user_sessions[user_id]["state"] = "awaiting_screenshot"
            user_sessions[user_id]["pending_product"] = pid
            text = f"""📸 *请发送付款截图*

商品: {p['name']}
价格: ¥{p['price']}/{p['period']}

请在此聊天中发送 PayPal 付款截图，我确认后立即发送下载链接！

💡 截图需包含：付款金额 + 交易号
"""
            await query.edit_message_text(text, parse_mode="Markdown")

        elif data == "list":
            await query.edit_message_text(get_product_list(), parse_mode="Markdown", reply_markup=make_order_keyboard())

        elif data == "guide":
            await query.edit_message_text(BUY_GUIDE, parse_mode="Markdown")

    async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        if user_id in user_sessions and user_sessions[user_id].get("state") == "awaiting_screenshot":
            pid = user_sessions[user_id]["pending_product"]
            p = PRODUCTS[pid]
            # 记录订单
            orders[user_id]["history"].append({
                "product_id": pid,
                "product_name": p["name"],
                "price": p["price"],
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "screenshot": True,
            })
            save_orders(orders)
            # 通知买家
            await update.message.reply_text(
                f"✅ 截图已收到！\n\n正在为您准备下载链接，请稍候 1-2 分钟…\n\n商品: {p['name']}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                parse_mode="Markdown"
            )
            # 通知管理员
            for admin_id in ADMIN_IDS:
                try:
                    await ctx.bot.send_message(
                        chat_id=int(admin_id),
                        text=f"📋 *新订单！*\n\n买家ID: `{user_id}`\n商品: {p['name']}\n价格: ¥{p['price']}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n请发送下载链接给买家！",
                        parse_mode="Markdown"
                    )
                except:
                    pass
            user_sessions[user_id] = {}
        else:
            await update.message.reply_text("📸 请先选择一个商品，再发送付款截图。\n\n输入 /start 开始选购！")

    async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or "unknown"
        first_name = update.effective_user.first_name or ""

        if user_id not in orders:
            orders[user_id] = {"history": [], "purchases": []}
            save_orders(orders)

        # 检查是否是商品名称或编号
        matched = None
        text_lower = text.lower()
        # 精确匹配编号
        try:
            idx = int(text)
            if 1 <= idx <= len(PRODUCTS):
                matched = list(PRODUCTS.keys())[idx - 1]
        except:
            pass
        # 模糊匹配商品名称
        if not matched:
            for pid, p in PRODUCTS.items():
                if pid.replace("-", " ") in text_lower or p["name"].lower() in text_lower:
                    matched = pid
                    break
                # 部分匹配
                for keyword in p["name"]:
                    if keyword in text and len(keyword) > 2:
                        matched = pid
                        break

        if matched:
            p = PRODUCTS[matched]
            pay_url = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=paypalyinanzo@hotmail.com&item_name=AI超市 - {p['name']}&amount={p['price']}&currency_code=USD"
            text_resp = f"""💳 *商品已找到！*

*{p['name']}*
📝 {p['desc']}
💰 价格：¥{p['price']}/{p['period']}

[👉 点击此处去 PayPal 付款]({pay_url})

付款后发送截图给我，我立即发送下载链接！"""

            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 去 PayPal 付款", url=pay_url)],
            ])
            await update.message.reply_text(text_resp, parse_mode="Markdown", reply_markup=kb)
            return

        # 默认回复
        await update.message.reply_text(
            "🤔 我没太理解，请试试：\n\n"
            "• 输入商品名称或编号直接下单\n"
            "• /list 查看商品列表\n"
            "• /buy 查看购买指南\n"
            "• 直接发送付款截图",
            parse_mode="Markdown"
        )

    # ── 管理命令 ──
    async def admin_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        if not is_admin(user_id):
            await update.message.reply_text("❌ 无权访问")
            return
        if not orders:
            await update.message.reply_text("暂无订单")
            return
        text = "*📋 所有订单*\n\n"
        for uid, info in orders.items():
            text += f"👤 `{uid}`\n"
            for o in info.get("history", []):
                text += f"  - {o['product_name']} ¥{o['price']} ({o['time']})\n"
            text += "\n"
        await update.message.reply_text(text, parse_mode="Markdown")

    async def admin_sendlink(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        if not is_admin(user_id):
            await update.message.reply_text("❌ 无权访问")
            return
        args = ctx.args
        if len(args) < 2:
            await update.message.reply_text("用法: /sendlink <user_id> <product_id> [下载链接]")
            return
        target_uid = args[0]
        product_id = args[1]
        link = args[2] if len(args) > 2 else f"https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/{product_id}.zip"
        p = PRODUCTS.get(product_id, {"name": product_id})
        try:
            await ctx.bot.send_message(
                chat_id=int(target_uid),
                text=f"📦 *下载链接来了！*\n\n商品: {p['name']}\n购买时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n🔗 点击下载：\n{link}\n\n感谢购买！🎉",
                parse_mode="Markdown"
            )
            await update.message.reply_text(f"✅ 链接已发送给用户 {target_uid}")
        except Exception as e:
            await update.message.reply_text(f"❌ 发送失败: {e}")

    async def admin_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        if not is_admin(user_id):
            await update.message.reply_text("❌ 无权访问")
            return
        total = sum(len(o.get("history", [])) for o in orders.values())
        users = len(orders)
        total_rev = sum(sum(o.get("price", 0) for o in od.get("history", [])) for od in orders.values())
        text = f"""📊 *统计概览*

👥 总用户: {users}
📦 总订单: {total}
💰 预估收入: ¥{total_rev}"""
        await update.message.reply_text(text, parse_mode="Markdown")

    async def admin_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        if not is_admin(user_id):
            await update.message.reply_text("❌ 无权访问")
            return
        await update.message.reply_text(ADMIN_HELP, parse_mode="Markdown")

    # ── 构建并启动 Bot ──
    import httpx
    from telegram import Bot
    from telegram.request import HTTPXRequest
    from telegram.ext import Updater

    if PROXY_URL:
        print(f"🔗 通过代理连接 Telegram...")
        proxies = {"http://": PROXY_URL, "https://": PROXY_URL}
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=20.0),
            proxies=proxies, trust_env=False
        )
        proxy_req = HTTPXRequest(httpx_client=http_client)
        bot = Bot(token=BOT_TOKEN, request=proxy_req)
        updater = Updater(bot=bot)
        app = updater.updater.application
        print("✅ 代理配置成功！")
    else:
        print("🌐 直连模式启动...")
        updater = Updater(token=BOT_TOKEN)
        app = updater.updater.application

    # 注册所有 Handler
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("list", list_cmd))
    app.add_handler(CommandHandler("buy", buy_cmd))
    app.add_handler(CommandHandler("orders", admin_orders))
    app.add_handler(CommandHandler("sendlink", admin_sendlink))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("admin", admin_help))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 AI超市客服机器人启动中...")
    print("💬 等待消息...")
    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()

if __name__ == "__main__":
    main()
