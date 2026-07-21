#!/usr/bin/env python3
"""
Sentry Webhook Handler
Receives Sentry webhook events and forwards to n8n for processing.
"""
import json
import hmac
import hashlib
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

SENTRY_SIGNING_SECRET = os.getenv("SENTRY_SIGNING_SECRET", "")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/sentry-alert")

def verify_sentry_signature(payload: bytes, signature: str) -> bool:
    if not SENTRY_SIGNING_SECRET:
        return True
    computed = hmac.new(
        SENTRY_SIGNING_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={computed}", signature)

@app.route("/webhook", methods=["POST"])
def handle_sentry():
    if not verify_sentry_signature(request.data, request.headers.get("Sentry-Signature", "")):
        return jsonify({"error": "Invalid signature"}), 401
    
    event = request.json
    print(f"[Sentry] Event: {event.get('event', {}).get('title', 'unknown')}")
    
    # Forward to n8n
    try:
        import urllib.request
        data = json.dumps(event).encode()
        req = urllib.request.Request(
            N8N_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[Sentry] Forward failed: {e}")
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
