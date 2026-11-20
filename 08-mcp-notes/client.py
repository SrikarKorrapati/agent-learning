"""List the notes tools and call list_my_notes via stdio or an HTTP URL."""

import argparse
import asyncio
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main(url=None):
    if url:
        transport = url
    else:
        script = Path(__file__).with_name("v1_local.py").resolve()
        transport = StdioTransport(command=sys.executable, args=[str(script)])

    async with Client(transport) as client:
        tools = await client.list_tools()
        print("Tools:", [tool.name for tool in tools])

        result = await client.call_tool("list_my_notes", {})
        print("Notes:", result.data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", help="HTTP endpoint (defaults to local stdio)")
    asyncio.run(main(parser.parse_args().url))
