# Project summaries

Workflow for creating and maintaining **summary documents** in the vault — long-lived synthesis pages that consolidate research, decisions, and context for a single topic (e.g. a feature request, an initiative, a vendor evaluation, a regulatory question).

Project-level skills (`df-research`, future per-project research skills) own the conventions and routing. This reference owns the *mechanics* of writing and updating a summary safely.

## When to use

Two distinct entry points:

1. **Explicit request** — user asks to create, save, persist, refresh, or update a summary.
   Triggers: `create the summary`, `save the summary`, `save to Obsidian`, `update the summary`, `collect into a summary document`, `add to vault`, `refresh <topic> summary`.
2. **Side-effect after saving a related note** — when a meeting note, communication, email, or other project artifact is saved under a project folder, check whether an existing summary in that project's `summaries/` subfolder should be updated. See [Cross-check after non-summary writes](#cross-check-after-non-summary-writes).

## Summary structure

The canonical structure (frontmatter, header block, body sections) lives in the template at `assets/frontmatter-templates/project-summary.md`. 
Start from that file rather than retyping YAML or section headings here.

What the template defines:

- **Frontmatter** — `updated`, `tags`, `related`, `summary`.
- **Header block** — `Type`, `Current Status`, `Jira` (when relevant), `Effort Estimate` (when relevant), `Sources` (when relevant). Omit rows entirely when a field doesn't apply.
- **Body sections** — `Problem Statement`, `Solution Description`, `Assumptions`, `Action Items`, `Risks`, `Open Questions`, `Decision Log`, `Solution Architecture` (with `Key Components` subsection), `Technical Implementation`.

Within each section, match the heading/list/table style already in the template — table-shaped sections (Action Items, Risks, Open Questions, Decision Log) stay tables; bullet-shaped sections (Assumptions, Key Components) stay bullets. 
Include links (vault-root-relative paths or external URLs) to source documents for each major claim, or add them to the `Sources` row in the header table.

---

## Inputs from the caller

Project-level skills must pass (or have the user pass) these inputs. Do **not** invent project conventions — if any are missing, ask.

| Input | Example |
|---|---|
| Summary identifier | `DF-XXXX`, initiative name, etc. — used for duplicate detection |
| Target folder | `Work/Vaimo/projects/ARB/summaries/` |
| Filename pattern | `DF-XXXX - <Feature Name>.md` |
| Required frontmatter tags | base tags (e.g. `work`, `vaimo`, `prj-AlRajhiBank`) + content tags |
| Required `related` links | project README, TASKS, relevant Communications notes |
| Body sections (optional override) | only if the caller's topic type needs sections different from the template default |
| Reference examples | one or two existing summaries in the same folder to mirror the tone and layout |

## New summary flow

1. Confirm with the user: target path, filename, tags, structure.
2. Detect duplicates using layered discovery (cheap first, broader if needed):
   - `obsidian search:context query="<identifier>"` — line-level match for the project code/initiative name
   - `obsidian files folder="<caller's canonical folder>"` — listing of existing summaries in that folder
   - `obsidian aliases file="<candidate>"` for any near-match — catches renamed/aliased summaries
   - `obsidian tag name="<primary project tag>" verbose` — surfaces sibling pages that may be the same summary under a different filename
3. If a summary already exists at the target path (or appears under a different filename via aliases/tag-siblings), switch to the **[update flow](#update-flow)** — never create a parallel file.
4. Compose the body using the [structure defined above](#summary-structure), the caller-provided body sections, and the reference examples.
5. Invoke `impersonator` before writing.
   _Why: summaries are decision-grade documents the user shares — keeping their tone avoids rewrites._
6. Apply the standard write steps from the main `SKILL.md` (Step 8 — Write content), including frontmatter and `obsidian reload`.

## Update flow

When updating an existing summary with new information (new research, new meeting notes, new communications):

1. Read the existing summary.
2. Compare incoming information against existing content. Classify each new fact into one of three buckets:
   - **Duplicate** — already explained in the summary at sufficient depth; skip.
   - **Addition** — new, valuable, and could impact future decisions; propose to add.
   - **Contradiction** — conflicts with what the summary currently states; flag for resolution.
3. Present a proposal to the user **before writing**. The proposal must include:
   - **Additions** — which sections gain content, plus a short preview of each addition.
   - **Contradictions** — both versions side-by-side, with the source of each, and a question about which to keep (or whether the summary should be reworded to acknowledge both).
   - **Skipped duplicates** — one short line per item, so the user can override if a nuance was missed.
4. Wait for **explicit approval**. Do not write until the user confirms. Approval can be partial — the user may accept some additions and reject others.
5. Invoke `impersonator` before writing.
   _Why: summaries are decision-grade documents the user shares — keeping their tone avoids rewrites._
6. On approval, update the file in place:
   - Bump `updated` in frontmatter: `obsidian property:set name="updated" value="<ISO datetime>" type=datetime path="<file>"`.
   - Extend `related` if the new source is a vault page: `obsidian property:read name="related" path="<file>"` → merge unique → `obsidian property:set name="related" value="..." type=list path="<file>"`.
   - Match the existing structure (heading style, list style, tone). Do not restructure the summary as a side-effect of an update.
7. Never create a parallel summary file when one already exists at the canonical path.
   _Why: parallel files silently fragment the canonical record. Once two summaries exist for the same topic, downstream pages link to whichever one was found first, and the user has no single source of truth._

If the filename pattern changes (e.g. caller updates the convention), use `obsidian rename file="<old>" name="<new>"` or `obsidian move path="<old>" to="<new>"` — these keep wikilinks intact across the vault.

## Cross-check after non-summary writes

When `obsidian-note` finishes writing any non-raw note that lands under a project folder (e.g. `Work/<persona>/projects/<Project>/<subfolder>/`):

1. Check whether the summaries folder exists:
   ```bash
   obsidian folder path="Work/<persona>/projects/<Project>/summaries"
   ```
   If the command reports the folder is missing, stop.
2. List candidate summaries:
   ```bash
   obsidian files folder="Work/<persona>/projects/<Project>/summaries"
   ```
3. Identify candidates the new note may relate to, using layered signals:
   - **Identifier match** — note mentions `DF-XXXX`/initiative code and a summary exists for that code (highest-confidence signal).
   - **Tag overlap** — run `obsidian tags file="<summary>"` for each candidate and intersect with the new note's tags.
   - **Backlink signal** — run `obsidian backlinks file="<summary>"`; if the new note already appears, the summary is in scope by definition.
   - **Keyword overlap** — strong overlap on title or first heading.
4. For each candidate, run the [update flow](#update-flow) classification (duplicate / addition / contradiction).
5. If anything is worth proposing, surface a **single follow-up proposal block** to the user covering one or more affected summaries. Frame it as a follow-up suggestion — do not block the original save.
6. If nothing is worth proposing, stay silent. Do not announce that no updates are needed.

The cross-check is skipped for raw-mode writes (user explicitly asked for no modifications) and for summary-mode writes themselves (the summary *is* the target, not a cross-check source).

## Approval is required

For both flows: **always** ask for approval before writing changes to a summary, with an explanation of what will be added or changed.

_Why this rule is strict (no shortcuts even when changes look obvious): summaries are decision-grade documents — they get cited in steerco discussions, vendor evaluations, regulatory answers, etc. 
A silent edit that flips a single fact (price, version, deadline) can compromise a downstream decision the user already made based on the prior version.
Asking before writing keeps the user as the final auditor of every change._
