#!/usr/bin/env python3
"""
MCP Client — Model Context Protocol Python SDK
Connects AI agents to external tools via MCP standard.
Reference implementation for agent-studio.

Usage:
    python3 mcp_client.py --server http://localhost:3000
    python3 mcp_client.py --stdio "npx some-mcp-server"
"""
import json, sys, asyncio, argparse
from typing import Optional, Any
from dataclasses import dataclass

try:
    import mcp
    from mcp.client import ClientSession
except ImportError:
    print("Installing mcp...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp", "-q"])
    import mcp
    from mcp.client import ClientSession


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: dict

    @classmethod
    def from_dict(cls, d: dict) -> "MCPTool":
        return cls(
            name=d.get("name", ""),
            description=d.get("description", ""),
            input_schema=d.get("inputSchema", {})
        )


class MCPClient:
    def __init__(self, server: Optional[str] = None, command: Optional[str] = None):
        self.server = server
        self.command = command
        self.session: Optional[ClientSession] = None
        self.tools: list[MCPTool] = []

    async def connect(self):
        """Connect to MCP server"""
        if self.server:
            print(f"[mcp] Connecting to HTTP server: {self.server}")
            # HTTP SSE transport
            from mcp.client.sse import sse_client
            async with sse_client(self.server) as (read, write):
                self.session = ClientSession(read, write)
                await self.session.initialize()
        elif self.command:
            print(f"[mcp] Starting stdio server: {self.command}")
            import shlex
            parts = shlex.split(self.command)
            async with ClientSession.create_subprocess(
                *parts
            ) as (read, write):
                self.session = ClientSession(read, write)
                await self.session.initialize()
        else:
            raise ValueError("Must specify --server or --command")

        # List available tools
        response = await self.session.list_tools()
        self.tools = [MCPTool.from_dict(t) for t in response.tools]
        print(f"[mcp] Connected. {len(self.tools)} tools available:")
        for t in self.tools:
            print(f"  • {t.name}: {t.description[:50]}")

    async def call_tool(self, name: str, arguments: dict) -> Any:
        """Call an MCP tool"""
        if not self.session:
            raise RuntimeError("Not connected")
        result = await self.session.call_tool(name, arguments)
        return result.content

    async def disconnect(self):
        if self.session:
            await self.session.close()
            print("[mcp] Disconnected")

    async def interactive(self):
        """Interactive REPL for testing MCP tools"""
        print("\n=== MCP Interactive Mode ===")
        print("Available commands: tools, call <name> <json_args>, quit")
        while True:
            try:
                cmd = input("mcp> ").strip()
                if not cmd:
                    continue
                if cmd == "quit":
                    break
                if cmd == "tools":
                    for t in self.tools:
                        print(f"  {t.name}: {t.description}")
                elif cmd.startswith("call "):
                    parts = cmd[5:].split(" ", 1)
                    name = parts[0]
                    args = json.loads(parts[1]) if len(parts) > 1 else {}
                    result = await self.call_tool(name, args)
                    print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")


async def main():
    parser = argparse.ArgumentParser(description="MCP Client — connect AI agents to tools")
    parser.add_argument("--server", help="MCP HTTP server URL")
    parser.add_argument("--command", help="MCP stdio server command (e.g. 'npx server')")
    parser.add_argument("--interactive", action="store_true", help="Interactive REPL mode")
    args = parser.parse_args()

    client = MCPClient(server=args.server, command=args.command)
    try:
        await client.connect()
        if args.interactive:
            await client.interactive()
        else:
            print("\nMCP Client ready. Use --interactive to explore tools.")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
