#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp>=1.0.0",
# ]
# ///
"""
Direct MCP tool caller — Python/uv port of direct-tool-call.mjs

Usage:
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --tool <tool_name> [--args '<json>'] \\
    [--server-command '<cmd>'] [--server-args '<json-array>'] [--cwd '<path>']

Defaults (Jira MCP):
  --server-command  node
  --server-args     ["dist/function.js"]
  --cwd             ~/.agents/mcp/jira-mcp

Examples:
  # Jira (all defaults)
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --tool fetch_jira_issue_details --args '{"issueKey":"SUNNYR-64"}'

  # Chrome DevTools
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --server-command npx \\
    --server-args '["-y","chrome-devtools-mcp@latest"]' \\
    --tool list_pages --args '{}'

  # Google Drive
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --server-command uv \\
    --server-args '["--directory","/Users/zamoroka_pavlo/.agents/mcp/google-drive-mcp","run","google-drive-mcp"]' \\
    --tool <tool_name> --args '{}'
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

THIS_DIR = Path(__file__).parent
DEFAULT_CWD = THIS_DIR.parent.parent / "mcp" / "jira-mcp"


def expand(p: str) -> Path:
    return Path(p).expanduser().resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call any stdio MCP server tool directly.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tool", required=True, help="Tool name to call")
    parser.add_argument("--args", default="{}", help="JSON object of tool arguments")
    parser.add_argument("--server-command", default="node", help="Server executable (default: node)")
    parser.add_argument(
        "--server-args",
        default='["dist/function.js"]',
        help='JSON array of server arguments (default: ["dist/function.js"])',
    )
    parser.add_argument(
        "--cwd",
        default=str(DEFAULT_CWD),
        help=f"Working directory for the server process (default: {DEFAULT_CWD})",
    )
    return parser.parse_args()


async def run(
    tool: str,
    tool_args: dict,
    server_command: str,
    server_args: list[str],
    cwd: str,
) -> None:
    params = StdioServerParameters(
        command=server_command,
        args=server_args,
        cwd=cwd,
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, tool_args)

    # Print each content item; prefer text, fall back to JSON
    if result.content:
        for item in result.content:
            text = getattr(item, "text", None)
            if text is not None:
                print(text)
            else:
                print(json.dumps(item.model_dump(), indent=2))
    else:
        print(json.dumps(result.model_dump(), indent=2))


def main() -> None:
    ns = parse_args()

    try:
        tool_args = json.loads(ns.args)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in --args: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        server_args: list[str] = json.loads(ns.server_args)
        if not isinstance(server_args, list) or not all(isinstance(a, str) for a in server_args):
            raise ValueError("Expected a JSON array of strings.")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Invalid JSON in --server-args: {exc}", file=sys.stderr)
        sys.exit(1)

    cwd = str(expand(ns.cwd))

    try:
        asyncio.run(
            run(
                tool=ns.tool,
                tool_args=tool_args,
                server_command=ns.server_command,
                server_args=server_args,
                cwd=cwd,
            )
        )
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

