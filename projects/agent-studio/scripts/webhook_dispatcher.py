#!/usr/bin/env python3
"""
Webhook Dispatcher
Listens on a local port and dispatches events to configured endpoints.
Used for connecting AI agents to external services via n8n webhooks.
"""
import json, os, hashlib, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

CONFIG_FILE = os.environ.get("DISPATCH_CONFIG", "dispatch.json")

DEFAULT_CONFIG = {
    "routes": [
        {
            "path": "/ai/event",
            "targets": ["http://localhost:5678/webhook/ai-events"],
            "auth": None,
            "log": True
        }
    ],
    "port": 8080,
    "timeout": 10
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return DEFAULT_CONFIG

def forward_request(url, payload, auth=None):
    """Forward payload to target URL"""
    import requests as req
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    try:
        r = req.post(url, json=payload, headers=headers, timeout=10)
        return r.status_code, r.text[:200]
    except Exception as e:
        return 0, str(e)

class DispatchHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[dispatch] {args[0]}")

    def do_POST(self):
        config = load_config()
        parsed = urlparse(self.path)
        path = parsed.path

        # Read body
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        try:
            payload = json.loads(body) if body else {}
        except:
            payload = {"raw": body}

        payload["_meta"] = {
            "received_at": time.time(),
            "source_ip": self.client_address[0],
            "path": path
        }

        # Find route
        route = next((r for r in config.get("routes", []) if r["path"] == path), None)
        if not route:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "route not found"}).encode())
            return

        # Log
        if route.get("log"):
            print(f"[dispatch] {path} → {len(route['targets'])} targets")

        # Forward to all targets
        results = []
        for target in route["targets"]:
            code, resp = forward_request(target, payload, route.get("auth"))
            results.append({"target": target, "status": code, "response": resp})

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"dispatched": len(results), "results": results}).encode())

def run():
    config = load_config()
    port = config.get("port", 8080)
    print(f"[dispatch] Listening on :{port}")
    server = HTTPServer(("0.0.0.0", port), DispatchHandler)
    server.serve_forever()

if __name__ == "__main__":
    run()
