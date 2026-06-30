---
name: agent-skills-kit
description: AI Agent 技能开发套件，参考 BuilderIO/skills 和 obra/superpowers 框架。用于：(1) 设计和构建 AI Agent 的可复用技能模块，(2) 定义工具调用接口和工作流，(3) 编写 SKILL.md 元数据，(4) 打包和发布技能到市场，(5) 测试和迭代技能效果。当用户说"给 AI Agent 开发技能"、"构建 Agent 工具"、"做个能力模块"、"Agent 技能框架"时触发此技能。
---

# Agent Skills Kit

## 什么是 Agent 技能

技能 = **触发条件** + **执行流程** + **工具接口**

```
用户请求
    → 触发识别（description 匹配）
    → 加载 SKILL.md
    → 读取 references/（按需）
    → 执行 scripts/（按需）
    → 返回结果
```

## 技能结构规范

```
skill-name/
├── SKILL.md              # 必需：name + description + 核心流程
├── scripts/              # 可选：确定性自动化脚本
├── references/           # 可选：按需加载的参考资料
└── assets/               # 可选：模板文件
```

## SKILL.md 标准格式

```markdown
---
name: my-skill
description: |
  技能描述 — 说明做什么 + 什么时候触发（这是AI判断是否使用的唯一依据）
  触发词示例：用户说"XX"时使用此技能
---

# My Skill

## 核心流程

步骤1：...
步骤2：...

## 工具调用

- API：...
- 脚本路径：...

## 示例

用户输入 → 技能处理 → 输出
```

## 触发条件写法（description 最重要）

**❌ 差的描述**：
> 这个技能可以处理文本

**✅ 好的描述**：
> 文本摘要与改写助手。用于：(1) 将长文章压缩为摘要，(2) 改写文本语气/风格，(3) 提取关键信息。当用户说"帮我总结"、"这篇文章说了什么"、"改写成正式语气"时触发。

## 技能开发流程

```
1. 明确需求：技能要解决什么问题？
2. 触发设计：用户会怎么说？
3. 流程设计：执行步骤是什么？
4. 工具准备：需要哪些脚本/API？
5. 编写 SKILL.md
6. 测试验证
7. 打包发布
```

## 脚本编写规范

### Python 脚本（推荐用于数据处理）
```python
#!/usr/bin/env python3
"""技能辅助脚本 — 描述脚本功能"""
import sys
import json

def main():
    # 从 stdin 读取 JSON
    data = json.load(sys.stdin)
    # 处理逻辑
    result = process(data)
    # 输出 JSON
    print(json.dumps(result, ensure_ascii=False))

def process(data):
    """核心处理函数"""
    # 实现逻辑
    return {"status": "ok", "result": data}

if __name__ == "__main__":
    main()
```

### Bash 脚本（推荐用于系统调用）
```bash
#!/bin/bash
set -euo pipefail

# 从参数或 stdin 读取输入
INPUT="${1:-$(cat -)}"

# 执行逻辑
RESULT=$(echo "$INPUT" | jq -r '.key')

# 输出结果
echo "{\"result\": \"$RESULT\"}"
```

## 打包与发布

```bash
# 打包
python3 scripts/package_skill.py ~/.openclaw/workspace/skills/my-skill

# 发布到 ClawHub（需账号）
clawhub skill publish ~/.openclaw/workspace/skills/my-skill
```

## 技能质量检查清单

- [ ] description 包含触发条件
- [ ] SKILL.md < 500 行
- [ ] 脚本有实测验证
- [ ] 目录结构符合规范
- [ ] 无多余文档文件（README/INSTALL 等）
- [ ] 打包验证通过

## 常用脚本路径

```
/usr/lib/node_modules/openclaw/skills/skill-creator/scripts/init_skill.py
/usr/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py
~/.openclaw/workspace/skills/          # 技能存放目录
```
