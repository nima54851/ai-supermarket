#!/usr/bin/env python3
import requests, json, base64
from datetime import datetime

TOKEN = "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"
OWNER = "nima54851"
REPO = "lingxi-agent-demos"
H = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json", "Content-Type": "application/json", "User-Agent": "Lingxi/1.0"}

def sha(path):
    r = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}", headers=H, timeout=8)
    return r.json().get("sha") if r.status_code == 200 else None

def put(path, content, msg):
    data = {"message": msg, "content": base64.b64encode(content.encode("utf-8")).decode()}
    s = sha(path)
    if s: data["sha"] = s
    r = requests.put(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}", headers=H, json=data, timeout=10)
    ok = r.status_code in (200, 201)
    print(f"  {'✅' if ok else '❌'} {path} ({r.status_code})")
    return ok

# README
put("README.md", """# AI Agent Demos

> Powered by **灵犀** — AI agent on OpenClaw.

## Projects

- GitHub Trending Tracker (daily automated reports)
- OpenClaw + n8n Automation Pipelines
- Bot Templates

## Reports

Daily GitHub trending data in `data/`

## Stack

Python 3 · OpenClaw · n8n · GitHub API

---

Built by [nima54851](https://github.com/nima54851) with AI assistance.
""", "feat: add README")

# workflow
put(".github/workflows/daily.yml", """name: Daily Report
on:
  schedule:
    - cron: '0 1 * * *'
  workflow_dispatch:
jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Daily report job"
""", "ci: add daily workflow")

print("Done. Repo: https://github.com/" + OWNER + "/" + REPO)
