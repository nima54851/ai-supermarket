# Cost Optimization Automation

**Purpose:** Continuously monitor and reduce cloud/AI infrastructure costs using AI-driven analysis.
**Platform:** OpenClaw Agent
**Author:** 灵犀 AI (nima54851)

---

## What This Skill Does

1. **Cost Monitoring** — Track cloud spend (AWS/GCP/Azure/Vercel/ Railway/OpenAI)
2. **Anomaly Detection** — AI detects unusual spending spikes
3. **Optimization Recommendations** — Right-sizing, reserved instances, caching, batch processing
4. **Automated Actions** — Scale down idle resources, switch to spot instances, cache responses
5. **Budget Alerts** — Slack/Discord/Telegram alerts at threshold

## Tool Requirements

- Python 3.10+
- Cloud provider APIs (AWS Cost Explorer, GCP Billing, etc.)
- OpenAI/Anthropic API for AI cost analysis
- Redis (optional, for response caching optimization)

## File Structure

```
cost-optimization-automation/
├── SKILL.md                          # This file
├── README.md
├── cost_monitor.py                   # Multi-cloud cost tracker
├── anomaly_detector.py               # AI anomaly detection on spend data
├── optimizer.py                      # Optimization recommendation engine
├── budget_alerts.py                  # Budget threshold alerts
├── requirements.txt
├── configs/
│   └── cloud_credentials.example.json # Credential template (DO NOT commit real keys)
└── n8n/
    └── cost-optimization-workflow.json # n8n: billing API → AI analyze → alert → auto-action
```

## Usage

### 1. Track Cloud Spend

```python
from cost_monitor import CostMonitor

monitor = CostMonitor()
# Configure cloud providers
monitor.add_aws(profile="production")
monitor.add_openai(api_key="sk-***")

spend = monitor.get_spend(days=30)
print(f"Total spend: ${spend['total']:.2f}")
print(f"By service: {spend['breakdown']}")
```

### 2. AI Cost Anomaly Detection

```python
from anomaly_detector import CostAnomalyDetector

detector = CostAnomalyDetector(monitor=monitor)
anomalies = detector.detect()
# Returns: [{'date': '2026-07-15', 'expected': '$5', 'actual': '$127', 'reason': 'LLM API spike'}]
```

### 3. Get Optimization Recommendations

```python
from optimizer import CostOptimizer

opt = CostOptimizer(monitor=monitor)
recommendations = opt.get_recommendations()
# Returns: [{'action': 'switch-to-spot', 'savings': '$340/mo', 'impact': 'low'}, ...]
```

### 4. Budget Alerts

```python
from budget_alerts import BudgetAlert

alert = BudgetAlert(threshold_usd=100, channels=["slack", "telegram"])
alert.check()  # Called daily by cron/n8n
```

## Skill Triggers

- "check cloud costs"
- "optimize spending"
- "cost anomaly"
- "budget alert"
- "reduce AI costs"

## Supported Platforms

- AWS (Cost Explorer API)
- Google Cloud (Billing API)
- Azure (Cost Management API)
- Vercel
- Railway
- OpenAI API (token spend)
- Anthropic API
- Custom (CSV import)

---

*Last updated: 2026-07-17*
