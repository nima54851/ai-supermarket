# GitHub Actions Automation Skill

Automate GitHub Actions workflows for AI-driven CI/CD pipelines, including automated testing, deployment, and release management.

## Overview

This skill provides templates and scripts for:
- Automated testing on every PR
- AI-augmented code review in CI
- Auto-deployment to staging/production
- Automated releases with changelog generation
- Scheduled workflow runs
- Cache management and optimization

## Directory Structure

```
skills/github-actions-automation/
├── SKILL.md
└── scripts/
    └── setup-actions.sh
integrations/github-actions-automation/
├── n8n-github-actions-trigger.json  # n8n workflow for triggering actions
├── workflow-templates/
│   ├── ai-pr-review.yml
│   ├── auto-deploy-staging.yml
│   └── scheduled-report.yml
└── README.md
workflows/
└── github-actions-runbook.md
```

## AI-Augmented PR Review Workflow

```yaml
name: AI PR Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run AI Code Review
        run: |
          # Use OpenClaw or any LLM to review PR diff
          DIFF=$(git diff origin/${{ github.base_ref }}...HEAD)
          echo "$DIFF" | python3 review.py --model gpt-4 --prompt "Review for bugs, security issues, and style"

      - name: Post Review Comment
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: process.env.REVIEW_RESULT
            })
```

## Auto-Deploy Staging Workflow

```yaml
name: Auto-Deploy Staging
on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Staging
        run: |
          # Customize based on your deployment target
          curl -X POST https://your-staging-server/deploy \
            -H "Authorization: Bearer ${{ secrets.STAGING_TOKEN }}"
```

## Scheduled Report Workflow

```yaml
name: Weekly Status Report
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Report
        run: |
          python3 scripts/weekly_report.py \
            --repo ${{ github.repository }} \
            --output report.md

      - name: Create Issue
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              title: `Weekly Status: ${new Date().toISOString().slice(0,10)}`,
              body: require('fs').readFileSync('report.md', 'utf8')
            })
```

## n8n Integration

Use n8n to trigger GitHub Actions workflows programmatically:

```json
{
  "nodes": [
    {
      "name": "GitHub Trigger",
      "type": "n8n-nodes-base.githubTrigger",
      "position": [250, 300],
      "parameters": {
        "events": ["push", "pull_request"],
        "repository": "nima54851/agent-studio"
      }
    },
    {
      "name": "AI Analysis",
      "type": "@n8n/n8n-nodes-langchain.openAi",
      "position": [500, 300],
      "parameters": {
        "resource": "chat",
        "prompt": "Analyze this GitHub event and suggest next steps"
      }
    },
    {
      "name": "Trigger Workflow",
      "type": "@n8n/n8n-nodes-langchain.httpRequest",
      "position": [750, 300],
      "parameters": {
        "url": "https://api.github.com/repos/nima54851/agent-studio/actions/workflows/ci.yml/dispatches",
        "method": "POST",
        "authentication": "genericCredentialType",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            { "name": "Authorization", "value": "Bearer {{ $env.GITHUB_TOKEN }}" },
            { "name": "Accept", "value": "application/vnd.github+json" }
          ]
        }
      }
    }
  ]
}
```

## Setup

```bash
# 1. Add GitHub Token to repository secrets
# Settings → Secrets → Actions → New repository secret
# Name: GITHUB_TOKEN, Value: Your Fine-grained PAT

# 2. Enable workflows
# Copy templates from integrations/github-actions-automation/workflow-templates/
# to .github/workflows/ in your repository

# 3. Configure n8n webhook trigger
# Import integrations/github-actions-automation/n8n-github-actions-trigger.json
# Set the webhook URL in GitHub webhook settings
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub Personal Access Token |
| `OPENAI_API_KEY` | API key for AI review |
| `DEPLOY_TOKEN` | Deployment authorization token |
| `STAGING_URL` | Staging server endpoint |

## Cache Optimization

```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.npm
    key: ${{ runner.os }}-deps-${{ hashFiles('**/requirements.txt', '**/package.json') }}
    restore-keys: |
      ${{ runner.os }}-deps-
```

## Monitoring

Track workflow runs and failures:

```bash
# Check workflow status
gh run list --workflow=ci.yml --limit=5

# Watch a specific run
gh run watch

# Download artifacts
gh run download <run-id>
```

## Use Cases

1. **AI Code Review Bot**: Auto-review every PR with GPT-4/Claude
2. **Auto-Release**: Semantic version bump + changelog on merge to main
3. **Scheduled Tasks**: Daily reports, weekly digests, monthly backups
4. **Multi-Environment Deploy**: Staging → Production with approval gates
5. **Dependency Updates**: Auto-update PRs for outdated dependencies
