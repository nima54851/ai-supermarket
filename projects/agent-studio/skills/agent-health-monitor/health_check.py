#!/usr/bin/env python3
"""
Agent Health Monitor — 监控 agent 服务健康状态，支持 webhook 上报
"""

import argparse
import json
import time
import urllib.request
import urllib.error
import os
from datetime import datetime

def check_endpoint(url: str, timeout: int = 10) -> dict:
    """检查 HTTP 端点健康状态"""
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "agent-health-monitor/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = (time.time() - start) * 1000
            return {
                "status": "up",
                "code": resp.status,
                "latency_ms": round(elapsed, 1),
                "timestamp": datetime.utcnow().isoformat()
            }
    except urllib.error.HTTPError as e:
        return {"status": "down", "code": e.code, "error": str(e), "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"status": "down", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

def send_alert(result: dict, webhook_url: str):
    """发送告警到 webhook"""
    payload = json.dumps({
        "text": f"🚨 Agent Health Alert: {result['status'].upper()} — {result.get('error', 'OK')}",
        "result": result
    }).encode()
    req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5):
            print("✅ Alert sent")
    except Exception as e:
        print(f"⚠️ Failed to send alert: {e}")

def main():
    parser = argparse.ArgumentParser(description="Agent Health Monitor")
    parser.add_argument("--service", default=os.getenv("HEALTH_ENDPOINT", "http://localhost:5678"))
    parser.add_argument("--threshold", type=int, default=int(os.getenv("ALERT_THRESHOLD_MS", "1000")))
    parser.add_argument("--webhook-url", default=os.getenv("ALERT_WEBHOOK", ""))
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Checking {args.service}...")
    result = check_endpoint(args.service, args.timeout)
    print(f"Result: {json.dumps(result, indent=2)}")

    is_alert = result["status"] == "down" or result.get("latency_ms", 0) > args.threshold
    if is_alert and args.webhook_url:
        send_alert(result, args.webhook_url)

    # 记录到日志
    log_path = "/tmp/health_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps({"service": args.service, **result}) + "\n")

    exit(0 if not is_alert else 1)

if __name__ == "__main__":
    main()
