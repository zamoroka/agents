# Calendar "What Was Done" Workflow

This reference defines the workflow for generating activity summaries from Google Calendar events and updating the "Vaimo whats done" Obsidian note.

## When to use

Invoke this workflow when the user asks about recent activity or wants to update their "whats done" note:

- "what was done this week"
- "what was done this month"
- "show my activity summary"
- "update whats done"
- "what did I do last week"

## Prerequisites

This workflow uses the `calendar_get_events` tool from the `google-drive` MCP server.
If the MCP server is not available, follow the instructions in `~/.agents/mcp/AGENTS.md` to call the tool directly.

## Workflow

### 1. Determine period

Use the bundled script — it owns the date math so the prose stays
locale-safe and the model does not have to do arithmetic in its head:

```bash
python3 /Users/zamoroka_pavlo/.agents/skills/obsidian-note/scripts/compute_period.py this-week
# {"start": "2026-05-11", "end": "2026-05-13"}
```

Supported periods: `this-week`, `last-week`, `this-month`, `last-month`,
`custom --start YYYY-MM-DD --end YYYY-MM-DD`.

Semantics:
- **this-week** → start = Monday of current week, end = today + 1 day (exclusive)
- **last-week** → start = Monday of previous week, end = Monday of current week
- **this-month** → start = 1st of current month, end = today + 1 day
- **last-month** → start = 1st of previous month, end = 1st of current month
- **custom** → extract explicit dates from user message; if unclear, ask before fetching

_Why a script: hand-rolled `date` arithmetic differs between macOS and Linux and is a frequent source of off-by-one errors when computing "last Monday" near a Sunday._

### 2. Fetch calendar events

Call:

```json
{
  "tool": "calendar_get_events",
  "server": "google-drive",
  "input": {
    "start_date": "2026-05-01",
    "end_date": "2026-05-08"
  }
}
```

Read the saved JSON file from the returned path.

### 3. Filter events

Remove:
- All-day events that are holidays/OOO/birthdays
- Personal blocks, lunch, sick leave
- Events the user declined (if status indicates)

Keep all-day events that represent meaningful work (e.g., offsites, training days).

### 4. Categorize events

Use the same 5-category classification:

**Sales:**
- External-facing meetings, presales, demos, client interactions

**Organisational:**
- All-hands, leadership, strategy, planning, team events

**People Lead:**
- 1:1s, coaching, hiring, interviews, mentoring

**Certifications:**
- Training, courses, workshops, exam prep

**Projects:**
- Standups, sprints, technical reviews, deployments, development work

### 5. Generate summary

Produce a concise summary using the standard template:

```markdown
**Timeframe:** [Period description] (e.g., Week 19, May 2026)

**Sales:**
- [3-5 bullet points summarizing sales activity]

**Organisational:**
- [3-5 bullet points summarizing organisational activity]

**People lead:**
- [3-5 bullet points summarizing people-lead activity]

**Certifications:**
- [3-5 bullet points summarizing certification activity]

**Projects:**
- [3-5 bullet points summarizing project activity]
```

Rules for bullets:
- Deduplicate recurring events (e.g., "Daily standups with Sunny team" not 5 separate entries)
- Highlight notable one-off events
- Keep each bullet concise (1 line)
- Omit categories with no events (or write "No activity this period")

### 6. Find and update the note

1. Search for the "Vaimo whats done" note using context-aware search:
   ```bash
   obsidian search:context query="whats done vaimo"
   ```
2. If found, run `obsidian outline path="<file>"` to understand structure, then read only if content merging is needed.
3. Propose appending the new period's summary to the note.
4. If not found, propose creating it in the appropriate `Work/Vaimo/` folder.

### 7. Confirm with user

Before writing, show:
- The generated summary
- The target note path
- Whether appending or creating

Ask: "Should I add this summary to your 'Vaimo whats done' note?"

### 8. Write via obsidian-note flow

After confirmation:
- Use the standard obsidian-note write flow (Step 8 from SKILL.md)
- Append the new period summary below existing content
- Maintain chronological order (newest at bottom or top — match existing note structure)
- Update YAML `updated` field atomically with explicit datetime type:
  ```bash
  obsidian property:set name="updated" value="<ISO datetime>" type=datetime path="<relative/path/to/note.md>"
  ```
  _Why `type=datetime`: without it Obsidian stores the value as plain text, so the property won't render with date formatting and Database.base date-range views will skip it._
