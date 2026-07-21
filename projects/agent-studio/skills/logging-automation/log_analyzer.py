#!/usr/bin/env python3
"""
log_analyzer.py — AI 日志异常检测 & 根因分析
支持 OpenAI / Azure OpenAI / Ollama / Anthropic
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


SYSTEM_PROMPT = """你是一个高级 SRE（站点可靠性工程师）。分析日志片段，输出结构化的 JSON 报告。
严格按以下 JSON schema 输出，不要输出其他内容：

{
  "summary": "一句话描述整体日志状态",
  "error_count": 整数，ERROR 日志条数,
  "warning_count": 整数，WARN 日志条数,
  "anomaly_score": 0.0-1.0 的浮点数，越高越异常,
  "issue_type": "database|network|authentication|timeout|memory|cpu|unknown",
  "root_causes": ["可能原因1", "可能原因2", "可能原因3"],
  "fix_suggestions": ["建议1", "建议2"],
  "affected_endpoints": ["受影响的接口/路径"],
  "severity": "critical|high|medium|low|info",
  "next_steps": ["下一步操作建议"]
}
"""

DEFAULT_MODEL = os.environ.get("LOG_ANALYZER_MODEL", "gpt-4o-mini")


def build_user_prompt(log_lines: list[dict]) -> str:
    body = "\n".join(
        f"[{l.get('timestamp', l.get('_parsed_at', '?'))}] "
        f"{l.get('level', l.get('severity', 'INFO'))} "
        f"{l.get('msg', l.get('message', l.get('line', json.dumps(l))))}"
        for l in log_lines[:200]  # 限制 token 窗口
    )
    return f"以下是最近的应用日志，请分析：\n\n{body}\n\n请输出 JSON 分析报告："


def analyze_with_openai(logs: list[dict], model: str, api_key: str | None) -> dict:
    client = openai.OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(logs)},
        ],
        temperature=0.1,
        max_tokens=1024,
    )
    content = response.choices[0].message.content.strip()
    # 尝试提取 JSON
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    return json.loads(content.strip())


def analyze_with_ollama(logs: list[dict], model: str, base_url: str) -> dict:
    import urllib.request
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(logs)},
        ],
        "stream": False,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{base_url}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.load(resp)
    content = result["message"]["content"].strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    return json.loads(content.strip())


def parse_args():
    p = argparse.ArgumentParser(description="AI 日志异常检测")
    p.add_argument("--input", "-i", required=True, help="解析后的 JSONL 日志文件")
    p.add_argument("--prompt", default=None, help="自定义 system prompt 文件")
    p.add_argument("--output", "-o", default="log_analysis.json", help="分析结果输出路径")
    p.add_argument("--model", "-m", default=DEFAULT_MODEL, help="使用的模型")
    p.add_argument("--api-key", default=None, help="OpenAI API Key（可设环境变量 OPENAI_API_KEY）")
    p.add_argument("--backend", choices=["openai", "ollama", "anthropic"], default="openai",
                   help="AI 后端")
    p.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    p.add_argument("--max-lines", type=int, default=0, help="最多分析行数（0=全部）")
    return p.parse_args()


def main():
    args = parse_args()
    logs = []
    with open(args.input) as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))
                if args.max_lines > 0 and len(logs) >= args.max_lines:
                    break

    if not logs:
        print("❌ No logs found in input file")
        sys.exit(1)

    print(f"📊 Analyzing {len(logs)} log lines with {args.backend} / {args.model}...")

    try:
        if args.backend == "openai":
            result = analyze_with_openai(logs, args.model, args.api_key)
        elif args.backend == "ollama":
            result = analyze_with_ollama(logs, args.model, args.ollama_url)
        else:
            print("❌ Anthropic backend not yet implemented")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)

    result["_meta"] = {
        "input": args.input,
        "model": args.model,
        "backend": args.backend,
        "lines_analyzed": len(logs),
        "analyzed_at": datetime.utcnow().isoformat(),
    }

    with open(args.output, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    score = result.get("anomaly_score", 0)
    severity = result.get("severity", "?")
    print(f"\n{'🔴' if score > 0.7 else '🟡' if score > 0.4 else '🟢'} "
          f"Anomaly Score: {score:.2f} | Severity: {severity.upper()}")
    print(f"📝 Summary: {result.get('summary', 'N/A')}")
    print(f"✅ Analysis saved to {args.output}")


if __name__ == "__main__":
    main()
