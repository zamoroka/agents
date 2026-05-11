from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from google_drive_mcp.config import Settings
from google_drive_mcp.services.google_docs import GoogleDocUrlError
from google_drive_mcp.tools.google_calendar import GoogleCalendarTools
from google_drive_mcp.tools.google_docs import GoogleDocsTools


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, object] = {}

    def tool(self, name: str, description: str):  # noqa: ANN001
        def decorator(func):  # noqa: ANN001
            self.tools[name] = func
            return func

        return decorator


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        credentials_path=tmp_path / "credentials.json",
        token_path=tmp_path / "token.json",
        download_dir=tmp_path / "downloads",
        calendar_id="primary-from-settings",
    )


@pytest.fixture
def registered_tools(settings: Settings) -> tuple[FakeMCP, dict[str, object]]:
    mcp = FakeMCP()
    GoogleDocsTools(settings=settings).register(mcp)  # pyright: ignore[reportArgumentType]
    GoogleCalendarTools(settings=settings).register(mcp)  # pyright: ignore[reportArgumentType]
    return mcp, mcp.tools


def test_registers_all_tools(registered_tools: tuple[FakeMCP, dict[str, object]]) -> None:
    _, tools = registered_tools
    assert set(tools.keys()) == {
        "doc_markdown_download",
        "doc_get_metadata",
        "doc_markdown_output_tty",
        "calendar_get_events",
    }


@pytest.mark.asyncio
async def test_doc_markdown_download_success(
    settings: Settings,
    registered_tools: tuple[FakeMCP, dict[str, object]],
) -> None:
    _, tools = registered_tools
    tool = tools["doc_markdown_download"]
    creds = MagicMock()

    with (
        patch("google_drive_mcp.tools.google_docs.extract_document_id", return_value="doc123") as mock_extract,
        patch("google_drive_mcp.tools.google_docs.get_or_authorize", return_value=creds) as mock_auth,
        patch(
            "google_drive_mcp.tools.google_docs.export_doc_markdown",
            new=AsyncMock(return_value="# test markdown"),
        ) as mock_export,
        patch("google_drive_mcp.tools.google_docs.save_markdown") as mock_save,
    ):
        result = await tool(
            doc_url="https://docs.google.com/document/d/doc123/edit",
            file_name="notes",
            output_dir=str(settings.download_dir),
        )

    expected_output_path = (settings.download_dir / "notes.md").resolve()
    mock_extract.assert_called_once()
    mock_auth.assert_called_once_with(
        credentials_path=settings.credentials_path,
        token_path=settings.token_path,
    )
    mock_export.assert_awaited_once_with(file_id="doc123", credentials=creds)
    mock_save.assert_called_once_with(markdown_text="# test markdown", output_path=expected_output_path)
    assert "Downloaded markdown for document doc123" in result
    assert str(expected_output_path) in result


@pytest.mark.asyncio
async def test_doc_markdown_download_invalid_url_short_circuits(
    registered_tools: tuple[FakeMCP, dict[str, object]],
) -> None:
    _, tools = registered_tools
    tool = tools["doc_markdown_download"]

    with (
        patch(
            "google_drive_mcp.tools.google_docs.extract_document_id",
            side_effect=GoogleDocUrlError("Invalid URL"),
        ),
        patch("google_drive_mcp.tools.google_docs.get_or_authorize") as mock_auth,
    ):
        result = await tool(doc_url="not-a-google-doc")

    mock_auth.assert_not_called()
    assert result == "Invalid URL"


@pytest.mark.asyncio
async def test_doc_get_metadata_success(registered_tools: tuple[FakeMCP, dict[str, object]]) -> None:
    _, tools = registered_tools
    tool = tools["doc_get_metadata"]
    creds = MagicMock()

    with (
        patch("google_drive_mcp.tools.google_docs.extract_document_id", return_value="doc123"),
        patch("google_drive_mcp.tools.google_docs.get_or_authorize", return_value=creds),
        patch(
            "google_drive_mcp.tools.google_docs.get_doc_metadata",
            new=AsyncMock(
                return_value={
                    "id": "doc123",
                    "name": "Title",
                    "createdTime": "2025-01-01T00:00:00Z",
                    "modifiedTime": "2025-01-02T00:00:00Z",
                }
            ),
        ),
    ):
        result = await tool("https://docs.google.com/document/d/doc123/edit")

    assert "id: doc123" in result
    assert "name: Title" in result
    assert "createdTime: 2025-01-01T00:00:00Z" in result
    assert "modifiedTime: 2025-01-02T00:00:00Z" in result


@pytest.mark.asyncio
async def test_doc_get_metadata_invalid_url(
    registered_tools: tuple[FakeMCP, dict[str, object]],
) -> None:
    _, tools = registered_tools
    tool = tools["doc_get_metadata"]

    with patch(
        "google_drive_mcp.tools.google_docs.extract_document_id",
        side_effect=GoogleDocUrlError("Bad URL"),
    ):
        result = await tool("bad-url")

    assert result == "Bad URL"


@pytest.mark.asyncio
async def test_doc_markdown_output_tty_success(
    registered_tools: tuple[FakeMCP, dict[str, object]],
) -> None:
    _, tools = registered_tools
    tool = tools["doc_markdown_output_tty"]
    creds = MagicMock()

    with (
        patch("google_drive_mcp.tools.google_docs.extract_document_id", return_value="doc123"),
        patch("google_drive_mcp.tools.google_docs.get_or_authorize", return_value=creds),
        patch(
            "google_drive_mcp.tools.google_docs.export_doc_markdown",
            new=AsyncMock(return_value="# markdown"),
        ) as mock_export,
    ):
        result = await tool("https://docs.google.com/document/d/doc123/edit")

    mock_export.assert_awaited_once_with(file_id="doc123", credentials=creds)
    assert result == "# markdown"


@pytest.mark.asyncio
async def test_doc_markdown_output_tty_invalid_url(
    registered_tools: tuple[FakeMCP, dict[str, object]],
) -> None:
    _, tools = registered_tools
    tool = tools["doc_markdown_output_tty"]

    with patch(
        "google_drive_mcp.tools.google_docs.extract_document_id",
        side_effect=GoogleDocUrlError("No ID"),
    ):
        result = await tool("bad-url")

    assert result == "No ID"


@pytest.mark.asyncio
async def test_calendar_get_events_success_uses_default_calendar_id(
    settings: Settings,
    registered_tools: tuple[FakeMCP, dict[str, object]],
) -> None:
    _, tools = registered_tools
    tool = tools["calendar_get_events"]
    creds = MagicMock()
    output_path = (settings.download_dir / "calendar-events-2025-06-01--2025-06-07.json").resolve()

    with (
        patch("google_drive_mcp.tools.google_calendar.get_or_authorize", return_value=creds) as mock_auth,
        patch(
            "google_drive_mcp.tools.google_calendar.fetch_calendar_events",
            new=AsyncMock(return_value=[{"id": "evt1"}]),
        ) as mock_fetch,
        patch(
            "google_drive_mcp.tools.google_calendar.save_calendar_events_json",
            return_value=output_path,
        ) as mock_save,
    ):
        result = await tool(start_date="2025-06-01", end_date="2025-06-07")

    mock_auth.assert_called_once_with(
        credentials_path=settings.credentials_path,
        token_path=settings.token_path,
    )
    mock_fetch.assert_awaited_once_with(
        calendar_id=settings.calendar_id,
        start_date="2025-06-01",
        end_date="2025-06-07",
        credentials=creds,
    )
    mock_save.assert_called_once()
    assert "Fetched 1 events from calendar 'primary-from-settings'" in result
    assert str(output_path) in result


@pytest.mark.asyncio
async def test_calendar_get_events_accepts_calendar_override(
    registered_tools: tuple[FakeMCP, dict[str, object]],
) -> None:
    _, tools = registered_tools
    tool = tools["calendar_get_events"]

    with (
        patch("google_drive_mcp.tools.google_calendar.get_or_authorize", return_value=MagicMock()),
        patch(
            "google_drive_mcp.tools.google_calendar.fetch_calendar_events",
            new=AsyncMock(return_value=[]),
        ) as mock_fetch,
        patch(
            "google_drive_mcp.tools.google_calendar.save_calendar_events_json",
            return_value=Path("/tmp/events.json"),
        ),
    ):
        await tool(
            start_date="2025-06-01",
            end_date="2025-06-07",
            calendar_id="override@domain.com",
        )

    assert mock_fetch.await_args.kwargs["calendar_id"] == "override@domain.com"


@pytest.mark.asyncio
async def test_calendar_get_events_invalid_date_returns_error(
    registered_tools: tuple[FakeMCP, dict[str, object]],
) -> None:
    _, tools = registered_tools
    tool = tools["calendar_get_events"]

    with patch("google_drive_mcp.tools.google_calendar.get_or_authorize") as mock_auth:
        result = await tool(start_date="2025/06/01", end_date="2025-06-07")

    mock_auth.assert_not_called()
    assert result == "Invalid start_date. Expected format: YYYY-MM-DD."
