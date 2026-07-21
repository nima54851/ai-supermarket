# Compliance Automation

## Overview
Automated compliance checking for GDPR, SOC 2, HIPAA, PCI-DSS, and ISO 27001. Generates evidence, policy documents, and audit reports using AI agents.

## What It Does
- **Policy Generator**: AI-generates compliant privacy policies, security policies, data processing agreements
- **Evidence Collector**: Auto-collects technical evidence for compliance controls
- **Gap Analyzer**: Compares current state against a compliance framework
- **Audit Report Gen**: AI-generated audit-ready reports with evidence links
- **Breach Detector**: Scans logs and data for potential compliance violations

## Supported Frameworks
| Framework | Coverage |
|---|---|
| GDPR | Articles 15-22 data subject rights, DPO requirements, breach notification |
| SOC 2 Type II | CC1-CC9 trust service criteria |
| HIPAA | Privacy Rule, Security Rule, Breach Notification Rule |
| PCI-DSS v4.0 | All 12 requirements with evidence mapping |
| ISO 27001 | Annex A controls, ISMS documentation |

## Workflow Pipeline
```
Compliance Scan Trigger (scheduled or manual)
  → n8n Webhook
  → AI Agent maps controls to evidence sources
  → Auto-collects: logs, configs, policies, screenshots
  → AI evaluates control effectiveness
  → Gap report generated
  → Audit report compiled (PDF/Markdown)
  → Alert sent if critical gaps found
```

## Files
- `SKILL.md` — this file
- `gdpr_checker.py` — GDPR-specific compliance checks
- `soc2_evidence.py` — SOC 2 evidence collection
- `gap_analyzer.py` — cross-framework gap analysis
- `audit_report.py` — AI-generated audit report

## Setup
```bash
cd integrations/compliance-automation
cp .env.example .env
# Fill in: AWS_ACCESS_KEY, AZURE_CONFIG, GCP_BUCKET, OPENAI_API_KEY
# Import n8n workflow: n8n-compliance-workflow.json
```

## Integration Points
- AWS Config / CloudTrail
- Azure Policy
- GCP Security Command Center
- Splunk / Elastic
- Okta / Azure AD
- GitHub / GitLab (policy-as-code)
- OpenAI / Claude (LLM inference)

## Related
- `security-auditor/` — security scanning and CVE detection
- `database-automation/` — data access compliance
- `auth-automation/` — access control compliance
