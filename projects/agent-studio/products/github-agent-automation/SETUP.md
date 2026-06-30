# AI Agent 社交媒体自动运营系统

> 全自动 GitHub 账号运营 · 无需写代码 · 5 分钟上线

---

## 🚀 功能一览

| 模块 | 说明 | 状态 |
|---|---|---|
| ⏰ 自动定时 | 每天 09:00 北京时间自动运行 | ✅ |
| 🔍 热点追踪 | 抓取当天 AI/ML 热门项目 | ✅ |
| ✍️ AI 评论 | GPT / 本地 Ollama 生成高质量评论 | ✅ |
| ⭐ 自动 Star | 每天自动 Star 优质项目 | ✅ |
| 📊 报告生成 | 自动生成每日资讯报告 | ✅ |
| 📡 多平台推送 | 支持 Telegram / 邮件 / Webhook | ✅ |

---

## 📦 产品包含

```
github-agent-automation/
├── workflow.json    ← n8n 工作流，直接导入
├── README.md        ← 本文件
└── SETUP.md         ← 5分钟部署指南
```

---

## ⚡ 快速部署（5分钟）

### 第一步：准备 Token

1. **GitHub Token**
   - 访问：https://github.com/settings/tokens
   - 生成新 Token（classic），勾选 `repo` scope
   - 复制保存（格式：`ghp_xxxx`）

2. **AI 评论（选一种，免费推荐）**

   **方案A：本地 Ollama（免费，无需 API Key）**
   ```bash
   # 安装 Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.2

   # n8n 节点中连接 http://localhost:11434
   ```

   **方案B：OpenAI API（付费，更强）**
   - 访问：https://platform.openai.com/api-keys
   - 填入 `sk-...` 格式的 API Key

### 第二步：导入 n8n

```bash
# 方式1：本地 n8n
npx n8n
# 或
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# 方式2：已有 n8n
# 直接导入 workflow.json
```

### 第三步：导入工作流并配置

1. n8n 右上角 → **Import from File** → 上传 `workflow.json`
2. 配置凭证：
   - GitHub API：填入 GitHub Token
   - Ollama 或 OpenAI：根据方案选择
   - SMTP（如需邮件）：填入邮箱配置

3. 修改关键节点：
   ```
   💬 AI 评论节点
     → 选择 Ollama 或 OpenAI

   ⭐ 自动 Star 节点
     → 设置要 Star 的仓库
   ```

### 第四步：激活

1. 点击右上角 **「Activate」**
2. 每天 09:00 北京时间自动执行
3. 查看 **Executions** 确认运行状态

---

## 🛠 架构说明

```
Schedule Trigger (09:00 北京时间)
        ↓
GitHub API — 抓取 AI/ML Trending（近30天）
        ↓
数据整理（提取 star数、描述、语言）
    ↓           ↓
自动 Star    AI 评论生成（Ollama/OpenAI）
    ↓           ↓
Webhook → Telegram / 飞书 / 邮件 / Discord
```

---

## ⚙️ 环境要求

| 组件 | 最低要求 | 推荐 |
|---|---|---|
| Node.js | 18.x+ | 最新 LTS |
| n8n | 1.x | 最新版 |
| GitHub Token | repo 权限 | classic token |
| Ollama（免费方案） | 2GB RAM | 8GB RAM + llama3.2 |

---

## ❓ 常见问题

**Q: Token 怎么生成？**
A: GitHub → Settings → Developer settings → Personal access tokens → Generate new token → 勾选 `repo`

**Q: 每天能运行几次？**
A: GitHub API 免费版 60次/小时，带 Token 5000次/小时

**Q: 如何自定义评论内容？**
A: 在 n8n 的 Code 节点中修改 prompt 模板

**Q: 支持其他平台吗？**
A: 支持任意有 Webhook 的平台（Telegram、飞书、钉钉、Discord）

**Q: Ollama 和 OpenAI 哪个好？**
A: OpenAI GPT-4 评论质量更高；Ollama 完全免费且离线可用。建议先用 Ollama 测试，再用 OpenAI 优化。

---

## 🔒 安全说明

- Token 建议存储在 n8n 的「Credentials」中，不要硬编码在工作流里
- 生产环境建议使用只读权限 Token
- 定期轮换 Token（建议每90天）

---

## 📞 技术支持

有问题？请提交 Issue：https://github.com/nima54851/agent-studio/issues

---

## 📄 许可证

MIT License — 可商用，可修改，可分发

**Powered by [agent-studio](https://github.com/nima54851/agent-studio) · Built by [nima54851](https://github.com/nima54851)**
