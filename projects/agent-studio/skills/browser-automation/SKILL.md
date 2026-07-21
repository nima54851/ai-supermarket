# Browser Automation Skill

> AI-powered browser automation using Playwright + OpenClaw Agent Browser skill.

## Overview

Automate any web interaction: scraping, form filling, screenshots, data extraction, end-to-end testing.

## Architecture

```
OpenClaw Agent Browser Skill
        ↓
Playwright / Puppeteer
        ↓
Target Website (headless/headed)
        ↓
Structured Data / Screenshots / Reports
```

## Setup

```bash
npm install -g playwright
playwright install chromium
```

## Core Capabilities

| Capability | Use Case | Command |
|---|---|---|
| **Web Scraping** | Extract structured data from any page | `npx playwright open <url>` |
| **Form Filling** | Auto-submit forms, upload files | `playwright.fill()` |
| **Screenshots** | Full page, viewport, element shots | `page.screenshot()` |
| **PDF Export** | Save page as PDF | `page.pdf()` |
| **E2E Testing** | Automated UI testing | `playwright test` |
| **Data Extraction** | Pull tables, lists, prices, product info | `page.locator().all_text_contents()` |

## Prompt Template

```
Use the agent-browser skill to:
1. Navigate to {URL}
2. Extract: {what to extract}
3. Return: {format (JSON/csv/markdown)}
```

## n8n Integration

See `integrations/browser-automation/browser-scraper.json` for the n8n workflow that:
- Accepts URL + extraction rules
- Runs Playwright scraper via webhook
- Returns structured JSON data

## Example: E-commerce Price Monitor

```python
import asyncio
from playwright.async_api import async_playwright

async def monitor_price(url, target_selector):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        price = await page.locator(target_selector).text_content()
        await browser.close()
        return {"url": url, "price": price}

# Run
asyncio.run(monitor_price("https://shop.example.com/item", ".price"))
```

## OpenClaw Agent Browser Skill Usage

The `agent-browser` skill provides:
- DOM inspection & traversal
- Form filling & submission
- Screenshot capture
- Web scraping with CSS/XPath selectors
- JavaScript execution in page context

```javascript
// OpenClaw agent-browser skill
skill: agent-browser
action: navigate + extract
url: https://example.com/products
selectors:
  - ".product-card .title"
  - ".product-card .price"
  - ".product-card .rating"
output: json
```

## Security Notes

- Use `headless: true` for production scrapers
- Respect `robots.txt` and `爬虫协议`
- Add delays between requests: `page.wait_for_timeout(1000)`
- Rotate User-Agent headers

## Resources

- [Playwright Docs](https://playwright.dev)
- [Agent Browser Skill](../agent-browser/SKILL.md)
- [n8n Browser Node](https://docs.n8n.io/nodes/n8n-nodes-base.playwright/)
