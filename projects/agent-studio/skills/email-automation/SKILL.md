# Email Automation Skill

**Skill Name:** email-automation  
**Category:** Communication & Productivity  
**Tags:** email, gmail, smtp, auto-reply, newsletter, drip-campaign  
**Last Updated:** 2026-06-30

## What This Skill Does

Automates email workflows: intelligent auto-reply, drip campaigns, newsletter delivery, lead nurturing, and Gmail/SMTP integration via n8n.

## Core Capabilities

### 1. Gmail Integration (n8n)
- OAuth2 Gmail trigger (new email)
- Auto-label and categorize incoming emails
- Smart auto-reply with AI-generated responses
- Thread-based reply context

### 2. SMTP Email Campaigns
- Drip campaign builder (time-based sequences)
- Newsletter templating with Markdown → HTML
- Unsubscribe handling (list-unsubscribe header)
- Bounce/click/open tracking via webhooks

### 3. AI Email Processing
- **Triage:** Sort emails by intent (urgent, follow-up, unsubscribe, info)
- **Reply Generation:** Draft responses using AI with context awareness
- **Summarization:** Condense long email threads for quick review
- **Priority Scoring:** Rank emails by sender importance + keywords

### 4. Use Cases
| Scenario | Description |
|---|---|
| Support Auto-Reply | AI reads ticket, drafts response, human approves |
| Welcome Drip | 5-email onboarding sequence triggered by sign-up |
| Newsletter | Weekly digest with unsubscribe handling |
| Lead Nurture | 7-day follow-up sequence for cold leads |
| Meeting Scheduler | Email → parse intent → create calendar event |

## Setup

### Prerequisites
- n8n running (see `integrations/email-automation/n8n-email-workflow.json`)
- Gmail API credentials (OAuth2) OR SMTP credentials
- AI Agent (OpenClaw) with email permissions

### Quick Start
```bash
# 1. Import the n8n workflow
# Open n8n → Import from File → integrations/email-automation/n8n-email-workflow.json

# 2. Configure Gmail OAuth2 credentials in n8n
# Settings → Credentials → Add Credential → Gmail OAuth2 API

# 3. Set up trigger
# The Gmail Trigger node activates on new incoming emails

# 4. Connect to AI Agent
# Use HTTP Request node → POST to OpenClaw webhook
```

## n8n Workflow Structure

```
Gmail Trigger
    ↓
AI Agent (classify intent)
    ↓
[Route by intent]
    ├── urgent → Slack/Discord notification
    ├── auto-reply → AI draft → Send
    ├── follow-up → Add to CRM / Schedule
    └── info → Archive + label
```

## Configuration

| Variable | Description | Default |
|---|---|---|
| `GMAIL_LABEL` | Gmail label to watch | `INBOX` |
| `AUTO_REPLY_ENABLED` | Toggle auto-reply | `true` |
| `REPLY_DELAY_SEC` | Delay before auto-reply | `60` |
| `MAX_DAILY_SENDS` | Rate limit | `100` |

## Security Notes

- **Never log email content** with PII in plaintext
- Use environment variables for SMTP/Gmail credentials
- Implement `List-Unsubscribe` header for all bulk emails
- Respect GDPR: don't store email content beyond necessary

## Files in This Skill

```
skills/email-automation/
├── SKILL.md                    ← This file
└── README.md                   ← Detailed guide

integrations/email-automation/
├── n8n-email-workflow.json     ← Main n8n workflow
├── n8n-drip-campaign.json      ← Drip campaign workflow
├── smtp-config.example.json    ← SMTP config template
└── email-templates/           ← HTML email templates
    ├── welcome.html
    ├── newsletter.html
    └── drip-sequence.html
```

## Example: AI Auto-Reply Flow

```javascript
// n8n Function node — AI Email Reply
const email = $json;
const sender = email.from;
const subject = email.subject;
const body = email.bodyText;

// Call AI agent for reply generation
const aiReply = await fetch('http://localhost:5678/webhook/ai-email-reply', {
  method: 'POST',
  body: JSON.stringify({ sender, subject, body }),
  headers: { 'Content-Type': 'application/json' }
}).then(r => r.json());

return {
  to: sender,
  subject: `Re: ${subject}`,
  body: aiReply.reply,
  sender: process.env.SENDER_EMAIL
};
```

---

*Part of agent-studio by nima54851 | CC-BY-4.0*
