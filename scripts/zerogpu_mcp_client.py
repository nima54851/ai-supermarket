#!/usr/bin/env python3
"""
灵犀 × ZeroGPU — MCP 客户端演示
通过标准 MCP Streamable-HTTP transport 调用 ZeroGPU 小模型

依赖：pip install mcp
运行：python3 scripts/zerogpu_mcp_client.py
"""

import json, time, sys

try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
except ImportError:
    print("需要安装 mcp: pip install mcp")
    sys.exit(1)

# ── 配置 ──────────────────────────────────────────────
API_KEY    = "zgpu-api-aa5921767b6bcde63756e1002f21bb3b7fc13c60824b34f71b52f5408a4d71cd"
PROJECT_ID = "b9dc3ebb-aaf5-45c4-af58-239c81575bab"
MCP_URL    = "https://mcp.zerogpu.ai/mcp"

# ── 工具映射 ──────────────────────────────────────────
TOOLS = {
    "summarize":       "zerogpu_summarize",
    "classify":        "zerogpu_classify_zero_shot",
    "extract_entities":"zerogpu_extract_entities",
    "extract_pii":     "zerogpu_extract_pii",
    "redact_pii":      "zerogpu_redact_pii",
    "extract_json":     "zerogpu_extract_json",
    "followups":       "zerogpu_generate_followups",
    "chat":            "zerogpu_chat",
}

def print_savings(savings: dict):
    if not savings:
        return
    print(f"  💰 ZeroGPU ${savings.get('zerogpu_cost_usd', 0):.6f}"
          f" | Claude估算 ${savings.get('baseline_cost_usd', 0):.6f}"
          f" | 节省 ${savings.get('savings_usd', 0):.6f}"
          f" | Token {savings.get('input_tokens',0)}+{savings.get('output_tokens',0)}")

async def run():
    headers = {
        "x-api-key": API_KEY,
        "x-project-id": PROJECT_ID,
    }

    async with ClientSession(sse_client(MCP_URL, headers=headers)) as session:
        await session.initialize()

        # ── 场景1: 摘要 ──
        print("\n📝 场景1: 长文摘要")
        article = (
            "人工智能正在加速渗透各行各业，从医疗诊断到金融风控，从自动驾驶到内容创作。"
            "大语言模型的能力边界不断扩展，但随之而来的是推理成本的急剧上升。"
            "如何在保证质量的前提下降低AI推理成本，成为产学研各界共同关注的核心课题。"
            "边缘计算与分布式推理的结合，正在为这一问题提供新的解决思路。"
        )
        result = await session.call_tool("zerogpu_summarize", {"text": article})
        text = result.content[0].text
        data = json.loads(text)
        print(f"  摘要: {data.get('summary','')}")
        print_savings(data.get("savings"))

        # ── 场景2: 零样本分类 ──
        print("\n🏷️  场景2: 零样本分类")
        news = "阿根廷球星梅西宣布将在本赛季结束后退役，结束长达20年的职业生涯。"
        result = await session.call_tool("zerogpu_classify_zero_shot", {
            "text": news, "labels": ["体育", "科技", "娱乐", "政治"]
        })
        data = json.loads(result.content[0].text)
        scores = data.get("scores", {})
        print(f"  新闻: {news}")
        print(f"  分类结果:")
        for label, score in sorted(scores.items(), key=lambda x: -x[1]):
            bar = "█" * int(score * 20)
            print(f"    {label}: {score:.3f} {bar}")
        print_savings(data.get("savings"))

        # ── 场景3: PII 提取 ──
        print("\n🔒 场景3: PII 信息检测")
        doc = ("甲方: 李明，电话 139-0000-8888，身份证号 110101199001011234，"
               "住址北京市朝阳区。乙方: 王芳，手机 186-1234-5678，邮箱 wangfang@example.com。")
        result = await session.call_tool("zerogpu_extract_pii", {"text": doc})
        data = json.loads(result.content[0].text)
        pii = data.get("pii", {})
        print(f"  检测到的PII:")
        for cat, items in pii.items():
            print(f"    [{cat}]: {items}")
        print_savings(data.get("savings"))

        # ── 场景4: 结构化提取 ──
        print("\n📋 场景4: 文本 → JSON")
        contract = ("订单编号：A20240620，金额：¥128,000，"
                    "供应商：深圳华腾电子有限公司，交货日期：2024年8月1日。")
        result = await session.call_tool("zerogpu_extract_json", {
            "text": contract,
            "schema": {
                "order": [
                    "order_no::str::订单号",
                    "amount::str::金额",
                    "supplier::str::供应商",
                    "delivery_date::str::交货日期",
                ]
            }
        })
        data = json.loads(result.content[0].text)
        print(f"  原文: {contract}")
        print(f"  提取结果: {json.dumps(data.get('data',{}), ensure_ascii=False, indent=4)}")
        print_savings(data.get("savings"))

        # ── 场景5: 追问生成 ──
        print("\n❓ 场景5: 自动生成追问")
        article2 = ("特斯拉最新财报显示，Q2营收达250亿美元，净利润18亿美元，"
                    "利润率环比下降3个百分点，主要受价格战和原材料成本上升影响。")
        result = await session.call_tool("zerogpu_generate_followups", {"text": article2})
        data = json.loads(result.content[0].text)
        qs = data.get("questions", [])
        print(f"  原文: {article2}")
        print(f"  生成追问:")
        for q in qs:
            print(f"    · {q}")
        print_savings(data.get("savings"))

if __name__ == "__main__":
    import asyncio
    print("=" * 60)
    print("灵犀 × ZeroGPU — MCP Streamable-HTTP 演示")
    print("=" * 60)
    asyncio.run(run())
    print("\n✅ 演示完成 — 所有任务走 ZeroGPU 边缘小模型")
