# 🛠️ Skill Builder — AI Agent 技能构建助手

## 产品说明

基于 agentic skills 框架，从零构建专业 AI Agent 技能的工具包。

## 包含内容

```
skill-builder-source/
├── SKILL.md              # 技能核心定义（触发条件 + 工作流）
├── scripts/              # 初始化 + 打包脚本
└── references/          # 参考文档
```

## 功能

- ✅ 从零创建新 AI Agent 技能
- ✅ 设计技能结构和工作流
- ✅ 编写 SKILL.md 和配套脚本
- ✅ 打包验证并发布到 ClawHub
- ✅ 接入 OpenClaw Agent 系统

## 适用场景

| 场景 | 示例 |
|------|------|
| 创建新技能 | "帮我做一个 GitHub 自动日报机器人" |
| 扩展 Agent 能力 | "给灵犀加一个定时提醒技能" |
| 技能打包发布 | "把这个技能发布到 ClawHub" |

## 安装步骤

### Step 1：安装到 OpenClaw

```bash
# 安装技能（ClawHub）
clawhub install skill-builder

# 或手动复制到工作目录
cp -r skill-builder-source ~/.openclaw/workspace/skills/
```

### Step 2：验证

```bash
clawhub list | grep skill-builder
```

### Step 3：使用

在 OpenClaw 中告诉灵犀：
> "帮我创建一个能自动追踪 B 站热榜的技能"

## 适用版本

- OpenClaw v0.18+
- Node.js 18+

## 价格

¥49 / $6.99 USD（永久授权，包含未来更新）

## 支持

购买后联系 Telegram [@diquchaxun78_bot](https://t.me/diquchaxun78_bot) 获取技术支持。
