# Authentication setup

## Bitbucket token

- `AGENT_CODEREVIEW_BITBUCKET_TOKEN` must be an Atlassian API token from https://id.atlassian.com/manage-profile/security/api-tokens.
- Do not use a Bitbucket App Password for this variable.

## Jira token by hosting type

- Self-hosted Jira (Server/Data Center):
  - Use a Jira PAT from `Profile -> Personal Access Tokens`.
  - Keep `AGENT_CODEREVIEW_JIRA_EMAIL` unset.
  - Client uses Bearer auth automatically.

- Jira Cloud:
  - Use an Atlassian API token from https://id.atlassian.com/manage-profile/security/api-tokens.
  - Set `AGENT_CODEREVIEW_JIRA_EMAIL` to your Atlassian account email.
  - Client uses Basic auth (`email:token`).

## 401 troubleshooting

- Verify the token type matches your Jira hosting type.
- For Jira Cloud, verify `AGENT_CODEREVIEW_JIRA_EMAIL` is set and correct.
- Verify `AGENT_CODEREVIEW_JIRA_URL` points to the correct Jira instance.
