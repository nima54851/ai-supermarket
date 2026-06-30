# SKILL.md — Cloudflare Workers AI Deployment

> Deploy your AI agent to Cloudflare Workers — globally distributed, serverless, edge-native.

## Overview

This skill helps you package and deploy an OpenClaw-compatible AI agent to **Cloudflare Workers**, with:
- ⚡ Sub-50ms cold start globally
- 💰 Pay-per-request pricing (no idle cost)
- 🔒 Built-in DDoS protection & rate limiting
- 🤖 Workers AI inference (Llama 3, Mistral, Stable Diffusion, etc.)
- 🔄 WebSocket support for real-time agent sessions

## What You Get

```
cloudflare-workers-ai/
├── wrangler.toml          # Cloudflare Workers config
├── src/
│   ├── index.ts           # Entry point
│   ├── agent.ts           # OpenClaw agent wrapper
│   ├── router.ts          # HTTP router (REST + WebSocket)
│   ├── auth.ts            # API key / JWT auth
│   └── middleware.ts      # Rate limiting, logging, CORS
├── workers-ai/
│   └── inference.ts       # Workers AI inference client
├── scripts/
│   ├── deploy.sh          # One-command deploy
│   └── local-test.sh      # Local dev with Wrangler
└── README.md
```

## Quick Deploy

```bash
cd cloudflare-workers-ai

# 1. Install Wrangler
npm install -g wrangler

# 2. Login to Cloudflare
wrangler login

# 3. Configure (edit wrangler.toml)
cp wrangler.toml.example wrangler.toml
# Set ACCOUNT_ID, WORKERS_AI_MODEL, etc.

# 4. Deploy
./scripts/deploy.sh
```

## wrangler.toml

```toml
name = "lingxi-agent"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[ai]
binding = "AI"

[[kv_namespaces]]
binding = "AGENT_MEMORY"
id = "<YOUR_KV_ID>"

[vars]
MODEL = "@cf/meta/llama-3-8b-instruct"
MAX_TOKENS = "2048"

[triggers]
routes = [
  { pattern = "agent.yourdomain.com", zone_name = "yourdomain.com" }
]
```

## Entry Point — src/index.ts

```typescript
import { handleRequest } from './router';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return handleRequest(request, env);
  },
};

interface Env {
  AI: Ai;
  AGENT_MEMORY: KVNamespace;
  API_KEY: string;
  MODEL: string;
  MAX_TOKENS: string;
}
```

## HTTP Router — src/router.ts

```typescript
import { authenticate } from './auth';
import { runAgent } from './agent';
import { rateLimit } from './middleware';

export async function handleRequest(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const path = url.pathname;

  // Rate limiting
  const rl = await rateLimit(request, env);
  if (rl) return rl;

  // Auth
  const auth = await authenticate(request, env);
  if (auth.error) {
    return new Response(JSON.stringify(auth), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  switch (path) {
    case '/v1/chat':
      return handleChat(request, env);
    case '/v1/complete':
      return handleComplete(request, env);
    case '/health':
      return new Response(JSON.stringify({ status: 'ok' }), {
        headers: { 'Content-Type': 'application/json' },
      });
    default:
      return new Response('Not Found', { status: 404 });
  }
}
```

## OpenClaw Agent Wrapper — src/agent.ts

```typescript
export async function runAgent(
  messages: ChatMessage[],
  env: Env
): Promise<AgentResponse> {
  // Load agent memory from KV
  const memory = await env.AGENT_MEMORY.get('memory', 'json') || [];

  // Build system prompt with memory
  const systemPrompt = buildSystemPrompt(memory);

  // Call Workers AI
  const response = await env.AI.run(env.MODEL, {
    messages: [
      { role: 'system', content: systemPrompt },
      ...messages,
    ],
    max_tokens: parseInt(env.MAX_TOKENS),
  });

  // Persist memory update
  await persistMemory(messages, response, env);

  return { content: response.response, usage: response.usage };
}

function buildSystemPrompt(memory: any[]): string {
  if (!memory.length) return 'You are a helpful AI agent running on Cloudflare Workers.';
  return `You are a helpful AI agent. Previous context:\n${JSON.stringify(memory.slice(-5))}`;
}
```

## Rate Limiting Middleware — src/middleware.ts

```typescript
export async function rateLimit(request: Request, env: Env): Promise<Response | null> {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const key = `rl:${ip}`;
  const limit = 60; // requests per minute
  const window = 60; // seconds

  const current = await env.AGENT_MEMORY.get(key, 'json') as { count: number; reset: number } | null;
  const now = Date.now();

  if (current && current.reset > now) {
    if (current.count >= limit) {
      return new Response('Rate limit exceeded', {
        status: 429,
        headers: {
          'X-RateLimit-Limit': String(limit),
          'X-RateLimit-Remaining': '0',
          'Retry-After': String(Math.ceil((current.reset - now) / 1000)),
        },
      });
    }
    await env.AGENT_MEMORY.put(key, JSON.stringify({ count: current.count + 1, reset: current.reset }));
  } else {
    await env.AGENT_MEMORY.put(key, JSON.stringify({ count: 1, reset: now + window * 1000 }));
  }

  return null;
}
```

## Workers AI Inference — workers-ai/inference.ts

```typescript
// Use Cloudflare's built-in Workers AI models
// No additional API key needed — it's baked into the platform

export async function chatWithWorkersAI(
  env: Env,
  model: string,
  messages: any[]
): Promise<AIChatResponse> {
  const result = await env.AI.run(model, { messages });
  return result as AIChatResponse;
}

// Available models:
// @cf/meta/llama-3-8b-instruct
// @cf/mistral/mistral-7b-instruct-v0.1
// @cf/openchat/openchat-7b
// @cf/thebloke/deepseek-7b-instruct-q4_K_M
// @cf/stabilityai/stable-diffusion-xl-base-1.0  (image generation)
// @cf/meta/m2m100-1.2b  (translation)
```

## Local Development

```bash
# Start local dev server with Workers AI emulation
./scripts/local-test.sh

# Or manually:
wrangler dev --local
# Visit http://localhost:8787/v1/chat
```

## Monitoring & Logs

```bash
# Tail logs
wrangler tail

# Check deployments
wrangler deployments list

# Analytics via Cloudflare Dashboard
# → Workers & Pages → lingxi-agent → Analytics
```

## Cost Estimation

| Requests | Model | Est. Cost |
|----------|-------|-----------|
| 10,000 | Llama 3 8B | ~$0.10 |
| 100,000 | Llama 3 8B | ~$1.00 |
| 1M | Llama 3 8B | ~$10.00 |

Workers AI pricing: $0.01 / 1K tokens (Llama 3 8B)  
Workers compute: $0.30 / million requests

## Auto-scale to Millions

```bash
# Set concurrency limits (in wrangler.toml)
[limits]
cpu_ms = 50        # Max CPU time per request
memory_mb = 128    # Max memory
subrequests = 100  # Max subrequests

# Enable smart pricing via Workers Analytics
# Budget alert at $50/month
```

---

*Deploy at the edge. Scale to infinity. Pay only for what you use.*
