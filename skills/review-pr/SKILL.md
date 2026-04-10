---
name: review-pr
description: "Reviews Bitbucket pull requests, summarizes diffs, and produces inline findings artifacts. Use when the user asks to review a PR, inspect PR changes, or run a pull request code review."
metadata:
  version: "2.1.0"
  category: "engineering"
---

# review-pr

Review a pull request. Findings are displayed in the terminal and saved as artifacts under `<project>/.agents/artifacts/`.

**Agent assumptions (applies to all agents and subagents):**

- All tools are functional and will work without error. Do not test tools or make exploratory calls. Make sure this is clear to every subagent that is launched.
- Only call a tool if it is required to complete the task. Every tool call should have a clear purpose.

---

## Step 0 — Ask for PR URL

Ask the user for the pull request URL.

When provided, validate format and detect provider:
- Bitbucket PR URL format: `https://bitbucket.org/<workspace>/<repo>/pull-requests/<number>`
- GitHub PR URL format: `https://github.com/<owner>/<repo>/pull/<number>`

If provider is GitHub: respond with `not supported yet` and stop.

Extract and store:
- `PR_URL`
- `PR_PROVIDER` (`bitbucket`)
- `PR_NUMBER`

---

## Step 1 — Detect project root

Check if the current working directory contains an `AGENTS.md` file.

- **If yes** → `PROJECT_ROOT` = current working directory.
- **If no** → Ask the user: *"You don't appear to be inside a project folder. Please provide the absolute path to the project root."* Wait for their response, then set `PROJECT_ROOT` to the provided path. Verify that `AGENTS.md` exists there before continuing.

---

## Step 2 — Bootstrap `.env.local`

Check `$PROJECT_ROOT/.env.local` for the following variables:

```
AGENT_CODEREVIEW_BITBUCKET_EMAIL
AGENT_CODEREVIEW_BITBUCKET_TOKEN
AGENT_CODEREVIEW_JIRA_URL
AGENT_CODEREVIEW_JIRA_TOKEN
OPENAI_API_KEY
```

For each missing variable, ask the user to provide the value (ask all missing variables at once in a single prompt, not one by one). Then append the missing variables to `$PROJECT_ROOT/.env.local`.

Also ensure `.env.local` is listed in `$PROJECT_ROOT/.gitignore`. If it is not, append `.env.local` to the `.gitignore` file.

> **Token note:** `AGENT_CODEREVIEW_BITBUCKET_TOKEN` must be an Atlassian API token (from https://id.atlassian.com/manage-profile/security/api-tokens), not a Bitbucket App Password.
>
> **Jira token note:** Authentication method depends on Jira hosting type:
> - **Self-hosted Jira (Server / Data Center):** Generate a PAT from *Profile → Personal Access Tokens*. Leave `AGENT_CODEREVIEW_JIRA_EMAIL` unset — the client will use Bearer auth automatically.
> - **Jira Cloud:** Use an Atlassian API token from https://id.atlassian.com/manage-profile/security/api-tokens. You must also add `AGENT_CODEREVIEW_JIRA_EMAIL` (your Atlassian account email) to `.env.local` — the client uses Basic auth (`email:token`) for Cloud.
>
> If you receive a 401 on the Jira fetch step, check which type of token is being used and whether `AGENT_CODEREVIEW_JIRA_EMAIL` is needed.

---

## Step 3 — Fetch PR data

Run the Bitbucket Node module, passing the project root:

```bash
npm install --prefix ~/.agents/skills/review-pr
PROJECT_ROOT="{PROJECT_ROOT}" npm --prefix ~/.agents/skills/review-pr --workspace pr-fetch run fetch:pr -- bitbucket {PR_URL}
```

This outputs PR details, comments, changed files, and full diff to stdout, and saves the diff artifact to `$PROJECT_ROOT/.agents/artifacts/pr-{PR_NUMBER}-diff.patch` with Bitbucket metadata in comment lines at the top (title, author, description, and related PR fields).

---

## Step 4 — Determine Jira issue key

The main agent must detect Jira issue key from PR data (title, branch, description, comments, changed files).

Always ask user to confirm detected key.
- If detected: ask `I found {ISSUE_KEY}. Correct?`
- If not detected: ask user to provide Jira issue key, or confirm skipping Jira step.

If user says PR is not related to Jira, skip Step 5 and Step 9 ticket-alignment check.

---

## Step 5 — Gather and summarize Jira ticket

Run the Jira Node entrypoint with the detected Jira key (for example `SUNNYR-25`). It fetches the ticket, summarizes it with a small OpenAI model, and writes:

- `$PROJECT_ROOT/.agents/artifacts/pr-{PR_NUMBER}-issue-summary.md`

Command:

```bash
npm install --prefix ~/.agents/skills/review-pr
PROJECT_ROOT="{PROJECT_ROOT}" npm --prefix ~/.agents/skills/review-pr --workspace jira-fetch run fetch:jira -- {PR_NUMBER} {ISSUE_KEY}
```

---

## Step 6 — Load relevant AGENTS.md files and detect project type

Launch an agent (model: haiku) to return a list of file paths (not their contents) for all relevant `AGENTS.md` files including:
- The root `AGENTS.md` at `$PROJECT_ROOT/AGENTS.md`
- Any `AGENTS.md` files in directories containing files modified by the pull request

Then read the root `$PROJECT_ROOT/AGENTS.md` and detect `PROJECT_TYPE` from explicit project identifiers.

For now support only:
- If AGENTS.md indicates Magento 2 / Adobe Commerce -> `PROJECT_TYPE=magento2`
- Otherwise -> `PROJECT_TYPE=unknown`

---

## Step 7 — Load project intelligence provider

Select an LSP/MCP provider based on `PROJECT_TYPE` and load system context before summarizing/reviewing code.

Current mapping:
- `magento2` -> use `magento2-lsp-mcp` (`npm install -g @mage-os/magento2-lsp`)

For `magento2`, the summarizer and review agents must call Magento MCP tools for changed PHP/XML areas to validate merged Magento behavior (DI preferences/plugins, event observers, template/layout wiring, config-driven behavior) instead of relying on raw file reading alone.

If `PROJECT_TYPE=unknown`, continue without LSP/MCP enrichment.

---

## Step 8 — Summarise the PR

Launch an agent to view the pull request diff and return a concise summary of the changes.

---

## Step 9 — Review

Launch 2 agents in parallel to independently review the changes. Each agent MUST return issues in this exact structured format — one JSON object per issue:

```
{"path": "app/code/Vaimo/Module/File.php", "line": 42, "severity": "warning", "description": "Description of the issue and suggested fix"}
```

- `path` — the file path as shown in the diff (relative to repo root)
- `line` — the line number in the **new version** of the file where the issue occurs (from the diff `+` side / `@@` hunk headers). If the issue is general and not tied to a specific line, use `0`.
- `severity` — one of: `error`, `warning`, `suggestion`
- `description` — what the issue is, why it was flagged, and how to fix it

Before review, load and apply rules from `review-guardrails.md`.
If the PR is a pure deletion, also apply `deletion-pr-checklist.md`.

If Jira step was not skipped, first launch 1 local agent to compare PR diff with `$PROJECT_ROOT/.agents/artifacts/pr-{PR_NUMBER}-issue-summary.md` and decide if implementation matches ticket scope. Return mismatches in the same issue JSON format (`line` can be `0` when mismatch is not line-specific).

If `PROJECT_TYPE=magento2`, both review agents must use `magento2-lsp-mcp` tool calls as evidence for Magento-specific claims.

Run both agents with distinct focus:
- **Agent 1 (model: sonnet): code-quality-pragmalist**
- **Agent 2 (model: sonnet): compliance-checker**

Merge findings from all launched agents.

---

## Step 10 — Assemble and save artifacts

Assume `$PROJECT_ROOT/.agents/artifacts/` already exists. Create it only if artifact write fails due to missing directory.

Save two files:

**a. Summary** → `$PROJECT_ROOT/.agents/artifacts/pr-review-{PR_NUMBER}.md`

Format:
```
{If no issues: "✅ No issues found"}
{If issues: "⚠️ {N} issue(s) found — see inline comments"}

🤖 *Reviewed by Agent ({MODEL_ID})*
```

**b. Inline comments** → `$PROJECT_ROOT/.agents/artifacts/pr-review-{PR_NUMBER}-inline.json`

Format:
```json
[
  {
    "path": "app/code/Vaimo/Module/File.php",
    "line": 42,
    "content": "**warning** — Description of the issue and suggested fix\n\n🤖 *Reviewed by Agent ({MODEL_ID})*"
  }
]
```

Only include issues where `line > 0`. Format each `content` field as: `**{severity}** — {description}\n\n🤖 *Reviewed by Agent ({MODEL_ID})*`.

If no issues were found, write an empty array `[]` to the inline JSON file.

Display the full review in the terminal.

---

## Additional references

- `review-guardrails.md` — behavior-claim evidence rule, reviewer scopes, and false-positive filters
- `deletion-pr-checklist.md` — extra checks for pure-deletion PRs

---

## Notes

- For Bitbucket PR fetch, use `npm --prefix ~/.agents/skills/review-pr --workspace pr-fetch run fetch:pr -- bitbucket {PR_URL}`.
- For GitHub PR URLs, respond with `not supported yet`.
- Use `npm --prefix ~/.agents/skills/review-pr --workspace jira-fetch run fetch:jira -- {PR_NUMBER} {ISSUE_KEY}` to fetch and summarize Jira ticket data for the PR.
- Detect project type from `$PROJECT_ROOT/AGENTS.md` and load the mapped LSP/MCP provider before PR summarization/review.
- For Magento projects, use `magento2-lsp-mcp` for merged-config/system understanding during review.
- Create a todo list before starting.
- When citing AGENTS.md rules, quote the relevant rule text directly.
