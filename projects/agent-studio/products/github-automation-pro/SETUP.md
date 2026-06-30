# 🔥 GitHub 自动化 Pro — 部署指南

---

## 前置要求

- Node.js 18+
- n8n
- OpenClaw
- GitHub 管理员权限（需要创建 GitHub App 或 Personal Access Token）

---

## 步骤 1：安装

```bash
cp -r agent-skill/* ~/.openclaw/skills/github-automation-pro/
```

---

## 步骤 2：配置 GitHub App（推荐）或 PAT

**方式A：GitHub App（推荐，用于组织仓库）**
1. GitHub Settings → Developer settings → GitHub Apps → New GitHub App
2. 设置 Webhook URL：`https://your-domain.com/webhook/github-pro`
3. 勾选所需权限：PR/Issues/Actions/Contents
4. 安装到仓库

**方式B：Personal Access Token（个人仓库）**
- 创建 Token，勾选对应权限
- 填入 n8n 凭证

---

## 步骤 3：配置自动化规则

编辑 `rules/automation.json` 设置你的合并策略：

```json
{
  "autoMergeConditions": ["ci:passing", "reviews:>=2", "ai:approved"],
  "autoLabelRules": [{ "pattern": "fix:*", "label": "bug" }]
}
```

---

## 验证

创建一个测试 PR，检查：
- AI 是否自动审查
- 标签是否自动添加
- 符合条件是否自动合并

---

## 获取帮助

购买后可通过 GitHub Issues 或邮件联系技术支持。
