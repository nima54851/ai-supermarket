# AI Docs Generator — SKILL.md

> Auto-generate README, API docs, and changelogs from code using AI agents.

## 功能
- 从代码注释自动生成 API 文档
- 从 commit 历史自动生成 Changelog
- 从项目结构自动生成 README 概览
- 生成 OpenAPI 3.0 规范文件

## 目录结构
```
docs-generator/
├── README.md           # 本文件
├── openapi-template.md # OpenAPI 文档模板
├── changelog-prompt.md # Changelog 生成提示词
├── readme-prompt.md    # README 生成提示词
└── scripts/
    ├── generate_docs.py
    └── generate_openapi.py
```

## 使用方法

### 1. 生成 Changelog
```bash
# 获取 commit 历史
git log --oneline --since="2026-06-01" --until="2026-07-01" > changelog_raw.txt

# 使用 AI 生成 changelog
python3 scripts/generate_docs.py \
  --input changelog_raw.txt \
  --mode changelog \
  --output CHANGELOG.md
```

### 2. 生成 README
```python
from generate_docs import DocsGenerator

gen = DocsGenerator()
gen.generate_readme(
    project_path=".",
    output="README_NEXT.md",
    template="agency"  # agency | minimal | detailed
)
```

### 3. 生成 OpenAPI 文档
```python
from generate_openapi import OpenAPIGenerator

gen = OpenAPIGenerator()
gen.scan_endpoints("src/api/")
gen.add_auth("Bearer", "X-API-Key")
gen.write("openapi.yaml")
```

## 与 n8n 集成
```json
{
  "name": "docs-generator-n8n",
  "nodes": [
    {"type": "GitHubTrigger", "params": {"events": ["push"]}},
    {"type": "Code", "params": {"js": "git log --oneline -20"}},
    {"type": "OpenAI", "params": {"prompt": "{{changelog_prompt}}"}},
    {"type": "GitHubFileEdit", "params": {"path": "CHANGELOG.md"}}
  ]
}
```

## 提示词模板

### Changelog 生成
\`\`\`
分析以下 git commit 历史，按以下分类整理：
- Features: 新功能
- Fixes: bug 修复  
- Improvements: 优化改进
- Docs: 文档更新

格式：
## [版本号] - YYYY-MM-DD
### Features
- ...

输出 Markdown 格式。
\`\`\`

### README 生成
\`\`\`
为以下项目生成 README.md：
- 项目描述：{description}
- 技术栈：{tech_stack}
- 主要功能：{features}

要求：
- 包含徽章（Build, License, Version）
- 包含目录
- 包含安装/使用/贡献指南
- 包含许可证
- 英文为主，适当中文注释
\`\`\`

## 输出示例
```markdown
# Project Name

[![Build](https://img.shields.io/github/actions/workflow/status/user/repo/ci.yml)](https://github.com/user/repo/actions)
[![License](https://img.shields.io/github/license/user/repo)](LICENSE)
[![Version](https://img.shields.io/github/v/release/user/repo)](https://github.com/user/repo/releases)

> One-line project description

## Features
- ✨ Feature 1
- 🔧 Feature 2

## Quick Start
\`\`\`bash
npm install
npm run dev
\`\`\`
```

## 在 OpenClaw 中使用
```python
# 使用 skill-builder 创建
skill_builder.create_skill(
    name="docs-generator",
    description="Auto-generate docs from code",
    prompts=["changelog-prompt.md", "readme-prompt.md"],
    scripts=["scripts/generate_docs.py"]
)
```

---

*适用于 AI Agent 开发者的自动化文档工具*
