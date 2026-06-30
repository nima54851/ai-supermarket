#!/usr/bin/env python3
"""
content-promoter — 快速推流脚本
生成可直接复制粘贴到各平台的文案
"""
import subprocess
import sys

# 直接可用的各平台文案（每次可重新生成最新）
PLATFORM_POSTS = {
    "掘金": {
        "title": "我做了个 AI Agent 开发工具箱，收录了 12+ 生产级技能模板",
        "tags": ["AI", "Agent", "GitHub", "自动化"],
        "checklist": [
            "✅ 登录掘金 (juejin.com)",
            "✅ 发布文章，粘贴下方正文",
            "✅ 添加标签：AI、GitHub、Python、自动化",
            "✅ 末尾引导：点赞、关注",
        ]
    },
    "CSDN": {
        "title": "AI Agent 开发者工具箱 — 12+技能模板 + n8n自动化 + GitHub Actions",
        "tags": ["AI", "GitHub", "自动化", "n8n"],
        "checklist": [
            "✅ 登录 CSDN (csdn.net)",
            "✅ 发布博客，粘贴下方正文",
            "✅ 设置分类：AI",
        ]
    },
    "V2EX": {
        "title": "分享一个 AI Agent 开发工具箱，12+可直接用的技能模板",
        "checklist": [
            "✅ 登录 V2EX (v2ex.com)",
            "✅ 发布主题，粘贴下方正文",
        ]
    },
    "Twitter/X": {
        "checklist": [
            "✅ 登录 Twitter/X",
            "✅ 粘贴下方推文",
            "✅ 附上链接",
        ]
    },
    "Reddit": {
        "checklist": [
            "✅ 先在 r/programming 或 r/AI 社区活跃几天",
            "✅ 以真实体验分享形式发帖",
            "✅ 不要直接硬广",
        ]
    },
}

AGENT_STUDIO_POSTS = {
    "掘金": """# 我做了个 AI Agent 开发工具箱，收录了 12+ 生产级技能模板

最近在探索 AI Agent 开发，找到了一个很实用的方向——把常用的工作流封装成可复用的"技能模块"。于是把这些积累整理成了一个开源工具箱。

## 🎯 它是什么

**agent-studio** 是一个收录了 12+ 可直接使用的 AI Agent 技能模板、工作流和自动化脚本的 GitHub 仓库。

目前已包含：
- **技能模板**：skill-builder、coding-tutor、n8n-workflow-builder、career-roadmap、self-hosted-ai、agent-memory 等
- **自动化脚本**：GitHub Trending 追踪、每日报告生成、Webhook 分发
- **n8n 工作流**：导入即用，支持 Discord/Telegram 推送
- **GitHub Actions**：每天北京时间 09:00 自动跑

## 🔥 核心亮点

- ⚡ **12 个 OpenClaw 技能模板**，克隆到 skills 目录即可用
- 🔄 **GitHub 运营自动化**，每天自动追踪 AI/ML 热门项目
- 🤖 **支持 Ollama 本地大模型**（免费）或 OpenAI GPT
- 🐳 **Docker Compose 一键部署**，零配置运行
- 📊 **每日 AI 资讯报告**，自动推送到 Telegram/Discord

## 🚀 快速上手

```bash
git clone https://github.com/nima54851/agent-studio.git
cd agent-studio

# 查看技能列表
ls skills/

# 运行 GitHub Trending 追踪
python3 scripts/github_trending.py
```

## 💰 定价

免费版可用，专业版 ¥99（一次性），含 GPT-4 AI 评论生成 + 多平台推送。

👉 产品页：https://nima54851.github.io/agent-studio/product.html

---

GitHub：https://github.com/nima54851/agent-studio
在线演示：https://nima54851.github.io/agent-studio

如果你也在做 AI Agent 相关开发，欢迎试用，有问题提 Issue。

#AI #Agent #GitHub #自动化""",

    "V2EX": """做了一个 AI Agent 开发工具箱，收录了 12+ 可直接用的技能模板和工作流自动化脚本。

GitHub：https://github.com/nima54851/agent-studio

亮点：
- 12 个 OpenClaw 技能模板（skill-builder、coding-tutor、n8n-workflow-builder 等）
- 支持 Ollama 本地大模型（免费）
- Docker 一键部署

免费版可用，专业版 ¥99。👉 https://nima54851.github.io/agent-studio/product.html

#AI #Agent #GitHub""",

    "Twitter/X": """🚀 AI Agent 开发工具箱 — 12 个生产级技能模板 + n8n 自动化 + GitHub Actions

⚡ 克隆即用：skill-builder、coding-tutor、n8n-workflow、career-roadmap
🤖 Ollama 免费方案 or OpenAI GPT-4
🐳 Docker 一键部署

👉 https://github.com/nima54851/agent-studio
📺 https://nima54851.github.io/agent-studio

#AI #Agent #OpenClaw #GitHub #automation""",

    "Reddit": """I've been building AI agent workflows for a few months and finally organized everything into one toolkit that actually works.

**agent-studio** — a production-ready AI Agent toolkit with:
- 12 OpenClaw skill templates (skill-builder, coding-tutor, n8n-workflow-builder, career-roadmap, self-hosted-ai, etc.)
- Daily GitHub Actions: trending AI repos + digest report at 09:00 Beijing time
- n8n workflows: GitHub → AI review → Discord/Telegram notification
- Docker Compose one-command deploy
- Free tier: Ollama local AI (no API key needed)

Free to use, Pro ¥99 one-time for GPT-4 + multi-platform push.

Repo: https://github.com/nima54851/agent-studio
Demo: https://nima54851.github.io/agent-studio
Product: https://nima54851.github.io/agent-studio/product.html

Not selling anything — the free tier is genuinely useful. Would love feedback from devs building AI agents.""",

    "CSDN": """# AI Agent 开发工具箱 — 12+技能模板 + n8n自动化 + GitHub Actions

## 一、项目介绍

agent-studio 是一个收录了 12+ 可直接使用的 AI Agent 技能模板、工作流和自动化脚本的 GitHub 仓库。

## 二、核心功能

| 功能 | 说明 |
|---|---|
| 12+ 技能模板 | skill-builder、coding-tutor、n8n-workflow-builder 等 |
| GitHub Trending 追踪 | 每天自动抓 AI/ML 热门项目 |
| n8n 工作流 | 导入即用，支持 Discord/Telegram |
| GitHub Actions | 每日 09:00 自动出报告 |
| Ollama 免费方案 | 无需 API Key，本地跑大模型 |

## 三、快速部署

```bash
git clone https://github.com/nima54851/agent-studio.git
cd agent-studio/docker
docker compose up -d
```

## 四、资源链接

- GitHub：https://github.com/nima54851/agent-studio
- 产品页：https://nima54851.github.io/agent-studio/product.html
- 在线演示：https://nima54851.github.io/agent-studio

免费版可用，专业版 ¥99（一次性）。""",
}

def main():
    product = sys.argv[1] if len(sys.argv) > 1 else "agent-studio"

    if product not in ("agent-studio",):
        print(f"Unknown product: {product}")
        sys.exit(1)

    posts = AGENT_STUDIO_POSTS

    for platform, content in posts.items():
        print(f"\n{'='*50}")
        print(f"📤 {platform}")
        print('='*50)
        print(content)
        print()

if __name__ == "__main__":
    main()
