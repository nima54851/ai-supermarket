# Workflow Orchestration Skill

**Skill Name:** workflow-orchestration  
**Author:** agent-studio  
**Version:** 1.0  
**Trigger Keywords:** orchestrate, workflow, pipeline, DAG, sequence, chain, dispatch, multi-step  

## Description

Comprehensive workflow orchestration framework for AI agents. Supports linear chains, parallel branches, DAG-based dependency graphs, and dynamic dispatch patterns. Built for OpenClaw + n8n integration.

## Architecture

```
User Intent
    ↓
Orchestrator Agent (Classify intent)
    ↓
┌─────────────────────────────────────┐
│ DAG Executor                        │
│                                     │
│   [Step A] ──┬──→ [Step C]         │
│             │                      │
│   [Step B] ──┴──→ [Step D]          │
│                                     │
│   Dependency resolution + error     │
│   recovery + retry logic            │
└─────────────────────────────────────┘
    ↓
Result Aggregator → User Response
```

## Core Patterns

### 1. Linear Chain
Steps execute sequentially. Each step's output feeds the next.

### 2. Parallel Branch
Independent tasks run concurrently. Results merge at a barrier.

### 3. DAG Executor
Directed Acyclic Graph with explicit dependencies. Handles complex multi-branch workflows.

### 4. Dynamic Dispatch
Intent-based routing to specialized sub-agents.

## Usage

```python
from workflow_orchestrator import DAGExecutor, Step

executor = DAGExecutor()

executor.add_step(Step("fetch", fetch_data))
executor.add_step(Step("transform", transform_data, depends=["fetch"]))
executor.add_step(Step("save", save_data, depends=["transform"]))

result = executor.execute(initial_input)
```

## n8n Integration

```bash
# n8n workflow: workflow-orchestration/
# Triggers: Webhook (POST /webhook/workflow-orchestrate)
# Nodes: Classify → Route → Execute Sub-Agent → Aggregate → Respond
```

## Best Practices

- **Idempotency:** Each step should be safe to retry
- **Timeout:** Set per-step timeouts; global timeout for the DAG
- **Error recovery:** Define fallback behavior per step
- **Logging:** Log step inputs/outputs for debugging

## Files

- `SKILL.md` — This file
- `workflow_orchestrator.py` — Core Python executor
- `README.md` — Full documentation

## Category

AI Agent Framework / Orchestration
