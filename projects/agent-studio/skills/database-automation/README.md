# Database Automation Guide

## Quick Start

1. Connect your PostgreSQL/MySQL database credentials in n8n
2. Import the workflow from `integrations/database-automation/`
3. Configure the AI Agent node with your preferred LLM
4. Set up a webhook trigger or schedule

## Workflow: AI Query Builder

```
User Input (Webhook/REST) → AI Agent (natural language → SQL)
→ PostgreSQL Node (execute read query) → Response to user
```

## Safety Rules
- Use read-only database roles for AI-generated queries
- Always include LIMIT clauses for large tables
- Log all queries for audit trail
- Require human approval for write operations (INSERT/UPDATE/DELETE)
