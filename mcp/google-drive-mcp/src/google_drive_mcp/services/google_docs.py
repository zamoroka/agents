from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import httpx
from google.oauth2.credentials import Credentials

GOOGLE_DOC_URL_PATTERN = re.compile(r"https?://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)")


class GoogleDocUrlError(ValueError):
    """Raised when a Google Doc URL does not contain a document id."""


def extract_document_id(doc_url: str) -> str:
    match = GOOGLE_DOC_URL_PATTERN.search(doc_url)
    if not match:
        raise GoogleDocUrlError(
            "Invalid Google Doc URL. Expected format: https://docs.google.com/document/d/{fileId}/..."
        )
    return match.group(1)


def build_markdown_export_url(file_id: str) -> str:
    return f"https://docs.google.com/document/d/{file_id}/export?format=md"


async def export_doc_markdown(file_id: str, credentials: Credentials) -> str:
    export_url = build_markdown_export_url(file_id)
    headers = {"Authorization": f"Bearer {credentials.token}"}
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(export_url, headers=headers)
        response.raise_for_status()
        return response.text


def save_markdown(markdown_text: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown_text)
    return output_path


async def get_doc_metadata(file_id: str, credentials: Credentials) -> dict[str, Any]:
    """Fetch document metadata (name, createdTime, modifiedTime) from the Drive API."""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    params = {"fields": "id,name,createdTime,modifiedTime"}
    headers = {"Authorization": f"Bearer {credentials.token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
