from __future__ import annotations

from pathlib import Path

import pytest

from google_drive_mcp.tools.google_calendar import (
    build_calendar_events_output_path,
    normalize_date_range,
)


class TestNormalizeDateRange:
    def test_normalizes_valid_dates(self):
        start_date, end_date = normalize_date_range("2025-06-01", "2025-06-07")
        assert start_date == "2025-06-01"
        assert end_date == "2025-06-07"

    def test_rejects_invalid_start_date(self):
        with pytest.raises(ValueError, match="Invalid start_date"):
            normalize_date_range("2025/06/01", "2025-06-07")

    def test_rejects_invalid_end_date(self):
        with pytest.raises(ValueError, match="Invalid end_date"):
            normalize_date_range("2025-06-01", "invalid")

    def test_rejects_reversed_range(self):
        with pytest.raises(ValueError, match="end_date must be on or after start_date"):
            normalize_date_range("2025-06-07", "2025-06-01")


class TestBuildCalendarEventsOutputPath:
    def test_builds_path_in_download_dir(self, tmp_path: Path):
        output_path = build_calendar_events_output_path(
            download_dir=tmp_path,
            start_date="2025-06-01",
            end_date="2025-06-07",
        )
        assert output_path.parent == tmp_path.resolve()
        assert output_path.name == "calendar-events-2025-06-01--2025-06-07.json"

    def test_rejects_path_escape(self, tmp_path: Path):
        with pytest.raises(ValueError, match="normalized in YYYY-MM-DD format"):
            build_calendar_events_output_path(
                download_dir=tmp_path,
                start_date="../../evil",
                end_date="2025-06-07",
            )
