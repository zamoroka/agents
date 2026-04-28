---
name: obsidian-meeting-manage
version: 2.3.0
description: "Obsidian: Add or update a meeting transcript wiki page with auto-tagging and wiki-linking."
metadata:
  category: "productivity"
---

# obsidian-meeting-manage

Create or update a meeting transcript wiki page in the Obsidian vault. Automatically derives tags, detects duplicates, and builds wiki-links to related pages.

## Vault context

- **Vault root:** see `AGENTS.md` — always read it first; it has the vault path, folder structure, project list, TASKS.md locations, and tagging rules
- **Meeting notes folder:** `Work/Vaimo/Meeting notes/`
- **Raw meeting note target root:** `~/Library/CloudStorage/GoogleDrive-zapashok0@gmail.com/My Drive/obsidian/zamoroka/Work/Vaimo/Meeting notes/`
- **Naming convention:** see **Meeting notes naming** rule in AGENTS.md Persona 3 (`1-1 P1 - P2` for 2-person, short descriptive title for 3+)

## When to use

Invoke this skill when the user wants to:
- Save a meeting transcript or notes
- Capture key points from a 1-1 or team meeting
- Update an existing meeting wiki page with follow-up content

## Instructions

Follow these steps precisely when this skill is invoked:

### Command usage policy

Use Obsidian CLI commands mainly for search efficiency and finding connected pages.

- Prefer `obsidian search` when locating existing meeting pages or related project context.
- For creating/updating page content, edit markdown files directly at the vault path.
- Use CLI create/append only when it is clearly faster than direct editing.

### Step 1 — Gather missing information

**If meeting content was NOT provided in the prompt:**
> Ask: *"Please paste the meeting transcript or notes, and I'll handle the rest."*
> Wait for the user's response before proceeding.

**If content is provided but project context is unclear** (no obvious project name, ticket, or tech stack mentioned):
> Ask: *"Was this meeting related to a Vaimo project? If yes, which one: ARB, SunnyEurope, SwissSense, Elon, SOGESMA, or general/none?"*

If the prompt contains Google Docs meeting URL(s), fetch transcript content first (Step 1a), then continue with parsing and classification.

### Step 1a — Google Docs URL ingestion

When user provides a Google Docs URL (for example `https://docs.google.com/document/d/...`):

1. Call MCP tool `doc_markdown_download` with:
   - `doc_url`: URL from the prompt.
2. If MCP is not configured, use direct fallback command:
   ```bash
   node /Users/zamoroka_pavlo/.agents/mcp/direct-tool-call.mjs \
     --server-command uv \
     --server-args '["--directory","/Users/zamoroka_pavlo/.agents/mcp/google-drive-mcp","run","google-drive-mcp"]' \
     --cwd /Users/zamoroka_pavlo/.agents/mcp/google-drive-mcp \
     --sdk-dir /Users/zamoroka_pavlo/.agents/mcp/jira-mcp/node_modules/@modelcontextprotocol/sdk \
     --tool doc_markdown_download \
     --args '{"doc_url":"<DOC_URL>"}'
   ```
3. Load the downloaded markdown file and use it as the meeting body input.
4. Preserve the source URL in YAML `source` (or in summary text if `source` is not used by vault schema).

### Step 2 — Parse the meeting content

Extract the following:
- **Date:** Look for explicit date mentions (e.g. "Mon, 14 Apr 26", "2026-04-14"). If absent, run `date +%Y-%m-%d` and use today's date.
- **Participants:** All named people. Format as CamelCase for tags (e.g. "Ivan Bordiuh" → `IvanBordiuh`). "Pavlo" always refers to the vault owner (Pavlo Zamoroka).
- **Discussion topics:** Group into logical sections with `###` headings.
- **Action items / next steps:** Any follow-ups assigned to specific people or deadlines. Keep these as plain bullet list items (`- ...`) in the meeting note, never checklist format (`- [ ] ...`).
- **Tech/content signals:** Detect keywords like `magento`, `docker`, `kubernetes`, `redis`, `newrelic`, `gcp`, `ai`, `architecture`, `decision`, `adr`, `transcript`.
- **Transcript links:** Strip any external transcript links (e.g. Granola `https://notes.granola.ai/...` or similar). Never include them in the page.

### Step 3 — Determine create vs. update

Search for existing meeting pages and connected context:
```bash
obsidian search query="<meeting date> <participant name> <project keyword>"
```

Use 1-2 additional focused searches (participant aliases, project code names, alternate date formats) to avoid duplicates and find related pages.

- **If a page with the same date and overlapping participants exists** → update that page (merge new content into the appropriate sections, append new action items).
- **Otherwise** → create a new page.

### Step 3a — Determine meeting subfolder (required)

Before create/update, determine the target subfolder under:
`Work/Vaimo/Meeting notes/`

Use topic/participants/project signals to propose a folder:
- 1-1 with Bartosz about SwissSense → suggest `SwissSense`
- EME Engineering meetup / leadership strategy topics → suggest `EME Engineering Leadership and Strategy Discussions`
- If no clear match, suggest `General`

Always provide:
1. suggested subfolder
2. short rationale
3. 1-3 alternatives

Then ask user approval. Do not write any file until subfolder is approved.

### Step 4 — Find related pages and detect contradictions

Search for pages related to the meeting topic:
```bash
obsidian search query="<project name> <key decision or topic>"
```

For each related page found:
1. Collect its filename for the `related` YAML property
2. Identify natural places in the meeting content to add `[[wiki-link]]` references (e.g. link to project README, previous meeting, ADR page)
3. **Check for contradictions** — if the meeting content contradicts an existing wiki page (e.g. a decision reverses a previous one), stop and ask the user in chat:
   > *"This meeting seems to reverse the decision in [[Previous ADR]] which said X. Should I update that page too, or just note the change here?"*
   Only proceed after the user decides.

### Step 5 — Derive YAML tags

Apply tags per the **Tagging Rules** in AGENTS.md. For meeting pages always include `work`, `vaimo`, `meeting`, plus:
- participant tags (CamelCase, no spaces): e.g. `IvanBordiuh`, `MaksymYavorskyi`
- project tag from content signals: `al-rajhi-bank`, `swisssense`, `sunnyeurope`, `elon`, `sogesma`
- content signal tags when detected: `transcript`, `architecture`, `adr`, `decision`, `magento`, `docker`, `kubernetes`, `redis`, `newrelic`, `gcp`, `ai`

### Step 6 — Confirm with user

Before writing any file, describe the planned change and ask for confirmation:
- **New page:** *"I'll create `Work/Vaimo/Meeting notes/<approved subfolder>/2026-04-23 1-1 Pavlo - Ivan.md` with tags: `work`, `vaimo`, `meeting`, `IvanBordiuh`. Related: `[[ARB]]`. Proceed?"*
- **Update:** *"I want to add [description] to the existing meeting page `Work/Vaimo/Meeting notes/<approved subfolder>/2026-04-02 1-1 Pavlo - Ivan.md`. Proceed?"*

Wait for confirmation before writing.

### Step 7 — Create or update the page

> **Raw mode is always used when the user provides a meeting transcript.** Do NOT invoke the `impersonator` skill, do NOT rewrite or restructure the transcript content, do NOT add wiki-links inside the body text.
> Exception: normalize checklist items (`- [ ]`, `- [x]`) into plain bullets (`-`) in the meeting note body.

**File path:** `Work/Vaimo/Meeting notes/<approved subfolder>/YYYY-mm-dd <meeting title>.md`.

Filename rules:
- Must always start with date prefix `YYYY-mm-dd` (for example `2026-04-28`)
- Then one space, then meeting title
- End with `.md`

Write the file as:
1. YAML frontmatter only (tags, created, updated, related, summary) — per **Wiki Page Format** in AGENTS.md.
2. The transcript content appended after the frontmatter, preserving source text except checklist normalization.
3. Meeting note body must not contain checklist syntax (`- [ ]`, `- [x]`); use plain bullets only (`- ...`).

**For updates:** Read the existing file, merge new sections intelligently. Do not duplicate existing content. Update `updated` timestamp.

### Step 8 — Action points policy

For Google Docs-ingested meetings:
1. Keep action points in the meeting note as simple bullet list items (`- ...`) only.
2. Extract all action points assigned to Pavlo (or unassigned). Format each as a ready-to-paste TASKS.md entry (include context such as project, source meeting page wiki-link, and due date if known).
3. Present the proposed todos as a concrete preview before asking for approval. Example:
   > *"I'd add the following to TASKS.md — confirm to proceed:*
   > ```
   > - [ ] Follow up with Ivan on Redis migration timeline [[2026-04-28 1-1 Pavlo - Ivan]]
   > - [ ] Send architecture proposal draft to Bartosz by 2026-05-02 [[2026-04-28 1-1 Pavlo - Ivan]]
   > ```
   > *Add these to TASKS.md?"*
4. Only update `TASKS.md` after explicit user approval. Do not add, remove, or reword items without re-confirming.

For non-Google-Docs meetings:
1. Keep action points in the meeting note as simple bullet list items (`- ...`) by default.
2. Extract all action points assigned to Pavlo (or unassigned). Format each as a ready-to-paste TASKS.md entry (include context such as project, source meeting page wiki-link, and due date if known).
3. Present the proposed todos as a concrete preview before asking for approval (same format as above).
4. Only update `TASKS.md` after explicit user approval. Do not add, remove, or reword items without re-confirming.

### Step 9 — Confirm

Report:
- ✅ Page created/updated: full file path
- ✅ Action points captured as simple list items in the meeting note
- ✅ Presented a concrete preview of proposed TASKS.md entries (Pavlo-assigned or unassigned todos) before asking for approval
- ✅ TASKS.md changed only if user explicitly approved the previewed items
- ✅ Related pages linked: list them
- Offer: *"Would you like me to open the page in Obsidian?"* — if yes, run `obsidian open path="..."`

## Examples

**Creating a new page:**
> User: *"Save this meeting: [transcript pasted]"*
> Skill: parses content, confirms with user, creates `Work/Vaimo/Meeting notes/<approved subfolder>/2026-04-14 1-1 Pavlo - Anton.md`, keeps action points as plain bullets in the note.

**Updating an existing page:**
> User: *"Add a follow-up to my meeting with Ivan from April 2nd"*
> Skill: finds `2026-04-02 1-1 Pavlo - Ivan.md`, confirms update plan, appends new content, keeps action points as plain bullets.

**No content provided:**
> User: *"Save my meeting notes"*
> Skill: asks *"Please paste the meeting transcript or notes, and I'll handle the rest."*

**Contradiction found:**
> Skill: *"This meeting says we'll switch to headless checkout, but [[ARB Architecture Decision]] says headless is out of scope. Should I update that ADR too, or just note the change in the meeting page?"*

## Notes

- "Pavlo" in content always refers to Pavlo Zamoroka (vault owner) — no need to ask for clarification.
- Write page content in the **same language as the provided content**. YAML tags always in English.
- If the obsidian CLI is unavailable, continue with direct markdown edits without interrupting the user.
