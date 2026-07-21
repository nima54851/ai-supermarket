# Incident Response Automation

## Overview
Automated incident detection, triage, escalation, and resolution using AI agents. Integrates with PagerDuty, Opsgenie, and custom monitoring systems.

## What It Does
- **AI Triage**: Automatically classify severity, identify root cause candidates, suggest remediation steps
- **Smart Escalation**: Route to the right on-call engineer based on expertise, time, and load
- **Post-mortem Gen**: Auto-generate structured post-mortem reports from incident data
- **War Room Assist**: Real-time AI summarizer for ongoing incidents

## Workflow Pipeline
```
Alert Fired (PagerDuty/Opsgenie/Custom)
  → n8n Webhook Trigger
  → AI Agent classifies severity (P1/P2/P3/P4)
  → AI Agent extracts key signals from metrics/logs
  → AI Agent suggests fix or routes to on-call
  → Auto-creates Slack war-room channel
  → AI summarizer updates every 5 minutes
  → On resolution: AI generates post-mortem
  → AI creates follow-up tickets for prevention
```

## Files
- `SKILL.md` — this file
- `incident_classifier.py` — severity classifier with LLM
- `postmortem_generator.py` — auto-generate post-mortem from incident data
- `pagerduty_responder.py` — PagerDuty API integration
- `war_room_summarizer.py` — real-time incident summarizer

## Setup
```bash
cd integrations/incident-response-automation
cp .env.example .env
# Fill in: PAGERDUTY_TOKEN, SLACK_BOT_TOKEN, OPENAI_API_KEY
# Import n8n workflow: n8n-import-workflow.json
```

## Integration Points
- PagerDuty Events API v2
- Slack Web API (war rooms, alerts)
- Grafana/Alertmanager webhooks
- Jira/Linear (ticket creation)
- OpenAI / Claude (LLM inference)

## Use Cases
- SRE / DevOps teams reducing MTTR
- On-call engineers getting instant AI context
- Post-mortem automation without manual effort
- Escalation policy automation

## Related
- `monitoring-alerting-automation/` — monitoring and alerting
- `llm-ops-automation/` — LLM cost tracking
- `error-tracking-automation/` — error monitoring
