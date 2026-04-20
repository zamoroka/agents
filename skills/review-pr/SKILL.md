---
name: review-pr
description: "Reviews Bitbucket pull requests, summarizes diffs, and produces a full review artifact. Use when the user asks to review a PR, inspect PR changes, or run a pull request code review."
metadata:
  version: "2.1.6"
  category: "engineering"
---

# review-pr

Review a pull request. Findings are displayed in the terminal and saved as artifacts under `<project>/.agents/artifacts/`.

**Agent assumptions (applies to all agents and subagents):**

- All tools are functional and will work without error. Do not test tools or make exploratory calls. Make sure this is clear to every subagent that is launched.
- Only call a tool if it is required to complete the task. Every tool call should have a clear purpose.

## Shared runtime fallback (Node 25)

If default Node is older than 18 and a fetch step fails with `fetch is not defined`, use Node 25 wrappers from the workspace directory:

- PR fetch (run in `~/.agents/skills/review-pr/scripts/pr-fetch`):
  - `PROJECT_ROOT="{PROJECT_ROOT}" npx -y node@25 --loader ts-node/esm src/function.ts bitbucket {PR_URL}`
- Jira MCP server (run in `~/.agents/mcp/jira-mcp`):
  - `PROJECT_ROOT="{PROJECT_ROOT}" npx -y node@25 --loader ts-node/esm src/function.ts`

Dependency note for fetch steps:
- Assume dependencies are already installed.
- Only run `npm install --prefix ~/.agents/skills/review-pr/scripts` if a fetch command fails due to missing modules/dependencies.
- Only run `npm install --prefix ~/.agents/mcp/jira-mcp` if Jira MCP startup/tool calls fail due to missing modules/dependencies.

---

## Step 0 — Ask for PR URL

Ask the user for the pull request URL.

When provided, validate format and detect provider:
- Bitbucket PR URL format: `https://bitbucket.org/<workspace>/<repo_slug>/pull-requests/<number>`
- GitHub PR URL format: `https://github.com/<owner>/<repo_slug>/pull/<number>`

If provider is GitHub: respond with `not supported yet` and stop.

Extract and store:
- `PR_URL`
- `PR_PROVIDER` (`bitbucket`)
- `REPO_SLUG`
- `PR_NUMBER`

---

## Step 1 — Detect project root

Check if the current working directory contains an `AGENTS.md` and file.

- **If yes** → `PROJECT_ROOT` = current working directory.
- **If no** → Ask the user: *"You don't appear to be inside a project folder. Please provide the absolute path to the project root."* Wait for their response, then set `PROJECT_ROOT` to the provided path. Verify that `AGENTS.md` exists there before continuing.

---

## Step 2 — Bootstrap `.env.local`

Check `$PROJECT_ROOT/.env.local` for the following variables:

```
AGENT_CODEREVIEW_BITBUCKET_EMAIL
AGENT_CODEREVIEW_BITBUCKET_TOKEN
```

For each missing variable, ask the user to provide the value (ask all missing variables at once in a single prompt, not one by one). Then append the missing variables to `$PROJECT_ROOT/.env.local`.

Also ensure `.env.local` is listed in `$PROJECT_ROOT/.gitignore`. If it is not, append `.env.local` to the `.gitignore` file.

Jira MCP credentials are not read from `$PROJECT_ROOT/.env.local`. They must be set in `~/.agents/mcp/jira-mcp/.env` (or passed directly in tool arguments).

For token requirements and Jira/Bitbucket authentication troubleshooting, use `./shared/auth-setup.md`.

---

## Step 3 — Fetch PR data

Run the Bitbucket Node module, passing the project root:

```bash
PROJECT_ROOT="{PROJECT_ROOT}" npm --prefix ~/.agents/skills/review-pr/scripts --workspace pr-fetch run fetch:pr -- bitbucket {PR_URL}
```

If needed, use the shared Node 25 fallback above.

This outputs PR details, comments, changed files, and full diff to stdout, and saves the diff artifact to `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-diff.patch` with Bitbucket metadata in comment lines at the top (title, author, description, and related PR fields).

---

## Step 4 — Determine Jira issue key

The main agent must detect Jira issue key from PR data (title, branch, description, comments, changed files).

Always ask user to confirm detected key.
- If detected: ask `I found {ISSUE_KEY}. Correct?`
- If not detected: ask user to provide Jira issue key, or confirm skipping Jira step.

If user says PR is not related to Jira, skip Step 5 and Step 9 ticket-alignment check.

---

## Step 5 — Gather and summarize Jira ticket

Call the `jira-mcp` MCP tool `fetch_jira_issue_ai_summary` with the detected Jira key (for example `SUNNYR-25`).

Tool input:

```json
{"issueKey":"{ISSUE_KEY}"}
```

The tool returns JSON containing `summary` markdown text. The agent must write that summary to:

- `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-issue-summary.md`

When writing this file, use this exact wrapper:

```md
# PR {PR_NUMBER} issue summary

Jira ticket: {ISSUE_KEY}

{summary}
```

If artifact write fails because the directory does not exist, create `$PROJECT_ROOT/.agents/artifacts/` and retry.

If needed, use the shared Node 25 fallback above to start `jira-mcp`.

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
- `magento2` -> use `magento2-lsp-mcp`

Environment note:
- `magento2-lsp-mcp` is expected to be preinstalled in this environment; do not reinstall it during normal review flow.

For `magento2`, the summarizer and review agents must call Magento MCP tools for changed PHP/XML areas to validate merged Magento behavior (DI preferences/plugins, event observers, template/layout wiring, config-driven behavior) instead of relying on raw file reading alone.

See `./shared/magento2-lsp-mcp-usage.md` for the expected evidence workflow.

If `PROJECT_TYPE=unknown`, continue without LSP/MCP enrichment.

---

## Step 8 — Summarise the PR

Launch an agent to view the pull request diff and return a concise summary of the changes.

---

## Step 9 — Review

Launch 3 agents with ordering constraints. Each agent that returns issues MUST use this exact structured format — one JSON object per issue:

```
{"path": "app/code/Vaimo/Module/File.php", "line": 42, "severity": "warning", "description": "Description of the issue and suggested fix"}
```

- `path` — the file path as shown in the diff (relative to repo root)
- `line` — the line number in the **new version** of the file where the issue occurs (from the diff `+` side / `@@` hunk headers). If the issue is general and not tied to a specific line, use `0`.
- `severity` — one of: `error`, `warning`, `suggestion`
- `description` — what the issue is, why it was flagged, and how to fix it

Before review, load and apply rules from `./shared/review-guardrails.md`.
If the PR is a pure deletion, also apply `./shared/deletion-pr-checklist.md`.

If Jira step was not skipped, run this sequence:

1. Run **Agent 1 (reasoning: medium): code-quality-checker** for code-review findings. 
   - This agent can work in parallel with others.
   - Checks code quality of the PR diff based on project specifications and rules as if the diff is already applied to the codebase.
   - Focus on correctness, runtime risk, logic defects, API misuse, and missing edge-case handling.
   - Flag any potential security concerns with severity `error` and detailed explanation.

2. Do not wait for **Agent 1** output and launch **Agent 2 (reasoning: medium): default-functionality-checker**.
   - Goal: check whether the Jira request can be covered by functionality that already exists in the project.
   - Strict constraint: this agent must not inspect or use the PR diff.
   - Inputs allowed: project source code/context, AGENTS.md guidance, and `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-issue-summary.md`.
   - Output behavior:
     - If existing functionality can cover the Jira request, propose using default/existing functionality.
     - If not, provide an implementation plan.
   - Artifact update rule:
     - Do not edit or rewrite existing sections in the issue summary file.
     - Append one new block at the end of the file titled exactly `## Agent proposal implementation`.
     - The block must contain either:
       - `Decision: Use existing/default functionality` + concrete proposal details, or
       - `Decision: New implementation required` + concise implementation plan.

3. After **Agent 2** finishes and the issue summary append is complete, launch the **Agent 3 (reasoning: medium): ticket-alignment** agent to compare PR diff with the updated issue summary file and return mismatches.
    - Agent checks if the PR implementation aligns with the Jira issue requirements and acceptance criteria as summarized in the issue summary artifact, including any updates from Agent 2.
    - For any misalignment, return an issue with severity `warning` and description explaining the mismatch and what would be needed to align the PR with the Jira issue.

If `PROJECT_TYPE=magento2`, all review agents that make Magento-specific claims must use `magento2-lsp-mcp` tool calls as evidence.

---

## Step 10 — Assemble and save artifacts

Assume `$PROJECT_ROOT/.agents/artifacts/` already exists. Create it only if artifact write fails due to missing directory.

Merge findings from all launched agents into a single review output, organized by file and line number when applicable. For each finding, include severity, impact, and suggested fix. Add concrete implementation suggestions and code snippets where useful.

Save output to one file:

**Review report** → `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-review.md`

Report format:

- If no issues: start with `✅ No issues found`
- If issues exist: start with `⚠️ {N} issue(s) found`
- Include a concise PR summary
- Group results by file (one section per file), not by finding type.
- Inside each file section, list that file's findings ordered by line number when applicable.
- For each finding, render location as:

```md
In `app/code/Vaimo/SunnySalesforceLivechat/view/frontend/layout/default.xml:10`
```

- Do not render separate `Path:` / `Line:` labels in the review markdown.
- If `line=0`, render location as `In \`path/to/file:0\`` and explain in impact/fix that it is a file-level issue.
- Directly under the location line, include a fenced code block with a short relevant snippet from the PR diff (the related hunk/context).
- For each finding include: severity, impact, and suggested fix
- Render severity labels with emoji in the markdown report:
  - `error` -> `❌ Error`
  - `warning` -> `⚠️ Warning`
  - `suggestion` -> `💡 Suggestion`
- Add concrete implementation suggestions and code snippets where useful

Do not display the full review in the terminal, just add path to the saved artifact and a summary line with the number of issues found.

---

## Naming convention

Use this naming convention for every artifact file:

`<YYYY>-<mm>-<dd>-pr-<repo_slug>-<number>-<artifact_type>`

- `repo_slug` comes from PR URL repo segment (for example `project_sunny-eu` from `https://bitbucket.org/vaimo/project_sunny-eu/pull-requests/726/`)
- `number` comes from PR URL number segment (for example `726`)
- `artifact_type` examples: `diff`, `issue-summary`, `review`
- 
## Additional references

- `./shared/auth-setup.md` — Bitbucket/Jira token requirements and auth troubleshooting
- `./shared/review-guardrails.md` — behavior-claim evidence rule, reviewer scopes, and false-positive filters
- `./shared/deletion-pr-checklist.md` — extra checks for pure-deletion PRs
- `./shared/magento2-lsp-mcp-usage.md` — Magento MCP usage and evidence expectations
