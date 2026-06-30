---
name: skill-builder
description: AI Agent 技能构建助手，基于 agentic skills 框架（参考 obra/superpowers 思想）。用于：(1) 从零创建新技能，(2) 根据用户需求设计技能结构，(3) 编写 SKILL.md 和配套脚本/引用文件，(4) 打包和发布技能。当用户说"创建一个技能"、"帮我做个 XX 助手"、"做一个能 XX 的能力"、或任何涉及构建 AI Agent 功能模块的需求时触发此技能。
---

# Skill Builder

构建 AI Agent 技能的核心工作流。

## 快速启动

### Step 1：理解需求

向用户确认：
- 这个技能要做什么？
- 典型使用场景是什么？（给 1-2 个例子）
- 涉及哪些工具或 API？

### Step 2：初始化

```bash
python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/init_skill.py <skill-name> \
  --path ~/.openclaw/workspace/skills \
  --resources scripts,references[,assets]
```

### Step 3：构建内容

- **SKILL.md**：技能的核心说明（触发条件 + 核心流程）
- **scripts/**：需要可靠执行的代码（API 调用、数据处理等）
- **references/**：参考资料（API 文档、Schema、示例）
- **assets/**：模板文件（HTML/React 骨架、配置文件等）

### Step 4：打包验证

```bash
python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  ~/.openclaw/workspace/skills/<skill-name>
```

## 技能结构模板

```
skill-name/
├── SKILL.md              # 必需：name + description + 核心流程
├── scripts/              # 可选：Python/Bash 自动化脚本
├── references/           # 可选：API文档、Schema、详细指南
└── assets/               # 可选：模板、图标、静态文件
```

## SKILL.md 写作规范

1. **description** 要写清楚"什么时候触发"，这是 AI 判断是否使用该技能的唯一依据
2. **body** 只写 AI 执行任务所需的关键步骤，不写冗余说明
3. **脚本要实测** — 创建完脚本后实际运行验证
4. **一个技能只做一件事** — 避免功能堆砌

## 常用工具路径

- 初始化脚本：`/usr/lib/node_modules/openclaw/skills/skill-creator/scripts/init_skill.py`
- 打包脚本：`/usr/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py`
- 技能存放目录：`~/.openclaw/workspace/skills/`
