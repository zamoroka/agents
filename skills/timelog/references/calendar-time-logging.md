# Calendar-Based Time Logging

This reference defines the workflow for logging Jira time based on Google Calendar events.

## When to use

Invoke this workflow when the user asks to log time based on their calendar, for example:

- "log time for this week"
- "log time for today"
- "log my calendar time"
- "log time from calendar for last 3 days"

## Prerequisites

This workflow uses the `calendar_get_events` tool from the `google-drive` MCP server.
If the MCP server is not available, follow the instructions in `~/.agents/mcp/AGENTS.md` to call the tool directly.

## Workflow

### 1. Determine date range

Parse the user's request to extract the time period:

- **today** → start = today, end = tomorrow
- **this week** → start = Monday of current week, end = Sunday + 1 (or today + 1 if mid-week)
- **last N days** → start = today - N, end = tomorrow
- **this month** → start = 1st of current month, end = today + 1

Use ISO format `YYYY-MM-DD` for all dates.

### 2. Fetch calendar events

Call:

```json
{
  "tool": "calendar_get_events",
  "server": "google-drive",
  "input": {
    "start_date": "2026-05-05",
    "end_date": "2026-05-08"
  }
}
```

Then read the saved JSON file from the returned path.

### 3. Filter events

Remove from the list:

- **All-day events** (holidays, OOO, birthdays)
- **Irrelevant events:** lunch, sick leave, personal blocks, focus time, "busy" placeholders
- **Cancelled events** (already filtered by MCP tool, but double-check status field)

Matching for irrelevant events — case-insensitive title contains:
- `lunch`, `обід`, `обед`
- `sick`, `sick leave`
- `personal`, `block`, `focus time`
- `out of office`, `ooo`
- `busy`

### 4. Resolve each event to a Jira issue

For each remaining event:

1. Check `timelog-issue-cache.json` — match event title against `timelog_reasons` entries (case-insensitive, partial match)
2. If the title clearly refers to self-study, training, learning path, or education, use `INTERNALCC-2533`
3. If no cache match, check event title for patterns that suggest a project/issue (e.g., contains project key like `SUNNYR-`, `SWISS-`, `INTERNALCS-`)
4. If still no match, mark as "unmatched" for user to assign

Keep the event as the unit of logging. Do not merge events that resolve to the same issue key.
Repeated issue keys must still be logged as separate Jira worklogs with individual event-title comments.

### 5. Calculate and round duration

For each event:
- Duration = endTime - startTime (in minutes)
- Round up to nearest 15 minutes:
  - 1–15m → 15m
  - 16–30m → 30m
  - 31–45m → 45m
  - 46–60m → 1h
  - etc.

### 6. Check existing Jira worklogs

Before asking for approval, call `fetch_jira_my_timelogs` for a period that covers the calendar range.
Mark likely duplicates as already logged when existing worklog `issueKey + date + duration + comment`
matches the proposed calendar entry. Show already-logged entries separately and do not include them in
the default log batch unless the user explicitly asks to duplicate them.

### 7. Present approval grouped by day

Approval must be day-first, because users review calendar time by day before writing to Jira.
For each day, show:

- The day name and date
- The total time proposed for that day
- One line per calendar event: `ISSUE-KEY — duration — event title`
- Any already-logged entries for that day, clearly marked as not included
- Any overlaps or unmatched events for that day
- The grand total proposed for logging
- Unmatched events listed separately with prompt to assign issue key

Format:

```markdown
Calendar events for 2026-05-05 to 2026-05-07:

**Monday 2026-05-05 — 6h 30m to log:**
- SUNNYR-60 — 15m — Sunny standup
- SUNNYR-60 — 1h — Sunny deploy discussion
- INTERNALCS-1145 — 1h 30m — Architecture review

Already logged:
- INTERNALCC-2533 — 3h — Claude Partner Network Learning Path. Introduction to Model Context Protocol

**Tuesday 2026-05-06 — 2h to log:**
- INTERNALCS-1181 — 1h — 1-1 Siemen / Pavlo
- INTERNALCS-1181 — 1h — Manager reviews

**Unmatched events:**
- "New initiative planning" (1h) — which issue?

**Grand total to log: 8h 30m**
```

### 8. Approval and logging

- Ask for a single combined approval after the day-grouped proposal: "Log all proposed entries above? (y/adjust/n)"
- If user wants to adjust: let them reassign unmatched events or change durations
- For unmatched events without an assigned issue: ask user for the issue key
- If events overlap, ask whether to log scheduled time or wall-clock time before writing; then apply that choice consistently to the batch
- After approval, log each calendar event via a separate `add_jira_timelog` call with:
  - `timeSpent`: rounded duration in Jira format (e.g., "1h 15m")
  - `comment`: the individual event title, not a concatenation of multiple events
  - `started`: event start timestamp in Jira datetime format (`YYYY-MM-DDTHH:mm:ss.000+0000`)
- After each `add_jira_timelog`, require a created worklog response with `id`, `issueId`, `timeSpent`, and `started`.
  If the response looks like an existing worklog list (`startAt`, `maxResults`, `worklogs`) or does not confirm creation,
  stop immediately and fix/restart the Jira MCP before continuing.
- Update `timelog-issue-cache.json` with any new issue mappings

### 9. Confirm

Report what was logged:
- Per-day confirmation with one line per created worklog
- Total logged time for the period
