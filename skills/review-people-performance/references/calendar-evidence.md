# Calendar Events as Self-Review Evidence

This reference defines how to use Google Calendar events as evidence when drafting Self Reviews.

## When to use

Apply this workflow during the **Context Gathering** step (step 2) of the session workflow, specifically when the review type is **Self Review** (`my-performance/`).

## Prerequisites

This workflow uses the `calendar_get_events` tool from the `google-drive` MCP server.
If the MCP server is not available, follow the instructions in `~/.agents/mcp/AGENTS.md` to call the tool directly.

## Workflow

### 1. Determine review period

Based on the confirmed review cycle timeframe:

- **H1** (first half) → start = `YYYY-01-01`, end = `YYYY-07-01`
- **H2** (second half) → start = `YYYY-07-01`, end = `YYYY+1-01-01`
- **Custom period** → use dates confirmed with user

### 2. Fetch calendar events

Call `calendar_get_events` with the full review period:

```json
{
  "tool": "calendar_get_events",
  "server": "google-drive",
  "input": {
    "start_date": "2026-01-01",
    "end_date": "2026-07-01"
  }
}
```

Read the saved JSON file from the returned path.

### 3. Categorize events

Classify each event into one of five categories based on title, description, and guests:

**Sales:**
- Events with external participants (non-@vaimo.com)
- Titles containing: presales, sales, demo, pitch, proposal, RFP, prospect, client meeting, discovery

**Organisational:**
- Internal all-hands, town halls, leadership meetings
- Titles containing: all-hands, townhall, leadership, strategy, org, planning, offsite, team building

**People Lead:**
- 1:1 meetings with direct reports
- Titles containing: 1:1, 1-1, one-on-one, coaching, feedback, performance, career, mentoring, hiring, interview

**Certifications:**
- Training and certification events
- Titles containing: training, certification, course, learning, workshop, exam, study

**Projects:**
- All other work events: standups, sprint ceremonies, technical discussions, code reviews
- Titles containing: standup, sprint, retro, planning, review, deploy, architecture, technical, dev, sync

### 4. Generate evidence list

For each category, produce a deduplicated summary of activities:

- Group recurring events (same title) into a single entry with frequency
- Highlight unique/notable events (one-off workshops, presentations, demos)
- Note collaboration patterns (frequent meetings with specific teams/people)

Format:

```markdown
## Calendar Evidence — [Period]

### Sales
- Participated in N presales/discovery calls with prospects (list notable ones)
- Delivered M client demos/presentations
- Key clients engaged: [list]

### Organisational
- Attended leadership meetings (bi-weekly)
- Participated in [specific offsite/planning event]

### People Lead
- Conducted regular 1:1s with N direct reports
- Held M hiring interviews
- [Notable coaching/mentoring events]

### Certifications
- [Specific training/cert events]

### Projects
- Active on N projects: [list project names from recurring standups]
- Led M architecture/technical review sessions
- [Notable one-off technical events]
```

### 5. Present for validation

Show the generated evidence list to the user and ask:

- "Here's what I found from your calendar for [period]. Which items are relevant for your self-review? Anything to add or remove?"

Only use confirmed items as evidence for drafting review answers. Do not fabricate details beyond what the calendar shows.

### 6. Integration with review drafting

Feed the validated evidence list into the review drafting process (step 4 — Draft Answers):

- Map evidence points to specific review questions
- Use calendar frequency data to substantiate claims (e.g., "conducted weekly 1:1s" backed by actual calendar entries)
- Reference specific notable events as concrete examples
