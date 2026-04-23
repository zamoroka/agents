# jira-mcp

MCP server that provides Jira tools for pull request workflows.

## Tools

### `fetch_jira_issue_details`

Fetches raw Jira issue details by key.

Input:

```json
{
  "issueKey": "SUNNYR-60",
  "jiraBaseUrl": "https://jira.example.com",
  "jiraApiToken": "optional-override-token",
  "jiraEmail": "optional-user@example.com",
  "jiraAuthType": "auto|bearer|basic'"
}
```

Required input:
- `issueKey`

Optional overrides (override `.env` values when provided):
- `jiraBaseUrl`
- `jiraApiToken`
- `jiraEmail`
- `jiraAuthType` (`auto` | `bearer` | `basic`)

Response:
- JSON string with full Jira issue payload from Jira REST API.

### `fetch_jira_my_timelogs`

Fetches current user's Jira worklogs for a rolling period and returns a grouped summary by project and issue.

Input:

```json
{
  "days": 30,
  "jiraBaseUrl": "https://jira.example.com",
  "jiraApiToken": "optional-override-token",
  "jiraEmail": "optional-user@example.com",
  "jiraAuthType": "auto|bearer|basic"
}
```

Required input:
- none

Optional overrides:
- `days` (default `30`, range `1..365`)
- Jira overrides: `jiraBaseUrl`, `jiraApiToken`, `jiraEmail`, `jiraAuthType`

Response:
- JSON string containing:
  - `period` (`from`, `to`, `days`)
  - `author`
  - `totalTimeSeconds` and `totalTime`
  - `projects[]` with per-project and per-issue totals
  - `details[]` with each worklog item and short description of what was done
  - `markdownSummary` ready for direct user-facing reporting

### `add_jira_timelog`

Adds a Jira worklog entry to an issue.

Input:

```json
{
  "issueKey": "SUNNYR-60",
  "timeSpent": "15m",
  "timeSpentSeconds": 900,
  "comment": "PR PoC review and notes",
  "started": "2026-04-20T10:15:00.000+0000",
  "jiraBaseUrl": "https://jira.example.com",
  "jiraApiToken": "optional-override-token",
  "jiraEmail": "optional-user@example.com",
  "jiraAuthType": "auto|bearer|basic"
}
```

Required input:
- `issueKey`
- one of `timeSpent` or `timeSpentSeconds`

Optional:
- `comment`
- `started` (Jira datetime format)
- Jira overrides: `jiraBaseUrl`, `jiraApiToken`, `jiraEmail`, `jiraAuthType`

Response:
- JSON string with created Jira worklog payload.

### `fetch_jira_issue_ai_summary`

Fetches Jira issue details first, then generates a markdown summary via LLM.

Input:

```json
{
  "issueKey": "SUNNYR-60",
  "jiraBaseUrl": "https://jira.example.com",
  "jiraApiToken": "optional-override-token",
  "jiraEmail": "optional-user@example.com",
  "jiraAuthType": "auto",
  "openaiApiKey": "optional-override-openai-key",
  "openaiModel": "gpt-5.4-nano"
}
```

Required input:
- `issueKey`

Optional overrides:
- Jira overrides: `jiraBaseUrl`, `jiraApiToken`, `jiraEmail`, `jiraAuthType`
- LLM overrides: `openaiApiKey`, `openaiModel`

Response:
- JSON string:
  - `issueKey`
  - `model`
  - `summary` (markdown text)

## Environment file

Server loads config from `mcp/jira-mcp/.env`.

If `.env` does not exist, the server creates a placeholder file automatically.

Supported variables:

```bash
JIRA_URL=
JIRA_TOKEN=
JIRA_EMAIL=
JIRA_AUTH_TYPE=auto
OPENAI_API_KEY=
JIRA_SUMMARY_OPENAI_MODEL=gpt-5.4-nano
```

Precedence:
1. Tool call arguments
2. `.env` values

## Auth behavior

- `jiraAuthType=auto`: tries Bearer first; if Jira returns `401` and `jiraEmail` exists, retries with Basic auth.
- `jiraAuthType=bearer`: only Bearer auth.
- `jiraAuthType=basic`: only Basic auth (`jiraEmail` required).

## Local run

From `mcp/jira-mcp`:

```bash
npm run start
```

## MCP client config example

Use a JSONC MCP config (for example in `~/.mcp.json`) and add this server under `servers`:

```jsonc
{
  "servers": {
    "jira-mcp": {
      "type": "stdio",
      "command": "npm",
      "args": ["run", "start", "--prefix", "/Users/zamoroka_pavlo/.agents/mcp/jira-mcp"],
      "env": {
        "JIRA_URL": "https://jira.example.com",
        "JIRA_TOKEN": "your_jira_token",
        "JIRA_EMAIL": "user@example.com",
        "JIRA_AUTH_TYPE": "auto",
        "OPENAI_API_KEY": "your_openai_api_key",
        "JIRA_SUMMARY_OPENAI_MODEL": "gpt-5.4-nano"
      }
    }
  }
}
```

If you already use `mcp/jira-mcp/.env`, you can keep `env` empty or omit values that are already in that file.

## Notes for agent workflows

- This server does not write artifacts.
- Agents that need markdown files should save `summary` output themselves (for example under `.agents/artifacts/`).
