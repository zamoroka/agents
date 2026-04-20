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

## Notes for agent workflows

- This server does not write artifacts.
- Agents that need markdown files should save `summary` output themselves (for example under `.agents/artifacts/`).
