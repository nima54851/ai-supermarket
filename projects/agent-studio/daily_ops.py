#!/usr/bin/env python3
"""
agent-studio Daily Operations Bot
每天自动执行 GitHub 账号运营任务
"""
import requests, json, base64, random, os, sys
from datetime import datetime

TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not TOKEN:
    # fallback: read from ~/.openclaw/workspace/TOOLS.md
    try:
        with open(os.path.expanduser("~/.openclaw/workspace/TOOLS.md"), "r") as f:
            for line in f:
                if "GitHub Token" in line or "ghp_" in line:
                    for part in line.split():
                        if part.startswith("ghp_"):
                            TOKEN = part
                            break
                    if TOKEN:
                        break
    except Exception:
        pass
if not TOKEN:
    print("ERROR: GITHUB_TOKEN environment variable not set")
    sys.exit(1)
OWNER = "nima54851"
REPO = "agent-studio"
LOG_FILE = "/root/.openclaw/workspace/projects/agent-studio/.daily_log"

H = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
    "User-Agent": "agent-studio-daily/1.0"
}

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def sha(path):
    r = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}", headers=H, timeout=6)
    return r.json().get("sha") if r.status_code == 200 else None

def put(path, content, msg):
    data = {"message": msg, "content": base64.b64encode(content.encode("utf-8")).decode()}
    s = sha(path)
    if s: data["sha"] = s
    r = requests.put(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}", headers=H, json=data, timeout=10)
    return r.status_code in (200, 201)

def post_comment(owner, repo, issue_num, body):
    r = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}/comments",
        headers=H, json={"body": body}, timeout=8
    )
    if r.status_code in (200, 201):
        log(f"✅ Comment on {owner}/{repo}#{issue_num}")
        return True
    log(f"❌ Comment failed {r.status_code}: {r.text[:80]}")
    return False

def star(owner, repo):
    r = requests.put(f"https://api.github.com/user/starred/{owner}/{repo}", headers=H, timeout=6)
    ok = r.status_code == 204
    log(f"{'✅' if ok else '⚠️'} Star {owner}/{repo} ({r.status_code})")
    return ok

# 预定义的有价值项目池（AI/Agent 领域热门项目）
TRENDING_REPOS = [
    ("langgenius", "dify"),
    ("NousResearch", "hermes-agent"),
    ("DietrichGebert", "ponytail"),
    ("vercel", "eve"),
    ("openai", "openai-python"),
    ("anthropics", "anthropic-cookbook"),
    ("openclaw", "openclaw"),
    ("n8n-io", "n8n"),
    ("crewai", "crewai"),
    ("AutoGPT", "AutoGPT"),
    ("significant", "gravitate"),
    ("mcp", "mcp"),
    ("modelcontextprotocol", "python-sdk"),
]

COMMENT_TEMPLATES = [
    """Really impressive work on the structured approach here. The design decisions around {aspect} are particularly well thought out.

Question: how does this handle {challenge} in production scenarios? Would love to see some real-world benchmarks or case studies in the docs.

Also wondering — has there been any consideration for {future}? Happy to contribute a PR if there's interest!
""",
    """Great addition! This solves a real pain point in the AI agent space.

I've been building similar tooling with OpenClaw + n8n, and the {aspect} approach here is exactly what the ecosystem needs. 

One thought: have you benchmarked this against {alternative}? Performance comparison would be super valuable for the community.
""",
    """Solid contribution! The {feature} implementation looks clean.

Quick feedback: the error handling in {module} could benefit from more granular retry logic for transient failures. Also, has the team considered adding structured logging from the start? It'll save a lot of debugging pain later.

Happy to help if you want a hand with any of this!
""",
]

ASPECTS = ["multi-agent orchestration", "tool calling patterns", "context management", "error recovery", "streaming output", "memory management"]
CHALLENGES = ["context overflow", "token budget management", "parallel tool execution", "rate limiting", "long-running tasks"]
ALTERNATIVES = ["LangChain", "AutoGPT", "CrewAI", "Semantic Kernel", "LlamaIndex"]
FEATURES = ["structured output", "the tool schema", "the streaming API", "rate limiting"]
MODULES = ["tool_registry.py", "agent_core.py", "dispatcher.py", "memory.py"]

def generate_comment():
    t = random.choice(COMMENT_TEMPLATES)
    return t.format(
        aspect=random.choice(ASPECTS),
        challenge=random.choice(CHALLENGES),
        alternative=random.choice(ALTERNATIVES),
        feature=random.choice(FEATURES),
        module=random.choice(MODULES),
        future="WebAssembly support" if random.random() > 0.5 else "plugin marketplace"
    )

def run():
    date = datetime.now().strftime("%Y-%m-%d")
    log(f"=== Daily run {date} ===")

    # 1. 生成 GitHub Trending 报告
    log("Step 1: Generating GitHub Trending report...")
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "/root/.openclaw/workspace/projects/agent-studio/scripts/github_trending.py"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "GITHUB_TOKEN": TOKEN}
        )
        if result.returncode == 0:
            report_file = "/root/.openclaw/workspace/projects/agent-studio/scripts/REPORT.md"
            if os.path.exists(report_file):
                with open(report_file) as f:
                    content = f.read()
                ok = put("REPORT.md", content, f"ci: daily trending report {date}")
                log(f"{'✅' if ok else '⚠️'} Report committed")
        else:
            log(f"⚠️ Trending script failed: {result.stderr[:100]}")
    except Exception as e:
        log(f"⚠️ Report generation error: {e}")

    # 2. 在一个 AI 项目发高质量评论
    log("Step 2: Posting quality comment...")
    target = random.choice(TRENDING_REPOS)
    try:
        r = requests.get(
            f"https://api.github.com/repos/{target[0]}/{target[1]}/issues",
            headers=H, params={"state": "open", "sort": "comments", "per_page": 3},
            timeout=8
        )
        issues = r.json()
        if issues:
            body = generate_comment()
            post_comment(target[0], target[1], issues[0]["number"], body)
            star(target[0], target[1])
    except Exception as e:
        log(f"⚠️ Comment action error: {e}")

    # 3. Star agent-studio 自己
    star(OWNER, REPO)

    # 4. 记录 GitHub 活动数据（star/fork 增长趋势）
    log("Step 4: Recording GitHub activity stats...")
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "scripts/github_activity_tracker.py", f"{OWNER}/{REPO}", "--add"],
            capture_output=True, text=True, timeout=15,
            cwd="/root/.openclaw/workspace/projects/agent-studio",
            env={**os.environ, "GITHUB_TOKEN": TOKEN}
        )
        if result.returncode == 0:
            log(f"✅ Activity tracked via API")
        else:
            log(f"⚠️ Activity tracker: {result.stderr[:100] or result.stdout[:100]}")
    except Exception as e:
        log(f"⚠️ Activity tracker error: {e}")

    log(f"=== Run complete {datetime.now().strftime('%H:%M:%S')} ===\n")

if __name__ == "__main__":
    run()
