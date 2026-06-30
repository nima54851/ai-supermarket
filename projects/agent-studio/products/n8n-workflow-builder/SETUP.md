# ⚙️ n8n 工作流构建 Agent — 部署指南

---

## 前置要求

- Node.js 18+
- n8n（[安装指南](https://docs.n8n.io/hosting/installation/)）
- OpenClaw（[安装指南](https://docs.openclaw.ai/)）

---

## 步骤 1：安装 Agent Skill

把 `agent-skill/` 目录放到 OpenClaw skills 目录：

```bash
cp -r agent-skill/* ~/.openclaw/skills/n8n-workflow-builder/
```

---

## 步骤 2：导入预设模板

打开 n8n → Import from File → 选择 `workflows/` 下的任意 `.json` 文件

---

## 步骤 3：生成新工作流

在 OpenClaw 对话框输入：

```
帮我生成一个工作流：
当 GitHub 有新 PR 时，自动用 AI 审查代码，并把结果发到 Slack 频道
```

Agent 会生成对应的 workflow.json，复制粘贴到 n8n 导入即可。

---

## 模板列表

| 模板名 | 功能 |
|---|---|
| github-pr-slack.json | GitHub PR → Slack 通知 |
| github-pr-review.json | GitHub PR → AI 审查 |
| twitter-auto-post.json | RSS → AI 改写 → Twitter 发布 |
| email-auto-reply.json | 新邮件 → AI 分析 → 自动回复分类 |
| cron-weather-reminder.json | 定时天气提醒 → 微信/邮件 |

---

## 获取帮助

购买后可通过 GitHub Issues 或邮件联系技术支持。
