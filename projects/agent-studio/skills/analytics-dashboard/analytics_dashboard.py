#!/usr/bin/env python3
"""
OpenClaw + GitHub Analytics Dashboard Generator
Generates a beautiful HTML dashboard from GitHub API + local stats.
"""
import json, os, sys, subprocess, time
from datetime import datetime, timedelta

REPO = "nima54851/agent-studio"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def gh_api(path):
    import urllib.request
    url = f"https://api.github.com/{path}"
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def gh_stars_history():
    """Get star count history by walking events"""
    events = gh_api(f"repos/{REPO}/events?per_page=100")
    stars_by_day = {}
    count = 0
    for e in events:
        if e["type"] == "WatchEvent":
            d = e["created_at"][:10]
            stars_by_day[d] = stars_by_day.get(d, 0) + 1
    return stars_by_day

def repo_stats():
    data = gh_api(f"repos/{REPO}")
    return {
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "watchers": data["subscribers_count"],
        "issues": data["open_issues_count"],
        "created": data["created_at"][:10],
        "updated": data["updated_at"][:10]
    }

def generate_dashboard(stats, star_history):
    today = datetime.now().strftime("%Y-%m-%d")
    stars_json = json.dumps(star_history)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>agent-studio Analytics Dashboard</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh;padding:2rem}}
  .header{{text-align:center;margin-bottom:2rem}}
  .header h1{{font-size:2rem;color:#38bdf8;margin-bottom:.5rem}}
  .header p{{color:#94a3b8}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem;margin-bottom:2rem}}
  .card{{background:#1e293b;border-radius:12px;padding:1.5rem;border:1px solid #334155}}
  .card .label{{font-size:.75rem;text-transform:uppercase;letter-spacing:.1em;color:#94a3b8;margin-bottom:.5rem}}
  .card .value{{font-size:2.5rem;font-weight:700;color:#38bdf8}}
  .card.star .value{{color:#facc15}}
  .card.fork .value{{color:#4ade80}}
  .card.issue .value{{color:#f87171}}
  .chart{{background:#1e293b;border-radius:12px;padding:1.5rem;border:1px solid #334155;margin-bottom:2rem}}
  .chart h2{{font-size:1.1rem;margin-bottom:1rem;color:#e2e8f0}}
  .footer{{text-align:center;color:#64748b;font-size:.85rem;margin-top:2rem}}
</style>
</head>
<body>
<div class="header">
  <h1>📊 agent-studio Analytics</h1>
  <p>Updated: {today} · {REPO}</p>
</div>
<div class="grid">
  <div class="card star"><div class="label">GitHub Stars</div><div class="value">{stats['stars']}</div></div>
  <div class="card fork"><div class="label">Forks</div><div class="value">{stats['forks']}</div></div>
  <div class="card"><div class="label">Watchers</div><div class="value">{stats['watchers']}</div></div>
  <div class="card issue"><div class="label">Open Issues</div><div class="value">{stats['issues']}</div></div>
</div>
<div class="chart">
  <h2>⭐ Star Activity</h2>
  <div id="chart"></div>
</div>
<script>
const data = {stars_json};
const entries = Object.entries(data).slice(-14);
document.getElementById('chart').innerHTML = entries.map(([d,v]) =>
  `<div style="display:flex;align-items:flex-end;gap:.5rem;margin-bottom:.5rem">
    <span style="width:80px;font-size:.75rem;color:#94a3b8">{d}</span>
    <div style="background:#38bdf8;height:{max(10, v*20)}px;min-width:20px;border-radius:4px"></div>
    <span style="font-size:.85rem;color:#38bdf8">{v} ⭐</span>
  </div>`
).join('');
</script>
<div class="footer">Built with OpenClaw · Updated daily</div>
</body>
</html>"""

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="dashboard.html")
    args = p.parse_args()
    
    print("Collecting GitHub stats...")
    stats = repo_stats()
    print(f"  Stars: {stats['stars']}, Forks: {stats['forks']}, Issues: {stats['issues']}")
    
    print("Generating dashboard...")
    html = generate_dashboard(stats, {})
    with open(args.output, "w") as f:
        f.write(html)
    print(f"✅ Dashboard saved to {args.output}")

if __name__ == "__main__":
    main()
