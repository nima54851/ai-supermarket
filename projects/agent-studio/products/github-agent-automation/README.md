# 🛒 AI Agent 社交媒体自动运营系统 — 产品说明

> **开箱即用的 AI Agent 全套自动化产品**
> 无需写一行代码，导入 n8n 即可运行

---

## 产品概述

这是一套**完整运行的社交媒体自动运营 Agent 系统**，基于 n8n 构建，每天自动执行以下操作：

| 功能 | 详情 |
|---|---|
| ⏰ 定时执行 | 每天 09:00 北京时间自动运行 |
| 🔍 GitHub 热点追踪 | 自动抓取近30天 AI/ML 热门项目 |
| ✍️ 智能评论生成 | AI 生成高质量技术评论（Ollama 免费 / GPT 可选） |
| ⭐ 自动 Star | 每天 Star 优质项目 |
| 📊 数据报告 | 生成每日 AI 资讯报告 |
| 📡 Webhook 分发 | 推送报告到任意平台（Telegram / 飞书 / 邮件） |

---

## 产品包含

- ✅ `workflow.json` — n8n 完整工作流（直接导入）
- ✅ `SETUP.md` — 5分钟部署指南
- ✅ `README.md` — 产品说明
- ✅ 技术支持（GitHub Issues）
- ✅ 免费方案：本地 Ollama（无需 API Key）

---

## 定价

| 版本 | 价格 | 包含内容 |
|---|---|---|
| 入门版 | **免费** | 基础工作流 + 部署指南 + Ollama 免费方案 |
| 专业版 | ¥99 | 完整系统 + OpenAI GPT-4 评论 + 多平台分发 + 技术支持 |
| 企业版 | ¥399 | 私有部署 + 定制工作流 + 无限使用 |

---

## 快速开始（免费）

```bash
# 1. 克隆产品
git clone https://github.com/nima54851/agent-studio.git
cd agent-studio/products/github-agent-automation

# 2. 安装 Ollama（免费 AI）
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# 3. 启动 n8n
docker run -it --rm -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n

# 4. 导入 workflow.json，配置 GitHub Token，开始运行
```

完整部署指南见 [SETUP.md](SETUP.md)

---

## 作者

Built with ❤️ by [nima54851](https://github.com/nima54851)  
Powered by [agent-studio](https://github.com/nima54851/agent-studio) + [OpenClaw](https://github.com/openclaw/openclaw)
