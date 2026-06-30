# 🔍 AI 代码审查 Agent — 产品说明

> 基于 OpenClaw + GitHub API 的自动化代码审查系统
> PR 提交 → 自动审查 → 评论反馈 → 质量报告

---

## 产品概述

这是一个**自动化 AI 代码审查 Agent**，监听 GitHub PR 事件，自动进行代码审查并留下专业评论。

| 功能 | 详情 |
|---|---|
| 🤖 自动 PR 审查 | 每次 PR 自动触发，AI 阅读 diff 并评论 |
| 🔍 问题检测 | 安全漏洞、逻辑错误、代码风格、性能问题 |
| ✅ LGTM 评分 | 为每个 PR 打质量分 |
| 📊 审查报告 | 每日生成代码质量报告 |
| 🔔 多渠道通知 | 审查结果推送到 Slack/微信/Telegram |

---

## 产品包含

- ✅ `workflow.json` — n8n 工作流（直接导入）
- ✅ `reviewer-setup.md` — 10分钟部署指南
- ✅ `agent-skill/` — OpenClaw 代码审查 Skill
- ✅ `prompts/` — 审查 prompt 模板
- ✅ 技术支持（购买后提供）

---

## 定价

| 版本 | 价格 | 包含内容 |
|---|---|---|
| 入门版 | ¥49 | 单仓库审查 + 基础 prompt |
| 专业版 | ¥199 | 多仓库 + Slack/微信通知 + 月度报告 |
| 企业版 | ¥699 | 私有部署 + 定制规则 + 无限仓库 |

---

## 购买方式

- **微信/支付宝：** 联系购买
- **Gumroad：** coming soon

---

## 作者

Built with ❤️ by [nima54851](https://github.com/nima54851)  
Powered by [agent-studio](https://github.com/nima54851/agent-studio) + OpenClaw
