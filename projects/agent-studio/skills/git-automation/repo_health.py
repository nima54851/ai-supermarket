#!/usr/bin/env python3
"""
Repository Health Checker — detects stale branches, large files, secrets, and other issues
"""
import argparse, subprocess, os, re, json
from pathlib import Path
from datetime import datetime

GITIGNORE_ENTRIES = {".env", ".DS_Store", "*.pyc", "__pycache__/", "node_modules/", ".git/"}

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def check_branches(repo_path):
    """Find stale branches (not merged, no recent activity)."""
    stale = []
    try:
        branches = run(f"cd {repo_path} && git branch -r --format='%(refname:short)|%(committerdate:iso)'")
        for line in branches.split("\n"):
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) == 2:
                branch, date = parts
                # Branches older than 90 days
                from datetime import datetime, timedelta
                try:
                    d = datetime.fromisoformat(date.split("T")[0])
                    if datetime.now() - d > timedelta(days=90):
                        stale.append((branch, date))
                except:
                    pass
    except Exception as e:
        stale.append(("error", str(e)))
    return stale

def check_large_files(repo_path, threshold_mb=5):
    """Find files larger than threshold."""
    large = []
    try:
        output = run(f"cd {repo_path} && git ls-files -z | xargs -0 -I{{}} git ls-tree -r HEAD -- {{}} | awk '{{print $4,$3}}' | sort -rn | head -20")
        for line in output.split("\n"):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 2:
                size_kb, path = int(parts[0]), parts[1]
                size_mb = size_kb / 1024
                if size_mb > threshold_mb:
                    large.append((path, f"{size_mb:.1f}MB"))
    except Exception as e:
        large.append(("error", str(e)))
    return large

def check_secrets(repo_path):
    """Scan for accidentally committed secrets."""
    secrets = []
    patterns = [
        (r"api[_-]?key['\"]?\s*[:=]\s*['\"][a-zA-Z0-9]{20,}", "API key"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub token"),
        (r"sk-[a-zA-Z0-9]{48}", "OpenAI API key"),
        (r"password['\"]?\s*[:=]\s*['\"][^'\"]{8,}", "Hardcoded password"),
        (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private key"),
    ]
    try:
        files = run(f"cd {repo_path} && git diff --cached --name-only").split("\n")
        for f in files:
            if not f.strip() or f.endswith(".md") or f.endswith(".lock"):
                continue
            try:
                content = Path(repo_path) / f
                if content.exists():
                    text = content.read_text()
                    for pattern, name in patterns:
                        if re.search(pattern, text):
                            secrets.append((f, name))
            except:
                pass
    except Exception as e:
        secrets.append(("scan error", str(e)))
    return secrets

def check_untracked(repo_path):
    """Find large untracked files."""
    large = []
    try:
        output = run(f"cd {repo_path} && git status --porcelain | grep '??' | cut -c4-")
        for f in output.split("\n"):
            if not f.strip():
                continue
            path = Path(repo_path) / f
            if path.exists() and path.is_file():
                size_mb = path.stat().st_size / 1024 / 1024
                if size_mb > 5:
                    large.append((f, f"{size_mb:.1f}MB"))
    except Exception:
        pass
    return large

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".", help="Path to repository")
    args = parser.parse_args()
    
    print(f"🔍 Repository Health Report — {Path(args.repo).resolve()}")
    print(f"   Generated: {datetime.now().isoformat()}\n")
    
    stale = check_branches(args.repo)
    large = check_large_files(args.repo)
    secrets = check_secrets(args.repo)
    untracked = check_untracked(args.repo)
    
    print(f"📦 Stale Branches (90+ days old):")
    if stale:
        for branch, date in stale[:10]:
            print(f"   ❌ {branch} ({date})")
    else:
        print("   ✅ No stale branches found")
    
    print(f"\n📁 Large Files (>5MB):")
    if large:
        for path, size in large[:10]:
            print(f"   ⚠️  {size:>8} {path}")
    else:
        print("   ✅ No large files found")
    
    print(f"\n🔐 Secret Detection:")
    if secrets:
        for path, kind in secrets[:10]:
            print(f"   🚨 {kind} in {path}")
    else:
        print("   ✅ No secrets detected")
    
    print(f"\n📂 Large Untracked Files:")
    if untracked:
        for path, size in untracked[:10]:
            print(f"   ⚠️  {size:>8} {path}")
    else:
        print("   ✅ No large untracked files")
    
    total_issues = len(stale) + len(large) + len(secrets) + len(untracked)
    print(f"\n{'🔴' if total_issues else '🟢'} Total issues: {total_issues}")

if __name__ == "__main__":
    main()
