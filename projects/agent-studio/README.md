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
| **Documentation** | Auto-generate README, API docs, and changelogs from code | `skills/docs-generator/` |
| **Analytics Dashboard** | GitHub stats, OpenClaw usage — live HTML dashboard | `skills/analytics-dashboard/` |
| **SEO Automation** | sitemap.xml, robots.txt, OG tags, JSON-LD auto-gen | `skills/seo-automation/` |
| **A/B Testing** | A/B test framework for n8n workflows and prompts | `skills/ab-testing-workflow/` |
| **Voice AI Automation** | Whisper STT → LLM → TTS 语音 AI 自动化管道 | `skills/voice-ai-automation/` |
| **Scheduled Tasks** | 跨平台定时任务调度（cron + n8n + 分布式锁） | `skills/scheduled-task-automation/` |
| **Email Automation** | Gmail SMTP, drip campaigns, AI auto-reply | `skills/email-automation/` |
| **Social Media** | Twitter/LinkedIn auto-post, content rewriting | `skills/social-media-automation/` |
| **Product Launch** | AI-powered launch automation and checklist | `skills/product-launch-assistant/` |
| **Image Generation** | DALL·E 3, Stable Diffusion, Flux — 自动配图 pipeline | `skills/image-generation-automation/` |
| **Video Automation** | Runway, Kling, Pika — AI 视频生成 + 自动剪辑 + 字幕 + YouTube 发布 | `skills/video-automation/` |
| **MCP Server** | Build MCP servers backed by n8n — any MCP-compatible AI can use your workflows as tools | `integrations/mcp-server-automation/` |
| **Prompt Versioning** | Git-like version control for AI prompts — diff, rollback, A/B test, environment promotion | `integrations/prompt-versioning-automation/` |
| **Testing Automation** | AI 生成 pytest/jest 测试用例 + coverage 跟踪 + CI 集成 | `skills/testing-automation/` |
| **Infrastructure as Code** | AI 生成 Terraform / Pulumi / Ansible 配置文件 | `skills/infrastructure-as-code/` |
| **Customer Support** | Ticket triage, auto-reply, escalation, FAQ resolver | `skills/customer-support-automation/` |
| **Performance** | HTTP stress test, WebSocket benchmarks | `skills/performance-testing-toolkit/` |
| **GitHub Actions** | AI-augmented PR review, auto-deploy, scheduled CI/CD | `skills/github-actions-automation/` |
| **Monitoring & Alerting** | Prometheus + Grafana + AI anomaly detection + n8n alerts | `skills/monitoring-alerting-automation/` |
| **Notion Sync** | Notion ↔ OpenClaw AI sync via n8n | `integrations/notion-sync/` |
| **Linear Automation** | Linear project management + AI triage + Sprint planning | `integrations/linear-automation/` |
| **Fine-Tuning Automation** | OpenAI/Axolotl/LLaMA-Factory 微调全流程 — 数据准备 → 训练 → 评估 → 部署 | `skills/fine-tuning-automation/` |
| **Event-Driven Architecture** | Kafka / RabbitMQ / Redis Streams 事件驱动架构 + AI 事件流 | `skills/event-driven-architecture/` |
| **AI Model Router** | 多模型智能路由 — OpenAI/Anthropic/Ollama 按成本/延迟自动选择最优模型 | `skills/ai-model-router/` |
| **Data Visualization** | Plotly/D3.js — CSV/JSON → interactive charts & dashboards | `skills/data-visualization-automation/` |
| **AI Code Refactoring** | AI refactor Python/JS/TS — type hints, async/await, DRY | `skills/ai-code-refactoring/` |
| **Logging Automation** | 日志采集 + AI 异常检测 + 告警路由（Filebeat/Loki/Grafana/n8n） | `skills/logging-automation/` |
| **LLM Ops Automation** | 统一 LLM 网关 + Token 成本追踪 + Prompt A/B 测试 + 预算告警 | `skills/llm-ops-automation/` |
| **Resilience Patterns** | 熔断器 / 重试策略 / 滑动窗口限流 / 优雅降级 | `skills/resilience-patterns/` |
| **Video Processing** | FFmpeg AI processing — auto-captions, vertical crop, multi-platform output | `skills/video-processing-automation/` |
| **Database Migration** | AI SQL migration — schema diff, zero-downtime, rollback, data校验 | `skills/database-migration-automation/` |
| **Sentiment Analysis** | Real-time sentiment analysis — multi-language, topic extraction, urgency alerts | `skills/sentiment-analysis-automation/` |
| **Blockchain Automation** | On-chain monitoring, wallet tracking, smart contract events, multi-chain alerts | `skills/blockchain-automation/` |
| **Workflow Orchestration** | Multi-step AI pipelines, retry logic, dead-letter queues, fan-out/fan-in patterns | `skills/workflow-orchestration/` |
| **Browser Automation** | Playwright + AI — scrape, screenshot, form fill, multi-step web workflows | `skills/browser-automation/` |
| **Integrations** | Discord Bot, Telegram Bot, Slack Bot, WhatsApp Bot, Voice AI, Scheduled Tasks, Data Viz, AI Refactor, Fine-Tuning, Event-Driven, GraphQL, Document Intelligence, Code Review, Blockchain, Workflow Orchestration, Browser Automation | `integrations/` |
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
| **[analytics-dashboard](skills/analytics-dashboard)** | HTML analytics dashboard — GitHub stats, OpenClaw usage, ZeroGPU savings |
| **[ab-testing-workflow](skills/ab-testing-workflow)** | A/B test framework for n8n workflows and OpenClaw prompts |
| **[seo-automation](skills/seo-automation)** | GitHub Pages SEO — sitemap, robots.txt, OG tags, JSON-LD |
| **[data-visualization-automation](skills/data-visualization-automation)** | Auto-generate charts & dashboards — Plotly, D3.js, CSV/JSON → HTML |
| **[ai-code-refactoring](skills/ai-code-refactoring)** | AI-powered code refactoring — Python/JS/TS, before/after diffs, quality checks |
| **[graphql-api-automation](skills/graphql-api-automation)** | AI GraphQL API design — schema generation, Apollo Server, Federation, n8n pipeline |
| **[ai-document-intelligence](skills/ai-document-intelligence)** | LLM-powered document extraction — PDFs, contracts, invoices, OCR pipeline |
| **[code-review-automation](skills/code-review-automation)** | AI PR code review — security, bugs, performance, automated GitHub comments |
| **[video-processing-automation](skills/video-processing-automation)** | FFmpeg + Whisper AI video processing — auto-captions, vertical crop, compression |
| **[database-migration-automation](skills/database-migration-automation)** | AI SQL migration generator — schema diff, zero-downtime, rollback, data integrity |
| **[sentiment-analysis-automation](skills/sentiment-analysis-automation)** | Real-time sentiment analysis — multi-language, topic extraction, urgency alerting |
| **[blockchain-automation](skills/blockchain-automation)** | On-chain monitoring, wallet tracking, smart contract events, multi-chain alerts |
| **[workflow-orchestration](skills/workflow-orchestration)** | Multi-step AI pipelines, retry logic, dead-letter queues, AI routing decisions |
| **[browser-automation](skills/browser-automation)** | Playwright + AI browser automation — scrape, screenshot, form fill, web workflows |
| **[incident-response-automation](skills/incident-response-automation)** | AI incident triage, PagerDuty integration, war-room summarizer, auto post-mortem |
| **[compliance-automation](skills/compliance-automation)** | GDPR, SOC 2, HIPAA, PCI-DSS compliance — evidence collection, gap analysis, audit reports |
| **[translation-automation](skills/translation-automation)** | AI multilingual translation — DeepL, quality scoring, terminology lock, batch processing |
| **[a11y-automation](skills/a11y-automation)** | WCAG accessibility testing — axe-core, Lighthouse, AI fix suggestions, CI enforcement |
| **[feature-flag-automation](skills/feature-flag-automation)** | LaunchDarkly/Unleash flag management — gradual rollouts, A/B targeting, AI recommendations |
| **[agent-memory-automation](skills/agent-memory-automation)** | 长期记忆管理 — ChromaDB/pgvector 向量存储、语义召回、会话摘要、遗忘策略 |
| **[cross-platform-notification](skills/cross-platform-notification)** | Email/Slack/Discord/Telegram/SMS 统一告警路由 + 升级策略 + 智能聚合 |
| **[supabase-automation](skills/supabase-automation)** | Supabase 后端 — Auth/Realtime/Storage/Edge Functions + PostgreSQL/pgvector 自动化 |

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

### Notion ↔ AI Agent Sync
```
Notion Database → n8n → OpenClaw AI → Analysis → Notion Update
```
AI-powered tagging, priority scoring, auto-reply · [See integration](integrations/notion-sync/)

### SEO Automation for GitHub Pages
```
Repo → SEO generator → sitemap.xml + robots.txt + OG tags → GitHub Pages
```
Automated SEO maintenance · [See skill](skills/seo-automation/)

### A/B Test Your Workflows
```
Variant A workflow ←→ Variant B workflow → Stats → Winner
```
Statistical significance testing · [See skill](skills/ab-testing-workflow/)

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
