# TOOLS.md - Local Notes

## n8n Automation Engine
- **URL:** http://localhost:5678
- **Email:** lingxi@openclaw.local
- **Password:** Lingxi2025
- **状态:** ✅ 运行中
- **用途:** OpenClaw 的"手"——负责执行具体自动化操作

### 已安装的 Skills
- n8n-workflow-automation
- n8n-openclaw-bridge (OpenClaw ↔ n8n 打通)
- agentic-workflow-designer

### GitHub Push API Fallback ✅ 已实现
- **触发条件:** `git push` 失败（443端口不通等网络问题）
- **fallback:** GitHub Contents API (`PUT /repos/{owner}/{repo}/contents/{path}`)
- **实现位置:** `.github/workflows/daily-report.yml`
- **逻辑:** `continue-on-error: true` + `if: failure()` → API 上传 REPORT.md（含 SHA 更新防止冲突）

### 可用工作流（示例）
- 测试 webhook: `http://localhost:5678/webhook-test/lingxi-process`
- API 基础: `http://localhost:5678/api/v1/`
- Session Cookie: `/tmp/n8n_cookies.txt`

### 启动/停止
```bash
nohup n8n start > /tmp/n8n.log 2>&1 &  # 启动
pkill -f "n8n start"                      # 停止
```

### Agent 集成模式（"Dispatch Pattern"）
```
用户请求 → 灵犀（理解意图） → 触发 n8n Webhook → n8n 执行 → 灵犀回报结果
```

### 核心能力
- 🔍 创建/管理/监控 n8n 工作流
- 📡 触发 Webhook 自动化
- 📊 监控执行状态/错误
- 💾 管理凭证和数据

## ZeroGPU Router ✅ 已配置
- **API Key:** `zgpu-api-aa5921767b6bcde63756e1002f21bb3b7fc13c60824b34f71b52f5408a4d71cd`
- **Project ID:** `b9dc3ebb-aaf5-45c4-af58-239c81575bab`
- **Project 名称:** _(待登录 platform.zerogpu.ai 查看)_
- **Dashboard:** https://platform.zerogpu.ai
- **MCP Server:** `https://mcp.zerogpu.ai/mcp`（已通过 `openclaw mcp set zerogpu` 接入）
- **累计节省:** ~$0.0067 | 372 tokens offloaded | 4次调用
- **作用:** 把分类/摘要/JSON提取/PII脱敏等轻量任务路由到ZeroGPU小模型，省主模型token

## 上网 & 搜索
- browser-web-search: 网页搜索
- web-scraping: 数据爬取
- multi-engine-search: 多引擎搜索

## 数据库
- postgres-db: PostgreSQL
- database-operations: 数据库操作

## 安全 & 保护
- agent-guardian: Agent 守护
- security-auditor: 安全审计

## 记忆 & 认知
- agent-long-term-memory: 长期记忆
- multi-user-long-term-memory: 多用户长期记忆

## ClawHub 市场
- molts-list: Agent 服务交易市场（@moltslist.com）
- swarmmarket2: Agent 2 Agent 真钱交易平台（@swarmmarket.io）
- ⚠️ 两个平台目前服务器 502，需等恢复

## 变现产品线 ✅ 已上线

### agent-studio GitHub 项目
- **URL**: https://github.com/nima54851/agent-studio
- **Pages**: https://nima54851.github.io/agent-studio ✅
- **产品页**: https://nima54851.github.io/agent-studio/product.html ✅
- **Release v1.0.0**: https://github.com/nima54851/agent-studio/releases/tag/v1.0.0 ✅
- **GitHub Token**: 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
- **Scheduler PID**: 153290 (daily_scheduler.sh，等待每天09:00自动运行)

### 🛒 变现产品包
| 产品 | 价格 | 状态 | 下载 |
|---|---|---|---|
| GitHub Agent 自动化系统 入门版 | 免费 | ✅ 上线 | [GitHub 下载](https://github.com/nima54851/agent-studio/tree/main/products/github-agent-automation) |
| GitHub Agent 自动化系统 专业版 | ¥299 | ✅ 可售 | 联系购买 |
| GitHub Agent 自动化系统 企业版 | ¥999 | ✅ 可售 | 联系购买 |
| Gumroad Package（打包好的zip） | — | ✅ 已打包 | [Release 下载](https://github.com/nima54851/agent-studio/releases/tag/v1.0.0) |

### 接单平台（待注册）
- 程序员客栈: https://www.codingmore.com（需浏览器注册）
- 码市: https://codemart.com（需浏览器注册）
- 开源中国众包: https://zb.oschina.net（需浏览器注册）
- Upwork: https://www.upwork.com（需浏览器注册）
- Fiverr: https://www.fiverr.com（需浏览器注册）

### 变现进度
- [x] 产品包创建（README + workflow.json + SETUP.md）
- [x] 产品销售页上线（product.html）
- [x] GitHub Release v1.0.0 创建
- [x] Gumroad Package ZIP 打包
- [x] 主 README 完善（加入变现路径）
- [ ] 注册程序员客栈账号（需浏览器）
- [ ] 注册码市账号（需浏览器）
- [ ] 创建 Gumroad 产品页（需浏览器）
- [ ] 上传第一个视频（B站/YouTube）
- [ ] 接第一个付费单

## UUMit Agent Card（新的变现路径！）
- **状态:** 设备授权待确认
- **待用户操作:** 访问 `https://m.uumit.com/link` → 输入码 `C6D1C87B`
- **平台:** https://api.uumit.com/api/v1/ — API 公开，市场有 11 万+ 能力
- **灵犀可注册的能力类型:** code_review（代码审查）、github_automation（GitHub 自动化）、n8n_workflow（n8n 工作流）、web_scraping（网页爬取）
- **MCP 工具（免费读）:** uuagent_discover / uuagent_search / uuagent_wallet / uuagent_price_suggestion
- **MCP 工具（付费）:** uuagent_invoke / uuagent_create_order
- **device_code:** `817HUgeAokg6tGkOWkoAS74whIOl9Z0Zre02T0qMQj0`（10分钟有效）
- **待配置:** device auth 完成后拿到 X-Api-Key 和 X-Platform-User-Id

## OpenClaw MCP Serve（把灵犀暴露给外部 Agent）
- **公网可达:** `https://175.27.140.23:20447`（已测试，连接成功）
- **Token:** `SKzBr2s09RGQgRyxD0Dvuua5MJgAQyF4p8TwpG5HbYIQuOnQ`
- **状态:** 待启动 `openclaw mcp serve` 并配置 UUMit 连接灵犀
- **启动命令:** `openclaw mcp serve --url wss://175.27.140.23:20447 --token-file ~/.openclaw/gateway.token`
- **⚠️ 警告:** 暴露公网需考虑安全边界，建议配合 IP 白名单或临时启动模式

## 灵犀全球 A2A Registry ✅ 已上线
- **GitHub:** https://github.com/nima54851/lingxi-a2a-registry
- **本地 API:** http://localhost:18432
- **公网 API:** http://175.27.140.23:18432
- **Agent Card:** http://175.27.140.23:18432/.well-known/agent.json
- **功能:** Agent 注册/发现/A2A路由/心跳/Agent Card
- **技术栈:** FastAPI + SQLite + 原生 HTML/JS
- **已注册 Agent:** 灵犀全球 A2A Registry、代码审查 Agent、网页爬虫 Agent、GitHub Trending 监控

## ClawHub 技能市场（6月26日解封）
- **GitHub 账号:** nima54851（8天，还差6天到14天）
- **发布命令:** `clawhub skill publish <path>`
- **待发布技能:** agent-long-term-memory / github / n8n-workflow-automation / browser-web-search / github-pages-auto-deploy / web-scraping
- **注意:** oss.uumit.com 的 uumit_agent.zip 下载链接目前 404（待官方修复）

## 项目结构
scripts/: github_trending.py, mcp_client.py, memory.py, webhook_dispatcher.py
skills/: agent-memory, github-trending-monitor, mcp-integration, webhook-dispatcher
workflows/: github-ai-digest.json + runbook
products/github-agent-automation/: 变现产品包（n8n workflow + 文档）
docs/: GitHub Pages（主站 + 产品页）
daily_ops.py: 自动化运营脚本（评论+Star+报告）
daily_scheduler.sh: 每日调度脚本

## TTS 语音
- saga / sag: ElevenLabs TTS，讲故事/语音播报用

## GitHub 推送备注
- **origin URL 问题：** agent-studio 仓库的 origin 曾错误指向 coursepay-sales。已修正：`https://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@github.com/nima54851/agent-studio.git`
- **git push 网络问题：** github.com:443 端口不可达（2026-06-20），GitHub API (api.github.com) 正常。推送需等网络恢复。

---

*最后更新: 2026-06-20（每日运营日检）*

## 新建技能（2026-06-23）
| 技能 | 功能 | 来源 |
|---|---|---|
| skill-builder | 从零创建 AI Agent 技能 | obra/superpowers |
| self-hosted-ai | 部署 Ollama / N8N / nginx | ollama/n8n |
| coding-tutor | 编程学习路线 | freeCodeCamp |
| n8n-workflow-builder | n8n 工作流设计 | n8n-io/n8n |
| career-roadmap | 程序员成长规划 | developer-roadmap |
| agent-skills-kit | AI Agent 技能开发框架 | BuilderIO/skills |

**打包文件：~/.openclaw/workspace/*.skill**
