# WhatsApp AI Agent Bot

> Receive WhatsApp messages → route to OpenClaw AI agent → reply via WhatsApp.
> Powered by n8n + WhatsApp Business API (Twilio or 360dialog).

## Architecture

```
WhatsApp Message (incoming)
  → Twilio / 360dialog Webhook
    → n8n HTTP Request Node
      → OpenClaw Agent (AI processing)
        → n8n responds to Twilio
          → WhatsApp reply delivered
```

## Prerequisites

- WhatsApp Business Account
- Twilio account with WhatsApp sandbox OR 360dialog account
- n8n instance (see `docker/` in agent-studio)
- OpenClaw agent with the `customer-support-automation` skill

## n8n Workflow

Import `whatsapp-ai-bot.json` into n8n:

```
1. Webhook (POST) — receives Twilio webhook
2. Code Node — parse incoming WhatsApp message
3. HTTP Request — send to OpenClaw agent API
4. Code Node — extract AI response
5. Twilio Node — send reply via WhatsApp
```

## Quick Setup

### 1. Configure Twilio WhatsApp Sandbox

```bash
# In your Twilio Console:
# Messaging → Senders → WhatsApp → Sandbox
# Set webhook URL to your n8n endpoint:
# https://your-n8n.example.com/webhook/whatsapp-ai
```

### 2. Import n8n Workflow

```
n8n → Workflows → Import from JSON → upload whatsapp-ai-bot.json
```

### 3. Set Environment Variables in n8n

| Variable | Value |
|----------|-------|
| `OPENCLAW_WEBHOOK_URL` | `http://your-openclaw:5678/webhook/your-agent` |
| `OPENCLAW_API_KEY` | Your OpenClaw API key |
| `TWILIO_AUTH_TOKEN` | From Twilio Console |
| `DEFAULT_REPLY` | `Thanks! A team member will respond shortly.` |

### 4. Activate the Workflow

n8n → Toggle workflow → set to Active

## Customization

### Route by keyword

Add a Switch node after the webhook:

| Keyword | Destination |
|---------|------------|
| `order` | Order status agent |
| `support` | Customer support agent |
| `sales` | Sales agent |
| `*` (default) | General AI assistant |

### Add conversation memory

Use n8n's Redis or Postgres nodes to store conversation history:

```
WhatsApp → Store to Redis (key: wa:{phone}) 
  → OpenClaw (with conversation context)
    → Reply → Update Redis
```

### Multi-language support

Add a Code node before the OpenClaw call to detect language and prepend context:

```javascript
const lang = detectLanguage($json.body);
$input.first().json.lang = lang;
$input.first().json.systemPrompt = `Reply in ${lang}. Context: ${conversationHistory}`;
```

## Files

```
whatsapp-bot/
├── README.md              ← This file
├── whatsapp-ai-bot.json   ← n8n workflow (import this)
└── twilio-setup.md        ← Detailed Twilio configuration guide
```

## Limitations

- WhatsApp Business API has rate limits (~100 msgs/min for sandbox)
- OpenAI/Claude API latency affects response time (typically 2–10s)
- For production: use a message queue (RabbitMQ/Redis) to handle spikes

---

*Part of [agent-studio](https://github.com/nima54851/agent-studio) · Built with 灵犀 AI*
