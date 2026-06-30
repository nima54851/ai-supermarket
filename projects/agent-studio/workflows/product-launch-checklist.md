# AI Agent 产品发布检查清单

> 从 0 到 1 发布你的 AI 产品。这份清单帮助独立开发者和 AI Agent 创作者系统化完成上线准备。

---

## 📋 第一阶段：产品定义

- [ ] 明确解决的问题（Problem Statement）
- [ ] 目标用户画像（User Persona）
- [ ] 核心功能列表（Top 3，不要贪多）
- [ ] 竞争优势分析（为什么选你不选别人？）
- [ ] 定价模型确定（免费/订阅/一次性/开源捐赠）

---

## 📄 第二阶段：文档准备

- [ ] 产品 README.md（一句话介绍 + 功能 + 截图 + 快速开始）
- [ ] 安装/配置指南
- [ ] API 文档（如果适用）
- [ ] 使用示例（5 个核心场景）
- [ ] FAQ / 已知问题
- [ ] 更新日志（CHANGELOG.md）
- [ ] LICENSE 选择（MIT / Apache 2.0 / 闭源）

---

## 🎨 第三阶段：品牌与展示

- [ ] 产品名称 + Logo（AI 生成：Midjourney / DALL-E / Canva）
- [ ] 产品截图 / Demo 视频（Loom / ScreenStudio）
- [ ] 着陆页（GitHub Pages / Vercel / Carrd）
- [ ] 定价页面（包含对比表）
- [ ] 社交媒体配图（Twitter 1200x675, 微博 900x383）

---

## 💳 第四阶段：支付与分发

- [ ] Gumroad / LemonSquisky 账户配置
- [ ] 产品页面完善（描述、截图、变体设置）
- [ ] 支付 webhook 配置（接收购买通知）
- [ ] 邮箱自动化（SendGrid / Resend 发送交付物）
- [ ] 许可证生成逻辑（Email / Gumroad 内置）

---

## 🔧 第五阶段：技术就绪

- [ ] 代码质量（README → lint → test → review）
- [ ] CI/CD 流程（GitHub Actions 自动构建）
- [ ] 环境变量文档（.env.example）
- [ ] Docker 支持（如适用）
- [ ] 健康检查端点
- [ ] 错误日志收集（Sentry / 日志文件）
- [ ] 数据备份策略

---

## 📣 第六阶段：发布与推广

### 预热（发布前 1-2 周）
- [ ] 在社交平台预告
- [ ] 邀请内测用户（5-10 人）
- [ ] 收集反馈并迭代
- [ ] 准备发布公告文案（3 个版本）

### 发布日
- [ ] GitHub Release 创建（含二进制文件）
- [ ] 发布公告推文/X
- [ ] 产品 Hunt / 导航站提交
- [ ] Email 列表通知
- [ ] 相关社区发帖（Reddit, V2EX, 即刻, 小众软件）

### 发布后
- [ ] 24h 数据监控（Stars / 下载 / 销量）
- [ ] 用户反馈聚合
- [ ] Bug 修复快速响应
- [ ] 第一版更新发布（v0.1.1）
- [ ] 复盘文档

---

## 📊 关键指标

| 指标 | 第一天目标 | 第一周目标 |
|------|----------|----------|
| GitHub Stars | 5 | 20 |
| 下载量（Gumroad）| 3 | 10 |
| 社区讨论帖 | 1 | 5 |
| 用户反馈 | 2 | 8 |
| 转化率（访客→下载）| 5% | 8% |

---

## 🛠 配套资源

- **自动化脚本**: `scripts/product_launch.py`
- **AI Agent**: `skills/product-launch-assistant/`
- **n8n Workflow**: `workflows/product-launch-automation.json`
- **推广文案**: `prompts/product-announcement.md`

---

*由 灵犀 × agent-studio 自动生成 | 2026-06-27*
