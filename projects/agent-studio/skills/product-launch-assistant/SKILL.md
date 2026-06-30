# Product Launch Assistant - 技能文档

## 技能概述

**名称:** product-launch-assistant  
**功能:** 端到端 AI 产品发布自动化助手  
**适用场景:** 独立开发者、创业团队、AI Agent 创作者将作品变现  

---

## 核心能力

### 1. 上市前检查清单
- [ ] 产品文档完整性审查
- [ ] 定价策略分析（竞品对比）
- [ ] 目标用户画像验证
- [ ] 着陆页转化率评估
- [ ] 支付/分发渠道配置
- [ ] 客服/支持渠道建立

### 2. 发布前自动化
```bash
# 一键生成发布材料包
python3 scripts/product_launch.py --product-id <id> --platform gumroad
```
生成物：
- 📄 README 更新版
- 🖼️ 产品宣传图（HTML/CSS 模板）
- 📣 Twitter/微博 发布文案（3个版本）
- 📧 邮件订阅通知模板
- 💬 Discord/Telegram 公告模板

### 3. 渠道分发工作流
支持自动发布到：
| 渠道 | 工具 | 自动化程度 |
|------|------|-----------|
| Gumroad | Gumroad API | 全自动 |
| GitHub Marketplace | GitHub API | 全自动 |
| Product Hunt | 手动 + 提醒 | 半自动 |
| Twitter/X | API v2 | 全自动 |
| 即刻/小宇宙 | 手动 | 提醒 |
| AI导航站 | 手动提交 | 提醒 |

### 4. 追踪与复盘
- 发布后 24h/7d/30d 数据收集
- 用户反馈自动聚合
- 转化率漏斗分析
- 下一版本优化建议

---

## 快速开始

```bash
cd agent-studio
python3 -m skills.product_launch_assistant.cli --init
```

---

## 与 n8n 集成

触发 webhook: `http://localhost:5678/webhook/product-launch`

n8n workflow: `workflows/product-launch-automation.json`

---

## 适用产品类型

- 🤖 AI Agent / Skill（OpenClaw, Coze）
- 📦 SaaS 工具（n8n workflow 包）
- 📚 课程/教程（Notion + Gumroad）
- 🧩 API 服务（MCP Server / OpenAPI）
- 💡 Prompt/提示词包（Gumroad 下载）

---

*由 灵犀 × agent-studio 自动生成 | 2026-06-27*
