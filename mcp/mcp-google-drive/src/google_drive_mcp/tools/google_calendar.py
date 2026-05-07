from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from google_drive_mcp.auth.oauth import get_or_authorize
from google_drive_mcp.config import Settings
from google_drive_mcp.services.google_calendar import (
    fetch_calendar_events,
    save_calendar_events_json,
)
from google_drive_mcp.tools.base import ToolRegistrar


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

            credentials = get_or_authorize(
                credentials_path=settings.credentials_path,
                token_path=settings.token_path,
            )

            events = await fetch_calendar_events(
                calendar_id=resolved_calendar_id,
                start_date=start_date,
                end_date=end_date,
                credentials=credentials,
            )

            file_name = f"calendar-events-{start_date}--{end_date}.json"
            output_path = Path(settings.download_dir) / file_name

            saved_path = save_calendar_events_json(events=events, output_path=output_path)

            return (
                f"Fetched {len(events)} events from calendar '{resolved_calendar_id}' "
                f"({start_date} to {end_date}). "
                f"Saved to: {saved_path}"
            )
