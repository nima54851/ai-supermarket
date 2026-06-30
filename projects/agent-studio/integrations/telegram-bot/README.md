# Telegram Bot Integration Template

> One-click n8n workflow template for building AI-powered Telegram bots.

## 🤖 What It Does

```
User message → Telegram Webhook → AI Agent → Response → Telegram
                    ↓
              PostgreSQL (store conversation)
                    ↓
              Memory (context for next turn)
```

## 🔑 Prerequisites

1. Create a bot via [@BotFather](https://t.me/BotFather) → get your `BOT_TOKEN`
2. Get your Chat ID via [@userinfobot](https://telegram.me/userinfobot)
3. n8n instance (local or cloud)
4. Optional: OpenAI API key for AI responses

## 📥 Import to n8n

1. Open n8n → **Workflows** → **Import from JSON**
2. Paste the content of `telegram-ai-bot.json`
3. Configure credentials:
   - Telegram Bot API: `BOT_TOKEN`
   - OpenAI (optional): `OPENAI_API_KEY`
   - PostgreSQL (optional): connection string
4. Activate the workflow

## ⚙️ Environment Variables

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=sk-your-key-here
POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/db
```

## 🧩 Key Features

| Feature | Description |
|---------|-------------|
| **AI Responses** | GPT-powered replies with conversation context |
| **Memory** | Remembers previous messages per user |
| **Command Support** | `/start`, `/help`, `/status`, `/reset` |
| **Logging** | All messages stored in PostgreSQL |
| **Rate Limiting** | Prevents bot spam (5 msg/min per user) |
| **Error Handling** | Graceful fallback on API failures |

## 📁 Files

```
telegram-bot/
├── telegram-ai-bot.json     # n8n workflow (import this)
├── telegram-bot-handler.js   # Custom code node
├── README.md                 # This file
└── commands/
    ├── start.js              # /start handler
    ├── help.js               # /help handler
    └── reset.js              # /reset handler
```

## 🧪 Test Your Bot

1. Send `/start` → bot greets you
2. Ask a question → AI responds
3. Send `/status` → shows your session info
4. Send `/reset` → clears conversation history

## 🔒 Security

- Validate Telegram hash on every request
- Store tokens in n8n credential store, never in workflow
- Rate limit all incoming messages
- Log access for audit trail

---

*Part of [agent-studio](https://github.com/nima54851/agent-studio) · Built by 灵犀 AI*
