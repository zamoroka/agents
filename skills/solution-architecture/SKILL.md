---
name: solution-architecture
description: "Captures and maintains solution-architecture knowledge for a software project. Three modes: (1) bootstrap a project AGENTS.md from the repository source code and the matching Obsidian-vault project folder, (2) update an existing project AGENTS.md when new information arrives (meeting notes, summaries, design decisions, code changes), and (3) draft follow-up clarification questions for a client, vendor, or third party by reading the project summary and project knowledge, then append them under the summary's Open Questions section. Trigger whenever the user wants to set up project knowledge for the AI agents, refresh the project AGENTS.md, capture freshly-learned project context, or draft clarifying questions for an external party — even with casual phrasing like 'bootstrap agents file for this repo', 'we just learned X, refresh the project knowledge', 'what should we ask the client', 'draft questions for the vendor', or 'extend the summary's open questions'."
metadata:
  category: "engineering"
  version: "0.1.0"
---

# solution-architecture

Owns the long-lived **solution-architecture knowledge** for a software project:

- the project's `AGENTS.md` at the repo root (single source of truth for agents working in the repo), and
- the project summary's *Open Questions* in the Obsidian vault (canonical follow-up backlog for clients/third parties).

The skill is intentionally split into three modes — each one is a different write target, with different review rigor.

## When to use

Pick the mode whose **intent** matches the user's request. Phrases in parentheses are illustrative — trust paraphrases over keyword matches.

1. **Bootstrap mode** — the user wants to create the project's `AGENTS.md` for the first time, or there is no `AGENTS.md` at the project root yet.
   _Examples: "bootstrap AGENTS.md for this repo", "set up project knowledge", "create the agents file", "initial agents.md from source code and obsidian"._
   → follow [references/bootstrap-agents-md.md](./references/bootstrap-agents-md.md).

2. **Update mode** — `AGENTS.md` already exists and new information should be merged into it (new meeting decisions, a refreshed project summary, a new integration, a renamed module, etc.).
   _Examples: "we just learned X, update AGENTS.md", "refresh project knowledge after the architecture call", "merge this decision into AGENTS.md", "the integration moved from REST to MQ — update agents.md"._
   → follow [references/update-agents-md.md](./references/update-agents-md.md).

3. **Follow-up questions mode** — the user wants clarifying questions to ask a client, vendor, or other third party, based on the current project summary and what is (or isn't) yet known.
   _Examples: "what should we ask the client", "draft questions for the integrator", "extend the open questions of the ARB summary", "follow-up questions for vendor on the SSO integration"._
   → follow [references/followup-questions.md](./references/followup-questions.md).

If the user's intent spans multiple modes (e.g. "refresh AGENTS.md and then draft questions for the client"), run them sequentially: update mode first, then follow-up questions mode using the freshly-updated knowledge.

## Shared context

These conventions apply to every mode. Read this section once per invocation.

### Project root

- `PROJECT_ROOT` defaults to the current working directory if it contains either an existing `AGENTS.md`, a `.git/` directory, or one of: `composer.json`, `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`.
- If none of those are present, ask the user: *"I don't see an obvious project root here. Please provide the absolute path to the project root."* — then verify before continuing.
- The project `AGENTS.md` is always written to `$PROJECT_ROOT/AGENTS.md`. Never write it elsewhere.

_Why one canonical location: every other skill in this setup (`review-pr`, `obsidian-note` cross-checks, etc.) reads `$PROJECT_ROOT/AGENTS.md`. If this skill writes to a different path, that ecosystem breaks silently._

### Obsidian vault

- The vault root and conventions match the `obsidian-note` skill — re-use its values rather than re-deriving:
  - `VAULT_ROOT`: `/Users/zamoroka_pavlo/Library/CloudStorage/GoogleDrive-zapashok0@gmail.com/My Drive/obsidian/zamoroka/`
  - Project folders live at `VAULT_ROOT/Work/<persona>/projects/<Project>/`.
  - Project summaries live at `VAULT_ROOT/Work/<persona>/projects/<Project>/summaries/`.
- Use the `obsidian` CLI for vault reads and writes (`obsidian search:context`, `obsidian files folder=...`, `obsidian outline path=...`, `obsidian property:set ...`, `obsidian reload`). The CLI is always installed; do not probe.

### Identifying the matching vault project

Bootstrap and follow-up-questions modes need to find the Obsidian project folder that corresponds to the current repo. Resolution order:

1. Ask the user if a vault project path was already mentioned in this conversation — if so, use it.
2. Heuristic match: derive a short name from the repo (folder name, `composer.json` `name`, `package.json` `name`) and search:
   ```bash
   obsidian search:context query="<repo-short-name>"
   obsidian search:context query="<repo-short-name> README"
   ```
3. List candidate folders to confirm with the user before reading:
   ```bash
   obsidian files folder="Work/<persona>/projects/"
   ```
4. If no candidate is plausible, ask the user for the project folder explicitly. Do not invent one.

_Why ask rather than guess: project names rarely match repo slugs (e.g. `project_sunny-eu` ↔ `Sunny`, `arb-integration` ↔ `AlRajhiBank`), and binding the wrong vault folder would poison every later step._

### Approval gate

All three modes write to durable, decision-grade artifacts (`AGENTS.md` is read by every agent in the repo; project summaries are cited in stakeholder discussions). Therefore:

- Always present a written **proposal** before writing.
- Wait for **explicit approval** ("yes", "go", "ok"). Approval can be partial — the user may accept some additions and reject others.
- Never silently overwrite or restructure existing sections as a side effect.

_Why this rule is strict: a silent change to AGENTS.md can ripple into every PR review, code-gen, and onboarding artifact downstream. Same logic as `obsidian-note` summary mode — the user must remain the final auditor._

### Style — use `impersonator`

Before drafting any prose that the user will eventually share or sign their name to (most of `AGENTS.md`, all follow-up questions destined for a client), invoke the `impersonator` skill so the text matches the user's voice.

Skip `impersonator` for purely structural content: file paths, command snippets, dependency lists, table cells with literal values.

## Bundled assets

- `assets/agents-md-template.md` — canonical section layout for a project `AGENTS.md`. Use as the starting structure in bootstrap mode and as the reference shape when reorganizing in update mode.

## References

- [Bootstrap mode workflow](./references/bootstrap-agents-md.md)
- [Update mode workflow](./references/update-agents-md.md)
- [Follow-up questions workflow](./references/followup-questions.md)

## Mandatory verification

After every create or modify action on this skill, run from the skill directory:

```bash
npx tessl skill review SKILL.md
```

Treat warnings/errors as actionable. See `skills/AGENTS.md` for the wider rule.
