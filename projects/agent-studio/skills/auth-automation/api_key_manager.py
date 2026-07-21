#!/usr/bin/env python3
"""
API Key Manager — generate, verify, revoke API keys with Redis backend.
Usage: python api_key_manager.py [generate|verify|revoke|list] <args>
"""

import hashlib
import secrets
import json
import redis
import os
from datetime import datetime, timedelta
from typing import Optional

PREFIX = "apikey"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))


def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def generate_key(user_id: str, name: str, expires_days: int = 365, rate_limit: str = "100/hour") -> dict:
    """Generate a new API key. Returns metadata including the plain key (show only once!)."""
    r = get_redis()
    plain_key = f"ask_{secrets.token_urlsafe(32)}"
    hashed = hashlib.sha256(plain_key.encode()).hexdigest()
    key_id = secrets.token_hex(8)

    ttl = expires_days * 86400
    r.hset(f"{PREFIX}:{hashed}", mapping={
        "user_id": user_id,
        "name": name,
        "key_id": key_id,
        "created": datetime.utcnow().isoformat(),
        "expires": (datetime.utcnow() + timedelta(days=expires_days)).isoformat(),
        "rate_limit": rate_limit,
        "active": "true"
    })
    r.expire(f"{PREFIX}:{hashed}", ttl)

    return {
        "plain_key": plain_key,
        "key_id": key_id,
        "hashed": hashed[:16] + "...",
        "user_id": user_id,
        "name": name,
        "rate_limit": rate_limit,
        "expires_in_days": expires_days,
        "warning": "⚠️ Save this key now — it cannot be retrieved again!"
    }


def verify_key(plain_key: str) -> Optional[dict]:
    """Verify an API key and return its metadata. Returns None if invalid."""
    r = get_redis()
    hashed = hashlib.sha256(plain_key.encode()).hexdigest()
    data = r.hgetall(f"{PREFIX}:{hashed}")

    if not data:
        return None

    if data.get("active") != "true":
        return {"valid": False, "reason": "Key is deactivated"}

    return {
        "valid": True,
        "key_id": data.get("key_id"),
        "user_id": data.get("user_id"),
        "name": data.get("name"),
        "created": data.get("created"),
        "rate_limit": data.get("rate_limit")
    }


def check_rate_limit(plain_key: str, limit: str = None) -> dict:
    """Check and increment rate limit. Returns {allowed: bool, remaining: int}."""
    r = get_redis()
    hashed = hashlib.sha256(plain_key.encode()).hexdigest()

    if limit is None:
        data = r.hgetall(f"{PREFIX}:{hashed}")
        limit = data.get("rate_limit", "100/hour")

    limit_amount, limit_period = limit.split("/")
    limit_amount = int(limit_amount)
    period_seconds = {"minute": 60, "hour": 3600, "day": 86400}.get(limit_period, 3600)

    key = f"{PREFIX}:rl:{hashed}"
    current = r.incr(key)

    if current == 1:
        r.expire(key, period_seconds)

    return {
        "allowed": current <= limit_amount,
        "remaining": max(0, limit_amount - current),
        "limit": limit_amount,
        "period": limit_period,
        "reset_in_seconds": r.ttl(key)
    }


def revoke_key(plain_key: str) -> bool:
    """Revoke an API key immediately."""
    r = get_redis()
    hashed = hashlib.sha256(plain_key.encode()).hexdigest()
    return r.delete(f"{PREFIX}:{hashed}") > 0


def list_keys(user_id: str) -> list:
    """List all API keys for a user (metadata only, no plain keys)."""
    r = get_redis()
    keys = []
    cursor = 0
    while True:
        cursor, key_list = r.scan(cursor=cursor, match=f"{PREFIX}:*", count=100)
        for key in key_list:
            if key.startswith(f"{PREFIX}:rl:"):
                continue
            data = r.hgetall(key)
            if data.get("user_id") == user_id:
                keys.append({
                    "key_id": data.get("key_id"),
                    "name": data.get("name"),
                    "created": data.get("created"),
                    "expires": data.get("expires"),
                    "active": data.get("active") == "true",
                    "rate_limit": data.get("rate_limit")
                })
        if cursor == 0:
            break
    return keys


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "generate":
        user_id = sys.argv[2] or "default_user"
        name = sys.argv[3] or "Default Key"
        result = generate_key(user_id, name)
        print("✅ API Key Generated!")
        print(json.dumps(result, indent=2))

    elif cmd == "verify":
        key = sys.argv[2]
        result = verify_key(key)
        print(json.dumps(result, indent=2))

    elif cmd == "revoke":
        key = sys.argv[2]
        success = revoke_key(key)
        print(f"{'✅ Revoked' if success else '❌ Not found'}")

    elif cmd == "list":
        user_id = sys.argv[2] or "default_user"
        keys = list_keys(user_id)
        print(json.dumps(keys, indent=2))

    else:
        print("Usage:")
        print("  python api_key_manager.py generate <user_id> <name>")
        print("  python api_key_manager.py verify <plain_key>")
        print("  python api_key_manager.py revoke <plain_key>")
        print("  python api_key_manager.py list <user_id>")
