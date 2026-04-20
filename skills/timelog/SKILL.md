---
name: timelog
description: "Summarizes Jira timelogs for a recent period and explains what work was done by project and issue. Use when the user asks for logged time reports such as 'my timelogs for last 30 days'."
metadata:
  version: "1.0.0"
  category: "engineering"
---

# timelog

Generate a Jira timelog report for the current user and present it in clear project-level and issue-level sections.

## When to use

Invoke this skill when user asks for time reports, for example:
- "What are my timelogs for last 30 days?"
- "Show where I spent time this month"
- "Summarize my Jira logged time by project"

## Inputs

- Period in days if user specifies it (e.g. 7, 14, 30, 90)
- If no period is provided, default to `30` days

## Tool call

Call Jira MCP tool:

```json
{
  "tool": "fetch_jira_my_timelogs",
  "input": {
    "days": 30
  }
}
```

If user explicitly provides Jira auth overrides, pass them through (`jiraBaseUrl`, `jiraApiToken`, `jiraEmail`, `jiraAuthType`).

## Response style

Return a concise human summary using tool output:
- Total logged time for the period
- Breakdown by project (highest time first)
- Top issues per project
- Short "what was done" bullets from worklog descriptions/comments

If no entries exist, reply with a clear no-data message and include checked period.

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
