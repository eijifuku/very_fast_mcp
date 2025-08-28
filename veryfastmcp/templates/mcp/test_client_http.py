#!/usr/bin/env python3
"""
Simple MCP client test using FastMCP official client (HTTP connection)
- Connects to HTTP MCP server at http://127.0.0.1:8009/mcp
- Calls tools/list and tools/call for greet
"""

import asyncio
import sys

from fastmcp.client.client import Client

async def main() -> None:
    print("Starting MCP client test (HTTP connection)...")

    # Connect to HTTP MCP server
    client = Client("http://127.0.0.1:8009/mcp")

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

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ConnectionError as e:
        print(f"Connection failed: {e}")
        print("Make sure the MCP server is running on http://127.0.0.1:8009/mcp")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
