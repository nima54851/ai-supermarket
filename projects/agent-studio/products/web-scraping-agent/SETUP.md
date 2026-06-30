# 🕷️ 网页爬取 Agent — 部署指南

---

## 前置要求

- Node.js 18+
- n8n（[安装指南](https://docs.n8n.io/hosting/installation/)）
- Playwright（`npx playwright install chromium`）
- OpenClaw

---

## 步骤 1：安装 Skill

```bash
cp -r agent-skill/* ~/.openclaw/skills/web-scraping-agent/
```

---

## 步骤 2：导入预设模板

n8n → Import → 选择 `workflows/` 下的模板

---

## 步骤 3：开始爬取

在 OpenClaw 输入：

```
帮我爬取 https://news.ycombinator.com/ 的前30条帖子，
提取标题、分数、评论数，输出成CSV
```

---

## 模板列表

| 模板 | 功能 |
|---|---|
| hackernews-scraper.json | HN 热帖 |
| amazon-price-tracker.json | 亚马逊价格追踪 |
| github-trending.json | GitHub Trending |
| job-board-scraper.json | 招聘网站职位列表 |

---

## 合规说明

本工具仅用于合法用途（竞品分析、公开数据研究等）。请遵守目标网站的 `robots.txt` 和服务条款。
