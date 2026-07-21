# Error Tracking Automation

## Overview
AI-powered error tracking using Sentry — auto-triage, alert routing, and developer notification pipeline powered by n8n.

## What It Does
- Connects Sentry webhooks to n8n
- Auto-classifies errors by severity (fatal/critical/error/warning)
- Routes alerts to Slack/Discord/Email based on error type
- Creates GitHub issues for critical errors
- Deduplicates similar errors
- Generates AI summary of new error patterns

## Files
- `n8n-sentry-workflow.json` — Sentry → n8n → alert pipeline
- `sentry_webhook_handler.py` — Local webhook receiver for self-hosted Sentry
- `error_digest.py` — Daily error digest generator

## Setup
1. Import `n8n-sentry-workflow.json` into n8n
2. Add Sentry DSN webhook URL
3. Configure alert channels (Slack webhook, Discord webhook, email)
4. Set severity thresholds

## Usage
Errors in Sentry → webhook → n8n → AI classification → route to correct channel
