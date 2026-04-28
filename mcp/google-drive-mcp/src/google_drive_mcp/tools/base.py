from __future__ import annotations

from abc import ABC, abstractmethod

from mcp.server.fastmcp import FastMCP


class ToolRegistrar(ABC):
    """Base interface for MCP tool registration."""

    @abstractmethod
    def register(self, mcp: FastMCP) -> None:
        raise NotImplementedError
