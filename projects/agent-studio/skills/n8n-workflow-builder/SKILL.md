---
name: n8n-workflow-builder
description: n8n 工作流可视化构建助手。用于：(1) 根据需求设计 n8n 工作流，(2) 生成完整的 workflow JSON，(3) 在 n8n 中导入和调试工作流，(4) 解决 n8n 节点报错，(5) 集成 AI 能力（LangChain、OpenAI、Ollama）到工作流中，(6) 配置 webhook 触发和数据处理。当用户说"帮我做个 n8n 工作流"、"n8n 自动化的例子"、"如何用 n8n 实现 XX"、"这个 n8n 节点报错"时触发此技能。
---

# n8n Workflow Builder

## 核心概念

```
触发器（Webhook/Cron/Manual）
    → 节点1（数据获取）
    → 节点2（数据处理）
    → 节点3（AI处理）
    → 节点4（输出/通知）
```

## 标准工作流模板

### 模板1：AI 内容处理管道
```json
{
  "name": "AI Content Pipeline",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {}
    },
    {
      "name": "LLM",
      "type": "@n8n/n8n-nodes-langchain.openAi",
      "parameters": {
        "operation": "complete",
        "prompt": "={{ $json.message }}"
      }
    },
    {
      "name": "Discord Notify",
      "type": "n8n-nodes-base.discord",
      "parameters": {
        "webhook": { "value": "{{DISCORD_WEBHOOK}}" }
      }
    }
  ]
}
```

### 模板2：GitHub + AI Code Review
```json
{
  "name": "GitHub Code Review",
  "nodes": [
    {
      "name": "GitHub Trigger",
      "type": "n8n-nodes-base.githubTrigger",
      "parameters": { "events": ["pull_request"] }
    },
    {
      "name": "Ollama",
      "type": "@n8n/n8n-nodes-langchain.ollama",
      "parameters": {
        "model": "codellama",
        "prompt": "请审查以下代码并提出改进建议：\n={{ $json.diff }}"
      }
    },
    {
      "name": "Add Comment",
      "type": "n8n-nodes-base.github",
      "parameters": { "operation": "createComment" }
    }
  ]
}
```

## 常用节点速查

| 节点 | 用途 | 关键参数 |
|---|---|---|
| HTTP Request | 调用外部 API | URL、Method、Auth |
| Code | 自定义 JS/Python | `$json`、`$inputs` |
| Set | 设置/修改变量 | `name`, `value` |
| IF / Switch | 条件分支 | `conditions` |
| Loop | 循环处理 | `batchSize` |
| Telegram / Discord | 发送通知 | webhook URL |
| Google Sheets | 读写表格 | spreadsheetId |
| PostgreSQL / MySQL | 数据库操作 | connection, query |

## AI 集成（LangChain）

```javascript
// Code 节点中的 Ollama 调用
const { Ollama } = require('@langchain/community/llms/ollama');
const ollama = new Ollama({ baseUrl: 'http://localhost:11434' });
const res = await ollama.invoke($json.user_input);
return [{ output: res }];
```

## 导入工作流

```bash
# 方法1：n8n UI 导入
# 复制 JSON → n8n → Settings → Import from JSON

# 方法2：API 创建
curl -X POST http://localhost:5678/rest/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: <YOUR_KEY>" \
  -d @workflow.json
```

## 常见报错

| 报错 | 原因 | 解法 |
|---|---|---|
| `Credentials for "XXX" are not configured` | 未配置凭证 | n8n → Settings → Credentials 新建 |
| `Webhook path already in use` | 路径冲突 | 改个唯一路径或加时间戳 |
| `Timeout: Promise did not resolve` | 外部 API 超时 | 增加节点超时时间，或加 IFError 处理 |
| `Binary data does not exist` | 节点未输出二进制 | 检查上游节点是否支持 binary |

## 最佳实践

1. **每个工作流只用一种触发器** — 避免状态混乱
2. **错误处理**：每个关键节点后加 IFError → 通知节点
3. **凭证分离**：不要把密钥硬编码在 workflow JSON 里
4. **版本记录**：重要工作流导出 JSON 备份
5. **测试先用手动触发**：确认无误再切换到自动触发
