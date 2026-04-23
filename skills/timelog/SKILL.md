---
name: timelog
description: "Summarizes Jira timelogs and logs new time entries in Jira. Use when the user asks for time reports or asks to log time (for example 'log 15m to SUNNYR-60' or 'log time on jira to pr PoC')."
metadata:
  version: "1.6.0"
  category: "engineering"
---

# timelog

Generate Jira timelog reports and add Jira worklogs with lightweight issue mapping cache.

This skill must use the Jira MCP server defined in `mcp/jira-mcp`.

## When to use

Invoke this skill when user asks for time reports or to log time, for example:
- "What are my timelogs for last 30 days?"
- "Show where I spent time this month"
- "Summarize my Jira logged time by project"
- "log 15m to SUNNYR-60"
- "log time on jira to pr PoC"

## Cache file

Use `skills/timelog/timelog-issue-cache.json`.

Schema:

```json
{
  "SUNNYR-57": {
    "issue_title": "Agile activities",
    "issue_description": "*USERSTORY*: ...",
    "timelog_reasons": ["internal sunny meeting", "sunny 1-1", "sunny daily meeting"]
  }
}
```

Rules:
- Always read this file first for log-time requests without explicit issue key.
- As soon as issue key is confirmed, update/create entry in this file.
- Never add duplicates to `timelog_reasons` (normalize trim + lowercase before compare).
- Append new reason phrase only when normalized value does not already exist.
- Always refresh `issue_title` and `issue_description` when newly fetched from Jira.

## Inputs

- Reporting: period in days if provided (e.g. 7, 14, 30, 90), default `30`.
- Logging: parse requested duration and reason text from user message.
- Logging date: if user specifies date, use it; otherwise use today's date.

## Jira MCP tools

Use only tools exposed by the `jira-mcp` server documented in `mcp/jira-mcp/README.md`.

- Reporting: `fetch_jira_my_timelogs`
- Log time: `add_jira_timelog`
- Issue details for cache refresh: `fetch_jira_issue_details`

Do not use direct Jira REST calls from this skill.

### Reporting

Call:

```json
{
  "tool": "fetch_jira_my_timelogs",
  "input": {
    "days": 30
  }
}
```

### Log time

Call:

```json
{
  "tool": "add_jira_timelog",
  "input": {
    "issueKey": "SUNNYR-60",
    "timeSpent": "15m",
    "comment": "pr poc",
    "started": "2026-04-20T09:00:00.000+0000"
  }
}
```

Pass Jira auth overrides if explicitly provided by user (`jiraBaseUrl`, `jiraApiToken`, `jiraEmail`, `jiraAuthType`).
If overrides are not provided, rely on `mcp/jira-mcp/.env` as described in `mcp/jira-mcp/README.md`.

## Logging workflow

1. Extract `timeSpent`, candidate issue, candidate comment/reason, and optional date from user text.
2. If time amount is missing, ask: "How much time should be logged?" and wait for answer.
3. Resolve logging date:
   - If user provided a date, use it.
   - If no date is provided, use today's date.
   - Build `started` in Jira datetime format (`YYYY-MM-DDTHH:mm:ss.000+0000`) using local timezone.
4. Resolve issue key:
   - If explicit issue key is provided, use it.
   - If not, check `skills/timelog/timelog-issue-cache.json` first (match `timelog_reasons`, then title).
   - If cache match found, always ask for approval: "I found <ISSUE_KEY> (<ISSUE_TITLE>) from cache. Is this the right issue?"
   - Never auto-log from cache without explicit user approval when issue key was not provided in the message.
   - If user says no, call `fetch_jira_my_timelogs` with `days=30`, infer best candidates, and ask confirmation again (or let user provide exact key).
   - If issue key is inferred from previous timelogs, always ask for explicit approval before logging.
   - Never auto-log from inferred previous-timelog match when issue key was not provided in the message.
5. Before writing, confirm comment text too (for example: "Use comment '<COMMENT>'?"). If comment is missing or unclear, ask user to provide one.
6. After user confirms issue + time + date + comment, fetch issue details with `fetch_jira_issue_details` for the final issue key.
7. Update `skills/timelog/timelog-issue-cache.json` for the final issue key:
   - upsert `issue_title`, `issue_description`
   - upsert normalized reason/comment in `timelog_reasons` without duplicates
8. Call `add_jira_timelog` with `started`.
9. Confirm logged time back to user with issue key, duration, date, and comment.

## Response style

For reports, return concise summary:
- Total logged time for the period
- Breakdown by project (highest time first)
- Top issues per project
- Short "what was done" bullets from worklog descriptions/comments

If no entries exist, reply with a clear no-data message and include checked period.

For log-time actions:
- Confirm what was logged and where.
- If resolution was inferred, include that confirmation step before writing.

## Output template

Use this structure:

1. Period + total time
2. Project breakdown
3. Key completed activities

Example:

```markdown
Last 30 days: 42h 15m logged.

- PROJECT-A (24h)
  - PROJECT-A-101 (10h): Implemented checkout API validation and bug fixes.
  - PROJECT-A-132 (8h): Added tests and deployment follow-ups.

- PROJECT-B (18h 15m)
  - PROJECT-B-44 (12h): Refactored import flow and improved error handling.
```
