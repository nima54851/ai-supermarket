#!/usr/bin/env python3
"""
灵犀集市每日运营脚本
功能：
1. 检查站点健康状态
2. 更新状态 Issue
3. 监控 GitHub Trending（AI/自动化相关）
"""
import requests
import os
import json
from datetime import datetime

GH_TOKEN = os.environ.get("GH_TOKEN", "")
REPO = "nima54851/ai-supermarket"
HEADERS = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def health_check():
    """健康检查"""
    urls = {
        "GitHub Pages": "https://nima54851.github.io/ai-supermarket/",
        "jsDelivr CDN": "https://cdn.jsdelivr.net/gh/nima54851/ai-supermarket@main/index.html",
        "GitHub API": "https://api.github.com/repos/nima54851/ai-supermarket",
    }
    results = []
    for name, url in urls.items():
        try:
            r = requests.get(url, timeout=10)
            status = "✅" if r.status_code == 200 else f"❌ {r.status_code}"
            results.append(f"- {name}: {status}")
        except Exception as e:
            results.append(f"- {name}: ❌ {e}")
    return "\n".join(results)

def get_latest_release():
    """获取最新 Release"""
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    r = requests.get(url, timeout=10)
    if r.status_code == 200:
        d = r.json()
        return f"[v{d['tag_name']}]({d['html_url']}) - {d['name']}"
    return "无"

def get_issue_number():
    """查找或创建状态 Issue"""
    url = f"https://api.github.com/repos/{REPO}/issues"
    params = {"labels": "status", "state": "open", "per_page": 5}
    r = requests.get(url, headers=HEADERS, params=params, timeout=10)
    
    if r.status_code == 200:
        issues = r.json()
        for issue in issues:
            if "状态" in issue["title"] or "Status" in issue["title"]:
                return issue["number"]
    
    # 创建新 Issue
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "title": f"📊 灵犀集市状态报告 - {today}",
        "body": f"## 📊 {today} 运营报告\n\n正在加载...",
        "labels": ["status"]
    }
    r = requests.post(url, headers=HEADERS, json=data, timeout=10)
    if r.status_code == 201:
        return r.json()["number"]
    return None

def update_status_issue(number, health, release):
    """更新状态 Issue"""
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    url = f"https://api.github.com/repos/{REPO}/issues/{number}"
    
    body = f"""## 📊 灵犀集市 每日运营报告

**更新时间**: {today} (北京时间)

### 🏥 服务健康状态
{health}

### 📦 最新 Release
{release}

### 🔗 快速链接
- 🌐 网站: https://nima54851.github.io/ai-supermarket
- 📥 下载面板: https://github.com/nima54851/ai-supermarket/releases/tag/ecloudsign-panel-v1.0
- 🤖 GitHub: https://github.com/nima54851/ai-supermarket

---
*由 GitHub Actions 自动更新 | 灵犀 Agent*
"""
    r = requests.patch(url, headers=HEADERS, json={"body": body}, timeout=10)
    return r.status_code == 200

def main():
    mode = os.environ.get("OPERATION_MODE", "publish")
    print(f"📦 灵犀集市运营脚本启动 | 模式: {mode}")
    
    health = health_check()
    print("🏥 健康检查完成")
    
    if GH_TOKEN:
        release = get_latest_release()
        print(f"📦 最新Release: {release}")
        
        issue_num = get_issue_number()
        if issue_num:
            ok = update_status_issue(issue_num, health, release)
            print(f"{'✅' if ok else '❌'} 状态Issue更新: #{issue_num}")
    else:
        print("⚠️ 未设置 GH_TOKEN，跳过Issue更新")
    
    print("\n🏥 健康状态:")
    print(health)
    print("\n✅ 运营脚本完成")

if __name__ == "__main__":
    main()
