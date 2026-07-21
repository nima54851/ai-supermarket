# Workflow Orchestration Integration

> n8n workflows for orchestrating multi-step AI agent pipelines, task queues, and distributed task execution.

## Overview

Build complex, reliable automation pipelines with retry logic, dead-letter queues, parallel execution, and AI-driven routing — all visual in n8n.

## Components

### n8n Workflow: `n8n-workflow-orchestrator.json`

- **Trigger:** Webhook, Schedule, Queue (via Redis/BullMQ)
- **Process:**
  1. Receive task request (API call, webhook, schedule)
  2. AI agent classifies intent and routes to correct pipeline
  3. Execute steps in parallel or sequential mode
  4. Error handling with retry (exponential backoff)
  5. Dead-letter queue for failed tasks
  6. AI summarizer summarizes output
  7. Route result to destination (email, Slack, Notion, DB)
- **Output:** Structured task results, error logs, performance metrics

### Patterns Included

- **Fan-out / Fan-in:** One trigger → parallel branches → merge results
- **Pipeline Chaining:** Step A → AI decision → Step B/C → Step D
- **Retry with Backoff:** Auto-retry failed nodes up to N times
- **Circuit Breaker:** Stop hammering failing services
- **Priority Queue:** Urgent tasks jump the queue
- **Idempotent Design:** Safe to retry without side effects
- **Human-in-the-Loop:** Pause workflow for manual approval

## Setup

```bash
# 1. Import workflow
# n8n → Settings → Import from JSON → paste n8n-workflow-orchestrator.json

# 2. Configure
# - Redis (optional): for BullMQ priority queues
# - OpenAI API key: for AI routing decisions
# - Slack webhook: for human-in-the-loop approvals

# 3. Webhook endpoint
# POST https://your-n8n-url/webhook/task-orchestrate
```

## Usage

```python
import requests

result = requests.post(
    "https://your-n8n-url/webhook/task-orchestrate",
    json={
        "task": "analyze_github_trending",
        "params": {"language": "python", "since": "daily"},
        "priority": "normal",
        "callback": "https://your-app.com/webhook/result"
    }
).json()
print(result["workflow_id"])  # Track progress
```

## Workflow Diagram

```
Webhook/Slack/Schedule
        │
        ▼
┌─────────────────────┐
│  AI Intent Router   │──→ classify task type
└─────────┬───────────┘
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
 StepA  StepB  StepC   ← parallel execution
    │     │     │
    └─────┼─────┘
          ▼
   ┌─────────────┐
   │ Error? Retry│──→ Dead Letter Queue
   └──────┬──────┘
          ▼
   ┌─────────────┐
   │ AI Summarizer│
   └──────┬──────┘
          ▼
  Slack / Email / DB
```

## Required Skills

- `n8n-workflow-builder` — Customize the orchestrator
- `agent-skills-kit` — Build sub-agent task steps
- `self-hosted-ai` — For local Ollama-powered routing

---

*Built with 灵犀 AI · agent-studio*
