---
name: mcp-integration
description: Integrate AI agents with the Model Context Protocol (MCP) ecosystem. Connect agents to external tools, databases, filesystems, and APIs via MCP servers.
---

# MCP Integration Skill

## WHAT IS MCP?

Model Context Protocol (MCP) is an open standard from Anthropic that lets AI agents connect to external tools and data sources in a standardized way.

## ARCHITECTURE

```
AI Agent (OpenClaw)
  ↕ MCP Client
  ↕ MCP Protocol
  ↕ MCP Server
↕ GitHub / Filesystem / Database / Custom tools
```

## MCP SERVERS (Popular)

| Server | Tools |
|--------|-------|
| `github` | Issues, PRs, repos, actions |
| `filesystem` | Read/write files |
| `postgres` | SQL queries |
| `slack` | Send messages |
| `fetch` | HTTP requests |
| Custom | Any API |

## QUICK START

### 1. Install MCP SDK

```bash
pip install mcp
```

### 2. Connect to a public MCP server

```bash
python3 scripts/mcp_client.py --server https://api.example.com/mcp
```

### 3. Use tools from OpenClaw

Once connected, tools become available to the agent via the MCP protocol.

## OPENCLAW INTEGRATION

Add to your OpenClaw skill:

```markdown
When the user asks to interact with GitHub, use the MCP GitHub server:
- MCP Server: github-mcp (or your configured endpoint)
- Available tools: create_issue, list_repos, search_code, etc.
```

## MCP SERVERS FOR AGENT-STUDIO

The `scripts/mcp_client.py` in this repo provides:
- HTTP/SSE transport (connect to remote MCP servers)
- Stdio transport (connect to local MCP servers)
- Interactive REPL for testing
- Tool discovery and invocation

## RESOURCES

- MCP Spec: https://modelcontextprotocol.io
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- MCP Servers: https://github.com/modelcontextprotocol/servers

---

*Part of [agent-studio](https://github.com/nima54851/agent-studio)*
