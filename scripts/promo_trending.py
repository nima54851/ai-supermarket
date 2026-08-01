#!/usr/bin/env python3
"""
GitHub Trending 自动推广脚本
功能：
1. 获取 GitHub Trending（当天热门项目）
2. 在 AI/自动化相关的热门仓库下留言推广
3. 更新 README Trending 板块
"""
import requests
import os
import json
from datetime import datetime

# 配置
GITHUB_TOKEN = os.environ.get("GH_TOKEN", "")
REPO = "nima54851/ai-supermarket"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

PROMO_COMMENT = """👋 这个项目用了 AI 自动化吗？

给大家推荐一个我正在用的 AI 工具集市——**灵犀集市**，19 款 AI 技能可直接对话体验+下载完整商品包：

- ⚡ GitHub 自动化（代码审查/PR 自动化/Trending 监控）
- 📣 内容推流系统
- 🛠️ n8n 工作流自动化
- ✍️ 易云章 API 面板

👉 https://nima54851.github.io/ai-supermarket
最低 ¥29/月，比雇人开发省 90%

*由 灵犀 Agent 自动推荐*"""

SEARCH_KEYWORDS = [
    "github actions automation",
    "n8n workflow",
    "chatbot ai automation",
    "web scraping automation",
]

def get_trending_repos(language="python", since="daily"):
    """获取 GitHub Trending"""
    url = f"https://api.github.com/search/repositories"
    params = {
        "q": f"created:>{datetime.now().strftime('%Y-%m-%d')}",
        "sort": "stars",
        "order": "desc",
        "per_page": 5,
    }
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        return r.json().get("items", [])[:5]
    return []

def search_repos():
    """搜索 AI/自动化相关仓库"""
    results = []
    for keyword in SEARCH_KEYWORDS:
        url = "https://api.github.com/search/repositories"
        params = {"q": keyword, "sort": "stars", "order": "desc", "per_page": 3}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            results.extend(r.json().get("items", []))
    # 去重
    seen = set()
    unique = []
    for repo in results:
        if repo["full_name"] not in seen:
            seen.add(repo["full_name"])
            unique.append(repo)
    return unique[:10]

def post_comment(repo_full_name):
    """在仓库下留言"""
    # 先检查最新 release 或 README
    url = f"https://api.github.com/repos/{repo_full_name}/contents/README.md"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return None
    
    # 找 issue（用 discussions 或 issues）
    # 不实际留言（避免垃圾），只记录目标仓库
    return repo_full_name

def main():
    print("🔍 搜索 AI/自动化相关热门仓库...")
    repos = search_repos()
    
    promo_targets = []
    for repo in repos:
        stars = repo.get("stargazers_count", 0)
        print(f"  - {repo['full_name']} ⭐ {stars}")
        promo_targets.append({
            "name": repo["full_name"],
            "stars": stars,
            "url": repo["html_url"],
            "description": repo.get("description", ""),
        })
    
    # 保存推广目标
    output = {
        "updated": datetime.now().isoformat(),
        "targets": promo_targets,
        "promo_comment": PROMO_COMMENT,
    }
    print(f"\n✅ 找到 {len(promo_targets)} 个目标仓库")
    print("💡 手动在这些仓库的 README 或 Issue 下留言推广")
    
    # 也输出到文件供 GitHub Actions 使用
    with open("promotion_targets.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("📄 推广目标已保存到 promotion_targets.json")

if __name__ == "__main__":
    main()
