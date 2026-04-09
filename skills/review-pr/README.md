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
- If Jira issue key is provided, agent checks `.env.local` for required API vars and runs `jira-fetch` to generate OpenAI summary.
- Agent checks whether Jira issue scope is aligned with PR implementation, then performs regular PR review (code quality, standards, etc.).
- Agent saves PR review artifact(s) at the end.

## Inputs

- PR URL from user.
- Optional Jira issue key confirmation from user.
- Environment values in `$PROJECT_ROOT/.env.local` when Jira summary step is used.

## Token setup tip

- Bitbucket API token: generate at `https://id.atlassian.com/manage-profile/security/api-tokens`.
- Jira API token/PAT: use a **standard Atlassian API token** from `https://id.atlassian.com/manage-profile/security/api-tokens` (use the regular **Create API token** option, not **Create API token with scopes**, unless your org explicitly requires scoped tokens).

## Outputs

- PR review artifacts in `$PROJECT_ROOT/.agents/artifacts/`.
- PR diff artifact `pr-<pr-no>-diff.patch` in `$PROJECT_ROOT/.agents/artifacts/`, including PR metadata in top comment lines (title, author, description, etc.).
- Jira summary artifact `pr-<pr-no>-issue-summary.md` when Jira step is used.
