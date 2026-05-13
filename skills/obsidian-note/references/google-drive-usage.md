# Google Drive — Download and Route Workflow

Use this workflow whenever the user provides a Google Docs URL (`https://docs.google.com/document/d/...`) as source content.

## Tool

| Property | Value |
|----------|-------|
| MCP server | `google-drive` |
| Tools | `doc_get_metadata`, `doc_markdown_download` |
| Fallback | `direct-tool-call` skill (when MCP is unavailable) |

**Never use `doc_markdown_output_tty`** for vault imports — it streams the markdown to the terminal without persisting it to `_raw`.

_Why this matters: the entire recovery story for botched imports depends on having the unedited export on disk. 
If something goes wrong mid-flow (wrong  placement, bad cleanup, partial frontmatter), `_raw/<doc-id>.md` is what we roll back to. A TTY-only output means there is nothing to roll back to._

---

## Step 0 — Fetch document metadata

Before downloading, call `doc_get_metadata` to get the document title and dates. 
The title often contains the review period, project name, or other context needed to derive a meaningful filename and vault placement.

```
doc_url : <source Google Doc URL>
```

Returns: `id`, `name`, `createdTime`, `modifiedTime`.

Use `name` as the primary signal for:
- Review period (e.g. "Q4 2023 Performance Review" → `2023-Q4`)
- File name (cleaned, lowercase-hyphenated)
- Content type detection (see Step 2)

If `doc_get_metadata` is unavailable, skip this step and proceed to Step 1. In that case, ask the user for the document title/period if it cannot be inferred from content.

---

## Step 1 — Download to `_raw`

_Why `_raw` exists as a staging area: 
Google Docs markdown export is noisy (backslash escapes, blank-line bloat, inline image placeholders). 
Doing the cleanup in place inside the final folder would mean the user's vault sees intermediate states. 
Staging in `_raw` keeps the final destination clean and preserves the unedited export for recovery._

Call `doc_markdown_download` for every Google Docs URL in the input:

```
doc_url    : <source Google Doc URL>
output_dir : VAULT_ROOT/_raw
```

Recommended `_raw` filename:
- `VAULT_ROOT/_raw/<doc-id>.md` (preferred, derived from the URL)
- `VAULT_ROOT/_raw/<YYYY-mm-dd>-gdoc-import.md` (fallback when doc-id is unavailable)

Keep the downloaded file as the canonical input for the next steps.

---

## Step 2 — Detect document content type

Analyse the downloaded markdown and classify the document into one of the following content types:

| Content type | Detection signals |
|---|---|
| **meeting-notes** | participant list, dated discussion, action items, `1-1`, `sync`, `standup`, `retrospective`, `call with`, agenda-style headings |
| **technical-doc** | architecture decisions, runbooks, ADRs, API specs, implementation guides, configuration references |
| **project-doc** | project briefs, roadmaps, requirement docs, sprint plans, status reports |
| **reference** | how-to guides, checklists, glossaries, templates, policies |
| **personal-note** | journal entries, personal reflections, health/life notes |
| **unknown** | cannot be reliably classified with the above signals |

If confident, proceed automatically. If ambiguous between two types, ask:
*"This looks like it could be [type A] or [type B]. Which fits better?"*

---

## Step 3 — Route by content type

### Meeting notes → delegate to meeting-notes.md

If content type is **meeting-notes**:

1. The file is already staged in `VAULT_ROOT/_raw/` from Step 1.
2. Continue with **Step 2** of [meeting-notes.md](./meeting-notes.md) (parse meeting content, find candidate page, propose subfolder, etc.).
3. The `_raw` file serves as the ingestion source — do not re-download.

### All other content types → analyse, edit in `_raw`, then move

If content type is **not** meeting-notes:

1. Read `VAULT_ROOT/AGENTS.md` to load vault structure and Persona 3 placement rules.
2. Run layered search to detect duplicate or closely related pages:
   - `obsidian search:context query="<key title terms>"` (1-2 queries)
   - For top hits: `obsidian tag name=<detected-tag> verbose` and `obsidian backlinks file="<hit>"`
3. Propose a placement plan and ask the user for confirmation before any move:

   > **Placement proposal**
   > - **Detected type:** `<content type>`
   > - **Suggested path:** `<VAULT_ROOT/Folder/Subfolder/YYYY-mm-dd Title.md>`
   > - **Tags:** `<tag1>`, `<tag2>`, …
   > - **Summary:** _one-sentence description of the document_
   >
   > Alternatives: `<alt path 1>`, `<alt path 2>`
   >
   > Confirm placement, or suggest a different folder?

4. Wait for explicit user confirmation before proceeding.
5. **Edit the `_raw` file in-place** — do not create a new file yet. Apply:
   - Prepend YAML frontmatter (`tags`, `created`, `source`, `summary`) to the top of the file.
   - Only permitted body cleanup:
     - Strip markdown export backslash escapes (`\-` → `-`, `4\.` → `4.`, `\!` → `!`, `\<-\>` → `<->`)
     - Remove duplicate blank lines
   Do **not** summarize, condense, rewrite, or restructure any body content from the source doc.
   Impersonator applies only to the YAML `summary` value — never to the document body.
6. **Move** the edited `_raw` file to the confirmed destination path using the Obsidian CLI so wikilinks stay intact:
   ```bash
   obsidian move path="_raw/<doc-id>.md" to="<Folder/Subfolder/YYYY-mm-dd Title.md>"
   ```
   (create flow). For update flow, merge content into the existing page instead — do not replace via move.
   If CLI is unavailable and `mv` is used as fallback, call `obsidian reload` afterward.

---

## Notes

- The canonical flow for every Google Doc is: **download → `_raw` → analyse & edit in `_raw` → `obsidian move` to final path**.
  Never skip the `_raw` staging step, even when the destination is immediately obvious — it preserves the original markdown and makes recovery straightforward.
- All edits (frontmatter injection, escaping cleanup) are done on the `_raw` file before the move, so the final destination always receives a fully prepared file.
- Always use `obsidian move` (not `mv`) — this keeps wikilinks pointing to the file intact across the vault.
- If MCP is unavailable, invoke the `direct-tool-call` skill and continue from Step 2.
- Write page content in the same language as the source document; keep YAML tags in English.


