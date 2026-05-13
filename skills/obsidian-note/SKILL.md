---
name: obsidian-note
description: "Obsidian vault management. Creates and updates wiki pages, meeting notes, transcripts, todo/task reports, email-thread captures, calendar activity summaries, Google Docs imports, and long-lived project summary documents. Trigger whenever the user wants to save, capture, log, file, archive, or note anything they would put in their Obsidian vault — including casual phrasing like 'save this transcript', 'what's on my plate', 'log this thread', 'what did I do this week', 'dump my list', 'file this in my vault', or any paste that looks like meeting notes, an email chain, or a transcript even when they don't say 'Obsidian'. Also trigger when a project-level skill delegates a summary write."
metadata:
  category: "productivity"
  version: "3.5.0"
---

# obsidian-note

Create or update any wiki page in the Obsidian vault. This is the single note-management skill and covers regular notes, meeting notes/transcripts, todo reports, raw save-as-is behavior, calendar activity summaries, email-thread captures, and project summary documents.

## Vault context

- **Vault root (`VAULT_ROOT`):** `/Users/zamoroka_pavlo/Library/CloudStorage/GoogleDrive-zapashok0@gmail.com/My Drive/obsidian/zamoroka/`
  (Google Drive: `obsidian/zamoroka/`). Personal vault, fixed path — do not probe for it. Always operate inside this directory.
- **Conventions:** read `VAULT_ROOT/AGENTS.md` once at the start of any write workflow. It is the source of truth for folder structure, personas, naming, and tagging.
- **Template:** `VAULT_ROOT/_templates/page.md`
- **CLI:** the Obsidian CLI is always installed — use `obsidian <command>` directly without a precheck. Per-mode placement and naming summary lives in [references/vault-preflight.md](./references/vault-preflight.md).

## When to use

Invoke this skill when the user wants to:
- capture or update any note/page
- save notes from a Google Doc URL
- save meeting notes/transcripts or email threads
- view their todo/task report
- save content exactly as-is (`raw`, `as-is`, `verbatim`, `don't rewrite`)
- create or update a long-lived **summary document** for a project topic (delegated by project-level skills such as `df-research`)
- update their "what was done" activity summary from calendar events

Examples:
- "Save this Google Doc as a note."
- "Create notes from this standup transcript."
- "Show what is on my todo list."
- "Log this email thread under ARB Communications."
- "What did I do last week?"

## Modes

- **Normal mode (default):** full processing with placement, duplicate detection, related pages, markdown links (vault-root-relative), and structure matching.
- **Meeting mode:** meeting-specific flow for transcript handling, meeting-folder selection, action-point extraction, and TASKS.md proposal flow.
- **Summary mode:** long-lived project summary document — strict duplicate detection, explicit approval before every additive/contradictory change, no parallel files. See [references/project-summaries.md](./references/project-summaries.md).
- **Raw mode:** save text as-is with minimal YAML frontmatter only; no rewriting, no wiki-links, no impersonation.

## Instructions

Follow this decision flow when invoked.

### Step 1 — Gather content

If no content was provided, ask: *"Please paste the note content and I'll handle the rest."*

### Step 2 — Resolve Google Docs URLs (if present)

If input includes one or more Google Docs URLs (`https://docs.google.com/document/d/...`),
follow [references/google-drive-usage.md](./references/google-drive-usage.md) for the full
download-and-route workflow. That reference covers:

- how to call `doc_markdown_download` (MCP server `google-drive`)
- staging to `VAULT_ROOT/_raw`
- content-type detection
- routing: meeting notes → [references/meeting-notes.md](./references/meeting-notes.md),
  all other types → placement confirmation flow

Resume the steps below only after the Google Drive workflow has resolved the content
and confirmed (or delegated) the write target.

### Step 3 — Detect mode

Pick the first mode below whose **intent** matches what the user is trying to
do. Phrases in parentheses are illustrative — trust paraphrases and casual
wording rather than waiting for an exact keyword match.

1. **Calendar activity summary** — the user wants a roll-up of recent activity from their calendar.
   _Examples: "what was done this week", "what did I do last month", "update whats done", "show my activity"._
   -> follow [references/calendar-whats-done.md](./references/calendar-whats-done.md).

2. **Todo report** — the user wants to see open tasks across the vault.
   _Examples: "what's on my todo", "show my tasks", "what's on my plate", "dump my list", "what do I need to do this week"._
   -> follow [references/todo-report.md](./references/todo-report.md).

3. **Raw mode** — the user is explicit about preserving the input verbatim.
   _Examples: "raw", "as-is", "verbatim", "just save it", "don't rewrite", "no changes", "don't modify"._
   _Why: the user is signalling that the value is in the exact wording — any rewriting destroys it._
   -> follow [Raw Mode](#raw-mode).

4. **Summary mode** — the user (or a project-level skill) wants to create or update a long-lived synthesis document.
   _Examples: "create the summary", "save the summary", "update the summary", "refresh the summary", "collect into a summary document", an explicit reference to an existing `summaries/<file>.md`, or a project-level skill delegating._
   -> follow [references/project-summaries.md](./references/project-summaries.md).

5. **Email thread** — the input is an email exchange (forwarded, replied, or pasted with headers).
   _Signals: ≥2 of {`Subject:`, `From:`, `To:`} on consecutive lines, `> ` quote chains, or the user explicitly says "email thread"/"forwarded"/"log this thread"._
   -> follow [references/email-threads.md](./references/email-threads.md).

6. **Meeting** — the input is a transcript, meeting notes, or the user is asking to save one.
   _Signals: dated participant discussion, action-items structure, "1-1", "sync", "standup", "retrospective", "call with", or the user says "meeting note"/"transcript"._
   -> follow [references/meeting-notes.md](./references/meeting-notes.md).

7. **Normal mode** — everything else. Continue with Steps 4-9 below.

### Step 4 — Load vault conventions

Read `VAULT_ROOT/AGENTS.md` before any write action. It is the source of truth
for folder structure, personas, naming, and tagging.

The placement quick-reference (non-authoritative; consult AGENTS.md for anything not
covered here) lives in [vault-preflight.md](./references/vault-preflight.md#3-load-vault-conventions).

### Step 5 — Placement and search

1. Determine folder via Persona 3 decision flow from `AGENTS.md`.
2. Run related-page discovery using this layered strategy:
   a. `obsidian search:context query="<keyword1> <keyword2>"` — 2-3 queries with `search:context` (returns matching lines, not just filenames)
   b. For each strong hit, run `obsidian backlinks file="<hit>"` and `obsidian links file="<hit>"` to expand the graph
   c. For each project/topic tag in the incoming note, run `obsidian tag name=<tag> verbose` to surface tag-siblings
   d. Check `obsidian aliases file="<candidate>"` when a candidate matches by title variant
3. Rank results: same-day + ≥1 participant/keyword overlap + ≥2 matching tags → **update**; otherwise **create new**.
4. Cap related-pages list at 5, ranked by overlap signal.
5. If contradictions with existing pages are found, stop and ask the user before proceeding.

### Step 6 — Tags and filename

1. Apply folder/content tags per `AGENTS.md` (minimum 2 tags).
2. Derive concise filename matching vault naming style (including emoji naming conventions where already used).

### Step 7 — Confirm plan

Before writing, ask for confirmation:
- New page path + tags + short content summary.
- Update target section + short change description.

### Step 8 — Write content

For normal mode only:

1. Invoke `impersonator` before writing.
   _Why: the user reviews and shares these pages — keeping their tone is the difference between a useful note and one they have to rewrite._
2. On update:
   - Run `obsidian outline path="<file>"` to get heading structure without reading the full file.
   - Read current file only when content merging is needed.
   - Match existing structure exactly (heading/list/checklist/table style, indentation, tone).
   _Why: drifting the structure on every update makes the page look like it was edited by committee and breaks any downstream parsing._
3. Merge without duplication.
4. Update YAML properties atomically with explicit types:
   - `obsidian property:set name="updated" value="<ISO datetime>" type=datetime path="<file>"`
   - `obsidian property:read name="related" path="<file>"` → merge unique → `obsidian property:set name="related" value="..." type=list path="<file>"`
   - `obsidian property:set name="summary" value="<text>" type=text path="<file>"` when meaningful
   - `obsidian property:set name="tags" value="..." type=list path="<file>"` if tags changed
   _Why specify `type=`: without it Obsidian sometimes stores dates as plain text, breaking date-based queries and Database.base views._
5. Prefer direct markdown edits; use `obsidian append` only for simple single-line entries when faster.
6. If file was created via direct write (not `obsidian create`), call `obsidian reload` afterward so Obsidian picks up the change immediately.
   _Why: Google Drive CloudStorage is async — without `reload`, Obsidian's index can lag behind disk, leading to "missing" backlinks until the next restart._

### Step 9 — Confirm result

Report:
- created/updated page path
- tags applied
- related pages linked
- optional offer to open page in Obsidian via `obsidian open path="..."`

### Step 10 — Cross-check related project summaries

After any non-raw write that lands under a project folder (e.g. `Work/<persona>/projects/<Project>/<subfolder>/`), check whether the new note should trigger an update proposal for an existing summary in `Work/<persona>/projects/<Project>/summaries/`.

Follow the [Cross-check after non-summary writes](./references/project-summaries.md#cross-check-after-non-summary-writes) procedure. If no candidate summary is affected, stay silent.

Skip this step for:
- raw-mode writes (the user explicitly asked for no modifications anywhere)
- writes that did not land under a project folder
- summary-mode writes themselves (the summary *is* the target, not a cross-check source)

## Raw Mode

Goal: save content untouched with minimal frontmatter only.
_Why this mode exists: the user is signalling that the value is in the exact wording — any rewriting, link-injection, or impersonation would destroy what they wanted preserved._

1. If content missing, ask for it.
2. Run the [vault preflight](./references/vault-preflight.md); determine folder/title via Persona 3 flow.
3. Derive tags per `AGENTS.md` (use template at `assets/frontmatter-templates/raw.md`).
4. Confirm target path and tags.
5. Write:
   - YAML frontmatter (`tags`, `created`)
   - original input text verbatim

Raw mode restrictions (the rules that define the mode):
- do not invoke `impersonator` — would rewrite tone
- do not add any links — would change the text
- do not rewrite/reformat content — would lose the value
- Step 10 cross-check is also skipped (user explicitly asked for no side effects)

## References

- Shared vault preflight (CLI probe, dynamic `VAULT_ROOT`, AGENTS.md): [references/vault-preflight.md](./references/vault-preflight.md)
- Calendar activity summary workflow: [references/calendar-whats-done.md](./references/calendar-whats-done.md)
- Todo reporting workflow: [references/todo-report.md](./references/todo-report.md)
- Email-thread capture and cleanup workflow: [references/email-threads.md](./references/email-threads.md)
- Meeting notes workflow: [references/meeting-notes.md](./references/meeting-notes.md)
- Google Drive download and routing: [references/google-drive-usage.md](./references/google-drive-usage.md)
- Project summary creation, updates, and cross-checks: [references/project-summaries.md](./references/project-summaries.md)

## Bundled scripts

- `scripts/compute_period.py` — ISO date math for `this-week`/`last-week`/`this-month`/`last-month` (used by [calendar-whats-done.md](./references/calendar-whats-done.md)).
  _Why scripted: date arithmetic is deterministic and a frequent source of off-by-one errors when done in-head. The todo report stays a judgment workflow because grouping/filtering needs understanding, not pattern matching._

## Bundled assets

- `assets/frontmatter-templates/` — one template per mode (`normal`, `meeting`, `email`, `project-summary`, `raw`). Match against these instead of re-typing YAML schemas.

## Notes

- Write page content in the same language as input (Ukrainian, English); keep YAML tags in English. Cleanup rules apply by **intent** (sign-off, body, metadata) regardless of language — do not transliterate or translate.
