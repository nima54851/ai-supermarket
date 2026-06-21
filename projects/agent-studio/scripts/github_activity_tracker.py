#!/usr/bin/env python3
"""
github_activity_tracker.py
Track GitHub stars, forks, and watchers over time for a repository.
Run daily via cron to build historical data and detect growth trends.
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("❌ requests not installed. Run: pip install requests")
    sys.exit(1)


GITHUB_API = "https://api.github.com/repos"
DATA_DIR = Path(__file__).parent / ".activity_data"
TOKEN = ""  # Set via GITHUB_TOKEN env var or fill in


def get_rate_limit():
    """Check remaining API rate limit."""
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
    resp = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
    if resp.ok:
        data = resp.json()
        remaining = data["resources"]["core"]["remaining"]
        reset_ts = data["resources"]["core"]["reset"]
        return remaining, reset_ts
    return 0, 0


def fetch_repo_stats(owner: str, repo: str) -> Optional[dict]:
    """Fetch current stats for a repository."""
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {"Accept": "application/vnd.github.v3+json"}
    url = f"{GITHUB_API}/{owner}/{repo}"
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 403:
            print("⚠️  Rate limited. Waiting...")
            return None
        if resp.status_code != 200:
            print(f"❌ API error: {resp.status_code}")
            return None
        
        data = resp.json()
        return {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "watchers": data["watchers_count"],
            "open_issues": data["open_issues_count"],
            "subscribers": data.get("subscribers_count", 0),
            "language": data.get("language"),
            "description": data.get("description", ""),
        }
    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return None


def load_history(owner: str, repo: str) -> list:
    """Load existing historical data."""
    DATA_DIR.mkdir(exist_ok=True)
    history_file = DATA_DIR / f"{owner}_{repo}.json"
    if history_file.exists():
        with open(history_file, "r") as f:
            return json.load(f)
    return []


def save_history(owner: str, repo: str, history: list):
    """Save updated historical data."""
    DATA_DIR.mkdir(exist_ok=True)
    history_file = DATA_DIR / f"{owner}_{repo}.json"
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)


def add_record(owner: str, repo: str, dry_run: bool = False):
    """Fetch and record today's stats."""
    stats = fetch_repo_stats(owner, repo)
    if stats is None:
        print("❌ Could not fetch stats. Aborting.")
        return False
    
    if dry_run:
        print(f"[DRY RUN] Would record: {stats}")
        return True
    
    history = load_history(owner, repo)
    today = stats["date"]
    
    # Replace today's record if exists, otherwise append
    updated = [r for r in history if r["date"] != today]
    updated.append(stats)
    updated.sort(key=lambda x: x["date"])
    
    save_history(owner, repo, updated)
    print(f"✅ Recorded {today}: ⭐{stats['stars']} 🍴{stats['forks']} 👀{stats['watchers']}")
    return True


def show_trend(owner: str, repo: str, days: int = 30):
    """Show growth trend over the past N days."""
    history = load_history(owner, repo)
    if not history:
        print("📊 No historical data. Run with --add first.")
        return
    
    today = datetime.utcnow()
    cutoff = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [r for r in history if r["date"] >= cutoff]
    
    if len(recent) < 2:
        print(f"📊 Only {len(recent)} data point(s) available. Need at least 2 for trends.")
        return
    
    first = recent[0]
    last = recent[-1]
    delta_stars = last["stars"] - first["stars"]
    delta_forks = last["forks"] - first["forks"]
    days_span = len(recent)
    
    print(f"\n📊 {owner}/{repo} — Growth over {days_span} days")
    print(f"   Stars:  {first['stars']:,} → {last['stars']:,}  ({delta_stars:+,})")
    print(f"   Forks:  {first['forks']:,} → {last['forks']:,}  ({delta_forks:+,})")
    print(f"   Watchers: {first['watchers']:,} → {last['watchers']:,}")
    print(f"   Daily avg: ⭐ {delta_stars/days_span:+.2f}/day  🍴 {delta_forks/days_span:+.2f}/day")
    print(f"   Open issues: {last['open_issues']}")
    print()


def show_chart(owner: str, repo: str):
    """Show ASCII sparkline of star growth."""
    history = load_history(owner, repo)
    if not history:
        print("📊 No data. Run with --add first.")
        return
    
    stars = [r["stars"] for r in history]
    forks = [r["forks"] for r in history]
    dates = [r["date"][-5:] for r in history]  # MM-DD
    
    print(f"\n📈 Star History: {owner}/{repo}")
    print(f"   Start: {stars[0]:,} ({dates[0]})  Current: {stars[-1]:,} ({dates[-1]})")
    
    # Sparkline
    min_s, max_s = min(stars), max(stars)
    scale = (max_s - min_s) or 1
    height = 5
    rows = [[" " for _ in stars] for _ in range(height)]
    
    for i, s in enumerate(stars):
        bar_height = int((s - min_s) / scale * (height - 1))
        for h in range(height - 1, bar_height - 1, -1):
            rows[h][i] = "█"
    
    for row in rows:
        print("   " + "".join(row))
    print(f"   " + "".join("▔" if i % max(1, len(stars)//10) == 0 else " " for i in range(len(stars))))
    print()


def main():
    parser = argparse.ArgumentParser(description="GitHub Activity Tracker")
    parser.add_argument("repo", nargs="?", default="nima54851/agent-studio", help="owner/repo")
    parser.add_argument("--add", action="store_true", help="Record today's stats")
    parser.add_argument("--trend", action="store_true", help="Show growth trend")
    parser.add_argument("--chart", action="store_true", help="Show ASCII sparkline")
    parser.add_argument("--days", type=int, default=30, help="Trend period in days")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    args = parser.parse_args()
    
    global TOKEN
    TOKEN = Path("/root/.openclaw/workspace/TOOLS.md").read_text()
    import os
    TOKEN = os.environ.get("GITHUB_TOKEN", "")
    
    owner, repo = args.repo.split("/")
    
    remaining, reset = get_rate_limit()
    print(f"ℹ️  API rate limit: {remaining} remaining")
    
    if args.add:
        add_record(owner, repo, dry_run=args.dry_run)
    
    if args.trend:
        show_trend(owner, repo, days=args.days)
    
    if args.chart:
        show_chart(owner, repo)
    
    if not (args.add or args.trend or args.chart):
        # Default: add + show trend
        add_record(owner, repo, dry_run=args.dry_run)
        show_trend(owner, repo, days=args.days)


if __name__ == "__main__":
    main()
