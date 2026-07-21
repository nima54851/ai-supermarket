# Auth Automation

> JWT, OAuth 2.0, API Keys, session management — automated auth patterns for AI agents and workflows.

## Overview

This skill provides complete authentication patterns for AI agent systems:
- **JWT tokens** — issuance, verification, refresh
- **OAuth 2.0** — Google, GitHub, Discord, custom OAuth flows
- **API Key auth** — generation, storage, validation
- **Session management** — Redis-backed sessions, rate limiting

## What's Included

- `SKILL.md` — this file
- `n8n-auth-workflow.json` — auth patterns n8n workflow
- `jwt_handler.py` — JWT issuance & verification
- `oauth_flow.py` — OAuth 2.0 flow automation
- `api_key_manager.py` — API key lifecycle management

## Architecture

```
User → Auth Request → [JWT / OAuth / API Key]
                         ↓
                   Validation Layer
                         ↓
            ┌────────────┼────────────┐
         Redis      Database     Memory
       (sessions)   (API keys)   (tokens)
                         ↓
                   AI Agent / API
```

## JWT Implementation

```python
# jwt_handler.py
import jwt
import time
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: str, metadata: dict = None) -> str:
    """Create a short-lived access token."""
    payload = {
        "sub": user_id,
        "type": "access",
        "iat": int(time.time()),
        "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "metadata": metadata or {}
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token."""
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": int(time.time()),
        "exp": int(time.time()) + REFRESH_TOKEN_EXPIRE_DAYS * 86400
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token. Raises jwt.ExpiredSignatureError on expiry."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def refresh_access_token(refresh_token: str) -> str:
    """Exchange a valid refresh token for a new access token."""
    payload = verify_token(refresh_token)
    if payload["type"] != "refresh":
        raise ValueError("Not a refresh token")
    return create_access_token(payload["sub"], payload.get("metadata"))


def require_auth(func):
    """Decorator to protect endpoints with JWT auth."""
    from functools import wraps
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise PermissionError("Missing Bearer token")
        token = auth_header.split(" ", 1)[1]
        payload = verify_token(token)
        request.user_id = payload["sub"]
        return func(request, *args, **kwargs)
    return wrapper
```

## OAuth 2.0 Flow

```python
# oauth_flow.py
import hashlib
import secrets
import time

# OAuth Provider Configs
OAUTH_CONFIGS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scopes": ["openid", "email", "profile"]
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scopes": ["user:email", "read:user"]
    }
}


class OAuthFlow:
    """Automates OAuth 2.0 Authorization Code flow."""

    def __init__(self, provider: str):
        self.provider = provider
        self.config = OAUTH_CONFIGS[provider]
        self.state_store = {}  # In production: Redis

    def get_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate the OAuth authorization URL."""
        state = state or secrets.token_urlsafe(32)
        self.state_store[state] = {"created": time.time(), "redirect_uri": redirect_uri}

        params = {
            "client_id": self.config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.config["scopes"]),
            "response_type": "code",
            "state": state
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.config['auth_url']}?{query}"

    def exchange_code(self, code: str, redirect_uri: str, state: str = None) -> dict:
        """Exchange authorization code for access token."""
        # Validate state
        if state and state not in self.state_store:
            raise ValueError("Invalid state parameter")
        if state:
            del self.state_store[state]

        response = requests.post(self.config["token_url"], data={
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }, headers={"Accept": "application/json"})

        return response.json()

    def get_user_info(self, access_token: str) -> dict:
        """Fetch user profile from OAuth provider."""
        resp = requests.get(
            self.config["userinfo_url"],
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return resp.json()


# n8n webhook: /webhook/oauth/{provider}/callback
# This node handles the OAuth callback in n8n workflow
OAUTH_CALLBACK_WORKFLOW = {
    "description": "OAuth callback handler — stores tokens in Redis, creates user session",
    "steps": [
        "1. OAuth Callback node (code: extract code + state)",
        "2. Exchange code → access_token",
        "3. Fetch user profile",
        "4. Create/update user in DB",
        "5. Create session in Redis (TTL: 7 days)",
        "6. Redirect to frontend with session cookie"
    ]
}
```

## API Key Management

```python
# api_key_manager.py
import hashlib
import secrets
import redis
from datetime import datetime, timedelta

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

PREFIX = "apikey"


def generate_api_key(user_id: str, name: str, expires_in_days: int = 365) -> tuple[str, str]:
    """Generate a new API key. Returns (plain_key, hashed_key). Store only the hash!"""
    plain_key = f"ask_{secrets.token_urlsafe(32)}"
    hashed_key = hashlib.sha256(plain_key.encode()).hexdigest()
    key_id = secrets.token_hex(8)

    ttl = expires_in_days * 86400
    redis_client.hset(f"{PREFIX}:{hashed_key}", mapping={
        "user_id": user_id,
        "name": name,
        "key_id": key_id,
        "created": datetime.utcnow().isoformat(),
        "rate_limit": "100/hour"
    })
    redis_client.expire(f"{PREFIX}:{hashed_key}", ttl)

    return plain_key, hashed_key


def verify_api_key(plain_key: str) -> dict | None:
    """Verify an API key and return its metadata."""
    hashed_key = hashlib.sha256(plain_key.encode()).hexdigest()
    data = redis_client.hgetall(f"{PREFIX}:{hashed_key}")
    return data if data else None


def revoke_api_key(plain_key: str) -> bool:
    """Revoke an API key immediately."""
    hashed_key = hashlib.sha256(plain_key.encode()).hexdigest()
    return redis_client.delete(f"{PREFIX}:{hashed_key}") > 0


def rate_limit_key(plain_key: str, limit: str = "100/hour") -> bool:
    """Check rate limit. Returns True if allowed, False if exceeded."""
    key = f"{PREFIX}:ratelimit:{plain_key}"
    limit_amount, limit_period = limit.split("/")
    limit_amount = int(limit_amount)

    current = redis_client.incr(key)
    if current == 1:
        period_seconds = {"minute": 60, "hour": 3600, "day": 86400}[limit_period]
        redis_client.expire(key, period_seconds)

    return current <= limit_amount
```

## n8n Auth Workflow

```json
{
  "name": "Auth Patterns Workflow",
  "nodes": [
    {
      "name": "Auth Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "auth",
        "method": "POST"
      }
    },
    {
      "name": "Route Auth Type",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "dataType": "string",
        "value1": "={{ $json.body.auth_type }}",
        "rules": {
          "rules": [
            {"value2": "jwt", "output": 0},
            {"value2": "oauth", "output": 1},
            {"value2": "apikey", "output": 2}
          ]
        },
        "fallbackOutput": 3
      }
    },
    {
      "name": "JWT Verify",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Verify JWT and extract user_id\n// Replace with actual jwt.verify() call\nconst token = $json.body.token;\nreturn [{ json: { valid: true, user_id: 'user_123' } }];"
      }
    },
    {
      "name": "OAuth Initiate",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "=https://github.com/login/oauth/authorize?client_id={{ $env.GITHUB_CLIENT_ID }}&scope=read:user&redirect_uri={{ $json.body.redirect_uri }}"
      }
    },
    {
      "name": "API Key Verify",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Verify API key via Redis\n// const keyData = redis.hgetall('apikey:' + sha256(api_key));\nreturn [{ json: { valid: true, user_id: 'user_456', rate_limit: '100/hour' } }];"
      }
    },
    {
      "name": "Return Unauthorized",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "respondWith": "json",
        "responseBody": "{\"error\": \"Unauthorized\", \"statusCode\": 401}"
      }
    }
  ]
}
```

## Security Best Practices

1. **Never store plain-text API keys** — hash with SHA-256 before storage
2. **Use short-lived JWTs** — 15-30 min for access tokens, rotate via refresh tokens
3. **Rate limit all auth endpoints** — especially token exchange and password reset
4. **Store secrets in environment variables** — never in code
5. **Use HTTPS everywhere** — OAuth redirects should always be HTTPS
6. **Validate state parameter in OAuth** — prevents CSRF attacks
7. **Rotate secrets regularly** — automate rotation with n8n

## See Also

- `skills/self-hosted-ai/` — deploy auth-protected services locally
- `skills/security-auditor/` — scan for leaked API keys and secrets
- `skills/monitoring-alerting-automation/` — auth failure alerting
