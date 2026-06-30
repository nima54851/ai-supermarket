name: webhook-dispatcher
description: Connect AI agents to external services via webhooks. Route events, transform payloads, and trigger automations in n8n or other platforms.
---

# Webhook Dispatcher Skill

## PURPOSE
Route AI agent events to external services (webhooks, APIs, n8n workflows) with auth, retries, and logging.

## WHEN TO USE
- "When I finish a task, notify me via Telegram"
- "Route GitHub events to n8n for processing"
- "Connect my AI agent to external APIs"
- "Build a webhook gateway for my agent"

## HOW IT WORKS
```
AI Agent → webhook_dispatcher.py → n8n / Telegram / Email / Slack
```

## EXAMPLE CONFIG (dispatch.json)
```json
{
  "routes": [
    {
      "path": "/ai/event",
      "targets": ["http://localhost:5678/webhook/ai-events"],
      "auth": "your-n8n-api-key",
      "log": true
    }
  ],
  "port": 8080
}
```

## RUN
```bash
python3 scripts/webhook_dispatcher.py
# Listens on :8080
# POST /ai/event → forwards to all configured targets
```

## USE WITH N8N
1. Create n8n workflow with Webhook trigger
2. Set webhook URL: `http://YOUR_SERVER:8080/ai/event`
3. Agent calls the dispatcher → dispatcher forwards to n8n
