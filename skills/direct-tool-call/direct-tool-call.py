#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp>=1.0.0",
# ]
# ///
"""
Usage:
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --server-command '<cmd>' --server-args '<json-array>' --cwd '<path>' \\
    (--tool <tool_name> | --prompt <prompt_name> | --resource <resource_uri>) [--args '<json>']

Examples:
  # Jira
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --server-command uv \\
    --server-args '["--directory","~/.agents/mcp/mcp-jira","run","mcp-jira"]' \\
    --cwd ~/.agents/mcp/mcp-jira \\
    --tool fetch_jira_issue_details --args '{"issueKey":"SUNNYR-64"}'

  # Jira prompt
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --server-command uv \\
    --server-args '["--directory","~/.agents/mcp/mcp-jira","run","mcp-jira"]' \\
    --cwd ~/.agents/mcp/mcp-jira \\
    --prompt jira_issue_summary_prompt --args '{"issueKey":"SUNNYR-64"}'

  # Read a resource
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --server-command '<command>' --server-args '<json-array>' --cwd '<path>' \\
    --resource 'resource://uri'

  # Chrome DevTools
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --server-command npx \\
    --server-args '["-y","chrome-devtools-mcp@latest"]' \\
    --tool list_pages --args '{}'

  # Google Drive
  uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \\
    --server-command uv \\
    --server-args '["--directory","~/.agents/mcp/mcp-google-drive","run","mcp-google-drive"]' \\
    --tool <tool_name> --args '{}'
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def expand(p: str) -> Path:
    return Path(p).expanduser().resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call any stdio MCP server tool, prompt, or resource directly.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--tool", help="Tool name to call")
    target.add_argument("--prompt", help="Prompt name to call")
    target.add_argument("--resource", help="Resource URI to read")
    parser.add_argument("--args", default="{}", help="JSON object of tool or prompt arguments")
    parser.add_argument("--server-command", required=True, help="Server executable")
    parser.add_argument(
        "--server-args",
        required=True,
        help="JSON array of server arguments",
    )
    parser.add_argument(
        "--cwd",
        required=True,
        help="Working directory for the server process",
    )
    return parser.parse_args()


async def run(
    tool: str | None,
    prompt: str | None,
    resource: str | None,
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
            if tool:
                result = await session.call_tool(tool, tool_args)
                print_tool_result(result)
                return

            if prompt:
                result = await session.get_prompt(prompt, stringify_prompt_args(tool_args))
                print_prompt_result(result)
                return

            result = await session.read_resource(resource)
            print_resource_result(result)
            return


def stringify_prompt_args(raw_args: dict) -> dict[str, str]:
    return {
        str(key): value if isinstance(value, str) else json.dumps(value)
        for key, value in raw_args.items()
    }


def print_content_item(item) -> None:
    text = getattr(item, "text", None)
    if text is not None:
        print(text)
    else:
        print(json.dumps(item.model_dump(), indent=2))


def print_tool_result(result) -> None:
    # Print each content item; prefer text, fall back to JSON
    if result.content:
        for item in result.content:
            print_content_item(item)
    else:
        print(json.dumps(result.model_dump(), indent=2))


def print_prompt_result(result) -> None:
    if result.messages:
        for message in result.messages:
            prefix = f"[{message.role}] " if getattr(message, "role", None) else ""
            text = getattr(message.content, "text", None)
            if text is not None:
                print(f"{prefix}{text}")
            else:
                payload = message.content.model_dump() if hasattr(message.content, "model_dump") else message.content
                print(f"{prefix}{json.dumps(payload, indent=2)}")
    else:
        print(json.dumps(result.model_dump(), indent=2))


def print_resource_result(result) -> None:
    if result.contents:
        for content in result.contents:
            text = getattr(content, "text", None)
            if text is not None:
                print(text)
                continue

            blob = getattr(content, "blob", None)
            if blob is not None:
                print(blob)
                continue

            payload = content.model_dump() if hasattr(content, "model_dump") else content
            print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(result.model_dump(), indent=2))


def main() -> None:
    ns = parse_args()

    try:
        tool_args = json.loads(ns.args)
        if not isinstance(tool_args, dict):
            raise ValueError("Expected a JSON object.")
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in --args: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Invalid value for --args: {exc}", file=sys.stderr)
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
                prompt=ns.prompt,
                resource=ns.resource,
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
