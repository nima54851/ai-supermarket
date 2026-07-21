# Blockchain Automation Skill

**Skill Name:** blockchain-automation  
**Author:** agent-studio  
**Version:** 1.0  
**Trigger Keywords:** blockchain, crypto, web3, wallet, defi, nft, token, contract, ether, ethereum, solana  

## Description

Automate blockchain operations via AI agents: wallet monitoring, DeFi interactions, NFT minting, smart contract calls, and on-chain event alerting. Supports Ethereum, Solana, and EVM-compatible chains via n8n + OpenClaw.

## Architecture

```
User Intent ("Transfer 0.1 ETH to 0x...")
    ↓
Blockchain Agent (Parse intent + validate)
    ↓
┌─────────────────────────────────────┐
│ Chain Abstraction Layer             │
│   ├── Ethereum RPC (ethers.js)      │
│   ├── Solana RPC (@solana/web3.js)   │
│   └── BSC / Polygon RPC              │
└─────────────────────────────────────┘
    ↓
Transaction Builder → Signer (Hot/Cold) → RPC Broadcast
    ↓
Event Monitor (on-chain confirmation)
```

## Core Capabilities

### Wallet Management
- Balance monitoring (ETH, SOL, ERC-20, SPL tokens)
- Multi-address watchlist
- Threshold alerts (e.g., "notify when ETH > 3.0")

### DeFi Operations
- Swap via DEX aggregators (1inch, Paraswap)
- Liquidity pool monitoring
- Yield farming position tracker

### NFT Automation
- Floor price monitoring (OpenSea, Blur)
- Auto-mint on mint events
- Floor sweep triggers

### Smart Contract Interaction
- Read-only calls (view functions)
- Write transactions with gas estimation
- Multi-sig support

## Usage

```python
from blockchain_automation import ChainClient, WalletMonitor

client = ChainClient(chain="ethereum", rpc_url=os.environ["ETH_RPC"])

# Check balance
balance = client.get_balance("0x...")
print(f"ETH Balance: {balance}")

# Send transaction
tx_hash = client.send(
    to="0x...",
    value=0.1,  # ETH
    gas_limit=21000
)
print(f"TX: {tx_hash}")
```

## n8n Integration

```bash
# n8n workflow: blockchain-automation/
# Triggers: Cron (every 5 min) or Webhook
# Nodes: Parse Intent → Chain Client → TX Builder → Sign → Broadcast → Confirm
```

## Security Notes

⚠️ **Never expose private keys in logs or code.**  
- Use environment variables for secrets  
- Prefer hardware wallet / MPC for production  
- Test on testnets (Sepolia, Goerli) before mainnet

## Files

- `SKILL.md` — This file
- `blockchain_client.py` — Chain abstraction client
- `wallet_monitor.py` — Balance & event monitor
- `README.md` — Full documentation

## Category

Web3 / Blockchain
