---
name: code-review
version: 2.0.0
description: "Open interactive code review for current changes or a PR URL"
metadata:
  openclaw:
    category: "engineering"
---

# code-review

Review a Bitbucket pull request. Findings are displayed in the terminal and saved as artifacts under `<project>/.agents/artifacts/`.

**Agent assumptions (applies to all agents and subagents):**

- All tools are functional and will work without error. Do not test tools or make exploratory calls. Make sure this is clear to every subagent that is launched.
- Only call a tool if it is required to complete the task. Every tool call should have a clear purpose.

---

## Step 0 — Detect project root

Check if the current working directory contains an `AGENTS.md` file.

- **If yes** → `PROJECT_ROOT` = current working directory.
- **If no** → Ask the user: *"You don't appear to be inside a project folder. Please provide the absolute path to the project root."* Wait for their response, then set `PROJECT_ROOT` to the provided path. Verify that `AGENTS.md` exists there before continuing.

---

## Step 1 — Bootstrap `.env.local`

Check `$PROJECT_ROOT/.env.local` for the following variables:

```
AGENT_CODEREVIEW_BITBUCKET_EMAIL
AGENT_CODEREVIEW_BITBUCKET_TOKEN
AGENT_CODEREVIEW_BITBUCKET_WORKSPACE
AGENT_CODEREVIEW_BITBUCKET_REPO
```

For each missing variable, ask the user to provide the value (ask all missing variables at once in a single prompt, not one by one). Then append the missing variables to `$PROJECT_ROOT/.env.local`.

Also ensure `.env.local` is listed in `$PROJECT_ROOT/.gitignore`. If it is not, append `.env.local` to the `.gitignore` file.

> **Token note:** `AGENT_CODEREVIEW_BITBUCKET_TOKEN` must be an Atlassian API token (from https://id.atlassian.com/manage-profile/security/api-tokens), not a Bitbucket App Password.

---

## Step 2 — Fetch PR data

Run the fetch script, passing the project root:

```bash
PROJECT_ROOT="{PROJECT_ROOT}" bash ~/.agents/skills/code-review/bitbucket-fetch-pr.sh {PR_NUMBER}
```

This outputs the PR details and full diff to stdout.

---

## Step 3 — Load relevant AGENTS.md files

Launch an agent (model: haiku) to return a list of file paths (not their contents) for all relevant `AGENTS.md` files including:
- The root `AGENTS.md` at `$PROJECT_ROOT/AGENTS.md`
- Any `AGENTS.md` files in directories containing files modified by the pull request

---

## Step 4 — Summarise the PR

Launch an agent (model: sonnet) to view the pull request diff and return a concise summary of the changes.

---

## Step 5 — Review

Launch 2 agents in parallel to independently review the changes. Each agent MUST return issues in this exact structured format — one JSON object per issue:

```
{"path": "app/code/Vaimo/Module/File.php", "line": 42, "severity": "warning", "description": "Description of the issue and suggested fix"}
```

- `path` — the file path as shown in the diff (relative to repo root)
- `line` — the line number in the **new version** of the file where the issue occurs (from the diff `+` side / `@@` hunk headers). If the issue is general and not tied to a specific line, use `0`.
- `severity` — one of: `error`, `warning`, `suggestion`
- `description` — what the issue is, why it was flagged, and how to fix it

**Before flagging any issue that claims "this won't work", "this will break X", or "this overrides/replaces Y":**
- The agent MUST read the relevant source files in the codebase to verify the claim is actually true.
- Specifically: if the concern is about how a framework, Magento core, or third-party library processes the changed code, read the actual processing logic in `vendor/` or the relevant module before asserting the behavior.
- **Evidence requirement**: When the issue depends on framework/library behavior, the agent MUST include a verbatim code snippet from the source file it read (with file path and line range) in the issue description as proof. If the agent cannot produce this snippet, it MUST drop the issue.
- If after reading the code the claim cannot be confirmed, drop the issue entirely. Never flag based on assumed behavior.
- **Never rely on general knowledge of how a method works.** Always read the actual implementation in this specific codebase — vendor code may be patched, overridden, or behave differently than the canonical version.

**Agent 1 (model: opus): code-quality-pragmalist**

**Agent 2 (model: opus): claude-md-compliance-checker**

---

## Step 6 — Assemble and save artifacts

Ensure `$PROJECT_ROOT/.agents/artifacts/` exists (`mkdir -p`).

Save two files:

**a. Summary** → `$PROJECT_ROOT/.agents/artifacts/pr-review-{PR_NUMBER}.md`

Format:
```
{If no issues: "✅ No issues found"}
{If issues: "⚠️ {N} issue(s) found — see inline comments"}

🤖 *Reviewed by Claude Code ({MODEL_ID})*
```

**b. Inline comments** → `$PROJECT_ROOT/.agents/artifacts/pr-review-{PR_NUMBER}-inline.json`

Format:
```json
[
  {
    "path": "app/code/Vaimo/Module/File.php",
    "line": 42,
    "content": "**warning** — Description of the issue and suggested fix\n\n🤖 *Reviewed by Claude Code ({MODEL_ID})*"
  }
]
```

Only include issues where `line > 0`. Format each `content` field as: `**{severity}** — {description}\n\n🤖 *Reviewed by Claude Code ({MODEL_ID})*`.

If no issues were found, write an empty array `[]` to the inline JSON file.

Display the full review in the terminal.

---

## False positive list

Do NOT flag the following (these are not real issues):

- Pre-existing issues
- Something that appears to be a bug but is actually correct
- Pedantic nitpicks that a senior engineer would not flag
- Issues that a linter will catch
- General code quality concerns (e.g., lack of test coverage, general security issues) unless explicitly required in AGENTS.md
- Issues mentioned in AGENTS.md but explicitly silenced in the code (e.g., via a lint ignore comment)

---

## Deletion PR checklist

When the PR is a pure deletion (modules/files being removed), the standard code quality checklist shifts. Focus on:

- **Orphaned references** in non-deleted files (composer.json require entries, patches/ directory, app/etc/hyva-themes.json, other XML di/config files referencing removed classes)
- **DB schema leftovers** — if any deleted module has `db_schema.xml`, its tables/columns will persist in the DB after `setup:upgrade`. Flag with the required manual SQL (`DROP TABLE` / `ALTER TABLE DROP COLUMN`)
- **config.php completeness** — all removed modules must be deregistered
- Skip pre-existing code quality issues in the deleted code itself

---

## Notes

- Use `~/.agents/skills/code-review/bitbucket-fetch-pr.sh` to fetch PR data. Do not use web fetch or any other API calls.
- Create a todo list before starting.
- When citing AGENTS.md rules, quote the relevant rule text directly.
