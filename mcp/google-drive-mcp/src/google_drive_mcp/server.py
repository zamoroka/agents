from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from google_drive_mcp.config import load_settings
from google_drive_mcp.tools.base import ToolRegistrar
from google_drive_mcp.tools.google_docs import GoogleDocsTools


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO)


def build_server() -> FastMCP:
    settings = load_settings()
    mcp = FastMCP("google-drive-mcp")

    registrars: list[ToolRegistrar] = [
        GoogleDocsTools(settings=settings),
    ]

    for registrar in registrars:
        registrar.register(mcp)

    return mcp


def main() -> None:
    configure_logging()
    server = build_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
