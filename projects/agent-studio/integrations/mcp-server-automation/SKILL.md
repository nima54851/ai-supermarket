# MCP Server Automation

Build and deploy Model Context Protocol (MCP) servers that expose your n8n workflows, databases, and APIs as AI-consumable tools.

## What This Skill Does

MCP (Model Context Protocol) is an emerging standard for connecting AI assistants to external tools. This skill lets you build MCP servers backed by your n8n automations — so any AI that supports MCP can use your workflows as tools.

## File Structure

```
integrations/mcp-server-automation/
├── SKILL.md                    # This file
├── mcp-server/
│   ├── server.py              # Python MCP server (FastMCP)
│   ├── requirements.txt       # Dependencies
│   └── config.yaml            # Tool registry
├── n8n-mcp-workflow.json      # n8n: MCP tool dispatcher
└── README.md                   # Setup guide
```

## Quick Start

```bash
cd integrations/mcp-server-automation/mcp-server
pip install -r requirements.txt
python server.py
```

## MCP Server (server.py)

```python
"""
MCP Server — exposes n8n workflows as MCP tools
Supports: OpenClaw MCP, Claude Desktop, Cursor, etc.
"""
import json
import httpx
from typing import Any
from fastmcp import FastMCP

mcp = FastMCP("n8n-AI-Agent-Studio")

N8N_BASE = "http://localhost:5678"
N8N_API_KEY = "your-n8n-api-key"  # Set via env N8N_API_KEY

def call_n8n_workflow(webhook_url: str, payload: dict) -> dict:
    headers = {"X-N8N-API-KEY": N8N_API_KEY}
    resp = httpx.post(webhook_url, json=payload, headers=headers, timeout=30)
    return resp.json()

@mcp.tool()
def github_activity_summary(repo: str, days: int = 7) -> str:
    """Get GitHub activity summary for a repository (stars, issues, commits)."""
    webhook_url = f"{N8N_BASE}/webhook/github-activity"
    result = call_n8n_workflow(webhook_url, {"repo": repo, "days": days})
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
def send_notification(channel: str, message: str, priority: str = "normal") -> str:
    """Send a notification via Slack/Discord/Telegram/Email based on channel."""
    webhook_url = f"{N8N_BASE}/webhook/notify"
    result = call_n8n_workflow(webhook_url, {
        "channel": channel,
        "message": message,
        "priority": priority
    })
    return f"Notification sent: {result.get('status', 'ok')}"

@mcp.tool()
def search_knowledge_base(query: str, top_k: int = 5) -> str:
    """Search the AI knowledge base for relevant documents and answers."""
    webhook_url = f"{N8N_BASE}/webhook/rag-search"
    result = call_n8n_workflow(webhook_url, {
        "query": query,
        "top_k": top_k
    })
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
def run_data_pipeline(pipeline_id: str, params: dict) -> str:
    """Trigger a data processing pipeline (ETL, enrichment, export)."""
    webhook_url = f"{N8N_BASE}/webhook/data-pipeline"
    result = call_n8n_workflow(webhook_url, {
        "pipeline_id": pipeline_id,
        "params": params
    })
    return f"Pipeline {pipeline_id} triggered: {result.get('run_id')}"

@mcp.tool()
def get_system_health() -> str:
    """Get health status of all integrated services (n8n, DB, APIs)."""
    webhook_url = f"{N8N_BASE}/webhook/health-check"
    result = call_n8n_workflow(webhook_url, {})
    return json.dumps(result, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Run with: python server.py
    # Or use: fastmcp run server.py
    mcp.run()
```

## n8n Workflow: MCP Tool Dispatcher

The n8n workflow `n8n-mcp-workflow.json` handles incoming MCP tool calls:
- Route by `tool_name` field
- Authenticate requests via API key
- Execute appropriate sub-workflow
- Return structured JSON response

## Connecting to AI Clients

### OpenClaw MCP Bridge
```json
{
  "mcpServers": {
    "agent-studio": {
      "command": "python",
      "args": ["/path/to/mcp-server/server.py"],
      "env": {
        "N8N_API_KEY": "your-n8n-api-key"
      }
    }
  }
}
```

### Claude Desktop
Add to `~/.claude/desktop/settings.json`:
```json
{
  "mcpServers": {
    "agent-studio": {
      "command": "python",
      "args": ["/path/to/mcp-server/server.py"]
    }
  }
}
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `N8N_API_KEY` | ✅ | n8n API key |
| `N8N_BASE_URL` | | n8n base URL (default: http://localhost:5678) |
| `MCP_LOG_LEVEL` | | Log level: DEBUG/INFO/WARNING (default: INFO) |
| `AUTH_SECRET` | | Shared secret for MCP client auth |

## Use Cases

1. **Universal AI Tool Backend** — Any MCP-compatible AI client can call your n8n workflows
2. **Multi-Agent Coordination** — Multiple AI agents share the same tool set via MCP
3. **Enterprise Integration** — Expose internal tools to AI without exposing credentials
4. **A/B Prompt Testing** — MCP makes it easy to swap tool implementations

## Dependencies

```
fastmcp>=0.1.0
httpx>=0.27.0
pyyaml>=6.0
python-dotenv>=1.0.0
```
