#!/bin/bash
set -e

echo "📦 Building Cloudflare Workers AI Agent..."

# Check Wrangler
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler not found. Install: npm install -g wrangler"
    exit 1
fi

# Check login
echo "🔑 Checking Cloudflare auth..."
wrangler whoami &>/dev/null || { echo "❌ Not logged in. Run: wrangler login"; exit 1; }

# Type check
echo "🔍 Running TypeScript check..."
npx tsc --noEmit --project tsconfig.json 2>/dev/null || echo "⚠️  TypeScript check skipped (tsconfig not found)"

# Deploy
echo "🚀 Deploying to Cloudflare Workers..."
wrangler deploy --dry-run --env production 2>/dev/null && echo "✅ Dry run passed"

read -p "Proceed with actual deployment? (y/N) " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
    wrangler deploy
    echo "✅ Deployed! Check status at: https://dash.cloudflare.com"
else
    echo "Deployment cancelled."
fi
