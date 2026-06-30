# Discord AI Bot Integration

> Discord 频道 × AI Agent 自动回复 · Webhook → AI → Discord 消息

## 📦 包含文件

```
discord-ai-bot/
├── README.md          ← 本文件
├── discord-workflow.json   ← n8n workflow
└── bot-setup.md       ← Discord Bot 创建指南
```

## 🚀 快速部署

### 第一步：创建 Discord Bot

1. 访问 https://discord.com/developers/applications
2. 点击 **New Application** → 命名（如 `Agent-Studio-Bot`）
3. 左侧 **Bot** → 点击 **Add Bot**
4. 复制 **TOKEN**（妥善保管！）

### 第二步：邀请 Bot 到服务器

1. 左侧 **OAuth2 → URL Generator**
2. Scopes: `bot`
3. Bot Permissions: `Send Messages`, `Read Message History`
4. 复制生成的 URL，浏览器打开并选择服务器

### 第三步：获取频道 Webhook

1. Discord 频道 ⚙️ → 集成 → Webhooks → 新建 Webhook
2. 复制 Webhook URL（格式：`https://discord.com/api/webhooks/...`）

### 第四步：导入 n8n Workflow

```bash
# 在 n8n 中导入 discord-workflow.json
# 配置节点：
#   - Discord Webhook URL：填入上面复制的 Webhook URL
#   - GitHub Token：你的 GitHub PAT
#   - AI Model：OpenAI / Claude API
```

### 第五步：激活

1. n8n → 点击 **Activate**
2. Bot 现在会在收到消息时自动 AI 回复！

---

## 🔧 功能说明

| 功能 | 说明 |
|------|------|
| 自动回复 | 识别消息意图，AI 生成回复 |
| GitHub 通知 | 自动推送 Star/Fork/PR 到频道 |
| 定时播报 | 每日 AI 资讯摘要推送到频道 |
| 命令菜单 | `/help` `/status` `/report` |

---

## ⚙️ n8n Workflow 节点说明

```
Discord Webhook Trigger
        ↓
AI Agent（意图识别）
        ↓
    ├── GitHub API 查询
    ├── AI 生成回复
    └── Discord 发送消息
```

---

## 🔒 安全注意

- Bot Token 存储在 n8n Credentials，不要硬编码
- 生产环境使用 Application Commands 而非 Webhook
- 建议设置消息频率限制，避免触发 Discord 限流

---

## 📄 License

MIT · Powered by [agent-studio](https://github.com/nima54851/agent-studio)
