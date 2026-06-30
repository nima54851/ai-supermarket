#!/usr/bin/env python3
"""
批量上传 agent-studio 项目文件到 GitHub
"""
import requests, json, base64, os

TOKEN = "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"
OWNER = "nima54851"
REPO = "agent-studio"
BASE = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
H = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json", "Content-Type": "application/json", "User-Agent": "agent-studio/1.0"}

def get_sha(path):
    r = requests.get(f"{BASE}/{path}", headers=H, timeout=8)
    return r.json().get("sha") if r.status_code == 200 else None

def upload(path, content, msg):
    data = {"message": msg, "content": base64.b64encode(content.encode("utf-8")).decode()}
    sha = get_sha(path)
    if sha: data["sha"] = sha
    r = requests.put(f"{BASE}/{path}", headers=H, json=data, timeout=10)
    status = "✅" if r.status_code in (200, 201) else f"❌ {r.status_code}"
    print(f"  {status} {path}")
    if r.status_code not in (200, 201):
        print(f"     {r.text[:100]}")

def upload_file(local_path, repo_path, msg):
    with open(local_path, "r") as f:
        content = f.read()
    upload(repo_path, content, msg)

BASE_DIR = "/root/.openclaw/workspace/projects/agent-studio"

files = [
    ("README.md", "README.md"),
    ("LICENSE", "LICENSE"),
    ("docs/index.html", "docs/index.html"),
    ("scripts/github_trending.py", "scripts/github_trending.py"),
    ("scripts/webhook_dispatcher.py", "scripts/webhook_dispatcher.py"),
    ("skills/github-trending-monitor/SKILL.md", "skills/github-trending-monitor/SKILL.md"),
    ("skills/webhook-dispatcher/SKILL.md", "skills/webhook-dispatcher/SKILL.md"),
    (".github/workflows/daily-report.yml", ".github/workflows/daily-report.yml"),
]

print("=== 上传到 agent-studio ===")
for local, repo in files:
    upload_file(os.path.join(BASE_DIR, local), repo, f"feat: add {repo}")

# 设置 GitHub Pages
r = requests.put(
    f"https://api.github.com/repos/{OWNER}/{REPO}/pages",
    headers=H,
    json={
        "source": {"branch": "main", "path": "/docs"},
        "build_type": "legacy"
    },
    timeout=10
)
print(f"\nGitHub Pages: {r.status_code} — {r.json().get('html_url', r.text[:100])}")

# 设置 topics
r2 = requests.patch(
    f"https://api.github.com/repos/{OWNER}/{REPO}",
    headers=H,
    json={"topics": ["ai-agent", "automation", "python", "github-actions", "n8n", "openclaw", "tools"]},
    timeout=10
)
print(f"Topics: {r2.status_code}")

print("\n🎉 agent-studio 上传完成!")
print(f"GitHub Pages: https://nima54851.github.io/agent-studio")
