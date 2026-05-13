#!/usr/bin/env python3
"""Compute absolute ISO date ranges from relative period strings.

Used by the calendar-whats-done workflow so the date math is locale-safe
and the model does not have to do arithmetic in its head.

Usage:
    python3 compute_period.py this-week
    python3 compute_period.py last-week
    python3 compute_period.py this-month
    python3 compute_period.py last-month
    python3 compute_period.py custom --start 2026-05-01 --end 2026-05-08

Output: a JSON object with ISO `start` and `end` dates (end is exclusive,
so a query for "this week" returns Monday through today+1).
"""

import argparse
import json
import sys
from datetime import date, timedelta


def monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def first_of_month(d: date) -> date:
    return d.replace(day=1)


def first_of_prev_month(d: date) -> date:
    first = first_of_month(d)
    return first_of_month(first - timedelta(days=1))


def compute(period: str, today: date, start: str | None, end: str | None) -> dict:
    if period == "this-week":
        return {"start": monday_of(today).isoformat(), "end": (today + timedelta(days=1)).isoformat()}
    if period == "last-week":
        this_mon = monday_of(today)
        return {"start": (this_mon - timedelta(days=7)).isoformat(), "end": this_mon.isoformat()}
    if period == "this-month":
        return {"start": first_of_month(today).isoformat(), "end": (today + timedelta(days=1)).isoformat()}
    if period == "last-month":
        return {"start": first_of_prev_month(today).isoformat(), "end": first_of_month(today).isoformat()}
    if period == "custom":
        if not (start and end):
            raise SystemExit("custom period requires --start and --end")
        return {"start": start, "end": end}
    raise SystemExit(f"unknown period: {period}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("period", choices=["this-week", "last-week", "this-month", "last-month", "custom"])
    parser.add_argument("--start", help="ISO start date for custom period")
    parser.add_argument("--end", help="ISO end date for custom period (exclusive)")
    parser.add_argument("--today", help="Override today's date (ISO, for testing)")
    args = parser.parse_args()

    today = date.fromisoformat(args.today) if args.today else date.today()
    result = compute(args.period, today, args.start, args.end)
    json.dump(result, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
