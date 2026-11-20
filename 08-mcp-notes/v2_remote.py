"""Serve the same MCP tools over Streamable HTTP on this machine."""

import argparse

from v1_local import mcp


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    mcp.run(transport="http", host="127.0.0.1", port=args.port)
