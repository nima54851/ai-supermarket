# customer-support-automation

> AI-powered customer support automation skill for OpenClaw agents.
> Handles ticket triage, auto-reply, escalation, and FAQ resolution.

## What It Does

- 🎫 **Ticket Triage** — Classifies incoming tickets by intent (bug, feature, billing, cancellation, general)
- 🤖 **Auto-Reply** — Drafts personalized responses based on ticket category and knowledge base
- 🔁 **Escalation Detection** — Flags high-priority tickets (refunds, legal, outages) for human review
- 📚 **FAQ Resolution** — Matches user questions to curated FAQ entries, returns answers instantly
- 📊 **Daily Summary** — Generates a daily support stats report (volume, CSAT, resolution time)

## Files

```
customer-support-automation/
├── SKILL.md                    ← This file
├── triage.py                  ← Ticket classifier (intent + priority)
├── auto_reply.py              ← Response generator using knowledge base
├── faq_resolver.py            ← FAQ matching + answer retrieval
├── escalation.py              ← Priority escalation logic
├── report.py                   ← Daily support summary generator
└── knowledge_base/
    ├── faq.md                  ← FAQ entries (edit to customize)
    └── templates/
        └── reply_templates.md  ← Response templates by category
```

## Usage

### Ticket Triage

```python
from triage import classify_ticket

ticket = {
    "subject": "I can't log in to my account",
    "body": "I've been trying since yesterday but keep getting a 500 error.",
    "sender_email": "user@example.com"
}

result = classify_ticket(ticket)
# → {"intent": "bug", "priority": "high", "category": "technical"}
```

### Auto-Reply

```python
from auto_reply import generate_reply

reply = generate_reply(ticket, result, knowledge_base_path="knowledge_base/")
# → {"reply": "...", "confidence": 0.92, "resolved": True}
```

### Escalation Check

```python
from escalation import should_escalate

if should_escalate(ticket, result):
    send_to_human_queue(ticket)  # Your webhook/email integration here
```

### Daily Report

```python
from report import generate_report

stats = generate_report(tickets_db_path="data/tickets.csv", days=7)
# → {"total": 142, "resolved": 130, "avg_response_time_hrs": 2.3, "csat": 4.6}
```

## Setup

1. Copy this skill to your OpenClaw skills directory:
   ```bash
   cp -r customer-support-automation ~/.openclaw/workspace/skills/
   ```

2. Edit `knowledge_base/faq.md` with your product's FAQ entries.

3. Customize `knowledge_base/templates/reply_templates.md` for your brand voice.

4. Connect to your ticket source:
   - **Zendesk**: Use their API + webhook → `scripts/zendesk_listener.py`
   - **Intercom**: Use Intercom webhook → `scripts/intercom_listener.py`
   - **Email**: Use IMAP/SMTP → `scripts/email_listener.py`
   - **Custom DB**: Point `report.py` at your tickets table

## Integration with n8n

```
Ticket Source (Zendesk/Intercom/Email)
  → n8n Webhook
    → OpenClaw Agent (customer-support-automation skill)
      → Classify → Auto-Reply → Escalation check
        → Post reply back via n8n HTTP Request
```

See `integrations/` for ready-made n8n workflows.

## Categories

| Category | Priority | Example |
|----------|----------|---------|
| bug | high | Login error, crash, data loss |
| feature | medium | Feature request, suggestion |
| billing | high | Payment issue, refund request |
| cancellation | high | Account cancellation, data export |
| general | low | How-to, account question |
| complaint | high | Escalate to human immediately |

## Customization Tips

- **FAQ matching**: Add more entries to `faq.md` for better coverage
- **Brand voice**: Adjust templates in `reply_templates.md`
- **Language**: All logic is language-agnostic; swap prompts for non-English
- **Sentiment**: Extend `triage.py` with sentiment analysis for priority boost

---

*Part of [agent-studio](https://github.com/nima54851/agent-studio) · Built with 灵犀 AI*
