---
name: review-pr
description: "Reviews Bitbucket pull requests, summarizes diffs, and produces a full review artifact. Use when the user asks to review a PR, inspect PR changes, or run a pull request code review."
allowed-tools: read, grep, glob, pr-fetch, jira-mcp, magento2-lsp-mcp
metadata:
  version: "2.2.0"
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

## Isolated subagent rules

Apply these rules to every isolated subagent launched by this skill (for example `jira-agent`, `functionality-checker-agent`, `changes-checker-agent`):

- Use only explicitly provided inputs and scope.
- Do not rely on broader conversation context.
- Return strict JSON only in the schema required by that step.

Main agent rules for isolated subagents:
- Treat subagent output as the single source for that delegated step.
- **TIMEOUT:** If a subagent has not returned within 10 minutes of launch, STOP and report a timeout error with the subagent name. Do not wait further or retry automatically.
- **MANDATORY VALIDATION:** If output is invalid JSON or missing required fields, STOP and report failure with specific details.
- **FABRICATION DETECTION:** If subagent admits to fabricating data, making up information, or not calling required tools, STOP and report fabrication error.
- **TOOL EXECUTION VALIDATION:** For Jira subagents, validate that required tools (`fetch_jira_issue_details`, `jira_issue_summary_prompt`) were actually executed by checking subagent's tool execution confirmation.
- **EXPLICIT ERROR HANDLING:** If subagent returns `status: "error"`, include error details in main review and do not proceed with that data source.

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

## Step 2.1 — Load project intelligence

Read the root `$PROJECT_ROOT/AGENTS.md` and detect `PROJECT_TYPE` from explicit project identifiers:
- If AGENTS.md indicates Magento 2 / Adobe Commerce -> `PROJECT_TYPE=magento2`
- Otherwise -> `PROJECT_TYPE=unknown`

Select an LSP/MCP provider based on `PROJECT_TYPE`:
- `magento2` -> use `magento2-lsp-mcp`

Environment note:
- `magento2-lsp-mcp` is expected to be preinstalled in this environment; do not reinstall it during normal review flow.

For `magento2`, the summarizer and review agents must call Magento MCP tools for changed PHP/XML areas to validate merged Magento behavior (DI preferences/plugins, event observers, template/layout wiring, config-driven behavior) instead of relying on raw file reading alone.

See [magento2-lsp-mcp-usage.md](./references/magento2-lsp-mcp-usage.md) for the expected evidence workflow.

If `PROJECT_TYPE=unknown`, continue without LSP/MCP enrichment.

---

## Step 3 — Fetch PR data

Run the Bitbucket Node module, passing the project root:

```bash
PROJECT_ROOT="{PROJECT_ROOT}" npm --prefix ~/.agents/skills/review-pr/scripts --workspace pr-fetch run fetch:pr -- bitbucket {PR_URL}
```

If needed, use the shared Node 25 fallback above.

This outputs PR details, comments, changed files, and full diff to stdout, and saves the diff artifact to `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-diff.patch` with Bitbucket metadata in comment lines at the top (title, author, description, and related PR fields).

---

## Step 3.1 — Load AGENTS.md from PR-modified directories

Using the list of changed files from Step 3, locate any `AGENTS.md` files in directories containing files modified by the pull request (beyond the root `AGENTS.md` already loaded in Step 2.1).

Read each located file and store the combined content as `PR_AGENTS_CONTEXT`. This context is passed to `changes-checker-agent` (Step 4) and `functionality-checker-agent` (Step 7.1) as additional guidance.

If no additional `AGENTS.md` files are found, set `PR_AGENTS_CONTEXT` to an empty string and continue.

---

## Step 4 — Launch isolated changes checker (in parallel)

Immediately after Step 3.1, launch isolated subagent `changes-checker-agent` from `~/.agents/agents/changes-checker-agent.md`.

Purpose:
- Understand what changed in the PR diff, how it works, and what it does.
- Identify coding-standard violations, architecture concerns, possible bugs, and security risks.
- Perform security analysis with explicit OWASP Top 10 and Magento-specific vectors (ObjectManager abuse, unescaped template output, ACL bypass, CSRF, insecure deserialization, and related risks).
- Own the PR code-review findings for standards/correctness/security.

Execution model:
- Start this subagent right after Step 3.1 and continue main flow without waiting (for example continue with Jira-key detection and Jira subagent launch).
- This subagent must run in isolated git worktree context created from `projectRoot` and apply the PR diff patch there, so the primary workspace and other agents are not modified.
- Main agent should collect this subagent output when available and merge it into final summary/review.

Required inputs:
- `projectRoot`: `$PROJECT_ROOT`
- `diffPatchPath`: `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-diff.patch`
- `projectType`: `PROJECT_TYPE`
- `agentsContext`: `PR_AGENTS_CONTEXT`

Expected output from subagent (strict JSON only):

```json
{
  "status": "ok | error",
  "prChangeSummary": "<concise description of changed behavior>",
  "howItWorks": "<high-level runtime/data-flow explanation>",
  "whatItDoes": "<functional impact description>",
  "issues": [
    {
      "path": "path/from-diff",
      "line": 0,
      "severity": "error | warning | suggestion",
      "description": "Issue + risk + suggested fix",
      "category": "coding_standards | architecture | bug_risk | security"
    }
  ],
  "files": [{"path": "<path>", "reason": "<evidence>"}],
  "confidence": "high | medium | low",
  "errors": ["<present only when status=error>"]
}
```

Failure handling:
- If output is invalid JSON or required fields are missing, stop and report failure.
- If `status=error`, include subagent errors in terminal output and stop before final report generation.
- **Worktree fallback (not yet implemented):** if git worktree creation fails, CC should fall back to applying the diff to a temporary copy of changed files rather than a full worktree, and return `confidence: "low"` in all findings to signal reduced isolation. Until implemented, a worktree failure is a hard stop.

---

## Step 5 — Determine Jira issue key

The main agent must detect Jira issue key from PR data (title, branch, description, comments, changed files).

Always ask user to confirm detected key.
- If detected: ask `I found {ISSUE_KEY}. Correct?`
- If not detected: ask user to provide Jira issue key, or confirm skipping Jira step.

If user says PR is not related to Jira, skip Step 6, Step 7, and Jira alignment checks in Step 8.

---

## Step 6 — Gather and summarize Jira ticket (isolated subagent only)

Main agent MUST delegate Jira summarization to an isolated subagent and then use only the subagent output for all further Jira processing.

### Step 6.1 — Launch isolated Jira summarizer subagent (`jira-agent`)

Launch the dedicated subagent named `jira-agent` from `~/.agents/agents/jira-agent.md`.
Keep `jira-agent` generic and Jira-focused; all PR/code-review-specific policy stays in this `review-pr` skill.

Subagent hard constraints:
- Fetch Jira data via this strict order:
  1. `jira-mcp.fetch_jira_issue_details` for `{ISSUE_KEY}` (primary).
  2. `jira-mcp.jira_issue_summary_prompt` with `jiraIssueJson` from step 1 (mandatory).
  3. If `jira-mcp` is unavailable or fails due to MCP connectivity/runtime/tool registration, invoke `direct-tool-call` skill and call the same Jira MCP tools as fallback.
- **EXECUTION PROOF REQUIRED:** Must include in response exactly which tools were called and their success/failure status.
- **NO SHORTCUTS:** Cannot skip jira_issue_summary_prompt. Cannot fabricate or improvise summary.
- Do not handcraft the summary prompt. The subagent MUST call `jira_issue_summary_prompt` and use the returned prompt messages as the summary contract.
- **EXPLICIT FAILURE:** If any required tool fails, return `status: "error"` with specific error details.
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
- **MANDATORY VALIDATION:** If subagent output `summary` is missing any **required** heading (`## Ticket`, `## Problem to solve`, `## Scope requirements`, `## Acceptance criteria or verification notes`), STOP and report failure with specific missing sections. If any **optional** heading is missing (`## Constraints and dependencies`, `## Open questions`, `## Reviewer checklist`), log a warning but continue.
- **TOOL EXECUTION VALIDATION:** Subagent MUST confirm it called both `fetch_jira_issue_details` and `jira_issue_summary_prompt`. If not confirmed, STOP and report tool execution failure.
- **NO FABRICATION:** If subagent admits to fabricating data or not calling required tools, STOP and report fabrication error.
- If subagent reports Jira MCP unavailable without attempting fallback, treat this as subagent failure and rerun with explicit fallback instructions.

### Step 6.2 — Write issue summary artifact from subagent output

The main agent must write the `summary` field returned by the subagent to:

- `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-issue-summary.md`

When writing this file, use this exact wrapper:

```md
# PR {PR_NUMBER} issue summary

Jira ticket: {ISSUE_KEY}

{summary}
```

If artifact write fails for any reason, STOP immediately and report the error. Do not attempt to continue. The user must resolve the issue (e.g. check directory permissions) and re-run the workflow.

---

## Step 7 — Existing functionality check (isolated subagent only)

Main agent MUST delegate existing-functionality validation to an isolated subagent after Jira summary is produced.

### Step 7.1 — Launch isolated functionality checker subagent (`functionality-checker-agent`)

Launch the dedicated subagent `functionality-checker-agent` from `~/.agents/agents/functionality-checker-agent.md`.

Additional subagent constraint:
- Do not use Jira tools directly.

Allowed inputs:
- `requiredFunctionality` - functionality to validate, derived from issue summary at `$PROJECT_ROOT/.agents/artifacts/YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-issue-summary.md`
- `projectRoot` - project source code root (`$PROJECT_ROOT`)
- `projectType` - main technology used (`PROJECT_TYPE`)
- `agentsContext` - `PR_AGENTS_CONTEXT` from Step 3.1
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

### Step 7.2 — Append proposal block to issue summary artifact

Main agent must append exactly one new block to the end of the issue summary file:

- Heading: `## Agent proposal implementation`
- Body:
  - If `status=implemented`: `Decision: Use existing/default functionality` + `howItWorks` details
  - If `status=partially_implemented`: `Decision: Use existing/default functionality with gaps to implement` + `howItWorks` + `gaps` + optional `nextSteps`
  - If `status=not_implemented`: `Decision: New implementation required` + `implementationProposal` details

Do not edit or rewrite existing sections in the issue summary file.

If the append fails for any reason, STOP immediately and report the error. The user must resolve the issue and re-run the workflow.

---

## Step 8 — Review

This step is aggregation and alignment analysis in the main agent only. Do not launch additional subagents in Step 8.

Wait for and consume outputs from already launched subagents:
- `changes-checker-agent` (required)
- `jira-agent` (when Jira flow is enabled)
- `functionality-checker-agent` (when Jira flow is enabled)

Issue output schema for code-review findings is owned by `changes-checker-agent` (`~/.agents/agents/changes-checker-agent.md`).
Main agent must consume that output format as-is and include those issues in final findings.

Build the concise PR summary in the main agent from `changes-checker-agent` output:
- Primary source: `prChangeSummary`
- Supporting context: `howItWorks`, `whatItDoes`, and fetched PR metadata

Always include `changes-checker-agent` output in the final findings set, regardless of whether Jira flow is skipped.

If Jira flow is enabled, the main agent must perform cross-checks directly (without new subagents):
- Compare PR changes (`changes-checker-agent` output) against Jira expectations (`jira-agent` summary artifact).
- Compare `functionality-checker-agent` decision/proposal with actual PR implementation from `changes-checker-agent`.
- Identify mismatches, missing scope, over-implementation, or contradictory conclusions between subagents.
- For each mismatch, add a finding with severity `warning` that explains the gap and what is needed to align with Jira intent.
- Add improvement suggestions when there is a clearly better implementation approach, with rationale tied to Jira scope and repository conventions.

If Jira flow is skipped, evaluate only `changes-checker-agent` output and PR metadata.

If `PROJECT_TYPE=magento2`, any Magento-specific claims included in final findings must be evidence-backed by `magento2-lsp-mcp` calls from existing subagent outputs or main-agent calls.

**Magento claim validation (not yet implemented):** when `PROJECT_TYPE=magento2`, `changes-checker-agent` should include a `magentoMcpCalls` array in its JSON output listing MCP tools it invoked. Main agent should validate this field is non-empty before accepting Magento-specific findings; findings without MCP evidence should be downgraded to `confidence: "low"` with an explicit `[unverified — no MCP evidence]` marker.

---

## Step 9 — Assemble and save artifacts

This step is artifact creation only. Do not launch additional subagents in Step 9.

Assume `$PROJECT_ROOT/.agents/artifacts/` already exists. If any artifact write fails for any reason, STOP immediately and report the error. The user must resolve the issue and re-run the workflow.

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
