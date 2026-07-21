#!/bin/bash
# GitHub Actions Automation Setup Script
# Usage: ./setup-actions.sh <github-token>

TOKEN=${1:-$GITHUB_TOKEN}
REPO="nima54851/agent-studio"

if [ -z "$TOKEN" ]; then
  echo "❌ GitHub token required. Pass as argument or set GITHUB_TOKEN env var."
  exit 1
fi

echo "🔧 Setting up GitHub Actions for $REPO..."

# Create workflow directory
mkdir -p .github/workflows

# Copy workflow templates
if [ -d "integrations/github-actions-automation/workflow-templates" ]; then
  cp integrations/github-actions-automation/workflow-templates/*.yml .github/workflows/
  echo "✅ Copied workflow templates to .github/workflows/"
fi

# Enable GitHub Actions (should already be on by default)
curl -s -X PUT \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$REPO/actions/permissions" \
  -d '{"enabled": true, "allowed_actions": "all"}' > /dev/null
echo "✅ GitHub Actions enabled"

# List available self-hosted runners
echo "📋 Workflow templates:"
ls -la .github/workflows/

echo ""
echo "🎉 Setup complete! Configure secrets in GitHub Settings → Secrets → Actions"
echo "   Required secrets: GITHUB_TOKEN, OPENAI_API_KEY"
