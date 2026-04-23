---
name: obsidian-meeting-manage
version: 2.0.0
description: "Obsidian: Add or update a Vaimo meeting wiki page with auto-tagging, wiki-linking, and task extraction."
metadata:
  openclaw:
    category: "productivity"
---

# obsidian-meeting-manage

Create or update a Vaimo meeting wiki page in the Obsidian vault. Automatically derives tags, detects duplicates, builds wiki-links to related pages, and extracts action items into the relevant project's TASKS.md.

## Vault context

- **Vault root:** see `AGENTS.md` — always read it first; it has the vault path, folder structure, project list, TASKS.md locations, and tagging rules
- **Meeting notes folder:** `Work/Vaimo/Meeting notes/`
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

### Step 2 — Parse the meeting content

Extract the following:
- **Date:** Look for explicit date mentions (e.g. "Mon, 14 Apr 26", "2026-04-14"). If absent, run `date +%Y.%m.%d` and use today's date.
- **Participants:** All named people. Format as CamelCase for tags (e.g. "Ivan Bordiuh" → `IvanBordiuh`). "Pavlo" always refers to the vault owner (Pavlo Zamoroka).
- **Discussion topics:** Group into logical sections with `###` headings.
- **Action items / next steps:** Any tasks assigned to specific people, deadlines, or follow-ups.
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
- **New page:** *"I'll create `Work/Vaimo/Meeting notes/2026.04.23 1-1 Pavlo - Ivan.md` with tags: `work`, `vaimo`, `meeting`, `IvanBordiuh`. Related: `[[ARB]]`. Proceed?"*
- **Update:** *"I want to add [description] to the existing meeting page `2026.04.02 1-1 Pavlo - Ivan.md`. Proceed?"*

Wait for confirmation before writing.

### Step 7 — Create or update the page

Invoke the `impersonator` skill before writing content.

Use the **Wiki Page Format** from AGENTS.md for YAML frontmatter. The meeting-specific body structure is:

```markdown
<Weekday>, <DD> <Mon> <YY> · <email or identifier of external participant if known>

### <Topic 1>

- Key point
- Key point

### <Topic 2>

- Key point

### Next Steps

- <Person>
    - <Action item>
```

**File path:** `Work/Vaimo/Meeting notes/YYYY.MM.DD <Title>.md` (see naming convention in Vault context above).

Create/update the markdown file directly at the vault path. If CLI create is used for speed, treat it as a scaffold and still finalize content via direct file edit.

**For updates:** Read the existing file, merge new sections intelligently. Do not duplicate existing content. Append to `### Next Steps` or create it if missing. Update `updated` timestamp.

### Step 8 — Update TASKS.md

For each action item extracted:
1. Determine which project it belongs to (from context or the project tag derived above).
2. Append tasks to the relevant `Work/Vaimo/projects/<Project>/TASKS.md`:
   - Group under an appropriate `### <Topic>` heading (create a new heading if needed).
   - Format: `- [ ] <task description>` (add `📅 YYYY-MM-DD` if a deadline was mentioned).
   - Do NOT duplicate tasks already listed.
   - Update `updated` timestamp in TASKS.md frontmatter.

If no clear project is identified, skip TASKS.md update and note this in the confirmation.

### Step 9 — Confirm

Report:
- ✅ Page created/updated: full file path
- ✅ Tasks added to TASKS.md (list them), or ⚠️ no tasks extracted
- ✅ Related pages linked: list them
- Offer: *"Would you like me to open the page in Obsidian?"* — if yes, run `obsidian open path="..."`

## Examples

**Creating a new page:**
> User: *"Save this meeting: [transcript pasted]"*
> Skill: parses content, confirms with user, creates `Work/Vaimo/Meeting notes/2026.04.14 1-1 Pavlo - Anton.md`, updates ARB TASKS.md with extracted actions.

**Updating an existing page:**
> User: *"Add a follow-up to my meeting with Ivan from April 2nd"*
> Skill: finds `2026.04.02 1-1 Pavlo - Ivan.md`, confirms update plan, appends new content, updates SunnyEurope TASKS.md.

**No content provided:**
> User: *"Save my meeting notes"*
> Skill: asks *"Please paste the meeting transcript or notes, and I'll handle the rest."*

**Contradiction found:**
> Skill: *"This meeting says we'll switch to headless checkout, but [[ARB Architecture Decision]] says headless is out of scope. Should I update that ADR too, or just note the change in the meeting page?"*

## Notes

- "Pavlo" in content always refers to Pavlo Zamoroka (vault owner) — no need to ask for clarification.
- Write page content in the **same language as the provided content**. YAML tags always in English.
- If the obsidian CLI is unavailable, continue with direct markdown edits without interrupting the user.
