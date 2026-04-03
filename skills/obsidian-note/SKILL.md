---
name: obsidian-note
version: 1.0.0
description: "Obsidian: Create or update any vault note from markdown or plain text input."
metadata:
  openclaw:
    category: "productivity"
---

# obsidian-note

Create or update any note in the Obsidian knowledge vault. Automatically determines the correct folder, derives tags, detects duplicates, and delegates meeting notes to the `obsidian-meeting-manage` skill.

## Vault context

- **Vault root:** `/Users/zamoroka_pavlo/Library/CloudStorage/GoogleDrive-zapashok0@gmail.com/My Drive/obsidian/zamoroka`
- **AGENTS.md:** `<vault root>/AGENTS.md` — always read this first; it is the source of truth for structure, tagging, personas, and conventions
- **Template:** `_templates/note.md`

## When to use

Invoke this skill when the user wants to:
- Capture a note, idea, or piece of information
- Save a personal reflection, dev tip, or work note
- Update an existing note with new content
- "Make a note of…", "Add to my notes…", "Write this down…"

> **Do NOT use for meeting notes/transcripts** — those are handled by `obsidian-meeting-manage`.

---

## Instructions

Follow these steps precisely when this skill is invoked.

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
- Persona instructions for Notes Manager (Persona 3)

---

### Step 4 — Understand content and determine placement

Analyse the content to determine:
- **Domain:** work vs personal
- **Topic signals:** tech terms, project names, people names, keywords matching AGENTS.md tagging rules

Use the following decision tree (from Persona 3 in AGENTS.md):

```
Work-related tech topic / how-to / tool reference  →  Work/Dev notes/<tool-or-topic>/
Work idea or proposal                               →  Work/💡Ideas.md  (append)
PoC or project research                             →  Work/PoC/<ProjectName>/
Personal reflection, value, or principle            →  Personal/Thoughts/
DIY or hands-on project                             →  Personal/DIY/
Life purpose, Ikigai, mission                       →  Personal/Ikigai/
Productivity tip or technique                       →  Personal/Productivity/
```

**If placement is ambiguous** (e.g. no clear work/personal signal, no recognisable project name), ask a single focused question before proceeding. Examples:
> *"Is this work-related or personal?"*
> *"Which project does this relate to — ARB, SunnyEurope, SwissSense, or general/none?"*
> *"Should this go under Dev notes, or is it a personal productivity tip?"*

Only ask one question at a time. Wait for the answer before continuing.

---

### Step 5 — Search for existing notes

Before creating a new file, check for duplicates:
```bash
obsidian search query="<2–3 key topic terms>"
```

- **Match found** (same topic / same folder / same title intent) → plan to **UPDATE** that note
- **No match** → plan to **CREATE** a new note

---

### Step 6 — Derive tags

Apply tags from two dimensions (per AGENTS.md Tagging Rules):

**1. Folder-based mandatory tags:**
| Destination folder | Required tags |
|--------------------|--------------|
| `Work/` | `work` |
| `Work/Dev notes/` | `work`, `dev` |
| `Work/PoC/` | `work`, `vaimo`, `poc` |
| `Personal/` | `personal` |
| `Personal/Thoughts/` | `personal`, `thoughts` |
| `Personal/Ikigai/` | `personal`, `ikigai` |
| `Personal/DIY/` | `personal`, `diy` |
| `Personal/Productivity/` | `personal`, `productivity` |

**2. Content-based tags (add when detected):**
- `architecture`, `adr`, `decision` — architecture or decision documents
- `ai`, `prompt` — AI-related content
- `magento`, `docker`, `kubernetes`, `redis`, `newrelic`, `gcp` — specific tech topics
- Project: `al-rajhi-bank`, `swisssense`, `elon`, `sunnyeurope`, `sogesma`
- People (CamelCase, no spaces): e.g. `ViktorYakovenko`, `IvanBordiuh`

Minimum **2 tags** per note.

---

### Step 7 — Determine the note title and filename

- Use a descriptive, concise title matching the vault's existing naming style
- Use emojis in filenames where vault convention already does (e.g. `💡Ideas.md`, `🍽️ Plate.md`)
- Dev notes: use the tool/technology name as the filename (e.g. `Docker Networking.md`)
- Personal notes: use a clear topic phrase (e.g. `On Deep Work.md`)

---

### Step 8 — Create or update the note

#### Creating a new note

Prefer direct file creation to ensure correct YAML frontmatter and tags:

1. Determine full path: `VAULT_ROOT/<folder>/<Title>.md`
2. Write the file with this format:
```markdown
---
tags:
  - <tag1>
  - <tag2>
---

# <Note Title>

<Content>
```
3. If a template-only scaffold is sufficient, use CLI:
   ```bash
   obsidian create name="<Title>" template=note
   ```
   Then overwrite with correct YAML + content via direct file operation.

#### Updating an existing note

1. Read current content:
   ```bash
   obsidian read file="<note name>"
   ```
   Or read directly from the file path.
2. Merge/append new content intelligently:
   - Append under the relevant existing section heading if it exists
   - Add a new `## <Section>` heading if the topic is new
   - **Do not duplicate** content already present
3. Write the updated file back directly (preserving frontmatter).

#### Appending to special files (`💡Ideas.md`, `🍽️ Plate.md`)

Use the CLI append command:
```bash
obsidian append file="💡Ideas" content="- <new idea>"
```

#### Fallback

If the Obsidian CLI is unavailable or fails, create/edit the file directly at the vault path without interrupting the user.

---

### Step 9 — Confirm

Report:
- ✅ Note created/updated: full file path
- ✅ Tags applied: list them
- Offer: *"Would you like me to open the note in Obsidian?"* — if yes, run:
  ```bash
  obsidian open path="<relative path from vault root>"
  ```

---

## Examples

**New dev note:**
> User: *"Make a note: to reload nginx config use `nginx -s reload`"*
> Skill: searches for existing nginx note → not found → creates `Work/Dev notes/nginx.md` with tags `work`, `dev`

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

---

## Notes

- Always write note content in the **same language as the provided content** (Ukrainian or English). YAML tags are always in English.
- Always load `AGENTS.md` first — it is the living source of truth; folder structure and tagging rules may have been updated since this skill was written.
- Never create a new file if an existing note should be updated.
- When the vault's AGENTS.md is updated with new projects, folders, or team members, respect those changes immediately.
