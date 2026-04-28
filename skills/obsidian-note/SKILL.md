---
name: obsidian-note
description: "Obsidian: Create or update any wiki page, including meeting notes and todo reports, with vault-aware placement, tagging, linking, and optional raw mode."
metadata:
  category: "productivity"
  version: "3.0.1"
---

# obsidian-note

Create or update any wiki page in the Obsidian vault. This is the single note-management skill and covers regular notes, meeting notes/transcripts, todo reports, and raw save-as-is behavior.

## Vault context

- **Vault root and conventions:** always read `AGENTS.md` first. It is the source of truth for vault path, folder structure, personas, naming, and tagging rules.
- **Template:** `_templates/page.md`

## When to use

Invoke this skill when the user wants to:
- capture or update any note/page
- save notes from a Google Doc URL
- save meeting notes/transcripts
- view their todo/task report
- save content exactly as-is (`raw`, `as-is`, `verbatim`, `don't rewrite`)

## Modes

- **Normal mode (default):** full processing with placement, duplicate detection, related pages, wiki-links, and structure matching.
- **Meeting mode:** meeting-specific flow for transcript handling, meeting-folder selection, action-point extraction, and TASKS.md proposal flow.
- **Raw mode:** save text as-is with minimal YAML frontmatter only; no rewriting, no wiki-links, no impersonation.

## Instructions

Follow this decision flow when invoked.

### Step 1 — Gather content

If no content was provided, ask: *"Please paste the note content and I'll handle the rest."*

### Step 2 — Resolve Google Docs URLs (if present)

If input includes Google Docs URLs (`https://docs.google.com/document/d/...`):

Tool policy for note ingestion:
- Always use `doc_markdown_download` for Google Docs note/meeting imports.
- Never use `doc_markdown_output_tty` for this workflow because it does not persist files into the vault `_raw` staging directory.

1. Download each document as markdown via MCP tool `doc_markdown_download` with:
   - `doc_url`: source Google Doc URL
   - `output_dir`: `VAULT_ROOT/_raw`
2. If MCP is unavailable, use fallback:
   ```bash
   node /Users/zamoroka_pavlo/.agents/mcp/direct-tool-call.mjs \
     --server-command uv \
     --server-args '["--directory","/Users/zamoroka_pavlo/.agents/mcp/google-drive-mcp","run","google-drive-mcp"]' \
     --cwd /Users/zamoroka_pavlo/.agents/mcp/google-drive-mcp \
     --sdk-dir /Users/zamoroka_pavlo/.agents/mcp/jira-mcp/node_modules/@modelcontextprotocol/sdk \
     --tool doc_markdown_download \
     --args '{"doc_url":"<DOC_URL>","output_dir":"VAULT_ROOT/_raw"}'
   ```
3. Use fetched markdown as canonical input content.
4. If mode resolves to meeting flow, stage Google Docs files under `VAULT_ROOT/_raw/` and follow [references/MEETING-NOTES.md](./references/MEETING-NOTES.md) for YAML prepend + `mv` placement.

### Step 3 — Detect mode

Detect in this order:

1. **Todo report trigger** (`what's on my todo`, `show my tasks`, `what do I need to do`) -> follow [references/TODO-REPORT.md](./references/TODO-REPORT.md).
2. **Raw mode trigger** (`raw`, `as-is`, `verbatim`, `just save it`, `don't rewrite`, `no changes`, `don't modify`) -> follow [Raw Mode](#raw-mode).
3. **Meeting signals** (transcript/meeting wording, dated participant discussion, action-items structure, `1-1`, `sync`, `standup`, `retrospective`, `call with`) -> follow [references/MEETING-NOTES.md](./references/MEETING-NOTES.md).
4. Otherwise -> continue normal mode below.

### Step 4 — Load vault context

Read `VAULT_ROOT/AGENTS.md` before any write action.

### Step 5 — Placement and search

1. Determine folder via Persona 3 decision flow from `AGENTS.md`.
2. Run 2-3 focused `obsidian search` queries for duplicate detection and related-page discovery.
3. If contradictions with existing pages are found, stop and ask the user before proceeding.

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
2. On update, read current file first and match existing structure exactly (heading/list/checklist/table style, indentation, tone).
3. Merge without duplication.
4. Update YAML (`updated`, `related`, and `summary` when meaningful).
5. Prefer direct markdown edits; use `obsidian append` only for simple single-line entries when faster.

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
- do not add wiki-links
- do not rewrite/reformat content

## References

- Todo reporting workflow: [references/TODO-REPORT.md](./references/TODO-REPORT.md)
- Meeting notes workflow: [references/MEETING-NOTES.md](./references/MEETING-NOTES.md)

## Notes

- Write page content in the same language as input; keep YAML tags in English.
- If Obsidian CLI is unavailable, continue with direct markdown edits.
