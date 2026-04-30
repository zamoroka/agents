---
name: review-pr
description: "Reviews Bitbucket pull requests, summarizes diffs, and produces a full review artifact. Use when the user asks to review a PR, inspect PR changes, or run a pull request code review."
allowed-tools: read, grep, glob, pr-fetch, jira-mcp, magento2-lsp-mcp
metadata:
  version: "2.1.16"
  category: "engineering"
---

# review-pr

Review a pull request. Findings are displayed in the terminal and saved as artifacts under `<project>/.agents/artifacts/`.

**Agent assumptions (applies to all agents and subagents):**

- All tools are functional and will work without error. Do not test tools or make exploratory calls. Make sure this is clear to every subagent that is launched.
- Only call a tool if it is required to complete the task. Every tool call should have a clear purpose.
- Prefer execution-first flow: run the primary command first, then remediate failures (missing file/dir/dependency/env) from actual errors instead of doing broad pre-check passes.

## Shared runtime fallback

If default Node is older than 18 and a fetch step fails with `fetch is not defined`, use Node 25 wrappers from the workspace directory:

- PR fetch (run in `~/.agents/skills/review-pr/scripts/pr-fetch`):
  - `PROJECT_ROOT="{PROJECT_ROOT}" npx -y node@25 --loader ts-node/esm src/function.ts bitbucket {PR_URL}`
- Jira tools:
  - Use connected `jira-mcp` MCP server first.
  - If not connected/unavailable, use `direct-tool-call` skill to call the server tools

Dependency note for fetch steps:
- Assume dependencies are already installed.
- Only run `npm install --prefix ~/.agents/skills/review-pr/scripts` if a fetch command fails due to missing modules/dependencies.
- Only run `uv pip install -e ~/.agents/mcp/jira-mcp` if Jira MCP startup/tool calls fail due to missing modules/dependencies.

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

For token requirements and Jira/Bitbucket authentication troubleshooting, use [auth-setup.md](./references/auth-setup.md).

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

If user says PR is not related to Jira, skip Step 5, Step 8, and Step 10 ticket-alignment check.

---

## Shared block — Isolated subagent rules

Apply these rules to every isolated subagent launched by this skill (for example `jira-agent`, `functionality-checker-agent`):

- Use only explicitly provided inputs and scope.
- Do not rely on broader conversation context.
- Return strict JSON only in the schema required by that step.

Main agent rules for isolated subagents:
- Treat subagent output as the single source for that delegated step.
- If output is invalid JSON or missing required fields, stop and report failure.

---

## Step 5 — Gather and summarize Jira ticket (isolated subagent only)

Main agent MUST delegate Jira summarization to an isolated subagent and then use only the subagent output for all further Jira processing.

### Step 5.1 — Launch isolated Jira summarizer subagent (`jira-agent`)

Launch the dedicated subagent named `jira-agent` from `~/.agents/agents/jira-agent.md`.
Keep `jira-agent` generic and Jira-focused; all PR/code-review-specific policy stays in this `review-pr` skill.

Subagent hard constraints:
- Fetch Jira data via this strict order:
  1. `jira-mcp.fetch_jira_issue_details` for `{ISSUE_KEY}` (primary).
  2. `jira-mcp.jira_issue_summary_prompt` with `jiraIssueJson` from step 1 (mandatory).
  3. If `jira-mcp` is unavailable or fails due to MCP connectivity/runtime/tool registration, invoke `direct-tool-call` skill and call the same Jira MCP tools as fallback.
- Do not handcraft the summary prompt. The subagent MUST call `jira_issue_summary_prompt` and use the returned prompt messages as the summary contract.
- Use only Jira issue raw data from `fetch_jira_issue_details` + that summary contract.
- Return strict JSON only, with at minimum:

```json
{
  "issueKey": "{ISSUE_KEY}",
  "summary": "<markdown summary>"
}
```

Main-agent constraints:
- Do not call Jira tools for summarization after launching this subagent.
- Do not mix Jira facts from any source outside the subagent output.
- If subagent output `summary` is missing any required heading from `jira_issue_summary_prompt` output format (`## Ticket`, `## Problem to solve`, `## Scope requirements`, `## Acceptance criteria or verification notes`, `## Constraints and dependencies`, `## Open questions`, `## Reviewer checklist`), stop and report failure.
- If subagent reports Jira MCP unavailable without attempting fallback, treat this as subagent failure and rerun with explicit fallback instructions.

### Step 5.2 — Write issue summary artifact from subagent output

The main agent must write the `summary` field returned by the subagent to:

- `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-issue-summary.md`

When writing this file, use this exact wrapper:

```md
# PR {PR_NUMBER} issue summary

Jira ticket: {ISSUE_KEY}

{summary}
```

If artifact write fails because the directory does not exist, create `$PROJECT_ROOT/.agents/artifacts/` and retry.

If needed, use the shared fallback above (`jira-mcp` connected first; direct-call workaround only if unavailable).

---

## Step 6 — Load relevant AGENTS.md files and detect project type

Launch an agent to return a list of file paths (not their contents) for all relevant `AGENTS.md` files including:
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

See [magento2-lsp-mcp-usage.md](./references/magento2-lsp-mcp-usage.md) for the expected evidence workflow.

If `PROJECT_TYPE=unknown`, continue without LSP/MCP enrichment.

---

## Step 8 — Existing functionality check (isolated subagent only)

Main agent MUST delegate existing-functionality validation to an isolated subagent after Jira summary is produced.

### Step 8.1 — Launch isolated functionality checker subagent (`functionality-checker-agent`)

Launch the dedicated subagent `functionality-checker-agent` from `~/.agents/agents/functionality-checker-agent.md`.

Additional subagent constraint:
- Do not use Jira tools directly.

Allowed inputs:
- `requiredFunctionality` - functionality to validate, derived from issue summary at `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-issue-summary.md`
- `projectRoot` - project source code root (`$PROJECT_ROOT`)
- `projectType` - main technology used (`PROJECT_TYPE`)
- Relevant `AGENTS.md` guidance, documentation and skills inside the project root.

Required behavior:
- Determine whether Jira requirements can be satisfied by already implemented/default functionality in the project.
- If yes, propose how to use the existing/default functionality.
- If no, provide a project-specific implementation proposal based on repository analysis.
- If implemented, describe how it works now and cite exact files.
- Return strict JSON only:

```json
{
  "status": "implemented | partially_implemented | not_implemented",
  "explanation": "<short rationale>",
  "howItWorks": "<present when implemented/partially_implemented>",
  "implementationProposal": "<present when not_implemented>",
  "nextSteps": ["<optional follow-up actions>"],
  "files": [{"path": "<path>", "reason": "<why this proves it>"}],
  "gaps": ["<missing behavior or mismatch>"],
  "confidence": "high | medium | low"
}
```

Field requirements by status:
- `implemented`: `howItWorks` + at least one `files` entry are required.
- `partially_implemented`: `howItWorks` + at least one `files` entry + clear `gaps` are required.
- `not_implemented`: `implementationProposal` is required.

Magento evidence rule:
- If `PROJECT_TYPE=magento2`, the subagent must use `magento2-lsp-mcp` for Magento-specific claims.

### Step 8.2 — Append proposal block to issue summary artifact

Main agent must append exactly one new block to the end of the issue summary file:

- Heading: `## Agent proposal implementation`
- Body:
  - If `status=implemented`: `Decision: Use existing/default functionality` + `howItWorks` details
  - If `status=partially_implemented`: `Decision: Use existing/default functionality with gaps to implement` + `howItWorks` + `gaps` + optional `nextSteps`
  - If `status=not_implemented`: `Decision: New implementation required` + `implementationProposal` details

Do not edit or rewrite existing sections in the issue summary file.

---

## Step 9 — Summarise the PR

Launch an agent to view the pull request diff and return a concise summary of the changes.

---

## Step 10 — Review

Launch review agents with ordering constraints. Each agent that returns issues MUST use this exact structured format — one JSON object per issue:

```
{"path": "app/code/Vaimo/Module/File.php", "line": 42, "severity": "warning", "description": "Description of the issue and suggested fix"}
```

- `path` — the file path as shown in the diff (relative to repo root)
- `line` — the line number in the **new version** of the file where the issue occurs (from the diff `+` side / `@@` hunk headers). If the issue is general and not tied to a specific line, use `0`.
- `severity` — one of: `error`, `warning`, `suggestion`
- `description` — what the issue is, why it was flagged, and how to fix it

Before review, load and apply rules from [review-guardrails.md](./references/review-guardrails.md).
If the PR is a pure deletion, also apply [deletion-pr-checklist.md](./references/deletion-pr-checklist.md).

If Jira step was not skipped, run this sequence:

1. Run **Agent 1 (reasoning: medium): code-quality-checker** for code-review findings. 
   - This agent can work in parallel with others.
   - Checks code quality of the PR diff based on project specifications and rules as if the diff is already applied to the codebase.
   - Focus on correctness, runtime risk, logic defects, API misuse, and missing edge-case handling.
   - Flag any potential security concerns with severity `error` and detailed explanation.

2. After Step 8 proposal append is complete, launch the **Agent 3 (reasoning: medium): ticket-alignment** agent to compare PR diff with the updated issue summary file and return mismatches.
    - Agent checks if the PR implementation aligns with the Jira issue requirements and acceptance criteria as summarized in the issue summary artifact, including the Step 8 proposal block.
    - For any misalignment, return an issue with severity `warning` and description explaining the mismatch and what would be needed to align the PR with the Jira issue.

If `PROJECT_TYPE=magento2`, all review agents that make Magento-specific claims must use `magento2-lsp-mcp` tool calls as evidence.

---

## Step 11 — Assemble and save artifacts

Assume `$PROJECT_ROOT/.agents/artifacts/` already exists. Create it only if artifact write fails due to missing directory.

Merge findings from all launched agents into a single review output, organized by file and line number when applicable. For each finding, include severity, impact, and suggested fix. Add concrete implementation suggestions and code snippets where useful.

Save output to one file:

**Review report** → `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-review.md`

Report format:

### What
One sentence explaining what this PR does. And what was requested in the Jira issue if applicable.

### Changes
- Bullet points of specific changes made
- Group related changes together
- Mention any files deleted or renamed

### Findings
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

- [auth-setup.md](./references/auth-setup.md) — Bitbucket/Jira token requirements and auth troubleshooting
- [review-guardrails.md](./references/review-guardrails.md) — behavior-claim evidence rule, reviewer scopes, and false-positive filters
- [deletion-pr-checklist.md](./references/deletion-pr-checklist.md) — extra checks for pure-deletion PRs
- [magento2-lsp-mcp-usage.md](./references/magento2-lsp-mcp-usage.md) — Magento MCP usage and evidence expectations
