#!/usr/bin/env python3
"""
AI Agent 内容推流 — 文案生成器
根据产品信息自动生成各平台适配的推广文案
"""
import json
import sys
import os
from datetime import datetime

PLATFORMS = {
    "juejin": {
        "lang": "zh",
        "max_chars": 1500,
        "style": "专业技术实战风，含代码示例"
    },
    "csdn": {
        "lang": "zh", 
        "max_chars": 2000,
        "style": "详细教程风，步骤清晰"
    },
    "zhihu": {
        "lang": "zh",
        "max_chars": 1000,
        "style": "深度分析，观点鲜明"
    },
    "v2ex": {
        "lang": "zh",
        "max_chars": 500,
        "style": "简洁直接，社区话题感"
    },
    "twitter": {
        "lang": "en",
        "max_chars": 280,
        "style": "短促有力，emoji开头"
    },
    "reddit": {
        "lang": "en",
        "max_chars": 800,
        "style": "真实体验分享，非硬广"
    },
    "hn": {
        "lang": "en",
        "max_chars": 400,
        "style": "技术深度，简洁英文"
    }
}

# 产品信息库
PRODUCTS = {
    "agent-studio": {
        "name": "agent-studio",
        "title": "AI Agent 开发者的全栈工具箱",
        "description": "一个收录了 12+ 生产级 AI Agent 技能、工作流和自动化脚本的 GitHub 仓库",
        "url": "https://github.com/nima54851/agent-studio",
        "pages_url": "https://nima54851.github.io/agent-studio",
        "product_url": "https://nima54851.github.io/agent-studio/product.html",
        "tags": ["AI", "Agent", "GitHub", "自动化", "n8n", "OpenClaw"],
        "features": [
            "12+ 可直接使用的 OpenClaw 技能模板",
            "GitHub Trending 自动追踪",
            "n8n 工作流自动化（Discord/Telegram/Webhook）",
            "AI 代码审查管道",
            "Docker 一键部署",
            "每日 GitHub Actions 运营报告"
        ],
        "pricing": "免费版可用，专业版 ¥99",
        "stars": "1 ⭐",
        "highlights_zh": [
            "⚡ 技能模板即插即用，克隆到 OpenClaw skills 目录即可",
            "🔄 自动化脚本覆盖 GitHub 运营全流程",
            "🤖 支持 Ollama 本地大模型（免费）或 OpenAI GPT",
            "🐳 Docker Compose 一键部署，零配置运行"
        ]
    }
}

def generate_juejin(product_key, p):
    """掘金：专业技术博客风"""
    features_md = "\n".join([f"  - {f}" for f in p["features"][:5]])
    return f"""# {p['title']}

最近在玩 AI Agent 开发，找到一个超好用的工具箱，分享一下。

## 🎯 它是什么

{p['description']}，目前收录：

- **12+ 技能模板**：skill-builder、coding-tutor、n8n-workflow-builder、career-roadmap、agent-memory 等
- **自动化脚本**：GitHub Trending 追踪、每日报告生成、Webhook 分发
- **n8n 工作流**：导入即用，自动 Star、评论、生成报告
- **GitHub Actions**：每天自动跑，北京时间 09:00 出报告

## 🔥 核心亮点

{features_md}

## 🚀 快速上手

```bash
# 克隆仓库
git clone https://github.com/nima54851/agent-studio.git
cd agent-studio

# 查看技能列表
ls skills/

# 使用任意技能（复制到 OpenClaw skills 目录即可）
```

## 💰 定价

{p['pricing']}，完整版 ¥99，含 GPT-4 AI 评论生成 + 多平台推送。

👉 产品页：{p['product_url']}

---

如果你也在做 AI Agent 相关开发，这个仓库值得 star 和试用。有问题可以提 Issue，作者响应挺快的。

{p['tags'][:4]} #{' #'.join(p['tags'][:4])}"""

def generate_v2ex(product_key, p):
    """V2EX：简洁社区风"""
    top_feature = p["features"][0]
    return f"""做了一个 AI Agent 开发工具箱，收录了 12+ 可直接用的技能模板和工作流自动化脚本。

GitHub：{p['url']}

亮点：{top_feature} | 支持 n8n + Ollama 免费方案 | Docker 一键部署

免费版可用，¥99 解锁完整功能。 产品页：{p['product_url']}

#AI #Agent #GitHub"""

def generate_twitter(product_key, p):
    """Twitter：短促有力"""
    top = p["highlights_zh"][:3]
    lines = "\n".join(top[:3])
    return f"""🚀 {p['title']}

{lines}

👉 {p['url']}

#AI #Agent #OpenClaw #GitHub #automation"""

def generate_reddit(product_key, p):
    """Reddit：真实分享，非硬广"""
    return f"""I've been building AI agent workflows for a while and finally put together a toolkit that works for me — figured others might find it useful too.

**What it does:**
- 12+ skill templates for OpenClaw (coding tutor, workflow builder, career roadmap, etc.)
- GitHub Actions that run daily — trending repos + AI digest report
- n8n workflows for automation (Discord/Telegram/webhook)
- Docker Compose for instant deploy

**What makes it different:**
- Free tier works out of the box (uses Ollama for local AI)
- No vendor lock-in, MIT license
- Actively maintained

Repo: {p['url']}
Live demo: {p['pages_url']}

Not trying to sell anything — the free tier is genuinely useful. Would love feedback from anyone working on AI agents."""

def generate_hn(product_key, p):
    """Hacker News：技术深度英文"""
    return f"""Show HN: A production-ready AI Agent toolkit with 12 skills, n8n workflows, and daily GitHub automation

I've been building AI agent workflows for a few months and collected the patterns that actually work into one repo.

Key features:
- 12 OpenClaw skill templates (skill-builder, coding-tutor, n8n-workflow-builder, career-roadmap, etc.)
- GitHub Actions CI — daily trending report at 09:00 Beijing time
- n8n workflows: GitHub → AI review → Discord/Telegram notification
- Docker Compose one-command deploy
- Ollama (free, local) or OpenAI GPT support

Tech stack: Python + TypeScript + n8n + OpenClaw

Demo: {p['pages_url']}
Repo: {p['url']}"""

def generate_csdn(product_key, p):
    """CSDN：详细教程风"""
    features_md = "\n".join([f"| {i+1} | {f} |" for i, f in enumerate(p["features"][:5])])
    return f"""# {p['title']} — 附完整上手指南

## 一、项目背景

{p['description']}。

目前已收录 **12+ 技能模板** + **多个自动化工作流**，全部开源免费使用。

## 二、核心功能一览

| 序号 | 功能 | 说明 |
|---|---|---|
{features_md}

## 三、快速部署（5分钟上手）

### 方式一：Docker 一键部署

```bash
git clone https://github.com/nima54851/agent-studio.git
cd agent-studio/docker
docker compose up -d
```

### 方式二：直接使用技能模板

```bash
# 克隆后复制技能到 OpenClaw skills 目录即可
cp -r skills/skill-builder ~/.openclaw/workspace/skills/
```

## 四、实战案例

配合 n8n 可以实现：

```
GitHub Trending 抓取 → AI 生成技术评论 → 自动 Star → 推送 Discord/Telegram
```

整个流程零代码，导入 n8n 工作流 JSON 即可运行。

## 五、定价

{p['pricing']}

## 六、资源链接

- GitHub：{p['url']}
- 产品页：{p['product_url']}
- 在线演示：{p['pages_url']}

---

觉得有用的话欢迎 star，有问题欢迎留言！

{p['tags'][:4]} #{' #'.join(p['tags'][:3])}"""

def main():
    product_key = sys.argv[1] if len(sys.argv) > 1 else "agent-studio"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./drafts"

    if product_key not in PRODUCTS:
        print(f"未知产品: {product_key}")
        print(f"可用产品: {', '.join(PRODUCTS.keys())}")
        sys.exit(1)

    p = PRODUCTS[product_key]
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d")

    generators = {
        "juejin.md": generate_juejin,
        "v2ex.md": generate_v2ex,
        "twitter.md": generate_twitter,
        "reddit.md": generate_reddit,
        "hn.md": generate_hn,
        "csdn.md": generate_csdn,
    }

    for filename, gen_fn in generators.items():
        content = gen_fn(product_key, p)
        filepath = os.path.join(output_dir, f"{ts}_{filename}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ {filename} → {filepath}")

    # Save manifest
    manifest = {
        "product": product_key,
        "generated_at": datetime.now().isoformat(),
        "files": [f"{ts}_{k}" for k in generators.keys()],
        "product_info": p
    }
    manifest_path = os.path.join(output_dir, f"{ts}_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"✅ manifest → {manifest_path}")
    print(f"\n📝 预览文案：ls {output_dir}/")

if __name__ == "__main__":
    main()
