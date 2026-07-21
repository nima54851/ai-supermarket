# Database Automation Skill

AI-powered database operations — schema design, query building, migration planning, and performance analysis.

## Overview

This skill turns natural language into SQL, plans migrations, detects performance bottlenecks, and manages PostgreSQL/MySQL/MongoDB operations through AI agents.

## Tools Used
- `postgres-db` / `postgres-mcp-skills`
- n8n workflows for scheduled queries and alerts

## Use Cases

### Natural Language → SQL
User: "Show me all users who signed up in the last 7 days with more than 3 orders"
→ Agent generates optimized SQL, executes safely via read-only role

### Schema Review
Upload a schema file → AI reviews normalization, indexes, constraints, suggests improvements

### Automated Backups + Health Alerts
Daily scheduled backup workflow → AI checks backup integrity → alert on failure

### Query Performance Audit
Paste slow query → AI explains plan, suggests indexes

## Example Workflows

1. **AI Database Query Builder** — n8n + PostgreSQL + AI Agent
2. **Nightly Data Quality Check** — scheduled schema validation
3. **Auto-create migration PRs** — detect schema drift, generate ALTER statements

## Setup
```bash
# Connect PostgreSQL credentials in n8n
# Import n8n workflow from integrations/database-automation/
```

## Files
- `SKILL.md` — this file
- `README.md` — detailed guide
- `prompts/query-builder.md` — SQL generation prompts
- `prompts/schema-review.md` — schema analysis prompts
