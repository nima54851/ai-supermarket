# Browser Automation Integration

> n8n workflow for AI-powered browser automation using Playwright — scrape, screenshot, fill forms, and run multi-step web workflows.

## Overview

Combine Playwright's browser automation power with AI decision-making. The agent can see pages, interact with them, and execute complex web workflows automatically.

## Components

### n8n Workflow: `n8n-browser-automation-workflow.json`

- **Trigger:** Webhook or schedule
- **Process:**
  1. Receive task (URL, action: click/scroll/screenshot/fill/submit)
  2. AI agent plans the browser interaction sequence
  3. Playwright Node executes actions headlessly
  4. Capture results: page HTML, screenshots, extracted data
  5. AI agent analyzes results
  6. Route output: JSON, Slack, email, database
- **Output:** Structured data, screenshots, AI analysis

### Use Cases

- **Web scraping:** Extract structured data from dynamic pages
- **Form automation:** Auto-fill and submit forms at scale
- **Screenshots as a service:** Full-page, region, or element screenshots
- **Login automation:** Handle auth flows, cookies, sessions
- **Price monitoring:** Track e-commerce prices automatically
- **SEO audits:** Screenshot + analyze pages for broken links, meta tags
- **A/B testing:** Automated visual comparison

## Setup

```bash
# 1. Install Playwright
npm install -g playwright
playwright install chromium

# 2. Import workflow
# n8n → Settings → Import from JSON → paste n8n-browser-automation-workflow.json

# 3. Environment variables
PLAYWRIGHT_BROWSER=chromium
BROWSER_HEADLESS=true
SCREENSHOT_DIR=/tmp/screenshots
```

## Usage

```python
import requests

# Trigger a browser task
result = requests.post(
    "https://your-n8n-url/webhook/browser-automation",
    json={
        "url": "https://github.com/trending/python",
        "actions": [
            {"type": "wait", "selector": ".Box-row"},
            {"type": "extract", "selector": ".Box-row a", "attr": "href"},
            {"type": "screenshot", "fullPage": True}
        ],
        "userAgent": "Mozilla/5.0..."
    }
).json()
print(result["extracted_data"])
print(result["screenshot_url"])
```

## Browser Actions Reference

| Action | Description | Example |
|--------|-------------|---------|
| `goto` | Navigate to URL | `{"type": "goto", "url": "..."}` |
| `click` | Click element | `{"type": "click", "selector": "#btn"}` |
| `fill` | Type text | `{"type": "fill", "selector": "input", "text": "..."}` |
| `screenshot` | Take screenshot | `{"type": "screenshot", "fullPage": true}` |
| `wait` | Wait for element | `{"type": "wait", "selector": ".content"}` |
| `extract` | Extract data | `{"type": "extract", "selector": "h1", "attr": "text"}` |
| `scroll` | Scroll page | `{"type": "scroll", "y": 1000}` |
| `select` | Select dropdown | `{"type": "select", "selector": "select", "value": "2"}` |
| `upload` | Upload file | `{"type": "upload", "selector": "input[type=file]", "path": "/tmp/file.pdf"}` |

## AI Agent Integration

The workflow calls OpenClaw agent (灵犀 AI) to:
1. Parse the natural language task → browser action sequence
2. Analyze extracted content for meaning
3. Decide next steps in multi-page workflows

```bash
# Direct AI agent call
curl -X POST https://your-openclaw-url/mcp \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"task": "Go to Hacker News, find posts about AI agents from today, and summarize them"}'
```

## Required Skills

- `browser-automation` — Core Playwright skill
- `agent-browser` — OpenClaw browser interaction skill
- `web-scraping` — Data extraction patterns
- `n8n-workflow-builder` — Customize the workflow

---

*Built with 灵犀 AI · agent-studio*
