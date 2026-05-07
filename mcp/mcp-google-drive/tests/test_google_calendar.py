"""Tests for google_drive_mcp.services.google_calendar module."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from google_drive_mcp.services.google_calendar import (
    _normalize_event,
    fetch_calendar_events,
    save_calendar_events_json,
)


class TestNormalizeEvent:
    def test_confirmed_event_with_datetime(self):
        raw = {
            "id": "evt1",
            "summary": "Team standup",
            "start": {"dateTime": "2025-06-01T00:00:00+02:00"},
            "end": {"dateTime": "2025-06-07T23:59:59+02:00"},
            "status": "confirmed",
            "description": "Daily sync",
            "location": "Room A",
            "attendees": [
                {"email": "alice@example.com", "self": False},
                {"email": "me@example.com", "self": True},
            ],
            "creator": {"email": "alice@example.com"},
            "recurringEventId": "recurring123",
        }
        result = _normalize_event(raw)
        assert result is not None
        assert result["id"] == "evt1"
        assert result["title"] == "Team standup"
        assert result["startTime"] == "2025-06-01T00:00:00+02:00"
        assert result["endTime"] == "2025-06-07T23:59:59+02:00"
        assert result["allDayEvent"] is False
        assert result["description"] == "Daily sync"
        assert result["location"] == "Room A"
        assert result["guests"] == ["alice@example.com"]
        assert result["creator"] == "alice@example.com"
        assert result["recurringEvent"] is True
        assert result["status"] == "confirmed"

    def test_all_day_event(self):
        raw = {
            "id": "evt2",
            "summary": "Holiday",
            "start": {"date": "2025-06-01"},
            "end": {"date": "2025-06-02"},
            "status": "confirmed",
        }
        result = _normalize_event(raw)
        assert result is not None
        assert result["allDayEvent"] is True
        assert result["startTime"] == "2025-06-01"
        assert result["endTime"] == "2025-06-02"

    def test_cancelled_event_returns_none(self):
        raw = {
            "id": "evt3",
            "summary": "Cancelled meeting",
            "start": {"dateTime": "2025-06-01T10:00:00Z"},
            "end": {"dateTime": "2025-06-01T11:00:00Z"},
            "status": "cancelled",
        }
        result = _normalize_event(raw)
        assert result is None

    def test_no_title_defaults(self):
        raw = {
            "id": "evt4",
            "start": {"dateTime": "2025-06-01T10:00:00Z"},
            "end": {"dateTime": "2025-06-01T11:00:00Z"},
            "status": "confirmed",
        }
        result = _normalize_event(raw)
        assert result is not None
        assert result["title"] == "(No title)"

    def test_no_recurring_event_id(self):
        raw = {
            "id": "evt5",
            "summary": "One-off",
            "start": {"dateTime": "2025-06-01T10:00:00Z"},
            "end": {"dateTime": "2025-06-01T11:00:00Z"},
            "status": "confirmed",
        }
        result = _normalize_event(raw)
        assert result is not None
        assert result["recurringEvent"] is False


class TestSaveCalendarEventsJson:
    def test_saves_json_file(self):
        events = [
            {"id": "e1", "title": "Meeting"},
            {"id": "e2", "title": "Standup"},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "sub" / "events.json"
            result = save_calendar_events_json(events, output_path)

            assert result.exists()
            loaded = json.loads(result.read_text())
            assert len(loaded) == 2
            assert loaded[0]["title"] == "Meeting"

    def test_creates_parent_dirs(self):
        events = [{"id": "e1", "title": "Test"}]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "deep" / "nested" / "dir" / "out.json"
            result = save_calendar_events_json(events, output_path)
            assert result.exists()


class TestFetchCalendarEvents:
    @pytest.mark.asyncio
    async def test_single_page(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "evt1",
                    "summary": "Meeting",
                    "start": {"dateTime": "2025-06-01T09:00:00Z"},
                    "end": {"dateTime": "2025-06-01T10:00:00Z"},
                    "status": "confirmed",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_creds = MagicMock()
        mock_creds.token = "fake-token"

        with patch("google_drive_mcp.services.google_calendar.httpx.AsyncClient", return_value=mock_client):
            events = await fetch_calendar_events(
                calendar_id="test@example.com",
                start_date="2025-06-01",
                end_date="2025-06-30",
                credentials=mock_creds,
            )

        assert len(events) == 1
        assert events[0]["title"] == "Meeting"

    @pytest.mark.asyncio
    async def test_pagination(self):
        page1_response = MagicMock()
        page1_response.json.return_value = {
            "items": [
                {
                    "id": "evt1",
                    "summary": "First",
                    "start": {"dateTime": "2025-06-01T09:00:00Z"},
                    "end": {"dateTime": "2025-06-01T10:00:00Z"},
                    "status": "confirmed",
                }
            ],
            "nextPageToken": "token123",
        }
        page1_response.raise_for_status = MagicMock()

        page2_response = MagicMock()
        page2_response.json.return_value = {
            "items": [
                {
                    "id": "evt2",
                    "summary": "Second",
                    "start": {"dateTime": "2025-06-02T09:00:00Z"},
                    "end": {"dateTime": "2025-06-02T10:00:00Z"},
                    "status": "confirmed",
                }
            ]
        }
        page2_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[page1_response, page2_response])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_creds = MagicMock()
        mock_creds.token = "fake-token"

        with patch("google_drive_mcp.services.google_calendar.httpx.AsyncClient", return_value=mock_client):
            events = await fetch_calendar_events(
                calendar_id="test@example.com",
                start_date="2025-06-01",
                end_date="2025-06-30",
                credentials=mock_creds,
            )

        assert len(events) == 2
        assert events[0]["title"] == "First"
        assert events[1]["title"] == "Second"

    @pytest.mark.asyncio
    async def test_date_range_params(self):
        """Start date → 00:00:00Z, end date → 23:59:59Z."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_creds = MagicMock()
        mock_creds.token = "fake-token"

        with patch("google_drive_mcp.services.google_calendar.httpx.AsyncClient", return_value=mock_client):
            await fetch_calendar_events(
                calendar_id="primary",
                start_date="2025-06-01",
                end_date="2025-06-07",
                credentials=mock_creds,
            )

        _, kwargs = mock_client.get.call_args
        params = kwargs["params"]
        assert params["timeMin"] == "2025-06-01T00:00:00Z"
        assert params["timeMax"] == "2025-06-07T23:59:59Z"

    @pytest.mark.asyncio
    async def test_calendar_id_is_url_encoded(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_creds = MagicMock()
        mock_creds.token = "fake-token"

        with patch("google_drive_mcp.services.google_calendar.httpx.AsyncClient", return_value=mock_client):
            await fetch_calendar_events(
                calendar_id="en.usa#holiday@group.v.calendar.google.com",
                start_date="2025-06-01",
                end_date="2025-06-30",
                credentials=mock_creds,
            )

        args, _ = mock_client.get.call_args
        assert args[0].endswith(
            "calendars/en.usa%23holiday%40group.v.calendar.google.com/events"
        )

    @pytest.mark.asyncio
    async def test_filters_cancelled_events(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "evt1",
                    "summary": "Active",
                    "start": {"dateTime": "2025-06-01T09:00:00Z"},
                    "end": {"dateTime": "2025-06-01T10:00:00Z"},
                    "status": "confirmed",
                },
                {
                    "id": "evt2",
                    "summary": "Cancelled",
                    "start": {"dateTime": "2025-06-01T11:00:00Z"},
                    "end": {"dateTime": "2025-06-01T12:00:00Z"},
                    "status": "cancelled",
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_creds = MagicMock()
        mock_creds.token = "fake-token"

        with patch("google_drive_mcp.services.google_calendar.httpx.AsyncClient", return_value=mock_client):
            events = await fetch_calendar_events(
                calendar_id="test@example.com",
                start_date="2025-06-01",
                end_date="2025-06-30",
                credentials=mock_creds,
            )

        assert len(events) == 1
        assert events[0]["title"] == "Active"
