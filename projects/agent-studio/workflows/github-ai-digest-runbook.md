# GitHub AI News Digest — Runbook

## Overview

Automated daily workflow that fetches the top 5 trending AI/ML repositories from GitHub, generates a Markdown digest, saves it locally, and optionally sends it via webhook to Telegram, email, or any other channel.

## Architecture

```
Schedule (09:00 Beijing)
  → GitHub API Search (topic:artificial-intelligence, stars:>100)
  → Filter Top 5 (by stargazers_count)
  → Generate Markdown Digest
  → Save to File
  → Webhook → Telegram/Email (optional)
```

## Setup

### 1. Import to n8n

1. Open n8n at `http://localhost:5678`
2. Click **Workflows** → **Import from JSON**
3. Paste the contents of `github-ai-digest.json`
4. Click **Save**

### 2. Configure Credentials

**GitHub API:**
- Set `GITHUB_TOKEN` environment variable in n8n
- Or add a GitHub credential in n8n: **Settings → Credentials → New → GitHub API**
- Without token: 60 requests/hour limit. With token: 5,000/hour.

**Webhook (optional):**
- Set the webhook URL to your Telegram bot or email service
- Example Telegram: `https://api.telegram.org/bot<TOKEN>/sendMessage`

### 3. Activate

Toggle the workflow to **Active** in n8n.

## Node Reference

| Node | Purpose |
|------|---------|
| Schedule Trigger | Runs daily at 01:00 UTC = 09:00 Beijing |
| Fetch GitHub Trending | `GET /search/repositories?q=topic:AI` |
| Filter Top 5 | JS code to pick top 5 by stars |
| Generate Digest | Markdown template with rank, stars, description |
| Save to File | Writes `daily-digest.md` |
| Webhook Notify | POSTs to configured endpoint |

## Environment Variables

```bash
GITHUB_TOKEN=ghp_your_token_here
# Optional: set via n8n Settings → Variables
```

## Customization

### Change search query
Edit the `url` field in "Fetch GitHub Trending":
```
https://api.github.com/search/repositories?q=language:python stars:>500
```

### Different output format
Modify the JS code in "Generate Markdown Digest" node.

### Add email delivery
Add n8n's **Gmail** or **SMTP** node after "Generate Digest".

## Troubleshooting

**Rate limit (403):** Add `GITHUB_TOKEN` env var  
**No results:** Check the query parameters in GitHub API node  
**File not saved:** Verify write path permissions

---

*Part of [agent-studio](https://github.com/nima54851/agent-studio)*
