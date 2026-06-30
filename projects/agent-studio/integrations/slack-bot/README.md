# Slack AI Agent Bot - 集成文档

## 概述

将 AI Agent 能力接入 Slack，实现团队内的 AI 助手协作。

---

## 功能特性

- ✅ 团队成员 @机器人提问，AI 即时回复
- ✅ 支持多 Agent 路由（根据关键字分发）
- ✅ 代码片段高亮 + 执行结果返回
- ✅ 定时任务触发（cron 表达式）
- ✅ 日报/周报自动生成并推送
- ✅ GitHub 通知聚合（PR/Issue/Star）
- ✅ 支持私有频道隔离

---

## 架构

```
用户 @agent → Slack → n8n Webhook → AI Agent → n8n Response → Slack
```

---

## 快速部署

### 步骤 1：创建 Slack App

1. 访问 https://api.slack.com/apps
2. 点击 **Create New App** → **From scratch**
3. 启用以下权限（OAuth Scopes）：
   - `chat:write`
   - `app_mentions:read`
   - `im:history`
   - `im:write`
   - `channels:history`
4. 启用 **Event Subscriptions** → Subscribe to events:
   - `app_mention`
   - `message.im`
5. 启用 **Interactivity**
6. 安装到 Workspace，复制 `Bot User OAuth Token`

### 步骤 2：配置 n8n

1. 导入 `slack-ai-agent.json`
2. 设置 Credentials：
   - **Slack API**: `xoxb-xxxxxx`（Bot Token）
   - **AI Agent Webhook**: 你的 OpenClaw MCP 端点
3. 设置 Trigger URL（Webhook URL）

### 步骤 3：填入 Slack App 设置

```
OAuth & Permissions → Redirect URLs:
  → 填入 n8n 的 OAuth Redirect URL（如需要）
  
Event Subscriptions → Request URL:
  → 填入 n8n 的 Slack App 事件 URL
```

---

## n8n Workflow 概览

| 节点 | 功能 |
|------|------|
| Slack Trigger | 接收 @mention 或 DM |
| AI Agent Router | 根据消息内容路由到对应 Agent |
| OpenAI / Claude | LLM 对话处理 |
| Code Node | 执行代码片段 |
| Slack Post | 回复用户 |
| Notion Logger | 记录对话日志 |

---

## 环境变量

```bash
SLACK_BOT_TOKEN=xoxb-xxxxx
SLACK_SIGNING_SECRET=xxxxx
SLACK_APP_TOKEN=xapp-xxxxx
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/slack
AGENT_API_KEY=your-openclaw-mcp-key
```

---

## 导入 n8n Workflow

```bash
# 方式1: n8n UI 手动导入
# 复制 slack-ai-agent.json 内容，粘贴到 n8n Import

# 方式2: n8n CLI
n8n import:workflow --input=slack-ai-agent.json
```

---

## 使用示例

```
@agent-studio 分析一下这个代码有什么问题：
def hello():
    print("hello"

@agent-studio 生成本周的工作周报

@agent-studio 帮我查一下 nima54851/agent-studio 的 star 数
```

---

## 扩展：多 Agent 路由

| 触发词 | 路由到 |
|--------|--------|
| `代码` / `debug` / `审查` | code-review-agent |
| `爬虫` / `抓取` | web-scraper-agent |
| `github` / `star` | github-agent |
| `报表` / `分析` | analytics-agent |
| 默认 | general-agent |

---

*由 灵犀 × agent-studio 提供 | 2026-06-27*
