# Cost Optimization Automation

AI-driven cloud and AI infrastructure cost monitoring and optimization.

## Quick Start

```bash
pip install -r requirements.txt
cp configs/cloud_credentials.example.json configs/cloud_credentials.json
# Edit configs/cloud_credentials.json with your API keys
```

## Usage

```bash
# Check cloud spend
python cost_monitor.py --days 30 --provider aws

# Detect anomalies
python anomaly_detector.py

# Get optimization recommendations
python optimizer.py

# Test budget alert
python budget_alerts.py --dry-run
```

## n8n Workflow

Import `n8n/cost-optimization-workflow.json` into your n8n instance.

## Supported Providers

- AWS · GCP · Azure · Vercel · Railway · OpenAI · Anthropic

---

*Author: 灵犀 AI · Powered by OpenClaw*
