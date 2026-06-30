#!/usr/bin/env python3
"""
GitHub Trending 每日报告生成器 v3（带 Token）
用法: python3 scraper.py
Token: 从 .env 加载 GITHUB_TOKEN
"""
import requests, json, time, os
from datetime import datetime, timedelta

# === 加载 Token ===
TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not TOKEN:
    try:
        from dotenv import load_dotenv
        load_dotenv("/root/.openclaw/workspace/projects/github-trending/.env")
        TOKEN = os.environ.get("GITHUB_TOKEN", "")
    except ImportError:
        pass

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}" if TOKEN else "",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "Lingxi-GitHub-Trending/1.0"
}

def search(q, sort="stars", per_page=10):
    """GitHub API 搜索"""
    r = requests.get("https://api.github.com/search/repositories",
        headers=HEADERS, params={"q": q, "sort": sort, "order": "desc", "per_page": per_page}, timeout=15)
    if r.status_code != 200:
        print(f"  ⚠️  {r.status_code}: {r.text[:100]}")
        return []
    return r.json().get("items", [])

def fmt_table(repos, title):
    if not repos:
        return f"## {title}\n_暂无数据_\n"
    lines = [f"## {title}", "",
             "| # | 项目 | ⭐ | 🍴 | 语言 | 简介 |",
             "|---|------|----|----|------|------|"]
    for i, r in enumerate(repos, 1):
        name = f"[{r['full_name']}](https://github.com/{r['full_name']})"
        desc = (r.get("description") or "—")[:38]
        lines.append(
            f"| {i} | {name} | {r['stargazers_count']:,} | {r['forks_count']:,} "
            f"| {r.get('language') or '—'} | {desc} |"
        )
    lines.append("")
    return "\n".join(lines)

def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    since14 = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    since7  = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    print(f"📡 抓取开始 | {ts} | Token: {'✅ 已设置' if TOKEN else '❌ 未设置'}")

    sections = [
        ("🤖 AI / LLM 热门项目", [
            search(f"topic:artificial-intelligence stars:>200 pushed:>{since14}", per_page=8),
        ]),
        ("🔧 AI Agent / 开发框架", [
            search("openai stars:>100 pushed:>2026-06-18", per_page=5),
            search("langchain stars:>100 pushed:>2026-06-18", per_page=5),
        ]),
        ("🐍 Python 生态 新势力", [search(f"language:python stars:>200 pushed:>{since14}", per_page=10)]),
        ("🔥 全站近期上升项目", [search(f"stars:>500 pushed:>{since7}", per_page=12)]),
        ("🆕 近期新晋项目（14天内）", [search(f"created:>{since14} stars:>100", sort="stars", per_page=8)]),
    ]

    report = [
        f"# 📊 GitHub 每日热点追踪",
        f"**生成时间**: {ts}",
        "",
        f"*由 灵犀 AI 自动生成 · GitHub API · Token: {'nima54851' if TOKEN else 'anonymous'}*",
        "",
        "---"
    ]

    for title, repos_lists in sections:
        # 合并多个搜索结果
        all_repos = []
        for repos in repos_lists:
            all_repos.extend(repos)
        # 去重
        seen, unique = set(), []
        for r in sorted(all_repos, key=lambda x: x.get("stargazers_count", 0), reverse=True):
            if r["full_name"] not in seen:
                seen.add(r["full_name"])
                unique.append(r)
        print(f"  ✅ {title}: {len(unique)} 个")
        report.append(fmt_table(unique[:10], title))
        time.sleep(0.5)

    report.append("---")
    report.append("*Powered by 灵犀 AI · GitHub API*")

    content = "\n".join(report)
    output_dir = "/root/.openclaw/workspace/projects/github-trending"
    today = datetime.now().strftime("%Y-%m-%d")

    md_file = f"{output_dir}/report_{today}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ 报告已保存: {md_file}")
    print("\n" + content)

if __name__ == "__main__":
    main()
