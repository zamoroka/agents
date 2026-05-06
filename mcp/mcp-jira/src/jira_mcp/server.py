from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from jira_mcp.tools.base import ToolRegistrar
from jira_mcp.tools.jira import JiraTools


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO)


def build_server() -> FastMCP:
    mcp = FastMCP("mcp-jira")
    registrars: list[ToolRegistrar] = [JiraTools()]

    for registrar in registrars:
        registrar.register(mcp)

    return mcp


mcp = build_server()


def main() -> None:
    configure_logging()
    server = build_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
