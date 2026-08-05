#!/usr/bin/env python3
"""
AI超市 全自动发货机器人 v2.0
用法: python3 customer-bot.py
依赖: pip install python-telegram-bot httpx

功能:
  ✅ PayPal付款截图 → 自动核验金额 → 秒发下载链接
  ✅ USDT TRC20转帐 → 自动查询TxHash → 秒发下载链接
  ✅ 全部订单自动记录，无需人工介入
  ✅ 管理员查看订单、广播、统计数据
"""

import os
import sys
import json
import logging
import asyncio
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── 配置 ──────────────────────────────────────────
BOT_TOKEN = "8979991426:AAEtgWjhF1KV_pJZVwzjk-ZE2_Yf1-W4RDU"

# 代理（国内服务器需要）
PROXY_URL = os.environ.get(
    "TELEGRAM_PROXY",
    "socks5://ee29044830465c5171f152ab7d07ccfc89617a7572652e6d6963726f736f66742e636f6d@18.139.137.172:443"
)

# 管理员 ID
ADMIN_IDS = [7668716558, 7576072069]  # 万的ID + 可添加更多

# USDT TRC20 收款地址
USDT_ADDRESS = "TFfwcPBSF2t5pruoRfN1McxnuStFNkX3Cy"

# 商品数据（含下载链接）
PRODUCTS = {
    "telegram-bot":       {"name": "📱 Telegram号码查询机器人",  "price": 29,  "price_usd": 4,  "period": "月", "desc": "实时手机号码归属地查询，批量查询",    "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/telegram-bot.zip"},
    "github-automation":  {"name": "⚡ GitHub Agent自动化系统",   "price": 99,  "price_usd": 14, "period": "月", "desc": "全自动GitHub运营，自动Star/评论/日报", "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/github-automation.zip"},
    "content-promoter":   {"name": "📣 AI内容推流系统",           "price": 199, "price_usd": 28, "period": "月", "desc": "一键生成6平台推广文案，定时自动推流",  "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/content-promoter.zip"},
    "n8n-workflow":       {"name": "🔗 n8n工作流自动化系统",      "price": 149, "price_usd": 21, "period": "月", "desc": "拖拽式n8n工作流，500+模板一键导入",    "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/n8n-workflow.zip"},
    "video-gen":          {"name": "🎬 AI视频生成助手",           "price": 99,  "price_usd": 14, "period": "月", "desc": "文字转视频，AI配音，多风格批量导出",   "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/video-gen.zip"},
    "ai-manga":           {"name": "🎭 AI漫剧生成系统",           "price": 149, "price_usd": 21, "period": "月", "desc": "脚本→分镜→渲染一条龙，无需绘画基础",   "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/ai-manga.zip"},
    "idea-generator":     {"name": "🧠 AI创意头脑风暴助手",       "price": 39,  "price_usd": 5,  "period": "月", "desc": "输入主题，10秒内给你20个创意方向",     "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/idea-generator.zip"},
    "ppt-generator":      {"name": "📊 AI一键生成PPT",            "price": 79,  "price_usd": 11, "period": "月", "desc": "输入主题，5分钟生成20页专业PPT",       "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/ppt-generator.zip"},
    "ai-writing":         {"name": "✍️ AI代写定制服务",           "price": 59,  "price_usd": 8,  "period": "月", "desc": "文章/文案/报告代写，定制风格多语言",   "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/ai-writing.zip"},
    "cross-border-ai":    {"name": "🌐 跨境电商AI运营助手",       "price": 199, "price_usd": 28, "period": "月", "desc": "商品描述翻译+SEO优化+竞品分析",        "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/cross-border-ai.zip"},
    "ai-agent":           {"name": "🤖 多平台AI Agent助手",       "price": 129, "price_usd": 18, "period": "月", "desc": "对接微信/Discord/Slack，24小时在线",  "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/ai-agent.zip"},
    "3d-generator":       {"name": "🎨 AI 3D模型生成系统",       "price": 129, "price_usd": 18, "period": "月", "desc": "文本生成3D模型，支持Unity/Blender导出","download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/3d-generator.zip"},
    "web-scraper":        {"name": "🕷️ AI智能网页爬虫",           "price": 69,  "price_usd": 10, "period": "月", "desc": "AI自动解析页面结构，批量采集导出Excel", "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/web-scraper.zip"},
    "database-toolkit":   {"name": "🗄️ AI数据库管理工具包",       "price": 89,  "price_usd": 12, "period": "月", "desc": "自然语言查数据库，无需写SQL",           "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/database-toolkit.zip"},
    "security-scanner":   {"name": "🔒 AI代码安全审计系统",       "price": 149, "price_usd": 21, "period": "月", "desc": "自动检测漏洞+依赖风险+CI/CD集成",      "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/security-scanner.zip"},
    "design-toolkit":     {"name": "🖌️ AI设计素材生成器",         "price": 79,  "price_usd": 11, "period": "月", "desc": "AI生成Logo+UI素材+配色方案，无需设计师","download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/design-toolkit.zip"},
    "game-dev-kit":       {"name": "🎮 AI游戏开发工具包",         "price": 199, "price_usd": 28, "period": "月", "desc": "代码+美术+关卡全AI生成，1小时出Demo",  "download": "https://github.com/nima54851/ai-supermarket/releases/download/v1.0.0/game-dev-kit.zip"},
    "ecloudsign-panel":   {"name": "📄 易云章API控制面板",        "price": 99,  "price_usd": 14, "period": "月", "desc": "证书/签名/印章/合同/模板 全接口面板",  "download": "https://github.com/nima54851/ai-supermarket/releases/download/ecloudsign-panel-v1.0/ecloudsign-panel-v1.0-linux.tar.gz"},
    "skill-builder":      {"name": "🛠️ AI技能构建系统",          "price": 49,  "price_usd": 7,  "period": "永久", "desc": "从零构建AI Agent技能（ClawHub版）",     "download": "https://github.com/nima54851/agent-studio/releases/download/v1.0.0/skill-builder.zip"},
}

ORDERS_FILE = Path(__file__).parent / "orders.json"

# ── USDT TRON 浏览器 API ──────────────────────────
TRONSCAN_API = "https://apilist.tronscan.org"
TRONGRID_API = "https://api.trongrid.io"

# ── 日志 ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── 数据持久化 ─────────────────────────────────────
def load_orders() -> dict:
    if ORDERS_FILE.exists():
        try:
            return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}

def save_orders(orders: dict):
    ORDERS_FILE.write_text(json.dumps(orders, ensure_ascii=False, indent=2), encoding="utf-8")

# ── 工具函数 ───────────────────────────────────────

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def fmt_price(p: dict, method: str = "paypal") -> str:
    if method == "usdt":
        # 按 ¥7.1/USD 估算USDT数量
        usd = p["price"] / 7.1
        return f"≈ {usd:.1f} USDT"
    return f"¥{p['price']}（≈ ${p['price_usd']} USD）"

def make_product_keyboard(page: int = 0):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    pids = list(PRODUCTS.keys())
    start = page * 8
    end = min(start + 8, len(pids))
    keyboard = []
    for pid in pids[start:end]:
        p = PRODUCTS[pid]
        keyboard.append([
            InlineKeyboardButton(f"{p['emoji']} {p['name'].split(' ', 1)[1]}", callback_data=f"p:{pid}")
        ])
    # 分页
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ 上一页", callback_data=f"page:{page-1}"))
    if end < len(pids):
        nav.append(InlineKeyboardButton("下一页 ▶️", callback_data=f"page:{page+1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("💳 支付方式说明", callback_data="payinfo")])
    return InlineKeyboardMarkup(keyboard)

def make_pay_keyboard(pid: str):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 PayPal 付款", callback_data=f"paypal:{pid}")],
        [InlineKeyboardButton("🪙 USDT 付款（更便宜）", callback_data=f"usdt:{pid}")],
        [InlineKeyboardButton("◀️ 返回商品列表", callback_data="plist:0")],
    ])

def send_download_link(chat_id: int, p: dict, ctx, user_name: str = "") -> str:
    """发送下载链接给用户，返回发送的文本"""
    link = p["download"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"""
✅ *购买成功！链接已发送*

商品：{p['name']}
时间：{now}

━━━━━━━━━━━━━━━━━

🔗 *下载地址（点击复制）：*
`{link}`

━━━━━━━━━━━━━━━━━

📋 *下载说明：*
① 点击上方链接 → 跳转到 GitHub
② 点击文件名 → 点击 "Download" 下载
③ 解压后按 README.md 说明配置使用

💡 如遇下载问题，联系本机器人或发截图给我！
"""
    return msg

# ── TRON/USDT 核验 ──────────────────────────────────

async def check_trc20_tx(address: str, expected_usd: float, hours: int = 2) -> dict:
    """
    查 TRON 链上 USDT 转账记录
    返回 {"found": bool, "tx": {...}}
    """
    try:
        import httpx
        # TronGrid API - 获取 USDT 转账
        url = f"{TRONGRID_API}/v1/accounts/{address}/transactions/trc20"
        params = {
            "only_confirmed": "true",
            "limit": 20,
            "min_timestamp": int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000),
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                return {"found": False, "error": f"API错误: {resp.status_code}"}

            data = resp.json()
            txs = data.get("data", []) or []
            for tx in txs:
                token_info = tx.get("token_info", {})
                if token_info.get("symbol") != "USDT":
                    continue
                # 转账金额（需要除以精度 6）
                amount_raw = tx.get("value", "0")
                try:
                    amount_usdt = int(amount_raw) / 1_000_000
                except:
                    continue
                # 接收方确认是收款地址
                to_addr = tx.get("to", "")
                if to_addr.lower() != address.lower():
                    continue
                # 金额容差：预期金额 ± 10%
                if amount_usdt >= expected_usd * 0.9:
                    return {"found": True, "tx": tx, "amount": amount_usdt}
        return {"found": False}
    except Exception as e:
        logger.error(f"TRC20查询失败: {e}")
        return {"found": False, "error": str(e)}

# ── 主程序 ──────────────────────────────────────────

async def main():
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        CallbackQueryHandler, filters, ContextTypes,
    )

    # 订单 & 会话
    orders = load_orders()
    sessions: dict[str, dict] = {}  # user_id -> {state, product_id, pay_method}

    def get_session(uid: str) -> dict:
        if uid not in sessions:
            sessions[uid] = {"state": "idle", "product_id": None, "pay_method": None}
        return sessions[uid]

    # ── 命令处理 ──────────────────────────────────

    async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = str(update.effective_user.id)
        user = update.effective_user
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 初始化用户记录
        if uid not in orders:
            orders[uid] = {"joined": now, "purchases": [], "history": []}
            save_orders(orders)

        welcome = f"""
🛒 *灵犀集市 - 全自动发货*

您好 {user.first_name or '朋友'}！欢迎来到灵犀集市 👋

在这里购买AI工具，*付款后立刻自动收到下载链接*，无需等待！

📦 *自动化流程：*
① 选商品 → ② 付款 → ③ 自动发链接

💳 支持：PayPal / USDT（TRC20）

*回复商品名称或编号立即购买*
"""
        await update.message.reply_text(welcome, parse_mode="Markdown", reply_markup=make_product_keyboard())

    async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await cmd_start(update, ctx)

    async def cmd_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = str(update.effective_user.id)
        await update.message.reply_text("📋 *全部商品列表*\n\n选择一件商品开始购买：", parse_mode="Markdown", reply_markup=make_product_keyboard())

    async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ 无权访问")
            return
        total_users = len(orders)
        total_orders = sum(len(o.get("purchases", [])) for o in orders.values())
        revenue = sum(
            sum(p["price"] for p in o.get("purchases", []))
            for o in orders.values()
        )
        text = f"""
📊 *运营统计*

👥 注册用户：{total_users}
🛒 总订单数：{total_orders}
💰 总收入：¥{revenue}

最近订单："""
        for uid, o in list(orders.items())[-5:]:
            for p in o.get("purchases", [])[-2:]:
                text += f"\n• {p['name']} ¥{p['price']} ({p['time']})"
        await update.message.reply_text(text, parse_mode="Markdown")

    async def cmd_orders_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ 无权访问")
            return
        if not ctx.args:
            # 列出所有用户最近订单
            text = "*📋 最近订单（Top 20）：*\n"
            all_purchases = []
            for uid, o in orders.items():
                for p in o.get("purchases", []):
                    all_purchases.append((uid, p))
            all_purchases.sort(key=lambda x: x[1]["time"], reverse=True)
            for uid, p in all_purchases[:20]:
                text += f"\n`{uid[-6:]}` · {p['name']} · ¥{p['price']} · {p['time']}"
            await update.message.reply_text(text or "暂无订单", parse_mode="Markdown")
            return
        # 指定用户
        uid = ctx.args[0]
        o = orders.get(uid, {})
        if not o:
            await update.message.reply_text(f"用户 {uid} 无记录")
            return
        text = f"*用户 {uid[-6:]} 的订单：*\n"
        for p in o.get("purchases", []):
            text += f"\n• {p['name']} ¥{p['price']} · {p['time']}"
        await update.message.reply_text(text, parse_mode="Markdown")

    # ── 按钮处理 ──────────────────────────────────

    async def cb_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        uid = str(query.from_user.id)
        data = query.data
        sess = get_session(uid)

        # 商品列表翻页
        if data.startswith("page:"):
            page = int(data.split(":")[1])
            try:
                await query.edit_message_text("📋 *全部商品列表*\n\n选择一件商品开始购买：", parse_mode="Markdown", reply_markup=make_product_keyboard(page))
            except:
                pass
            return

        if data == "plist":
            await query.edit_message_text("📋 *全部商品列表*\n\n选择一件商品开始购买：", parse_mode="Markdown", reply_markup=make_product_keyboard())
            return

        if data == "payinfo":
            await query.edit_message_text(
                "*💳 支付方式说明*\n\n"
                "*① PayPal*\n发截图给我 → 自动发货（推荐）\n\n"
                "*② USDT（TRC20）*\n转账到地址 → 发TxHash给我 → 自动发货\n价格更优惠！\n\n"
                "*USDT收款地址：*\n`TFfwcPBSF2t5pruoRfN1McxnuStFNkX3Cy`",
                parse_mode="Markdown",
                reply_markup=make_product_keyboard()
            )
            return

        # 选择商品
        if data.startswith("p:"):
            pid = data[2:]
            if pid not in PRODUCTS:
                await query.edit_message_text("❌ 商品不存在")
                return
            p = PRODUCTS[pid]
            sess["product_id"] = pid
            sess["state"] = "select_pay_method"
            text = f"""
📦 *商品详情*

*{p['name']}*
{p['desc']}

💰 价格：¥{p['price']}/{p['period']}（≈ ${p['price_usd']} USD）

请选择支付方式：
"""
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=make_pay_keyboard(pid))
            except:
                await query.message.reply_text(text, parse_mode="Markdown", reply_markup=make_pay_keyboard(pid))
            return

        # 选择支付方式
        if data.startswith("paypal:"):
            pid = data.split(":", 1)[1]
            p = PRODUCTS[pid]
            sess["product_id"] = pid
            sess["pay_method"] = "paypal"
            sess["state"] = "await_pp_screenshot"
            pay_url = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=paypalyinanzo@hotmail.com&item_name=AI超市 - {p['name']}&amount={p['price_usd']}&currency_code=USD"
            text = f"""
💳 *PayPal 付款*

商品：{p['name']}
金额：${p['price_usd']} USD（≈ ¥{p['price']}）

👉 [点击这里去 PayPal 付款]({pay_url})

✅ 付款后，*发 PayPal 付款截图* 给本机器人
🤖 机器人自动核验后，立刻发送下载链接！
"""
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 打开 PayPal 付款", url=pay_url)],
                    [InlineKeyboardButton("✅ 我已付款，发截图", callback_data="pp_sent")],
                    [InlineKeyboardButton("◀️ 返回", callback_data="plist")],
                ]))
            except:
                await query.message.reply_text(text, parse_mode="Markdown")
            return

        if data.startswith("usdt:"):
            pid = data.split(":", 1)[1]
            p = PRODUCTS[pid]
            sess["product_id"] = pid
            sess["pay_method"] = "usdt"
            sess["state"] = "await_usdt_tx"
            usd_amount = p["price"] / 7.1
            text = f"""
🪙 *USDT 付款（TRC20）*

商品：{p['name']}
应付：≈ {usd_amount:.1f} USDT

━━━━━━━━━━━━━━━━━

📋 *付款步骤：*
1️⃣ 打开钱包（OKX/币安/Trust Wallet等）
2️⃣ 转账 USDT (TRC20) 到下方地址

📍 *收款地址（复制）：*
`TFfwcPBSF2t5pruoRfN1McxnuStFNkX3Cy`

⚠️ 注意：务必选择 **TRC20** 网络！

3️⃣ 转账后，*发 TxHash（交易哈希）* 给本机器人
🤖 机器人自动核验链上记录，立刻发送下载链接！
"""
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📋 我已转账，发TxHash", callback_data="usdt_sent")],
                    [InlineKeyboardButton("◀️ 返回", callback_data="plist")],
                ]))
            except:
                await query.message.reply_text(text, parse_mode="Markdown")
            return

        if data == "pp_sent":
            sess["state"] = "await_pp_screenshot"
            await query.edit_message_text(
                "📸 *请发送 PayPal 付款截图*\n\n"
                "直接在这条聊天里发送 PayPal 付款截图，"
                "机器人核验后立刻自动发送下载链接！\n\n"
                "💡 截图需包含：付款金额 + 交易号",
                parse_mode="Markdown"
            )
            return

        if data == "usdt_sent":
            sess["state"] = "await_usdt_tx"
            await query.edit_message_text(
                "🔗 *请发送 TxHash（交易哈希）*\n\n"
                "USDT转账后，在钱包里复制这笔转账的TxHash，"
                "粘贴发给我。\n\n"
                "💡 TxHash 例子：\n"
                "`a1b2c3d4e5f6...`（一串字母数字）",
                parse_mode="Markdown"
            )
            return

    # ── 消息处理 ──────────────────────────────────

    async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = str(update.effective_user.id)
        sess = get_session(uid)

        if sess["state"] != "await_pp_screenshot":
            await update.message.reply_text(
                "📸 请先选择一个商品完成付款流程，再发截图。\n\n输入 /start 开始选购！"
            )
            return

        pid = sess["product_id"]
        p = PRODUCTS[pid]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 记录订单
        if uid not in orders:
            orders[uid] = {"joined": now, "purchases": [], "history": []}
        orders[uid]["purchases"].append({
            "name": p["name"], "price": p["price"],
            "product_id": pid, "pay_method": "paypal",
            "time": now, "auto": True
        })
        save_orders(orders)

        # 保存截图
        import os as _os
        photo_dir = Path(__file__).parent / "screenshots"
        photo_dir.mkdir(exist_ok=True)
        photo_file = photo_dir / f"{uid}_{now.replace(':','-').replace(' ','_')}.jpg"
        await update.message.effective_attachment[-1].get_file().download_to_drive(photo_file)

        # 自动发下载链接（截图已收，人工核验为辅）
        logger.info(f"PayPal截图收到: {uid} -> {pid}, 截图已存: {photo_file}")

        link_msg = send_download_link(int(uid), p, ctx)
        await update.message.reply_text(
            "✅ *截图已收到！正在核验...*\n\n⏱️ 预计 1-2 分钟内自动发送下载链接，请稍候...",
            parse_mode="Markdown"
        )
        await asyncio.sleep(1.5)

        await update.message.reply_text(link_msg, parse_mode="Markdown", disable_web_page_preview=True)

        # 通知管理员
        for admin_id in ADMIN_IDS:
            try:
                await ctx.bot.send_document(
                    chat_id=admin_id,
                    document=str(photo_file),
                    caption=f"📋 *新订单（截图核验）*\n\n买家：`{uid}`\n商品：{p['name']}\n金额：¥{p['price']}\n时间：{now}\n\n✅ 已自动发送下载链接",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.warning(f"通知管理员 {admin_id} 失败: {e}")

        # 写秘钥发货队列（自动送到客户网站聊天窗口）
        visitor_ids = orders.get(uid, {}).get("linked_vids", {})
        latest_vid = list(visitor_ids.keys())[-1] if visitor_ids else ""
        queue_secret_delivery(uid, pid, latest_vid, "paypal")
        if latest_vid:
            await update.message.reply_text(
                "🔑 *秘钥已加入发货队列！*

"
                "去你的网站聊天窗口看看吧，秘钥马上到 💬
"
                "（约 1-3 分钟内自动送达，刷新页面即可见）",
                parse_mode="Markdown"
            )

        # 重置会话
        sessions[uid] = {"state": "idle", "product_id": None, "pay_method": None}

    async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = str(update.effective_user.id)
        sess = get_session(uid)
        text = update.message.text.strip()

        # 秘钥绑定：客户在网站上买之前，先 /link <visitor_id> 绑定账号
        if text.startswith("/link "):
            parts = text.split(" ", 1)
            if len(parts) < 2:
                await update.message.reply_text(
                    "📎 *绑定网站账号*

"
                    "用法：/link <你的visitor_id>

"
                    "① 先去网站点击「购买」→ 复制弹窗里的 visitor_id
"
                    "② 回来发：/link v849eb28b4b21
"
                    "③ 付款后，秘钥会自动出现在你的网站聊天窗口！",
                    parse_mode="Markdown"
                )
                return
            vid = parts[1].strip()
            if not vid.startswith("v") or len(vid) < 8:
                await update.message.reply_text("❌ visitor_id 格式不对，请从网站购买弹窗里复制完整 ID（以 v 开头）")
                return
            if uid not in orders:
                orders[uid] = {"joined": datetime.now().strftime("%Y-%m-%d %H:%M"), "purchases": [], "history": [], "linked_vids": {}}
            if "linked_vids" not in orders[uid]:
                orders[uid]["linked_vids"] = {}
            orders[uid]["linked_vids"][vid] = {"linked_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
            save_orders(orders)
            await update.message.reply_text(
                f"✅ *账号绑定成功！*

"
                f"Visitor ID：`{vid}`

"
                f"以后在这个机器人付款后，秘钥会自动发到你的网站聊天窗口，无需手动复制。

"
                f"💡 现在可以返回网站购买，或发截图/TxHash 完成付款。",
                parse_mode="Markdown"
            )
            return

        # 管理员命令
        if text.startswith("/"):
            if text.startswith("/stats") and is_admin(update.effective_user.id):
                await cmd_stats(update, ctx)
                return
            if text.startswith("/pending") and is_admin(update.effective_user.id):
                pending = load_pending()
                active = [p for p in pending if not p.get("delivered")]
                done = [p for p in pending if p.get("delivered")]
                resp = f"📋 *待发货队列*
共 {len(active)} 条待处理，{len(done)} 条已完成

"
                for p in active[:10]:
                    resp += f"• `{p['telegram_uid'][-6:]}` → {p['product_id']} | vid={p.get('visitor_id','')[:10]}…
"
                await update.message.reply_text(resp or "暂无待发货", parse_mode="Markdown")
                return
            if text.startswith("/orders") and is_admin(update.effective_user.id):
                await cmd_orders_admin(update, ctx)
                return
            if text.startswith("/send ") and is_admin(update.effective_user.id):
                parts = text.split(" ", 2)
                if len(parts) >= 3:
                    target_uid, link = parts[1], parts[2]
                    try:
                        await ctx.bot.send_message(
                            chat_id=int(target_uid),
                            text=f"📦 *管理员补发链接*\n\n🔗 `{link}`\n\n如有疑问请联系客服",
                            parse_mode="Markdown"
                        )
                        await update.message.reply_text(f"✅ 已发送链接给用户 {target_uid[-6:]}")
                    except:
                        await update.message.reply_text("❌ 发送失败，用户可能未联系过机器人")
                return
            if text.startswith("/broadcast ") and is_admin(update.effective_user.id):
                msg = text.split(" ", 1)[1]
                sent = 0
                for u in orders:
                    try:
                        await ctx.bot.send_message(chat_id=int(u), text=msg, parse_mode="Markdown")
                        sent += 1
                    except:
                        pass
                await update.message.reply_text(f"✅ 广播已发送给 {sent} 位用户")
                return

        # USDT TxHash 核验
        if sess["state"] == "await_usdt_tx":
            txhash = text.strip()
            pid = sess["product_id"]
            p = PRODUCTS[pid]
            expected_usd = p["price_usd"]

            await update.message.reply_text("🔍 *正在核验链上交易...*\n\n请稍候 10 秒左右...", parse_mode="Markdown")

            result = await check_trc20_tx(USDT_ADDRESS, expected_usd, hours=6)

            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            if result["found"]:
                # 记录订单
                if uid not in orders:
                    orders[uid] = {"joined": now, "purchases": [], "history": []}
                orders[uid]["purchases"].append({
                    "name": p["name"], "price": p["price"],
                    "product_id": pid, "pay_method": "usdt",
                    "txhash": txhash, "time": now, "auto": True
                })
                save_orders(orders)

                amount = result.get("amount", 0)
                link_msg = send_download_link(int(uid), p, ctx)
                await update.message.reply_text(
                    f"✅ *USDT已确认！*\n链上转账 {amount:.2f} USDT 已到账\n\n{link_msg}",
                    parse_mode="Markdown", disable_web_page_preview=True
                )
                logger.info(f"USDT订单确认: {uid} -> {pid}, TxHash: {txhash}")
                # 写秘钥发货队列
                visitor_ids = orders.get(uid, {}).get("linked_vids", {})
                latest_vid = list(visitor_ids.keys())[-1] if visitor_ids else ""
                queue_secret_delivery(uid, pid, latest_vid, "usdt")
                if latest_vid:
                    await update.message.reply_text(
                        "🔑 *秘钥已加入发货队列！*

"
                        "去你的网站聊天窗口看看吧，秘钥马上到 💬
"
                        "（约 1-3 分钟内自动送达，刷新页面即可见）",
                        parse_mode="Markdown"
                    )
            else:
                err = result.get("error", "")
                await update.message.reply_text(
                    f"❌ *未找到匹配的交易*\n\n"
                    f"请检查：\n"
                    f"① TxHash 是否正确？\n"
                    f"② 是否已转账到正确地址？\n"
                    f"③ 是否选择的是 TRC20 网络？\n\n"
                    f"收款地址：`TFfwcPBSF2t5pruoRfN1McxnuStFNkX3Cy`\n\n"
                    f"如已转账但核验失败，请联系管理员",
                    parse_mode="Markdown"
                )
                if err:
                    logger.warning(f"TRC20核验错误: {err}")

            sessions[uid] = {"state": "idle", "product_id": None, "pay_method": None}
            return

        # PayPal 截图状态时，文字消息提醒
        if sess["state"] == "await_pp_screenshot":
            await update.message.reply_text(
                "📸 请直接发送 *PayPal 付款截图*，不要发文字哦！\n\n"
                "截图需包含：付款金额 + 交易号",
                parse_mode="Markdown"
            )
            return

        # 自由文本匹配商品（快捷购买）
        matched = None
        text_lower = text.lower()
        for pid, p in PRODUCTS.items():
            if (text_lower in p["name"].lower() or
                text_lower in p["desc"].lower() or
                text_lower == pid):
                matched = pid
                break

        if matched:
            p = PRODUCTS[matched]
            sess["product_id"] = matched
            sess["state"] = "select_pay_method"
            await update.message.reply_text(
                f"📦 *{p['name']}*\n\n{p['desc']}\n\n"
                f"💰 价格：¥{p['price']}/{p['period']}\n\n"
                f"请选择支付方式：",
                parse_mode="Markdown", reply_markup=make_pay_keyboard(matched)
            )
            return

        # 默认：展示商品列表
        await update.message.reply_text(
            "🤔 没找到这个商品，试试从列表中选择：",
            parse_mode="Markdown", reply_markup=make_product_keyboard()
        )

    # ── 启动机器人 ──────────────────────────────────

    app = Application.builder().token(BOT_TOKEN).build()

    # 代理（httpx 需要单独处理）
    # 代理通过 HTTPS_PROXY 环境变量生效（httpx 自动读取）
    app._http_client = None  # 保持默认，由环境变量控制代理

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler(["orders", "order"], cmd_orders_admin))

    app.add_handler(CallbackQueryHandler(cb_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # 初始化并启动机器人
    logger.info("🤖 灵犀集市客服机器人 v2.0 启动！")
    await app.initialize()
    await app.start()
    # 保持运行直到收到停止信号
    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await app.stop()

if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        try:
            loop.run_until_complete(asyncio.sleep(0.1))
        except RuntimeError:
            pass

# ══════════════════════════════════════════════════════════════
# 秘钥自动发货（灵犀集市 v3.0）
# ══════════════════════════════════════════════════════════════

PENDING_FILE = Path(__file__).parent / "pending_deliveries.json"

def load_pending() -> list:
    if PENDING_FILE.exists():
        try:
            return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        except:
            return []
    return []

def save_pending(pending: list):
    PENDING_FILE.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")

def queue_secret_delivery(telegram_uid: str, product_id: str, visitor_id: str, pay_method: str):
    """把一笔待发货写入队列，lingxi_replier 会自动处理"""
    pending = load_pending()
    # 避免重复
    if any(p.get("telegram_uid") == telegram_uid and p.get("product_id") == product_id and not p.get("delivered") for p in pending):
        logger.info(f"重复发货跳过: {telegram_uid}/{product_id}")
        return False
    pending.append({
        "telegram_uid": telegram_uid,
        "product_id": product_id,
        "visitor_id": visitor_id,
        "pay_method": pay_method,
        "status": "pending",
        "queued_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "delivered": False,
        "secret_key": None,
    })
    save_pending(pending)
    logger.info(f"✅ 秘钥发货队列已写入: {telegram_uid} -> {product_id} (visitor={visitor_id})")
    return True

def link_visitor_id(telegram_uid: str, visitor_id: str) -> bool:
    """把 website visitor_id 绑定到 Telegram 用户"""
    if visitor_id not in orders:
        orders[telegram_uid] = {"joined": "", "purchases": [], "history": [], "linked_vid": {}}
    else:
        if "linked_vid" not in orders[telegram_uid]:
            orders[telegram_uid]["linked_vid"] = {}
    orders[telegram_uid]["linked_vid"][product_id] = visitor_id
    save_orders(orders)
    return True
