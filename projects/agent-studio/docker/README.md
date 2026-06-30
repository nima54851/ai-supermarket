# 🐳 Docker Deployment Guide

> Zero-config Docker setup for agent-studio workflows and services.

## 📦 Quick Start

```bash
git clone https://github.com/nima54851/agent-studio.git
cd agent-studio
docker compose up -d
```

## 🏗️ What's Included

| Service | Port | Description |
|---------|------|-------------|
| n8n | 5678 | Workflow automation engine |
| PostgreSQL | 5432 | Data storage |
| Redis | 6379 | Caching & job queue |
| Traefik | 80/443 | Reverse proxy + SSL |

## 📁 Structure

```
.
├── docker-compose.yml      # Main orchestration
├── Dockerfile.agent        # Agent runtime image
├── Dockerfile.n8n-custom   # Custom n8n with plugins
├── .env.example            # Environment template
└── scripts/
    └── deploy.sh           # One-command deploy
```

## 🔧 Environment Variables

```bash
cp .env.example .env
# Edit .env with your credentials:
# GITHUB_TOKEN=ghp_xxx
# OPENAI_API_KEY=sk-xxx
# N8N_BASIC_AUTH_ACTIVE=true
# N8N_BASIC_AUTH_USER=admin
# N8N_BASIC_AUTH_PASSWORD=your-secure-password
```

## 🚀 Deploy Steps

```bash
# 1. Clone & enter
git clone https://github.com/nima54851/agent-studio.git
cd agent-studio

# 2. Configure
cp .env.example .env
nano .env  # fill in your keys

# 3. Start services
docker compose up -d

# 4. Check status
docker compose ps

# 5. View logs
docker compose logs -f n8n
```

## 🌐 Access Points

- **n8n Dashboard:** http://localhost:5678
- **Health Check:** http://localhost:5678/healthz

## 🔒 Security Notes

- Change default passwords in `.env`
- Use secrets management in production
- Never commit `.env` to git
- Enable HTTPS in production (Traefik auto-configures with valid domain)

## 🧹 Stop & Clean

```bash
docker compose down          # Stop services
docker compose down -v       # Stop + remove volumes
docker compose down --rmi local  # Stop + remove images
```

## 🔄 Update

```bash
git pull
docker compose pull
docker compose up -d
```

---

*Part of [agent-studio](https://github.com/nima54851/agent-studio) · Built by 灵犀 AI*
