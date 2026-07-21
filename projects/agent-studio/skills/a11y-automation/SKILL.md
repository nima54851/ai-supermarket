# Accessibility Automation (A11y)

## Overview
Automated web accessibility testing and remediation using axe-core, Lighthouse, and AI-powered fix suggestions. Integrates with CI/CD to enforce WCAG 2.1 AA / AAA compliance.

## What It Does
- **Automated Scanning**: Run axe-core and Lighthouse on any URL or local site
- **AI Fix Suggestions**: AI generates specific CSS/HTML fixes for each violation
- **CI/CD Enforcement**: Block PRs that introduce accessibility regressions
- **PDF/Document A11y**: Check PDF and document accessibility
- **Color Contrast Checker**: Verify contrast ratios meet WCAG standards
- **Screen Reader Simulation**: Test content ordering for screen readers

## Standards Supported
| Standard | Level | Coverage |
|---|---|---|
| WCAG 2.1 | A, AA, AAA | All 78 criteria |
| WCAG 2.2 | A, AA | New criteria (2.5.7-3.3.7) |
| Section 508 | Full | US federal compliance |
| EN 301 549 | Full | EU web accessibility |
| ADA | Partial | US civil rights |

## Workflow Pipeline
```
PR opened or scheduled scan trigger
  → n8n Webhook / CI step
  → AI Agent runs axe-core against target URL
  → AI Agent runs Lighthouse accessibility audit
  → Violations categorized by severity (critical/major/minor)
  → AI generates specific fix suggestions (with code)
  → If critical violations → PR comment + block merge
  → Accessibility report generated
  → Trend tracked over time
```

## Files
- `SKILL.md` — this file
- `axe_scanner.py` — axe-core scanner with AI fix generator
- `lighthouse_runner.py` — Lighthouse CI accessibility runner
- `contrast_checker.py` — WCAG contrast ratio checker
- `a11y_reporter.py` — HTML/JSON accessibility report generator

## Setup
```bash
cd integrations/a11y-automation
cp .env.example .env
# Fill in: CI_TOKEN, SLACK_WEBHOOK, GITHUB_TOKEN
# Import n8n workflow: n8n-a11y-workflow.json
# Add to GitHub Actions: .github/workflows/a11y.yml
```

## Integration Points
- axe-core (playwright/puppeteer)
- Lighthouse CI
- GitHub Actions / GitLab CI
- Storybook (component-level testing)
- Figma (design-to-code contrast checks)
- Slack / Email (violation alerts)

## Related
- `browser-automation/` — Playwright automation
- `testing-automation/` — general test generation
- `seo-automation/` — SEO and discoverability checks
