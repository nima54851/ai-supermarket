#!/usr/bin/env python3
"""
model_gateway.py — 统一 LLM 网关
支持模型路由、熔断降级、限流、负载均衡、Token 计数
"""

import json
import time
import uuid
import threading
import argparse
from dataclasses import dataclass, field
from typing import Callable
from datetime import datetime, timedelta

try:
    import openai
    import anthropic
    HAS_LLM = True
except ImportError:
    HAS_LLM = False


@dataclass
class ModelRoute:
    name: str
    provider: str  # openai | anthropic | ollama
    base_url: str | None = None
    api_key: str | None = None
    model: str = ""
    max_rpm: int = 60  # requests per minute
    enabled: bool = True


@dataclass
class RequestLog:
    req_id: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    status: str = "ok"
    cost_usd: float = 0.0
    ts: str = ""


# Token pricing (per 1M tokens)
TOKEN_PRICES = {
    "gpt-4o": (2.5, 10.0),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.0, 30.0),
    "claude-3-5-sonnet": (3.0, 15.0),
    "claude-3-haiku": (0.25, 1.25),
    "llama3": (0.0, 0.0),  # self-hosted
}


class RateLimiter:
    def __init__(self, rpm: int):
        self.rpm = rpm
        self.window = timedelta(minutes=1)
        self.requests: list[datetime] = []
        self.lock = threading.Lock()

    def allow(self) -> bool:
        now = datetime.utcnow()
        with self.lock:
            self.requests = [t for t in self.requests if now - t < self.window]
            if len(self.requests) < self.rpm:
                self.requests.append(now)
                return True
            return False


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure: datetime | None = None
        self.state = "closed"  # closed | open | half-open
        self.lock = threading.Lock()

    def record_success(self):
        with self.lock:
            self.failures = 0
            self.state = "closed"

    def record_failure(self):
        with self.lock:
            self.failures += 1
            self.last_failure = datetime.utcnow()
            if self.failures >= self.failure_threshold:
                self.state = "open"

    def allow(self) -> bool:
        with self.lock:
            if self.state == "closed":
                return True
            if self.state == "open" and self.last_failure:
                if datetime.utcnow() - self.last_failure > timedelta(seconds=self.recovery_timeout):
                    self.state = "half-open"
                    return True
            return False


class LLMGateway:
    def __init__(self, routes: list[ModelRoute], fallback: str):
        self.routes = {r.name: r for r in routes}
        self.fallback = fallback
        self.limiters = {r.name: RateLimiter(r.max_rpm) for r in routes}
        self.breakers = {r.name: CircuitBreaker() for r in routes}
        self.logs: list[RequestLog] = []
        self.log_lock = threading.Lock()
        self.cost_lock = threading.Lock()
        self.total_cost_usd = 0.0

    def call(self, model: str, messages: list[dict], **kwargs) -> dict:
        req_id = str(uuid.uuid4())[:8]
        start = time.time()

        # Select route
        route = self.routes.get(model)
        if not route or not route.enabled:
            route = self.routes.get(self.fallback)
        if not route:
            return {"error": "No available model", "req_id": req_id}

        # Rate limit check
        if not self.limiters[route.name].allow():
            return {"error": "Rate limit exceeded", "req_id": req_id, "status": 429}

        # Circuit breaker check
        if not self.breakers[route.name].allow():
            return {"error": "Circuit breaker open", "req_id": req_id, "status": 503}

        try:
            result = self._call_provider(route, messages, **kwargs)
            self.breakers[route.name].record_success()
            elapsed_ms = int((time.time() - start) * 1000)

            # Estimate tokens
            in_tok = result.get("usage", {}).get("prompt_tokens", 0)
            out_tok = result.get("usage", {}).get("completion_tokens", 0)
            cost = self._estimate_cost(route.model, in_tok, out_tok)

            with self.cost_lock:
                self.total_cost_usd += cost

            log = RequestLog(req_id, route.name, in_tok, out_tok, elapsed_ms, "ok", cost)
            log.ts = datetime.utcnow().isoformat()
            with self.log_lock:
                self.logs.append(log)

            return {"req_id": req_id, "model": route.model, "response": result, "cost_usd": cost}
        except Exception as e:
            self.breakers[route.name].record_failure()
            elapsed_ms = int((time.time() - start) * 1000)
            log = RequestLog(req_id, route.name, status=f"error: {e}", latency_ms=elapsed_ms)
            log.ts = datetime.utcnow().isoformat()
            with self.log_lock:
                self.logs.append(log)
            return {"error": str(e), "req_id": req_id, "status": 500}

    def _call_provider(self, route: ModelRoute, messages: list[dict], **kwargs):
        if route.provider == "openai":
            client = openai.OpenAI(api_key=route.api_key, base_url=route.base_url)
            resp = client.chat.completions.create(model=route.model, messages=messages, **kwargs)
            return {"content": resp.choices[0].message.content, "usage": resp.usage.model_dump()}
        elif route.provider == "anthropic":
            client = anthropic.Anthropic(api_key=route.api_key, base_url=route.base_url)
            system = kwargs.pop("system", None)
            resp = client.messages.create(model=route.model, system=system, messages=messages, **kwargs)
            return {"content": resp.content[0].text, "usage": {"prompt_tokens": resp.usage.input_tokens, "completion_tokens": resp.usage.output_tokens}}
        else:
            raise NotImplementedError(f"Provider {route.provider} not supported")

    def _estimate_cost(self, model: str, in_tok: int, out_tok: int) -> float:
        key = model.lower()
        for k, (in_p, out_p) in TOKEN_PRICES.items():
            if k in key:
                return in_tok / 1_000_000 * in_p + out_tok / 1_000_000 * out_p
        return 0.0

    def stats(self) -> dict:
        with self.log_lock:
            logs = self.logs[-100:]
        total = len(logs)
        errors = sum(1 for l in logs if l.status != "ok")
        avg_latency = sum(l.latency_ms for l in logs) / max(total, 1)
        with self.cost_lock:
            cost = self.total_cost_usd
        return {
            "total_requests": total,
            "errors": errors,
            "error_rate": errors / max(total, 1),
            "avg_latency_ms": avg_latency,
            "total_cost_usd": cost,
            "circuit_breakers": {n: {"state": b.state, "failures": b.failures} for n, b in self.breakers.items()},
        }


def main():
    p = argparse.ArgumentParser(description="LLM Model Gateway")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--routes", default="openai,anthropic")
    p.add_argument("--fallback", default="ollama")
    args = p.parse_args()

    routes = [
        ModelRoute("openai", "openai", model="gpt-4o-mini", api_key=""),
        ModelRoute("anthropic", "anthropic", model="claude-3-haiku", api_key=""),
    ]

    gateway = LLMGateway(routes, args.fallback)
    print(f"🚀 LLM Gateway running on :{args.port}")
    print(f"   Routes: {list(gateway.routes.keys())}")
    print(f"   Fallback: {args.fallback}")
    print(f"\n   Endpoints:")
    print(f"   POST /v1/chat  → Call LLM")
    print(f"   GET  /stats   → Gateway stats")
    print(f"\n   Press Ctrl+C to stop")

    try:
        import http.server, socketserver, urllib.parse
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path == "/v1/chat":
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = json.loads(self.rfile.read(content_len))
                    model = body.get("model", "openai")
                    messages = body.get("messages", [])
                    result = gateway.call(model, messages)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_GET(self):
                if self.path == "/stats":
                    stats = gateway.stats()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(stats, indent=2).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, fmt, *args):
                pass  # silence default logging

        with socketserver.TCPServer(("", args.port), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Gateway stopped")


if __name__ == "__main__":
    main()
