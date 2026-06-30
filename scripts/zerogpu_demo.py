#!/usr/bin/env python3
"""
灵犀 × ZeroGPU — 演示项目
参考 ZeroGPU Router 架构，展示如何把轻量任务路由到边缘小模型，省主模型 token。

运行方式：
  python3 demo.py

效果：
  任务 → ZeroGPU 小模型 → 结果 + 节省金额
"""

import urllib.request
import urllib.error
import json
import time

# ── 配置 ──────────────────────────────────────────────
API_KEY   = "zgpu-api-aa5921767b6bcde63756e1002f21bb3b7fc13c60824b34f71b52f5408a4d71cd"
PROJECT_ID = "b9dc3ebb-aaf5-45c4-af58-239c81575bab"
MCP_URL   = "https://mcp.zerogpu.ai/mcp"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "x-api-key": API_KEY,
    "x-project-id": PROJECT_ID,
}

# ── MCP 请求封装 ──────────────────────────────────────
def mcp_rpc(method, params=None):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": int(time.time() * 1000),
        "method": method,
        "params": params or {},
    }).encode()
    req = urllib.request.Request(MCP_URL, data=payload, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode()
            # SSE 模式: 找最后一个 data: 行
            for line in reversed(raw.splitlines()):
                line = line.strip()
                if line.startswith("data:"):
                    return json.loads(line[5:].strip())
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}

# ── 工具函数 ──────────────────────────────────────────
def summarize(text: str):
    """摘要 — 用 llama-3.1-8b-instruct-fast，~100× 便宜过 Claude"""
    result = mcp_rpc("tools/call", {
        "name": "zerogpu_summarize",
        "arguments": {"text": text}
    })
    return parse_result(result)

def classify_zero_shot(text: str, labels: list):
    """零样本分类 — 用 DeBERTa，极便宜"""
    result = mcp_rpc("tools/call", {
        "name": "zerogpu_classify_zero_shot",
        "arguments": {"text": text, "labels": labels}
    })
    return parse_result(result)

def extract_pii(text: str):
    """PII 脱敏 — 自动检测人名/电话/邮箱/地址"""
    result = mcp_rpc("tools/call", {
        "name": "zerogpu_extract_pii",
        "arguments": {"text": text}
    })
    return parse_result(result)

def redact_pii(text: str):
    """PII 掩码 — 把敏感信息打码"""
    result = mcp_rpc("tools/call", {
        "name": "zerogpu_redact_pii",
        "arguments": {"text": text}
    })
    return parse_result(result)

def extract_json(text: str, schema: dict):
    """结构化提取 — 把非结构化文本变成 JSON"""
    result = mcp_rpc("tools/call", {
        "name": "zerogpu_extract_json",
        "arguments": {"text": text, "schema": schema}
    })
    return parse_result(result)

def generate_followups(text: str):
    """生成追问 — 从文章/对话自动生成后续问题"""
    result = mcp_rpc("tools/call", {
        "name": "zerogpu_generate_followups",
        "arguments": {"text": text}
    })
    return parse_result(result)

def parse_result(result):
    """统一解析 MCP 返回"""
    if "error" in result:
        return {"error": result["error"]}
    content = result.get("result", {}).get("content", [])
    for block in content:
        if block.get("type") == "text":
            try:
                return json.loads(block["text"])
            except json.JSONDecodeError:
                return {"result": block["text"]}
    return result

def print_savings(tool_name: str, savings: dict):
    """漂亮打印节省金额"""
    if not savings:
        return
    z_cost = savings.get("zerogpu_cost_usd", 0)
    baseline = savings.get("baseline_cost_usd", 0)
    saved = savings.get("savings_usd", 0)
    tokens = savings.get("input_tokens", 0) + savings.get("output_tokens", 0)
    print(f"  💰 ZeroGPU 费用: ${z_cost:.6f} | 原 Claude 估算: ${baseline:.6f} | 节省: ${saved:.6f} | Token: {tokens}")

# ── 演示场景 ──────────────────────────────────────────
def demo():
    print("=" * 60)
    print("灵犀 × ZeroGPU 演示项目")
    print("=" * 60)

    # 场景 1: 摘要
    print("\n📝 场景 1: 长文摘要")
    article = """人工智能正在加速渗透各行各业，从医疗诊断到金融风控，从自动驾驶到内容创作。
大语言模型的能力边界不断扩展，但随之而来的是推理成本的急剧上升。
如何在保证质量的前提下降低 AI 推理成本，成为产学研各界共同关注的核心课题。
边缘计算与分布式推理的结合，正在为这一问题提供新的解决思路。"""
    r = summarize(article)
    print(f"  摘要: {r.get('summary', r)}")
    print_savings("summarize", r.get("savings"))

    # 场景 2: 零样本分类
    print("\n🏷️  场景 2: 零样本分类")
    news = "阿根廷球星梅西宣布将在本赛季结束后退役，结束长达20年的职业生涯。"
    r = classify_zero_shot(news, ["体育", "科技", "娱乐", "政治"])
    scores = r.get("scores", {})
    print(f"  新闻: {news}")
    print(f"  分类结果:")
    for label, score in sorted(scores.items(), key=lambda x: -x[1]):
        bar = "█" * int(score * 20)
        print(f"    {label}: {score:.3f} {bar}")
    print_savings("classify_zero_shot", r.get("savings"))

    # 场景 3: PII 脱敏
    print("\n🔒 场景 3: PII 信息脱敏")
    doc = "甲方: 李明，电话 139-0000-8888，身份证号 110101199001011234，住址北京市朝阳区。乙方: 王芳，手机 186-1234-5678，邮箱 wangfang@example.com。"
    r = extract_pii(doc)
    print(f"  原文: {doc[:60]}...")
    pii = r.get("pii", {})
    print(f"  检测到的 PII:")
    for cat, items in pii.items():
        print(f"    [{cat}]: {items}")
    print_savings("extract_pii", r.get("savings"))

    # 场景 4: 脱敏掩码
    print("\n🚫 场景 4: PII 自动掩码")
    r = redact_pii(doc)
    print(f"  脱敏后: {r.get('redacted_text', r)}")
    print_savings("redact_pii", r.get("savings"))

    # 场景 5: 结构化提取
    print("\n📋 场景 5: 非结构化文本 → JSON")
    contract = "订单编号：A20240620，金额：¥128,000，供应商：深圳华腾电子有限公司，交货日期：2024年8月1日。"
    r = extract_json(contract, {
        "order": ["order_no::str::订单号", "amount::str::金额", "supplier::str::供应商名称", "delivery_date::str::交货日期"]
    })
    print(f"  原文: {contract}")
    print(f"  提取结果: {json.dumps(r.get('data', r), ensure_ascii=False, indent=4)}")
    print_savings("extract_json", r.get("savings"))

    # 场景 6: 生成追问
    print("\n❓ 场景 6: 自动生成追问")
    article2 = "特斯拉最新财报显示，Q2 营收达 250 亿美元，净利润 18 亿美元，利润率环比下降 3 个百分点，主要受价格战和原材料成本上升影响。"
    r = generate_followups(article2)
    qs = r.get("questions", r.get("followups", []))
    print(f"  原文: {article2}")
    print(f"  生成的问题:")
    for q in (qs if isinstance(qs, list) else []):
        print(f"    · {q}")
    print_savings("generate_followups", r.get("savings"))

    print("\n" + "=" * 60)
    print("✅ 演示完成 — 所有任务走 ZeroGPU 边缘小模型")
    print("=" * 60)

if __name__ == "__main__":
    demo()
