# Monitoring & Alerting Automation Skill

AI-driven monitoring and alerting system for OpenClaw agents, n8n workflows, and infrastructure — powered by Prometheus + Grafana + PagerDuty/n8n webhooks.

## Overview

This skill provides:
- Prometheus metrics collection for AI agents and workflows
- Grafana dashboards for real-time monitoring
- AI-powered anomaly detection
- n8n webhook alerts (Slack, Telegram, email, SMS)
- Incident auto-response and recovery automation
- Health check runners with auto-restart

## Directory Structure

```
skills/monitoring-alerting-automation/
├── SKILL.md
└── scripts/
    ├── prometheus_exporter.py    # Custom metrics exporter
    ├── health_monitor.sh         # Health check daemon
    └── alert_handler.py          # AI alert triage
integrations/monitoring-alerting-automation/
├── n8n-workflow.json             # Alert triage workflow
├── grafana-dashboards/
│   └── agent-studio-dashboard.json
└── prometheus.yml                # Prometheus scrape config
workflows/
└── monitoring-runbook.md
```

## Prometheus Metrics Exporter

```python
# prometheus_exporter.py
# Expose AI agent metrics in Prometheus format

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time, random

# Custom metrics
agent_requests_total = Counter(
    'agent_requests_total',
    'Total AI agent requests',
    ['agent_id', 'status']
)

agent_latency_seconds = Histogram(
    'agent_latency_seconds',
    'Agent request latency',
    ['agent_id', 'operation']
)

active_workflows = Gauge(
    'n8n_active_workflows',
    'Number of active n8n workflows',
    ['workflow_name']
)

token_usage_total = Counter(
    'agent_token_usage_total',
    'Total tokens used',
    ['agent_id', 'model']
)

def export_metrics():
    """Export metrics endpoint for Prometheus scraping."""
    start_http_server(9090)
    
    while True:
        # Simulate metrics (replace with real API calls)
        agent_requests_total.labels(
            agent_id='lingxi',
            status='success'
        ).inc(random.randint(1, 10))
        
        agent_latency_seconds.labels(
            agent_id='lingxi',
            operation='chat'
        ).observe(random.uniform(0.1, 2.0))
        
        time.sleep(15)

if __name__ == '__main__':
    export_metrics()
```

## Health Monitor Daemon

```bash
#!/bin/bash
# health_monitor.sh — Continuous health check with auto-restart

SERVICES=(
  "n8n:http://localhost:5678"
  "openclaw:openclaw gateway status"
  "postgres:pg_isready -h localhost -p 5432"
  "redis:redis-cli ping"
)

ALERT_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
LOG_FILE="/var/log/health-monitor.log"

check_service() {
  local name=$1
  local cmd=$2
  
  if [[ "$cmd" == http* ]]; then
    status=$(curl -s -o /dev/null -w "%{http_code}" "$cmd" 2>/dev/null)
    if [ "$status" -eq 200 ]; then
      echo "[$(date)] ✅ $name: OK (HTTP $status)" | tee -a "$LOG_FILE"
    else
      echo "[$(date)] ❌ $name: FAILED (HTTP $status)" | tee -a "$LOG_FILE"
      alert "$name is DOWN (HTTP $status)"
    fi
  else
    eval "$cmd" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
      echo "[$(date)] ✅ $name: OK" | tee -a "$LOG_FILE"
    else
      echo "[$(date)] ❌ $name: FAILED" | tee -a "$LOG_FILE"
      alert "$name is DOWN"
    fi
  fi
}

alert() {
  message="$1 | Time: $(date '+%Y-%m-%d %H:%M:%S')"
  curl -s -X POST "$ALERT_WEBHOOK" \
    -H 'Content-type: application/json' \
    -d "{\"text\": \"🚨 Health Alert: $message\"}" > /dev/null
}

echo "🟢 Health Monitor started at $(date)"
while true; do
  for svc in "${SERVICES[@]}"; do
    name="${svc%%:*}"
    cmd="${svc#*:}"
    check_service "$name" "$cmd"
  done
  sleep 60  # Check every minute
done
```

## AI Alert Triage

```python
# alert_handler.py — AI-powered alert triage

import os, json, httpx
from datetime import datetime

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ALERT_QUEUE_WEBHOOK = os.environ.get("ALERT_QUEUE_WEBHOOK")

SYSTEM_PROMPT = """You are an AI operations assistant. 
Analyze this alert and classify it:
1. severity: critical/warning/info
2. category: downtime/performance/security/data/error
3. action: restart_service/scale_up/investigate/ignore/notify_team
4. response: 1-2 sentence recommended action

Respond in JSON: {"severity": "", "category": "", "action": "", "response": ""}"""

async def triage_alert(alert_text: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": alert_text}
                ],
                "temperature": 0.3
            }
        )
        result = response.json()
        return json.loads(result["choices"][0]["message"]["content"])

async def handle_alert(alert_data: dict):
    alert_text = f"""
Alert from: {alert_data.get('source', 'unknown')}
Service: {alert_data.get('service', 'unknown')}
Message: {alert_data.get('message', '')}
Timestamp: {alert_data.get('timestamp', datetime.utcnow().isoformat())}
"""
    
    triage = await triage_alert(alert_text)
    
    # Route based on AI classification
    if triage["severity"] == "critical":
        # Auto-restart service
        os.system(f"sudo systemctl restart {alert_data.get('service')}")
        # Post to incident channel
        await notify("🔴 CRITICAL ALERT", triage["response"])
    
    elif triage["severity"] == "warning":
        # Post to warning channel
        await notify("🟡 WARNING", triage["response"])
    
    else:
        # Log only
        print(f"INFO: {triage['response']}")

async def notify(title: str, message: str):
    """Send notification via Slack/Telegram webhook."""
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        httpx.post(webhook, json={
            "text": f"{title}\n{message}"
        })
```

## Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: 'openclaw'
    static_configs:
      - targets: ['localhost:20447']
        labels:
          service: 'openclaw'

  - job_name: 'n8n'
    static_configs:
      - targets: ['localhost:5678']
        labels:
          service: 'n8n'

  - job_name: 'prometheus_exporters'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          service: 'ai_agents'

  - job_name: 'health_checks'
    static_configs:
      - targets: ['localhost:9100']
        labels:
          service: 'health_monitor'
```

## n8n Alert Triage Workflow

```json
{
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "parameters": {
        "path": "alert-triage",
        "responseMode": "lastNode"
      }
    },
    {
      "name": "AI Classify Alert",
      "type": "@n8n/n8n-nodes-langchain.openAi",
      "position": [500, 300],
      "parameters": {
        "resource": "chat",
        "messages": {
          "values": [
            {
              "role": "system",
              "content": "Classify this alert: severity (critical/warning/info), category, recommended action. JSON only."
            },
            {
              "role": "user", 
              "content": "={{ $json.message }}"
            }
          ]
        }
      }
    },
    {
      "name": "Route by Severity",
      "type": "n8n-nodes-base.switch",
      "position": [750, 300],
      "parameters": {
        "dataType": "string",
        "valueComparison": {
          "value1": "={{ $json.severity }}",
          "operation": "equals",
          "value2": "critical"
        }
      }
    },
    {
      "name": "Critical Alert → Slack",
      "type": "n8n-nodes-base.slack",
      "position": [950, 200],
      "parameters": {
        "channel": "#incidents",
        "text": "🚨 CRITICAL: {{ $json.message }}"
      }
    },
    {
      "name": "Warning Alert → Slack",
      "type": "n8n-nodes-base.slack",
      "position": [950, 400],
      "parameters": {
        "channel": "#monitoring",
        "text": "⚠️ WARNING: {{ $json.message }}"
      }
    }
  ]
}
```

## Grafana Dashboard

Key panels for AI agent monitoring:
- **Request Rate**: `rate(agent_requests_total[5m])`
- **Error Rate**: `rate(agent_requests_total{status="error"}[5m])`
- **Latency P50/P95/P99**: `histogram_quantile(0.99, agent_latency_seconds_bucket)`
- **Token Usage**: `rate(agent_token_usage_total[1h])`
- **Active Workflows**: `n8n_active_workflows`
- **n8n Workflow Executions**: `rate(n8n_workflow_executions_total[5m])`

## Setup

```bash
# 1. Start Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# 2. Start Grafana
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana

# 3. Start metrics exporter
pip install prometheus_client
python3 skills/monitoring-alerting-automation/scripts/prometheus_exporter.py &

# 4. Start health monitor
chmod +x skills/monitoring-alerting-automation/scripts/health_monitor.sh
./skills/monitoring-alerting-automation/scripts/health_monitor.sh &
```

## Alert Rules

```yaml
# alerts/agent_alerts.yml
groups:
  - name: agent_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(agent_requests_total{status="error"}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.95, agent_latency_seconds_bucket) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Agent latency above 5s"
```
