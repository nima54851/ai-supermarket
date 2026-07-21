#!/usr/bin/env python3
"""
Serper Daily Hot Topics — 每日热点搜索报告
每天运行一次，搜索各领域热点并汇总
"""
import requests
import json
from datetime import datetime

API_KEY = "a1e27f773565e1f150d753e3f8b2b889012434a3"
BASE = "https://google.serper.dev"

TOPICS = [
    ("🤖 AI Agent", "AI agent 2026 latest", 5),
    ("🔥 GitHub Trending", "GitHub trending 2026", 5),
    ("🎮 HTML5 Games", "Three.js HTML5 game 2026", 5),
    ("⚡ No-Code 自动化", "n8n automation workflow 2026", 5),
    ("💡 实用工具", "AI productivity tools 2026", 5),
]

def search(topic_name, query, num=5):
    try:
        resp = requests.post(
            f"{BASE}/search",
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": num, "gl": "cn", "hl": "zh-cn"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("organic", [])[:num]:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "snippet": r.get("snippet", "")[:100]
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]

def build_report():
    date_str = datetime.now().strftime("%Y-%m-%d")
    lines = [f"# 📊 每日热点报告 — {date_str}\n"]

    for topic_name, query, num in TOPICS:
        lines.append(f"\n## {topic_name}")
        results = search(topic_name, query, num)
        for i, r in enumerate(results, 1):
            if "error" in r:
                lines.append(f"  {i}. ❌ {r['error']}")
            else:
                lines.append(f"  {i}. **{r['title']}**")
                lines.append(f"     {r['url']}")
                if r['snippet']:
                    lines.append(f"     {r['snippet']}")

    lines.append("\n---\n*由 灵犀 自动整理 · Serper API*")
    return "\n".join(lines)

if __name__ == "__main__":
    report = build_report()
    # 保存报告
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = f"/root/.openclaw/workspace/reports/daily-hot-{date_str}.md"
    import os
    os.makedirs("/root/.openclaw/workspace/reports", exist_ok=True)
    with open(path, "w") as f:
        f.write(report)
    print(f"✅ 报告已保存: {path}")
    print("\n" + report)
