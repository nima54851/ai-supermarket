# 🔍 代码审查 Agent — 部署指南

> 10分钟完成自动化代码审查系统搭建

---

## 前置要求

- Node.js 18+
- n8n（[安装指南](https://docs.n8n.io/hosting/installation/)）
- GitHub 账号 + 个人访问 Token（[创建地址](https://github.com/settings/tokens)）
- OpenClaw（[安装指南](https://docs.openclaw.ai/)）

---

## 步骤 1：导入工作流

1. 打开 n8n：`http://localhost:5678`
2. 点击右上角 **Import from File**
3. 上传 `workflow.json`
4. 保存工作流

---

## 步骤 2：配置凭证

在 n8n 中配置以下凭证：

| 凭证名 | 说明 | 获取方式 |
|---|---|---|
| `GITHUB_TOKEN` | GitHub 个人访问 Token | github.com → Settings → Developer settings → Personal access tokens |
| `OPENAI_API_KEY` | OpenAI API Key | platform.openai.com |

---

## 步骤 3：配置 GitHub Webhook

1. 在 GitHub 仓库 → Settings → Webhooks → Add webhook
2. Payload URL: `https://your-n8n-domain.com/webhook/github-review`
3. Content type: `application/json`
4. Events: Pull requests, Pull request reviews
5. 生成并保存 Secret

---

## 步骤 4：启动

```bash
n8n start
```

---

## 验证

创建一个测试 PR，检查：
- n8n 是否收到 Webhook
- AI 是否自动评论 PR
- 通知是否发出

---

## 常见问题

**Q: Webhook 没有触发？**
→ 检查 GitHub Webhook URL 是否可公网访问（内网需用 ngrok）

**Q: AI 评论为空？**
→ 检查 OpenAI API Key 是否有效

**Q: 评论格式不对？**
→ 在 OpenClaw Skill 中调整 prompt 模板

---

## 获取帮助

购买后可通过 GitHub Issues 或邮件联系技术支持。
