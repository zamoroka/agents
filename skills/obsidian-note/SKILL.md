---
name: obsidian-note
description: "Obsidian: Creates or updates vault pages (notes, meetings, and todo reports), imports Google Docs markdown, and can save content verbatim in raw mode. Use for note capture, transcript handling, or task-report requests."
metadata:
  category: "productivity"
  version: "3.3.0"
---

# obsidian-note

Create or update any wiki page in the Obsidian vault. This is the single note-management skill and covers regular notes, meeting notes/transcripts, todo reports, and raw save-as-is behavior.

## Vault context

- **Vault root (`VAULT_ROOT`):** `/Users/zamoroka_pavlo/Library/CloudStorage/GoogleDrive-zapashok0@gmail.com/My Drive/obsidian/zamoroka/`
  (Google Drive: `obsidian/zamoroka/`). Always operate inside this directory. **Do not search the filesystem for other vaults** — a stale legacy copy may exist (e.g. `~/Downloads/zamoroka/`) and must be ignored.
- **Conventions:** always read `VAULT_ROOT/AGENTS.md` first. It is the source of truth for folder structure, personas, naming, and tagging rules.
- **Template:** `VAULT_ROOT/_templates/page.md`

## When to use

Invoke this skill when the user wants to:
- capture or update any note/page
- save notes from a Google Doc URL
- save meeting notes/transcripts
- view their todo/task report
- save content exactly as-is (`raw`, `as-is`, `verbatim`, `don't rewrite`)

Examples:
- "Save this Google Doc as a note."
- "Create notes from this standup transcript."
- "Show what is on my todo list."

## Modes

- **Normal mode (default):** full processing with placement, duplicate detection, related pages, markdown links (vault-root-relative), and structure matching.
- **Meeting mode:** meeting-specific flow for transcript handling, meeting-folder selection, action-point extraction, and TASKS.md proposal flow.
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

Detect in this order:

1. **Calendar "what was done" trigger** (`what was done`, `what did I do`, `show my activity`, `update whats done`) -> follow [references/calendar-whats-done.md](./references/calendar-whats-done.md).
2. **Todo report trigger** (`what's on my todo`, `show my tasks`, `what do I need to do`) -> follow [references/todo-report.md](./references/todo-report.md).
3. **Raw mode trigger** (`raw`, `as-is`, `verbatim`, `just save it`, `don't rewrite`, `no changes`, `don't modify`) -> follow [Raw Mode](#raw-mode).
4. **Email-thread signals** (`email thread`, ≥2 of {`Subject:`, `From:`, `To:`} on consecutive lines, or `> ` quote chains with email headers, forwarded/replied chains) -> follow [references/email-threads.md](./references/email-threads.md).
5. **Meeting signals** (transcript/meeting wording, dated participant discussion, action-items structure, `1-1`, `sync`, `standup`, `retrospective`, `call with`) -> follow [references/meeting-notes.md](./references/meeting-notes.md).
6. Otherwise -> continue normal mode below.

### Step 4 — Load vault context

1. Probe CLI availability first: `obsidian vault info=name`. If this fails, fall back to direct markdown edits for all write operations.
2. Read `VAULT_ROOT/AGENTS.md` before any write action.

**Persona 3 placement summary (from AGENTS.md):**
- `Work/Vaimo/` — work, professional, Vaimo-related content
- `Work/Vaimo/Meeting notes/` — meetings (see meeting-notes.md for subfolders)
- `Work/Vaimo/projects/<prj-Name>/` — project-specific docs
- `Personal/` — personal life, health, finance, goals
- `Work/Dev notes/` — technical references, runbooks, ADRs
- If ambiguous, ask the user before placing.

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
2. On update:
   - Run `obsidian outline path="<file>"` to get heading structure without reading the full file.
   - Read current file only when content merging is needed.
   - Match existing structure exactly (heading/list/checklist/table style, indentation, tone).
3. Merge without duplication.
4. Update YAML properties atomically:
   - `obsidian property:set name="updated" value="<ISO datetime>" path="<file>"`
   - `obsidian property:read name="related" path="<file>"` then merge and set back
   - `obsidian property:set name="summary" value="<text>" path="<file>"` when meaningful
5. Prefer direct markdown edits; use `obsidian append` only for simple single-line entries when faster.
6. If file was created via direct write (not `obsidian create`), call `obsidian reload` afterward so Obsidian picks up the change immediately.

### Step 9 — Confirm result

Report:
- created/updated page path
- tags applied
- related pages linked
- optional offer to open page in Obsidian via `obsidian open path="..."`

## Raw Mode

Goal: save content untouched with minimal frontmatter only.

1. If content missing, ask for it.
2. Read `AGENTS.md`; determine folder/title via Persona 3 flow.
3. Derive tags per `AGENTS.md`.
4. Confirm target path and tags.
5. Write:
   - YAML frontmatter (`tags`, `created`)
   - original input text verbatim

Raw mode restrictions:
- do not invoke `impersonator`
- do not add any links
- do not rewrite/reformat content

## References

- Calendar activity summary workflow: [references/calendar-whats-done.md](./references/calendar-whats-done.md)
- Todo reporting workflow: [references/todo-report.md](./references/todo-report.md)
- Email-thread capture and cleanup workflow: [references/email-threads.md](./references/email-threads.md)
- Meeting notes workflow: [references/meeting-notes.md](./references/meeting-notes.md)
- Google Drive download and routing: [references/google-drive-usage.md](./references/google-drive-usage.md)

## Notes

- Write page content in the same language as input; keep YAML tags in English.
- If the CLI probe in Step 4 fails, skip all `obsidian` commands and operate via direct filesystem edits; call `obsidian reload` once available to sync Obsidian's index.
