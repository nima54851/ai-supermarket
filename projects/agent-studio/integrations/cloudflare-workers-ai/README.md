# Cloudflare Workers AI Integration

Deploy your AI agent on Cloudflare's global edge network.

## Quick Links

- **Skill:** [`../skills/cloudflare-workers-ai/SKILL.md`](../skills/cloudflare-workers-ai/SKILL.md)
- **Wrangler CLI:** https://developers.cloudflare.com/workers/wrangler
- **Workers AI Models:** https://developers.cloudflare.com/workers-ai/

## What's Included

| File | Purpose |
|------|---------|
| `wrangler.toml` | Workers config, KV namespace, AI binding |
| `src/index.ts` | Entry point |
| `src/agent.ts` | OpenClaw agent wrapper with memory |
| `src/router.ts` | REST API router |
| `src/middleware.ts` | Rate limiting + logging |
| `src/auth.ts` | API key / JWT authentication |
| `scripts/deploy.sh` | One-command deploy |
| `scripts/local-test.sh` | Local development |

## Architecture

```
User Request
    ↓
Cloudflare Edge (全球节点)
    ↓
Workers AI (Llama 3 / Mistral / SDXL)
    ↓
KV Namespace (Agent Memory)
    ↓
Response (<50ms cold start)
```

## Setup Steps

```bash
# 1. Install Wrangler
npm install -g wrangler

# 2. Authenticate
wrangler login

# 3. Create KV namespace for agent memory
wrangler kv:namespace create AGENT_MEMORY

# 4. Copy config
cp wrangler.toml.example wrangler.toml
# Fill in your ACCOUNT_ID and KV namespace ID

# 5. Deploy
wrangler deploy

# 6. Add custom domain (optional)
wrangler routes update --zone-name yourdomain.com
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MODEL` | Workers AI model | `@cf/meta/llama-3-8b-instruct` |
| `MAX_TOKENS` | Max response length | `2048` |
| `API_KEY` | Access key | `ck_xxxx...` |

Set via `wrangler secret put` (never commit to git):
```bash
wrangler secret put API_KEY
```

## Live Example

```typescript
// Call your deployed agent
const response = await fetch('https://agent.yourdomain.com/v1/chat', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Hello, deploy my agent to the edge!' }
    ],
  }),
});

const { content, usage } = await response.json();
console.log(content);
```

## Pricing Notes

- **Workers AI:** ~$0.01 / 1K tokens
- **Workers Compute:** $0.30 / million requests
- **KV Reads:** $0.00 / 1M (class A), $0.00 / 1M (class B)
- **Free tier:** 100K requests/day, 10K AI tokens/day

---

*Zero cold starts. Global edge. Serverless AI.*
