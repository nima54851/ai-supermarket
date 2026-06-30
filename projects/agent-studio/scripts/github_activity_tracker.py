#!/usr/bin/env python3
"""
GitHub Repository Health Monitor
Tracks star/fork growth over time and alerts on significant changes
"""
import requests
import json
import os
import sys
from datetime import datetime

def get_stats(owner, repo, token):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=10)
    if r.status_code != 200:
        print(f"Error fetching stats: {r.status_code}")
        return None
    d = r.json()
    return {
        "stars": d["stargazers_count"],
        "forks": d["forks_count"],
        "open_issues": d["open_issues_count"],
        "watchers": d["watchers_count"],
        "subscribers": d["subscribers_count"],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def load_history(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return []

def save_history(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: github_activity_tracker.py <owner/repo> [--add]")
        sys.exit(1)
    
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("GITHUB_TOKEN not set")
        sys.exit(1)
    
    repo = sys.argv[1]
    owner, repo_name = repo.split("/")
    history_file = f"/tmp/{repo_name}_activity.json"
    
    history = load_history(history_file)
    current = get_stats(owner, repo_name, token)
    
    if current:
        history.append(current)
        # Keep last 90 days
        if len(history) > 90:
            history = history[-90:]
        save_history(history_file, history)
        
        print(f"📊 {owner}/{repo_name} — Stars: {current['stars']}, Forks: {current['forks']}")
        print(f"   Last updated: {current['timestamp']}")
        
        # Alert on significant changes
        if len(history) >= 2:
            prev = history[-2]
            star_diff = current['stars'] - prev['stars']
            fork_diff = current['forks'] - prev['forks']
            if star_diff > 0 or fork_diff > 0:
                print(f"   📈 +{star_diff} stars, +{fork_diff} forks since last check")
