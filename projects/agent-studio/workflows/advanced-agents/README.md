# Advanced Agents Workflows

> Multi-agent orchestration patterns for n8n + AI agent systems

## 📁 Contents

### multi-agent-parallel.json
Parallel task orchestration: routes a single task to specialized agents (Research, Code, Review) concurrently and aggregates results.

## Architecture

```
┌─────────────┐
│   Trigger  │
└──────┬──────┘
       ▼
┌─────────────┐
│Task Router  │─── research ──▶ ┌─────────────┐
│  (Switch)   │─── code ──────▶ │  Code Agent │
└──────┬──────┘─── review ───▶ │ Review Agent │
       │                        └──────┬──────┘
       │                              │
       │              ┌─────────────────┘
       ▼              ▼
┌─────────────────────────────┐
│    Aggregate Results        │
│  (merge agent outputs)      │
└─────────────────────────────┘
```

## Usage

1. Import `multi-agent-parallel.json` into your n8n instance
2. Configure the HTTP Request nodes to point to your agent endpoints (OpenClaw MCP, OpenAI, Anthropic, etc.)
3. Set `task_type` in the trigger payload: `research`, `code`, `review`, or `deploy`
4. Each agent processes in parallel — total time ≈ slowest agent

## Environment Variables

| Variable | Description |
|---|---|
| `AGENT_API_KEY` | API key for your agent endpoint |
| `AGENT_BASE_URL` | Base URL of your agent service |
| `MAX_CONCURRENT` | Max parallel agent calls (default: 5) |

## Extending

Add more specialized agents by:
1. Adding a new rule to the Router (Switch node)
2. Connecting the output to your new agent node
3. Adding the agent to the aggregator's input array
