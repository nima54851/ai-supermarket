# Feature Flag Automation

## Overview
Automated feature flag management using LaunchDarkly or Unleash. Controls rollouts, A/B tests, and kill switches with AI-powered flag recommendations.

## What It Does
- **Flag Lifecycle Management**: Create, update, archive flags programmatically
- **Gradual Rollouts**: Automated percentage-based rollouts with safety gates
- **A/B Test Integration**: Run experiments with flag-based targeting
- **Kill Switches**: Emergency flag-off with automated health checks before re-enabling
- **Flag Recommendations**: AI suggests new flags based on code diffs
- **Technical Debt Detection**: Flag flags that have been on/off for too long

## Supported Platforms
| Platform | Status |
|---|---|
| LaunchDarkly | ✅ Full SDK + REST API |
| Unleash | ✅ Full SDK + Admin API |
| Flagsmith | ✅ API |
| Custom (JSON) | ✅ File-based |

## Workflow Pipeline
```
Feature branch merged to main
  → n8n Webhook Trigger
  → AI Agent analyzes code diff
  → Recommends feature flag (name, targeting rules)
  → Creates flag in LaunchDarkly/Unleash
  → Sets gradual rollout schedule (5% → 25% → 50% → 100%)
  → Monitors metrics during rollout
  → If anomaly detected → auto-pause rollout
  → Full rollout or rollback based on results
```

## Files
- `SKILL.md` — this file
- `launchdarkly_manager.py` — LaunchDarkly flag CRUD + targeting
- `unleash_manager.py` — Unleash flag management
- `rollout_orchestrator.py` — gradual rollout with monitoring
- `flag_recommender.py` — AI feature flag suggestion from code diffs

## Setup
```bash
cd integrations/feature-flag-automation
cp .env.example .env
# Fill in: LAUNCHDARKLY_SDK_KEY or UNLEASH_URL + UNLEASH_TOKEN
# Import n8n workflow: n8n-feature-flag-workflow.json
```

## Integration Points
- LaunchDarkly REST API / SDK
- Unleash API / SDK
- GitHub PR webhooks
- Datadog / Grafana (rollout metrics)
- PagerDuty (kill switch alerts)
- Slack (rollout notifications)

## Related
- `ab-testing-workflow/` — A/B testing framework
- `monitoring-alerting-automation/` — metrics monitoring
- `incident-response-automation/` — emergency response
