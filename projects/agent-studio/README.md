# agent-studio 🤖

<h align="center">

[![Stars](https://img.shields.io/github/stars/nima54851/agent-studio?style=flat&logo=github&color=24292e)](https://github.com/nima54851/agent-studio/stargazers)
[![Forks](https://img.shields.io/github/forks/nima54851/agent-studio?style=flat&logo=github&color=24292e)](https://github.com/nima54851/agent-studio/network/members)
[![Last Commit](https://img.shields.io/github/last-commit/nima54851/agent-studio?style=flat&color=238636)](https://github.com/nima54851/agent-studio/commits/main)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-blue?style=flat)](https://nima54851.github.io/agent-studio)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat)](CONTRIBUTING.md)

</h>

> **The AI Agent developer's production toolkit.** Everything you need to build, deploy, and scale AI agents — in one repo.
> Built by [灵犀 AI](https://github.com/nima54851) · Powered by [OpenClaw](https://github.com/openclaw/openclaw)

---

## 🎯 What Is This?

A curated, **production-ready** collection of tools, workflows, and skill templates for AI Agent developers. Stop reinventing the wheel — clone, configure, ship.

**What you get:**
- ⚡ Skill templates that plug straight into OpenClaw
- 🔄 Automation scripts (GitHub trending, daily reports, webhook pipelines)
- 🤖 Integrations (Discord, Telegram, n8n, webhooks)
- 🐳 Zero-config Docker deployments
- 📋 Proven prompt patterns for code review, architecture, planning

---

## 📦 What's Inside

| Category | Contents | Count |
|----------|----------|-------|
| **Skills** | OpenClaw-compatible agent skill templates | `skills/` |
| **Scripts** | Python automation (GitHub trending, MCP, webhooks) | `scripts/` |
| **Security** | Secret scanner, CVE audit, security reports | `skills/security-auditor/` |
| **Customer Support** | Ticket triage, auto-reply, escalation, FAQ resolver | `skills/customer-support-automation/` |
| **Performance** | HTTP stress test, WebSocket benchmarks | `skills/performance-testing-toolkit/` |
| **Integrations** | Discord Bot, Telegram Bot, Slack Bot, Webhook → AI pipelines | `integrations/` |
| **Docker** | Docker Compose for instant deployment | `docker/` |
| **Prompts** | Battle-tested prompt patterns | `prompts/` |
| **GitHub Actions** | Daily reports, CI/CD, GitHub Pages deploy | `.github/workflows/` |

---

## 🛠️ Featured Skills

| Skill | Description |
|-------|-------------|
| **[skill-builder](skills/skill-builder)** | Create AI Agent skills from scratch — SKILL.md + scripts + packaging |
| **[coding-tutor](skills/coding-tutor)** | Learn Python, JavaScript, React — with exercises and projects |
| **[n8n-workflow-builder](skills/n8n-workflow-builder)** | Design and debug n8n workflows — AI-powered automation |
| **[career-roadmap](skills/career-roadmap)** | Programmer growth path — from junior to architect |
| **[agent-skills-kit](skills/agent-skills-kit)** | Agent skills development framework — tools, templates, best practices |
| **[self-hosted-ai](skills/self-hosted-ai)** | Deploy Ollama, n8n, Open WebUI — full local AI stack |
| **[agent-memory](skills/agent-memory)** | Long-term memory for AI agents |
| **[test-master](skills/test-master)** | Automated testing patterns for AI agent outputs |
| **[cloudflare-workers-ai](skills/cloudflare-workers-ai)** | Deploy AI inference on Cloudflare Workers AI globally |
| **[email-automation](skills/email-automation)** | AI auto-reply, drip campaigns, Gmail/SMTP via n8n |
| **[social-media-automation](skills/social-media-automation)** | Auto-post Twitter/LinkedIn, content repurposing, AI threads |
| **[github-trending-monitor](skills/github-trending-monitor)** | Track GitHub trending in real time |
| **[agent-health-monitor](skills/agent-health-monitor)** | Monitor agent health and uptime |
| **[content-promoter](skills/content-promoter)** | AI-powered social media content generation & scheduling |
| **[product-launch-assistant](skills/product-launch-assistant)** | End-to-end AI product launch automation — landing page, social posts, email templates |
| **[performance-testing-toolkit](skills/performance-testing-toolkit)** | HTTP/WebSocket/API stress testing + benchmarks |
| **[security-auditor](skills/security-auditor)** | Secret scanning, CVE detection, API security audit |
| **[customer-support-automation](skills/customer-support-automation)** | AI-powered ticket triage, auto-reply, FAQ resolution |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/nima54851/agent-studio.git
cd agent-studio

# Run GitHub Trending tracker
python3 scripts/github_trending.py

# Use a skill with OpenClaw
# Just copy skills/<name> to your OpenClaw skills directory
```

---

## 📖 Featured Workflows

### GitHub Trending → AI Digest → Daily Report
```
GitHub API → Filter AI/ML repos → AI summarize → REPORT.md → GitHub Pages
```
Runs daily via GitHub Actions · [See workflow](.github/workflows/daily-report.yml)

### AI Product Launch Pipeline
```
产品定义 → 发布材料包 → n8n 自动化 → Twitter/Email/社区 发布 → 数据追踪复盘
```
Script + Skill + Checklist · [See skill](skills/product-launch-assistant/) · [See checklist](workflows/product-launch-checklist.md)

### Slack → AI Agent → Team Notification
```
@mention in Slack → n8n route by intent → AI Agent process → Slack reply
```
Multi-agent routing built-in · [See integration](integrations/slack-bot/)

### AI Code Review Pipeline
```
Pull Request → Webhook trigger → AI code review → Post comment
```
Automate code review on any repo · [See skill](skills/)

---

## 🐳 One-Command Deploy

```bash
cd docker
cp .env.example .env
# Edit .env with your API keys
docker compose up -d
```

Supported: n8n · Discord Bot · Telegram Bot · Webhook listeners

---

## 📈 Live Demo

| | |
|---|---|
| **GitHub Pages** | https://nima54851.github.io/agent-studio |
| **Product Page** | https://nima54851.github.io/agent-studio/product.html |

---

## 🛒 Ready-to-Use Products

Want a **production AI agent automation system** up and running today?

| Product | Description | Price |
|---------|-------------|-------|
| **AI 社交媒体自动运营系统** | n8n workflow — 自动抓 GitHub Trending / AI 评论 / Star / 报告推送 | **¥99**（一次性） |
| 含入门版（免费） | 基础 GitHub Trending + Webhook推送 | ¥0 |
| 含企业版 | 私有部署 + 定制 + 无限使用 | ¥399（一次性） |

> 🎯 [👉 查看完整产品页（含免费版）](https://nima54851.github.io/agent-studio/product.html)

Free version: https://github.com/nima54851/agent-studio/tree/main/products/github-agent-automation

---

## 🌟 Why agent-studio?

| Regular Template Repo | agent-studio |
|---|---|
| Readme only, no tools | Full working scripts |
| Theoretical examples | Production-ready pipelines |
| One framework | Multi-framework (OpenClaw, n8n, LangChain…) |
| No automation | GitHub Actions CI/CD built-in |
| Static docs | Live GitHub Pages demos |

---

## 🤝 Contributing

Contributions welcome! Here's how:

1. **Add a skill** — See [`skills/skill-builder`](skills/skill-builder) for the format
2. **Share a workflow** — Add to [`integrations/`](integrations/)
3. **Improve docs** — PRs on README and docs/ are always open
4. **Star & share** — It helps more than you think 🙏

---

## 📄 License

MIT · Use it, modify it, sell it (just keep the credit).

---

<h align="center">

*Built with [灵犀 AI](https://github.com/nima54851) · [Open an Issue](https://github.com/nima54851/agent-studio/issues) · [Submit a PR](https://github.com/nima54851/agent-studio/pulls)*

</h>
