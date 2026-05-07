from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from google.oauth2.credentials import Credentials

LOGGER = logging.getLogger(__name__)

CALENDAR_EVENTS_API = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
MAX_RESULTS_PER_PAGE = 2500


async def fetch_calendar_events(
    calendar_id: str,
    start_date: str,
    end_date: str,
    credentials: Credentials,
) -> list[dict[str, Any]]:
    """Fetch events from Google Calendar API v3 for a date range.

    Args:
        calendar_id: Calendar ID (email or 'primary').
        start_date: ISO date string (YYYY-MM-DD) for range start (inclusive, 00:00:00 UTC).
        end_date: ISO date string (YYYY-MM-DD) for range end (inclusive, 23:59:59 UTC).
        credentials: Google OAuth2 credentials.

    Returns:
        List of normalized event dicts.
    """
    url = CALENDAR_EVENTS_API.format(calendar_id=calendar_id)
    headers = {"Authorization": f"Bearer {credentials.token}"}

    time_min = f"{start_date}T00:00:00Z"
    time_max = f"{end_date}T23:59:59Z"

    params: dict[str, Any] = {
        "timeMin": time_min,
        "timeMax": time_max,
        "maxResults": MAX_RESULTS_PER_PAGE,
        "singleEvents": "true",
        "orderBy": "startTime",
    }

    all_events: list[dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                normalized = _normalize_event(item)
                if normalized:
                    all_events.append(normalized)

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
            params["pageToken"] = next_page_token

    LOGGER.info("Fetched %d events from calendar %s", len(all_events), calendar_id)
    return all_events


def save_calendar_events_json(events: list[dict[str, Any]], output_path: Path) -> Path:
    """Save events list as pretty-printed JSON file.

    Args:
        events: List of event dicts to save.
        output_path: Full path for the output JSON file.

    Returns:
        Resolved output path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(events, indent=2, ensure_ascii=False))
    LOGGER.info("Saved %d events to %s", len(events), output_path)
    return output_path.resolve()


def _normalize_event(item: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize a raw Calendar API event item into a clean dict."""
    status = item.get("status", "confirmed")
    if status == "cancelled":
        return None

    start = item.get("start", {})
    end = item.get("end", {})

    start_time = start.get("dateTime") or start.get("date", "")
    end_time = end.get("dateTime") or end.get("date", "")
    all_day = "date" in start and "dateTime" not in start

    attendees = item.get("attendees", [])
    guests = [a.get("email", "") for a in attendees if not a.get("self", False)]

    creator = item.get("creator", {})
    creator_email = creator.get("email", "")

    return {
        "id": item.get("id", ""),
        "title": item.get("summary", "(No title)"),
        "startTime": start_time,
        "endTime": end_time,
        "allDayEvent": all_day,
        "description": item.get("description", ""),
        "location": item.get("location", ""),
        "guests": guests,
        "creator": creator_email,
        "recurringEvent": item.get("recurringEventId") is not None,
        "status": status,
    }
