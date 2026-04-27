---
name: obsidian-note
version: 2.0.0
description: "Obsidian: Create or update any wiki page from markdown or plain text input."
metadata:
  category: "productivity"
---

# obsidian-note

Create or update any wiki page in the Obsidian vault. Automatically determines the correct folder, derives tags, detects duplicates, builds wiki-links to related pages, and delegates meeting notes to the `obsidian-meeting-manage` skill.

## Vault context

- **Vault root:** see `AGENTS.md` — always read it first; it is the source of truth for the vault path, structure, tagging, personas, and conventions
- **Template:** [_templates/page.md](_templates/page.md)

## When to use

Invoke this skill when the user wants to:
- Capture a note, idea, or piece of information
- Save a personal reflection, dev tip, or work note
- Update an existing wiki page with new content
- "Make a note of…", "Add to my notes…", "Write this down…"
- View their todo/task list — "what's on my todo?", "show my tasks", "what do I need to do?"

> **Do NOT use for meeting notes/transcripts** — those are handled by `obsidian-meeting-manage`.

---

## Instructions

Follow these steps precisely when this skill is invoked.

### Command usage policy

Use Obsidian CLI commands for discovery efficiency (mainly search and relationship discovery between pages).

- Prefer `obsidian search` to find candidate pages, related topics, and nearby context.
- For page updates, edit markdown files directly at the vault path.
- For page creation, default to direct markdown file creation; CLI create/append is optional only when it is clearly faster.

### Step 1 — Gather input

**If no content was provided in the prompt:**
> Ask: *"Please paste the note content and I'll handle the rest."*
> Wait for the user's response before proceeding.

---

### Step 2 — Detect meeting note / transcript → delegate

Check for meeting signals in the content:
- Explicit meeting-related words: "discussed", "next steps", "action items", "transcript", "sync", "1-1", "standup", "retrospective", "call with"
- Named participants + a date + discussion structure
- User explicitly calls it a "meeting note" or "transcript"

**If any of these signals are present → stop and invoke the `obsidian-meeting-manage` skill instead.** Do not process the content further here.

---

### Step 3 — Load vault context

Before any further analysis, always read the vault's AGENTS.md:
```bash
cat "VAULT_ROOT/AGENTS.md"
```
(Replace `VAULT_ROOT` with the actual vault root path.)

This provides:
- Current folder structure
- Tagging rules (folder-based and content-based)
- Known projects, team members, and tech stack
- Persona instructions for Wiki Page Manager (Persona 3)

---

### Step 4 — Understand content and determine placement

Analyse the content to determine domain (work vs personal) and topic signals (tech terms, project names, keywords).

Use the **Persona 3 Decision Flow** from AGENTS.md to pick the correct folder. If placement is ambiguous, ask one focused question before continuing.

---

### Step 5 — Search for existing and related pages

Run 2-3 focused searches to cover both duplicate detection and related-page discovery in one pass:
```bash
obsidian search query="<key topic terms>"
obsidian search query="<related concept or project>"
```

- **Existing match** (same topic / same folder / same title intent) → plan to **UPDATE** that page
- **No match** → plan to **CREATE** a new page
- **Related pages found** → collect filenames for the `related` YAML property and identify natural `[[wiki-link]]` placements in content

**Contradiction check:** if an existing page and the new content state conflicting facts, follow the **Contradiction Detection** rules in AGENTS.md — ask the user in chat what to do before proceeding.

---

### Step 6 — Derive tags

Apply tags per the **Tagging Rules** in AGENTS.md (folder-based mandatory tags + content-based tags). Minimum 2 tags per page.

---

### Step 7 — Determine the page title and filename

- Use a descriptive, concise title matching the vault's existing naming style
- Use emojis in filenames where vault convention already does (e.g. `💡Ideas.md`, `🍽️ Plate.md`)
- Dev notes: use the tool/technology name as the filename (e.g. `Docker Networking.md`)
- Personal notes: use a clear topic phrase (e.g. `On Deep Work.md`)

---

### Step 8 — Confirm with user

Before writing any file, describe the planned change and ask for confirmation:
- **New page:** *"I'll create `Work/Dev notes/Redis.md` with these tags: `work`, `dev`, `redis`. Content: [brief summary]. Proceed?"*
- **Update:** *"I want to add [description] to the `## Caching` section of `Work/Dev notes/Redis.md`. Proceed?"*

Wait for confirmation before writing.

---

### Step 9 — Create or update the page

Invoke the `impersonator` skill before writing any content.

#### Creating a new page

Use the most structurally similar existing page as a layout template. Use the **Wiki Page Format** from AGENTS.md for YAML frontmatter. Add `[[wiki-links]]` naturally in the content to related pages found in Step 5.

#### Updating an existing page

1. **Always read the file first** — before writing anything, read the current content directly from the file path.
2. **Analyse the existing structure** — identify the formatting conventions used:
   - Does it use `## headings` with prose, or flat `- [ ] checklist` items, or bullet lists, or a table?
   - What is the tone/verbosity of existing entries?
   - Are there recurring patterns (e.g. emoji prefixes, nesting depth, date stamps)?
3. **Match the existing structure exactly** — new content must blend in:
   - Use the same list style (`- [ ]`, `-`, `*`, numbered) as the surrounding entries
   - Use the same heading level and style if adding under a section
   - Use the same nesting depth and indentation
   - **Do not introduce new formatting conventions** (e.g. don't add `##` headings to a flat checklist file, don't add prose paragraphs to a bullet-list file)
4. Merge/append new content:
   - Insert under the relevant existing section heading if it exists
   - Add a new `## <Section>` heading only if the rest of the file also uses `##` headings
   - **Do not duplicate** content already present
5. Update YAML frontmatter:
   - Set `updated` to current datetime
   - Add or update `related` with any newly discovered wiki-links
   - Update `summary` if the page content has changed meaningfully
6. Write the updated markdown file back directly (preserving frontmatter).

#### Appending to special files (`💡Ideas.md`, `🍽️ Plate.md`)

1. **Read the file first** to understand its structure (see "Updating an existing page" above).
2. Format the new entry to match the existing style exactly.
3. Use the CLI append command only if the formatted content is a simple single-line entry and direct edit is not simpler:
   ```bash
   obsidian append file="💡Ideas" content="- <new idea>"
   ```
    For multi-line or structured entries, update the markdown file directly to ensure correct formatting.

#### Fallback

If the Obsidian CLI is unavailable or fails, create/edit the file directly at the vault path without interrupting the user.

---

### Step 10 — Confirm

Report:
- ✅ Page created/updated: full file path
- ✅ Tags applied: list them
- ✅ Related pages linked: list them (or note if none found)
- Offer: *"Would you like me to open the page in Obsidian?"* — if yes, run:
  ```bash
  obsidian open path="<relative path from vault root>"
  ```

---

## Wiki Audit

See the **Lint / Audit** section in `AGENTS.md` for full audit instructions.

Triggered when user asks: *"lint the wiki"*, *"audit my notes"*, *"check for broken links"*

Summary:
1. Collect all `.md` files in the vault
2. Check each for: missing/empty YAML properties, broken `[[wiki-links]]`, broken URLs, inconsistent tags
3. Report grouped results with suggested fixes

---

## Todo Report

Triggered when user asks: *"what's on my todo?"*, *"show my tasks"*, *"what do I need to do?"*

Load and follow the dedicated [todo-report.md](./todo-report.md) instructions only when this trigger is active:

- [todo-report.md](./todo-report.md)

---

## Examples

**New dev page:**
> User: *"Make a note: to reload nginx config use `nginx -s reload`"*
> Skill: searches for existing nginx page → not found → confirms with user → creates `Work/Dev notes/nginx.md` with tags `work`, `dev`

**Append to Ideas:**
> User: *"Add idea: build a CLI tool that summarises Jira tickets with AI"*
> Skill: appends to `Work/💡Ideas.md`

**Personal reflection:**
> User: *"Write a note about my thoughts on deep work"*
> Skill: creates `Personal/Thoughts/On Deep Work.md` with tags `personal`, `thoughts`

**Ambiguous input:**
> User: *"Make a note about the Redis caching discussion"*
> Skill: asks *"Is this work-related or personal?"* → after answer, places in `Work/Dev notes/Redis.md` or similar

**Meeting note → delegation:**
> User: *"Add notes from my call with Ivan today about ARB"*
> Skill: detects meeting signals → delegates to `obsidian-meeting-manage`

**Todo report:**
> User: *"What's on my todo?"*
> Skill: runs `obsidian tasks todo`, filters/groups/sorts the output, renders the report

**Contradiction found:**
> Skill: *"I found a conflict: `Work/Dev notes/Redis.md` says we're not using Redis in ARB, but the new content says Redis is active. Which is correct?"*

---

## Notes

- Always load `AGENTS.md` first (Step 3) — it is the living source of truth; folder structure, tagging rules, and project lists may have changed.
- Write page content in the **same language as the provided content**. YAML tags always in English.
- If the obsidian CLI is unavailable, fall back to direct file operations without interrupting the user.
