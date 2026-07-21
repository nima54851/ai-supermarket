# Analytics Dashboard Skill

Generate beautiful HTML analytics dashboards showing OpenClaw agent usage stats, GitHub activity trends, and workflow performance metrics.

## Features
- GitHub stars/forks/watchers timeline
- OpenClaw session usage charts
- n8n workflow execution stats
- ZeroGPU token savings tracker
- Daily/weekly/monthly views

## Usage
```bash
python3 analytics_dashboard.py --period 30d --output dashboard.html
```

## Files
- `analytics_dashboard.py` — Main generator
- `dashboard_template.html` — HTML/CSS template
- `metrics_collector.py` — GitHub API + OpenClaw stats collector
