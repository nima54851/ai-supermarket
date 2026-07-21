# Webhook Automation Guide

## Setup

1. Import workflow from `integrations/webhook-automation/`
2. Configure webhook endpoints in n8n
3. Set up HMAC secret verification in each endpoint
4. Configure AI Agent with routing instructions

## Supported Sources
| Source | Events | Signature Verification |
|--------|--------|----------------------|
| GitHub | push, pull_request, issues, star | HMAC-SHA256 |
| Stripe | payment_intent, customer.subscription | Stripe-Signature |
| Slack | slash commands, events API | Slack Signing Secret |
| Telegram | message, callback_query | Bot Token |
| Custom | Any JSON | HMAC-SHA256 |

## Routing Logic
```
Event → AI Agent classifies intent → 
  HIGH priority → Immediate action + alert
  MEDIUM priority → Process + log
  LOW priority → Queue for batch processing
```
