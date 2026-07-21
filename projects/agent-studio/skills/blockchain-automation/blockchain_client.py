#!/usr/bin/env python3
"""
Blockchain Automation Client
Supports Ethereum (EVM) and Solana chains.
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("blockchain")


@dataclass
class ChainConfig:
    chain_id: int
    rpc_url: str
    explorer_url: str
    symbol: str


CHAINS = {
    "ethereum": ChainConfig(1, os.environ.get("ETH_RPC", ""), "https://etherscan.io", "ETH"),
    "sepolia": ChainConfig(11155111, os.environ.get("SEPOLIA_RPC", ""), "https://sepolia.etherscan.io", "ETH"),
    "polygon": ChainConfig(137, os.environ.get("POLYGON_RPC", ""), "https://polygonscan.com", "MATIC"),
    "solana": ChainConfig("mainnet", os.environ.get("SOLANA_RPC", ""), "https://solscan.io", "SOL"),
}


class ChainClient:
    """Unified blockchain client."""

    def __init__(self, chain: str = "ethereum", rpc_url: Optional[str] = None):
        if chain in CHAINS:
            self.config = CHAINS[chain]
        else:
            raise ValueError(f"Unknown chain: {chain}")
        if rpc_url:
            self.rpc_url = rpc_url
        else:
            self.rpc_url = self.config.rpc_url

        self.chain = chain
        self.is_solana = chain == "solana"

    def get_balance(self, address: str) -> float:
        """Get native token balance."""
        if self.is_solana:
            return self._solana_balance(address)
        else:
            return self._eth_balance(address)

    def _eth_balance(self, address: str) -> float:
        """ETH/EVM balance via eth_getBalance."""
        try:
            import requests
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }
            r = requests.post(self.rpc_url, json=payload, timeout=10)
            wei = int(r.json()["result"], 16)
            return wei / 1e18
        except Exception as e:
            logger.error(f"Balance fetch failed: {e}")
            return 0.0

    def _solana_balance(self, address: str) -> float:
        """Solana balance via getBalance."""
        try:
            import requests
            r = requests.post(
                self.rpc_url,
                json={"jsonrpc": "2.0", "id": 1, "method": "getBalance", "params": [address]},
                timeout=10
            )
            lamports = r.json()["result"]["value"]
            return lamports / 1e9
        except Exception as e:
            logger.error(f"Solana balance failed: {e}")
            return 0.0

    def send_transaction(self, to: str, value: float, from_privkey: Optional[str] = None) -> str:
        """Send native token. Requires private key."""
        if not from_privkey:
            raise ValueError("Private key required to send transactions")

        if self.is_solana:
            return self._solana_transfer(to, value, from_privkey)
        else:
            return self._eth_transfer(to, value, from_privkey)

    def _eth_transfer(self, to: str, value_eth: float, privkey: str) -> str:
        """ETH transfer via raw transaction."""
        logger.info(f"Sending {value_eth} ETH to {to}")
        # Note: In production, use ethers.js or web3.py with proper nonce/gas handling
        # This is a placeholder — full implementation requires eth_estimateGas + sign + sendTransaction
        logger.warning("Full ETH send requires nonce management and signing — see ethers.js integration")
        return f"tx_placeholder_{to[:10]}"

    def _solana_transfer(self, to: str, value_sol: float, privkey: str) -> str:
        """Solana transfer via JSON-RPC."""
        logger.info(f"Sending {value_sol} SOL to {to}")
        logger.warning("Full Solana send requires @solana/web3.js or solders — see README")
        return f"tx_placeholder_{to[:10]}"

    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction receipt/status."""
        if self.is_solana:
            try:
                import requests
                r = requests.post(
                    self.rpc_url,
                    json={"jsonrpc": "2.0", "id": 1, "method": "getTransaction", "params": [tx_hash]},
                    timeout=10
                )
                return r.json().get("result", {})
            except Exception as e:
                return {"error": str(e)}
        else:
            try:
                import requests
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_getTransactionReceipt",
                    "params": [tx_hash],
                    "id": 1
                }
                r = requests.post(self.rpc_url, json=payload, timeout=10)
                return r.json().get("result", {})
            except Exception as e:
                return {"error": str(e)}


class WalletMonitor:
    """Monitor wallet balances and emit alerts."""

    def __init__(self, client: ChainClient, threshold_eth: float = 0.0):
        self.client = client
        self.threshold = threshold_eth
        self.addresses: Dict[str, float] = {}

    def watch(self, address: str, label: str = ""):
        self.addresses[address] = self._read_balance(address)

    def _read_balance(self, address: str) -> float:
        return self.client.get_balance(address)

    def check_all(self) -> Dict[str, Dict[str, Any]]:
        """Check all addresses, return alerts for those crossing threshold."""
        results = {}
        for addr, prev in self.addresses.items():
            current = self._read_balance(addr)
            changed = abs(current - prev) > 0.0001
            results[addr] = {
                "current": current,
                "prev": prev,
                "changed": changed,
                "alert": current >= self.threshold and changed
            }
            if changed:
                self.addresses[addr] = current
        return results


if __name__ == "__main__":
    # Demo (requires RPC URL)
    client = ChainClient(chain="ethereum")
    balance = client.get_balance("0x0000000000000000000000000000000000000000")
    print(f"ETH Supply Contract Balance: {balance} ETH")
