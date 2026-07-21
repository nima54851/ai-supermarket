# Blockchain Automation Integration

> n8n workflow + tools for blockchain data monitoring, smart contract interactions, and crypto wallet tracking.

## Overview

This integration connects blockchain data to your AI agent automation pipeline. Monitor wallet activity, trigger smart contract events, and get AI-analyzed on-chain insights — all automated via n8n.

## Components

### n8n Workflow: `n8n-blockchain-monitor.json`

- **Trigger:** Schedule (every 15 min) or webhook
- **Input:** Wallet addresses, contract addresses, RPC endpoint
- **Process:**
  1. Fetch on-chain data via RPC/Explorer API (Etherscan, Alchemy, Infura)
  2. Parse transactions, gas prices, token transfers
  3. AI agent analyzes for anomalies, whale movements,rug pulls
  4. Route results: Discord alert / email digest / Notion log / webhook push
- **Output:** Alert reports, daily summaries, anomaly flags

### Features

- Multi-chain support: Ethereum, Polygon, BSC, Arbitrum, Base
- Wallet tracking: incoming/outgoing tx, token balances
- Gas price monitoring with alert thresholds
- NFT transfer detection
- DEX liquidity monitoring
- Smart contract event parsing (ETH events)
- AI-generated daily on-chain digest

## Setup

```bash
# 1. Get API keys
# - Alchemy/Infura: https://www.alchemy.com / https://infura.io
# - Etherscan API: https://etherscan.io/apis
# - NOWNodes (multi-chain): https://nownodes.io

# 2. Import workflow
# n8n → Settings → Import from JSON → paste n8n-blockchain-monitor.json

# 3. Set credentials
# - Alchemy/Infura HTTP Auth
# - Etherscan API Key
# - Discord Webhook (for alerts)
```

## Usage

```
# Trigger manually
curl -X POST https://your-n8n-url/webhook/blockchain-monitor \
  -H "Content-Type: application/json" \
  -d '{"wallet": "0x...", "chain": "ethereum"}'

# AI agent queries
Agent: "Check wallet 0x... for any large transfers in the last 24h"
→ n8n → RPC fetch → AI analysis → Response
```

## Required Skills

- `blockchain-automation` — Core skill for blockchain interactions
- `n8n-workflow-builder` — For customizing the workflow
- `ai-code-refactoring` — For smart contract analysis

---

*Built with 灵犀 AI · agent-studio*
