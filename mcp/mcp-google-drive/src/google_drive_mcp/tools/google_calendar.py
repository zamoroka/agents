from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from google_drive_mcp.auth.oauth import get_or_authorize
from google_drive_mcp.config import Settings
from google_drive_mcp.services.google_calendar import (
    fetch_calendar_events,
    save_calendar_events_json,
)
from google_drive_mcp.tools.base import ToolRegistrar

ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def normalize_date_range(start_date: str, end_date: str) -> tuple[str, str]:
    """Validate and normalize tool input dates to YYYY-MM-DD."""
    try:
        start = date.fromisoformat(start_date)
    except ValueError as exc:
        raise ValueError("Invalid start_date. Expected format: YYYY-MM-DD.") from exc

    try:
        end = date.fromisoformat(end_date)
    except ValueError as exc:
        raise ValueError("Invalid end_date. Expected format: YYYY-MM-DD.") from exc

    if end < start:
        raise ValueError("Invalid date range. end_date must be on or after start_date.")

    return start.isoformat(), end.isoformat()


def build_calendar_events_output_path(download_dir: Path, start_date: str, end_date: str) -> Path:
    """Build a safe output path in the configured download directory."""
    if not ISO_DATE_PATTERN.fullmatch(start_date) or not ISO_DATE_PATTERN.fullmatch(end_date):
        raise ValueError("Output path dates must be normalized in YYYY-MM-DD format.")

    file_name = f"calendar-events-{start_date}--{end_date}.json"
    resolved_download_dir = download_dir.expanduser().resolve()
    output_path = (resolved_download_dir / file_name).resolve()
    if output_path.parent != resolved_download_dir:
        raise ValueError("Resolved output path escapes configured download directory.")
    return output_path


class GoogleCalendarTools(ToolRegistrar):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def register(self, mcp: FastMCP) -> None:
        settings = self.settings

        @mcp.tool(
            name="calendar_get_events",
            description="Fetch Google Calendar events for a date range and save as JSON.",
        )
        async def calendar_get_events(
            start_date: str,
            end_date: str,
            calendar_id: str | None = None,
        ) -> str:
            """Fetch calendar events and save them as a JSON file.

            Args:
                start_date: Start date in YYYY-MM-DD format (inclusive, treated as 00:00:00 UTC).
                end_date: End date in YYYY-MM-DD format (inclusive, treated as 23:59:59 UTC).
                calendar_id: Optional calendar ID. Defaults to GOOGLE_CALENDAR_ID env var.
            """
            resolved_calendar_id = calendar_id or settings.calendar_id

            try:
                normalized_start_date, normalized_end_date = normalize_date_range(
                    start_date=start_date,
                    end_date=end_date,
                )
                output_path = build_calendar_events_output_path(
                    download_dir=Path(settings.download_dir),
                    start_date=normalized_start_date,
                    end_date=normalized_end_date,
                )
            except ValueError as exc:
                return str(exc)

            credentials = get_or_authorize(
                credentials_path=settings.credentials_path,
                token_path=settings.token_path,
            )

            events = await fetch_calendar_events(
                calendar_id=resolved_calendar_id,
                start_date=normalized_start_date,
                end_date=normalized_end_date,
                credentials=credentials,
            )

            saved_path = save_calendar_events_json(events=events, output_path=output_path)

            return (
                f"Fetched {len(events)} events from calendar '{resolved_calendar_id}' "
                f"({normalized_start_date} to {normalized_end_date}). "
                f"Saved to: {saved_path}"
            )
