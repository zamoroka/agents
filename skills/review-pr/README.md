# Review

## Flow

- Agent always asks user to confirm project root, or asks for absolute project root path if it is not clear.
- Agent asks for PR URL.
- User provides PR URL.
- Agent validates URL shape, detects git provider, and runs `pr-fetch` with provider + PR URL for Bitbucket.
- If provider is GitHub, agent responds: `not supported yet`.
- `pr-fetch` returns PR details, comments, and full diff to the agent.
- Agent determines Jira issue key from PR data.
- Agent always asks user to confirm detected Jira issue key.
- If key is not in PR details, agent asks user to provide one or confirm skipping Jira step when PR is not Jira-related.
- If Jira issue key is provided, agent checks `.env.local` for required API vars, calls `jira-mcp` tool `fetch_jira_issue_ai_summary`, and saves the returned markdown summary to the issue-summary artifact file.
- Agent checks whether Jira issue scope is aligned with PR implementation, then performs regular PR review (code quality, standards, etc.).
- Agent saves PR review artifact(s) at the end.

## Inputs

- PR URL from user.
- Optional Jira issue key confirmation from user.
- Environment values in `$PROJECT_ROOT/.env.local` for Bitbucket fetch.
- Jira/LLM values in `~/.agents/mcp/jira-mcp/.env` (or passed as MCP tool arguments) when Jira summary step is used.

## Token setup tip

- Bitbucket API token: generate at `https://id.atlassian.com/manage-profile/security/api-tokens`.
- Jira API token/PAT: use a **standard Atlassian API token** from `https://id.atlassian.com/manage-profile/security/api-tokens` (use the regular **Create API token** option, not **Create API token with scopes**, unless your org explicitly requires scoped tokens).

## Outputs

- PR review artifacts in `$PROJECT_ROOT/.agents/artifacts/`.

## Runtime notes

- Prefer execution-first flow: run the main command and remediate concrete failures (missing files/dirs/deps/env) instead of broad pre-check passes.
- `pr-fetch` requires a Node runtime with global `fetch` support (Node 18+).
- If the local default Node is older (for example Node 17) and commands fail with `fetch is not defined`, run PR fetch with Node 25 and run Jira via `uv`:
  - `PROJECT_ROOT="{PROJECT_ROOT}" npx -y node@25 --loader ts-node/esm src/function.ts bitbucket {PR_URL}` from `~/.agents/skills/review-pr/scripts/pr-fetch`
  - `uv run jira-mcp` from `~/.agents/mcp/jira-mcp`
- `magento2-lsp-mcp` is expected to be preinstalled in this environment; skip reinstall in standard review runs.

### Artifact naming convention

- Format: `<YYYY>-<mm>-<dd>-pr-<repo_slug>-<number>-<artifact_type>`
- `repo_slug` is extracted from PR URL repo segment (example: `project_sunny-eu` from `https://bitbucket.org/vaimo/project_sunny-eu/pull-requests/726/`)
- `number` is extracted from PR URL PR number segment (example: `726`)
- `artifact_type` examples: `diff`, `issue-summary`, `review`

Examples in `$PROJECT_ROOT/.agents/artifacts/`:
- `YYYY-mm-dd-pr-<repo_slug>-<number>-diff.patch`
- `YYYY-mm-dd-pr-<repo_slug>-<number>-issue-summary.md`
- `YYYY-mm-dd-pr-<repo_slug>-<number>-review.md`

### Review artifact content

- Put the complete review into `-review.md`.
- Include findings, suggested fixes, and optional code snippets in the same file.
- Do not create a separate `-review-inline.json` artifact.
