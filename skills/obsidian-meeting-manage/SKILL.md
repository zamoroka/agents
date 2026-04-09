---
name: obsidian-meeting-manage
version: 1.0.0
description: "Obsidian: Add or update a Vaimo meeting note with auto-tagging and task extraction."
metadata:
  openclaw:
    category: "productivity"
---

# obsidian-meeting-manage

Create or update a Vaimo meeting note in the Obsidian vault. Automatically derives tags, detects duplicates, and extracts action items into the relevant project's TASKS.md.

## Vault context

- **Vault root:** `/Users/zamoroka_pavlo/Library/CloudStorage/GoogleDrive-zapashok0@gmail.com/My Drive/obsidian/zamoroka`
- **Meeting notes folder:** `Work/Vaimo/Meeting notes/`
- **Naming convention:** `YYYY.MM.DD <Title>.md` where `<Title>` is `1-1 <P1> - <P2>` for 2-person meetings, or a descriptive name (e.g. `ARB Team Sync`) for 3+ people
- **TASKS.md locations:** `Work/Vaimo/projects/ARB/TASKS.md`, `Work/Vaimo/projects/SunnyEurope/TASKS.md`, `Work/Vaimo/projects/SwissSense/TASKS.md`
- **Known projects:** ARB (Al-Rajhi Bank), SunnyEurope, SwissSense, Elon, SOGESMA

## When to use

Invoke this skill when the user wants to:
- Save a meeting transcript or notes
- Capture key points from a 1-1 or team meeting
- Update an existing meeting note with follow-up content

## Instructions

Follow these steps precisely when this skill is invoked:

### Command usage policy

Use Obsidian CLI commands mainly for search efficiency and finding connected notes.

- Prefer `obsidian search` when locating existing meeting notes or related project context.
- For creating/updating note content, edit markdown files directly at the vault path.
- Use CLI create/append only when it is clearly faster than direct editing.

### Step 1 — Gather missing information

**If meeting content was NOT provided in the prompt:**
> Ask: *"Please paste the meeting transcript or notes, and I'll handle the rest."*
> Wait for the user's response before proceeding.

**If content is provided but project context is unclear** (no obvious project name, ticket, or tech stack mentioned):
> Ask: *"Was this meeting related to a Vaimo project? If yes, which one: ARB, SunnyEurope, SwissSense, Elon, SOGESMA, or general/none?"*

### Step 2 — Parse the meeting content

Extract the following:
- **Date:** Look for explicit date mentions (e.g. "Mon, 14 Apr 26", "2026-04-14"). If absent, run `date +%Y.%m.%d` and use today's date.
- **Participants:** All named people. Format as CamelCase for tags (e.g. "Ivan Bordiuh" → `IvanBordiuh`). "Pavlo" always refers to the vault owner (Pavlo Zamoroka).
- **Discussion topics:** Group into logical sections with `###` headings.
- **Action items / next steps:** Any tasks assigned to specific people, deadlines, or follow-ups.
- **Tech/content signals:** Detect keywords like `magento`, `docker`, `kubernetes`, `redis`, `newrelic`, `gcp`, `ai`, `architecture`, `decision`, `adr`, `transcript`.
- **Transcript links:** Strip any external transcript links (e.g. Granola `https://notes.granola.ai/...` or similar). Never include them in the note.

### Step 3 — Determine create vs. update

Search for existing meeting notes and connected context:
```bash
obsidian search query="<meeting date> <participant name> <project keyword>"
```

Use 1-2 additional focused searches (participant aliases, project code names, alternate date formats) to avoid duplicates and find related notes.

- **If a note with the same date and overlapping participants exists** → update that note (merge new content into the appropriate sections, append new action items).
- **Otherwise** → create a new note.

### Step 4 — Derive YAML tags

Always include:
- `work`, `vaimo`, `meeting`

Add from participants (CamelCase, no spaces):
- e.g. `IvanBordiuh`, `MaksymYavorskyi`, `ViktorYakovenko`

Add from project:
- `al-rajhi-bank` (ARB), `swisssense`, `sunnyeurope`, `elon`, `sogesma`

Add from content signals (if detected):
- `transcript`, `architecture`, `adr`, `decision`, `magento`, `docker`, `kubernetes`, `redis`, `newrelic`, `gcp`, `ai`

### Step 5 — Create or update the note

**File path:** `Work/Vaimo/Meeting notes/YYYY.MM.DD <Title>.md`
where `<Title>` is determined as follows:
- **Exactly 2 participants** → `1-1 <P1> - <P2>` (e.g. `1-1 Pavlo - Ivan`)
- **3 or more participants** → a short descriptive name (e.g. `ARB Team Sync`)

**Note format:**
```markdown
---
tags:
  - work
  - vaimo
  - meeting
  - <people-tags>
  - <project-tag>
  - <content-tags>
---
<Weekday>, <DD> <Mon> <YY> · <email or identifier of external participant if known>

### <Topic 1>

- Key point
- Key point

### <Topic 2>

- Key point

### Next Steps

- <Person>
    - <Action item>
- <Person>
    - <Action item>
```

Create/update the markdown file directly at the vault path.

If CLI create is used for speed, treat it as a scaffold only and still verify/finalize file content via direct markdown edit.

**For updates:** Read the existing markdown file, merge new sections intelligently. Do not duplicate content that already exists. Append to `### Next Steps` or create it if missing.

### Step 6 — Update TASKS.md

For each action item extracted:
1. Determine which project it belongs to (from context or the project tag derived above).
2. Append tasks to the relevant `Work/Vaimo/projects/<Project>/TASKS.md`:
   - Group under an appropriate `### <Topic>` heading (create a new heading if needed).
   - Format: `- [ ] <task description>` (add `📅 YYYY-MM-DD` if a deadline was mentioned).
   - Do NOT duplicate tasks already listed.

If no clear project is identified, skip TASKS.md update and note this in the confirmation.

### Step 7 — Confirm

Report:
- ✅ Note created/updated: full file path
- ✅ Tasks added to TASKS.md (list them), or ⚠️ no tasks extracted
- Offer: *"Would you like me to open the note in Obsidian?"* — if yes, run `obsidian open path="..."`

## Examples

**Creating a new note:**
> User: *"Save this meeting: [transcript pasted]"*
> Skill: parses content, creates `Work/Vaimo/Meeting notes/2026.04.14 1-1 Pavlo - Anton.md`, updates ARB TASKS.md with extracted actions.

**Updating an existing note:**
> User: *"Add a follow-up to my meeting with Ivan from April 2nd"*
> Skill: finds `2026.04.02 1-1 Pavlo - Ivan.md`, appends new content, updates SunnyEurope TASKS.md.

**No content provided:**
> User: *"Save my meeting notes"*
> Skill: asks *"Please paste the meeting transcript or notes, and I'll handle the rest."*

## Notes

- Always write note content in the **same language as the provided content** (Ukrainian or English). YAML tags are always in English.
- Participant tags use CamelCase with no spaces (e.g. `PavloZamoroka`, `IvanBordiuh`).
- "Pavlo" in content always refers to Pavlo Zamoroka (vault owner) — no need to ask for clarification.
- If the obsidian CLI is unavailable, continue with direct markdown edits without interrupting the user.
