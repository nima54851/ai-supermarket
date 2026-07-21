# Notion ↔ OpenClaw Sync

Sync your Notion database with OpenClaw AI agents to create a powerful "AI brain" for your projects.

## How It Works
```
Notion Database → n8n Webhook → OpenClaw AI Agent → n8n → Notion Update
```

## Features
- Pull Notion items → OpenClaw for AI analysis
- AI-powered tagging, categorization, priority scoring
- Auto-reply to Notion comments
- Daily digest generation into Notion pages

## Setup
1. Create a Notion integration at https://www.notion.so/my-integrations
2. Share your database with the integration
3. Import the n8n workflow: `n8n-notion-sync.json`
4. Set environment variables: `NOTION_TOKEN`, `NOTION_DATABASE_ID`

## n8n Workflow
```json
// See n8n-notion-sync.json for full workflow
```
