# Agent Memory Automation

> AI Agent 的长期记忆管理系统 — 让 Agent 在会话之间保持上下文连续性

## 核心功能

- **向量记忆存储** — ChromaDB / Qdrant / Weaviate 持久化记忆
- **会话摘要提取** — 自动从对话历史中提取关键事实、偏好、决策
- **记忆召回** — 基于语义相似度的上下文注入（Recall）
- **记忆遗忘** — 按时间 / 重要性 / 去重策略自动清理
- **多 Agent 共享记忆** — 团队 Agent 共享知识库

## 目录结构

```
agent-memory-automation/
├── SKILL.md                          ← 本文件
└── workflows/
    └── n8n-memory-pipeline.json      ← n8n 记忆 pipeline workflow
```

## 使用场景

| 场景 | 描述 |
|------|------|
| 个人 AI 助手 | 记住用户的项目、偏好、习惯 |
| 客服 Agent | 记住客户历史问题，提供连贯服务 |
| 开发 Agent | 记住代码规范、架构决策、技术债 |
| 团队知识库 | 多 Agent 共享项目上下文 |

## 快速开始

### 1. n8n Workflow

导入 `workflows/n8n-memory-pipeline.json` 到你的 n8n 实例：

- **触发器：** HTTP Request（接收 Agent 消息）
- **向量存储：** ChromaDB（记忆写入）/ Qdrant（召回检索）
- **LLM 步骤：** 摘要提取 → 存储决策 → 上下文注入

### 2. 记忆写入

```bash
curl -X POST https://your-n8n.com/webhook/memory-store \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "dev-assistant-01",
    "user_id": "alice",
    "session_id": "sess-123",
    "content": "项目使用 FastAPI + PostgreSQL，数据库迁移用 Alembic",
    "metadata": {"type": "fact", "importance": "high"}
  }'
```

### 3. 记忆召回

```bash
curl -X POST https://your-n8n.com/webhook/memory-recall \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "dev-assistant-01",
    "user_id": "alice",
    "query": "项目用的数据库是什么？"
  }'
```

### 4. OpenClaw 集成

在 OpenClaw 的 `memory/YYYY-MM-DD.md` 中调用：

```python
# 写入记忆
memory_store(
    agent_id="lingxi",
    content="用户偏好用 markdown 格式回复",
    importance=0.8
)

# 召回相关记忆
context = memory_recall(
    agent_id="lingxi",
    query="用户的代码风格偏好"
)
```

## 记忆类型

| 类型 | 描述 | TTL |
|------|------|-----|
| `fact` | 客观事实（技术栈、架构） | 永久 |
| `preference` | 用户偏好（格式、语气） | 30天 |
| `decision` | 重要决策（方案选型） | 永久 |
| `context` | 会话上下文 | 会话结束 |
| `todo` | 待办事项 | 完成时删除 |

## 向量数据库选择

| 数据库 | 适用场景 | 部署难度 |
|--------|---------|---------|
| ChromaDB | 本地开发、简单场景 | ⭐ 简单 |
| Qdrant | 生产级、高并发 | ⭐⭐ 中等 |
| Weaviate | 复杂语义搜索 | ⭐⭐⭐ 复杂 |
| Supabase pgvector | 已有 PostgreSQL | ⭐⭐ 中等 |

## 相关 Skills

- `rag-knowledge-base/` — RAG 知识库（基于记忆的问答）
- `database-automation/` — PostgreSQL 数据库管理
- `ollama-self-hosted-llm/` — 本地 LLM 支持

---

*Version 1.0 | 2026-07-20*
