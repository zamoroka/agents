from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from google_drive_mcp.auth.oauth import get_or_authorize
from google_drive_mcp.config import Settings
from google_drive_mcp.services.google_docs import (
    GoogleDocUrlError,
    download_doc_markdown,
    extract_document_id,
    save_markdown,
)
from google_drive_mcp.tools.base import ToolRegistrar


class GoogleDocsTools(ToolRegistrar):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def register(self, mcp: FastMCP) -> None:
        settings = self.settings

        @mcp.tool()
        async def doc_markdown_download(
            doc_url: str,
            file_name: str | None = None,
            output_dir: str | None = None,
        ) -> str:
            """Download a Google Doc as markdown and save it locally.

            Args:
                doc_url: Google Doc URL, e.g. https://docs.google.com/document/d/{fileId}/edit
                file_name: Optional output file name. Defaults to {fileId}.md
                output_dir: Optional output directory. Defaults to configured download directory
            """
            try:
                file_id = extract_document_id(doc_url)
            except GoogleDocUrlError as exc:
                return str(exc)

            credentials = get_or_authorize(
                credentials_path=settings.credentials_path,
                token_path=settings.token_path,
            )
            markdown_text = await download_doc_markdown(file_id=file_id, credentials=credentials)

            normalized_name = file_name.strip() if file_name else f"{file_id}.md"
            if not normalized_name.endswith(".md"):
                normalized_name = f"{normalized_name}.md"

            target_dir = Path(output_dir).expanduser() if output_dir else Path(settings.download_dir)
            output_path = (target_dir / normalized_name).resolve()

            save_markdown(markdown_text=markdown_text, output_path=output_path)
            return (
                f"Downloaded markdown for document {file_id} to {output_path}. "
                f"Characters: {len(markdown_text)}"
            )

        @mcp.tool()
        async def doc_markdown_output_tty(doc_url: str) -> str:
            """Fetch a Google Doc as markdown and return it to the MCP client output.

            Args:
                doc_url: Google Doc URL, e.g. https://docs.google.com/document/d/{fileId}/edit
            """
            try:
                file_id = extract_document_id(doc_url)
            except GoogleDocUrlError as exc:
                return str(exc)

            credentials = get_or_authorize(
                credentials_path=settings.credentials_path,
                token_path=settings.token_path,
            )
            markdown_text = await download_doc_markdown(file_id=file_id, credentials=credentials)
            return markdown_text
