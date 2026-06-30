---
name: github-trending-monitor
description: Monitor and report GitHub trending repositories daily. Use when you need to track AI/ML project trends, competitive intelligence, or developer ecosystem insights.
---

# GitHub Trending Monitor Skill

## PURPOSE
Monitor GitHub trending repositories and generate daily/weekly reports for AI/ML developers, investors, or content creators.

## WHEN TO USE
- "Give me today's GitHub trending AI projects"
- "What's hot in the AI community this week?"
- "Track competitor repos automatically"
- "Build a daily dev trends newsletter"

## CAPABILITIES
- Search by topic, language, stars, date
- Deduplicate and rank results
- Output: Markdown, JSON, or email digest
- Schedule: daily via cron or n8n

## EXAMPLE WORKFLOW
1. Trigger: daily cron at 9am
2. Run: `python3 scripts/github_trending.py`
3. Output: Markdown report + JSON data
4. (Optional) Send via webhook to Telegram/email

## EXAMPLE USAGE
```bash
GITHUB_TOKEN=ghp_xxx python3 scripts/github_trending.py
```

## OUTPUT FORMAT
```json
{
  "generated": "2025-06-19T09:00:00Z",
  "sections": [
    {
      "title": "🤖 AI/ML 热门",
      "repos": [
        {"name": "owner/repo", "stars": 12345, "url": "..."}
      ]
    }
  ]
}
```
