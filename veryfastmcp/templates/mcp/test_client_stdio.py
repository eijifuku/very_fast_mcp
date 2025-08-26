#!/usr/bin/env python3
"""
Simple MCP client test using FastMCP official client (stdio transport)
- Spawns local MCP server process via stdio and connects to it
- Calls tools/list and tools/call for greet
"""

import asyncio
import sys
from pathlib import Path

from fastmcp.client.client import Client
from fastmcp.client.transports import PythonStdioTransport


async def main() -> None:
    print("Starting MCP client test (stdio connection)...")

    # Resolve server script path
    here = Path(__file__).resolve().parent
    server_script = here / "mcp_server.py"

    if not server_script.exists():
        print(f"Server script not found: {server_script}", file=sys.stderr)
        sys.exit(1)

    # Connect to MCP server over stdio (spawns process)
    try:
        print(f"Creating stdio transport with server script: {server_script}")
        transport = PythonStdioTransport(str(server_script))
        client = Client(transport)

        async with client:
            # tools/list
            print("Listing tools via official client...")
            tools = await client.list_tools()
            print(f"Tools: {[t.name for t in tools]}")

            # tools/call greet
            print("Calling greet via official client...")
            result = await client.call_tool("greet", {"name": "TestUser"})
            print(f"Greet result: {result}")

        print("All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


