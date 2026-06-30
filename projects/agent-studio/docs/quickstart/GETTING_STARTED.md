# Agent Studio Quickstart

> Get up and running with agent-studio in 5 minutes

## 🚀 Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nima54851/agent-studio.git
cd agent-studio
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Your API Keys

Create a `.env` file:

```bash
GITHUB_TOKEN=ghp_your_token_here
OPENAI_API_KEY=sk-your-key-here
N8N_URL=http://localhost:5678
```

### 4. Start n8n

```bash
docker-compose up -d
# or: n8n start
```

### 5. Import a Workflow

Import any workflow from `workflows/` into your n8n instance:
- Navigate to n8n → Settings → Import from File
- Select a workflow JSON

## 📂 What's Included

| Directory | Description |
|---|---|
| `workflows/` | Ready-to-use n8n workflows |
| `skills/` | OpenClaw-compatible AI agent skills |
| `scripts/` | Automation scripts |
| `products/` | Ready-to-sell product packages |
| `integrations/` | Third-party integrations (Discord, Telegram) |
| `docker/` | Docker deployment configs |

## 🔥 Start with a Template

### GitHub AI Digest (Daily Automation)
```bash
python3 daily_ops.py
```

### Deploy with Docker
```bash
cd docker && docker-compose up -d
```

## 📚 Next Steps

- Read `README.md` for full documentation
- Check `products/` for monetization-ready packages
- Join discussions on the GitHub repo

## 💡 Tips

- **Self-hosting**: See `docker/` for full stack setup
- **Customization**: Edit `skills/*.md` to customize agent behavior
- **Sales**: Products in `products/` are ready to sell on Gumroad
