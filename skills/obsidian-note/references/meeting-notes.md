# Meeting Notes Workflow

Use this workflow when meeting signals are detected by `obsidian-note`.

## Contents

- [Scope](#scope)
- [Step 1 — Gather missing context](#step-1--gather-missing-context)
- [Step 1a — Google Docs ingestion via vault `_raw`](#step-1a--google-docs-ingestion-via-vault-_raw)
- [Step 2 — Parse meeting content](#step-2--parse-meeting-content)
- [Step 3 — Find candidate page (create vs update)](#step-3--find-candidate-page-create-vs-update)
- [Step 4 — Propose target folder (required)](#step-4--propose-target-folder-required)
- [Step 5 — Related pages and contradictions](#step-5--related-pages-and-contradictions)
- [Step 6 — Derive tags](#step-6--derive-tags)
- [Step 7 — Confirm write plan](#step-7--confirm-write-plan)
- [Step 8 — Write/update meeting page](#step-8--writeupdate-meeting-page)
- [Step 9 — Action points and TASKS.md](#step-9--action-points-and-tasksmd)
- [Step 10 — Confirm result](#step-10--confirm-result)
- [Recovery rule — note saved too early](#recovery-rule--note-saved-too-early)
- [Cleanup example: transcript wall-of-text → paragraphs](#cleanup-example-transcript-wall-of-text--paragraphs)

## Scope

- Creates or updates meeting pages in either:
  - `Work/Vaimo/projects/<ProjectName>/meeting-notes/` — for any project-scoped meeting (ARB, SunnyEurope, SwissSense, etc)
  - `Work/Vaimo/Meeting notes/` — for non-project meetings only (leadership 1-1s, EME-wide, `Direct reports 1-1s/`)
- Works for pasted meeting notes and Google Docs transcripts
- For Google Docs, the download and content-type detection is handled by [google-drive-usage.md](./google-drive-usage.md); this workflow receives the staged `_raw` file as input
- Keeps transcript text mostly raw while enforcing meeting-note rules

## Step 1 — Gather missing context

If meeting content is missing, ask:
*"Please paste the meeting transcript or notes, and I'll handle the rest."*

If content exists but project context is unclear, ask:
*"Was this related to a Vaimo project? If yes, which one: prj-ARB, prj-SunnyEurope, prj-SwissSense, etc, or general/none? Is this a direct report 1-1 (Oleksandr, Oleksii, Siemen)?"*

## Step 1a — Google Docs ingestion via vault `_raw`

When the source is a Google Doc URL, the download is handled **upstream** by
[google-drive-usage.md](./google-drive-usage.md) before this workflow is entered.
By the time this step runs, the markdown file is already staged in `VAULT_ROOT/_raw/`.

If this workflow is entered directly (not via `google-drive-usage.md`) and a Google
Docs URL is present, redirect to `google-drive-usage.md` first — do not call
`doc_markdown_download` here.

Expected state when entering this workflow from a Google Docs source:
- `VAULT_ROOT/_raw/<doc-id>.md` (or `<YYYY-mm-dd>-gdoc-import.md`) exists
- Use that file as the ingestion source for parsing (Step 2 below)
- Do not write the final meeting file before analysing the `_raw` file and deriving metadata

## Step 2 — Parse meeting content

Extract:
- meeting date (use today's date if missing)
- participants (use CamelCase person tags, e.g. `IvanBordiuh`)
- key topics/sections
- action points / next steps
- project and tech signals (`magento`, `docker`, `kubernetes`, `redis`, `newrelic`, `gcp`, `ai`, `architecture`, `decision`, `adr`, `transcript`)

Body cleanup rules:
- keep original language
- remove external transcript links (for example Granola URLs)
  _Why: these expire and leak privately-shared meeting recordings into the vault._
- convert checklist bullets (`- [ ]`, `- [x]`) to plain bullets (`- ...`)
  _Why: action items come from a dedicated extraction step (Step 9). Checklists in the transcript body would double up with `TASKS.md` and pollute `obsidian tasks todo`._
- always split transcript walls of text into readable paragraphs separated by blank lines, breaking on speaker shifts and topic transitions (a single paragraph should stay tight — one speaker, one idea)
- preserve any existing speaker labels verbatim (for example `Me:`, `Them:`, named speakers); do not strip them
- only attach a speaker name when the transcript itself names them in that turn (e.g. "Thanks, Mohammed —" → next paragraph attributable to Mohammed; an introduction like "I'm Aaqib, product manager" → label that speaker's following lines as Aaqib). Never guess from tone, role, or context alone — if the speaker is not explicitly identified, keep the original label (`Them:` / `Me:`) without a parenthetical name
  _Why: misattributing words to a participant can affect a real-world relationship. Better to leave anonymous than to guess wrong._

## Step 3 — Find candidate page (create vs update)

Run layered searches:

```bash
# Primary: context-aware search (returns matching lines, not just filenames)
obsidian search:context query="<meeting date> <participant> <project>"

# Expand graph for strong hits
obsidian backlinks file="<candidate file>"
obsidian links file="<candidate file>"

# Check tag siblings for project tag
obsidian tag name="<prj-tag>" verbose

# Check aliases to catch title variants
obsidian aliases file="<candidate file>"
```

Duplicate rule:
- Same date **+** ≥1 participant overlap **+** ≥2 matching tags → **update**
- Otherwise → **create new page**

## Step 4 — Propose target folder (required)

Two possible roots:
- **Project meeting** → `Work/Vaimo/projects/<ProjectName>/meeting-notes/` (e.g. `Work/Vaimo/projects/ARB/meeting-notes/`)
- **Non-project meeting** → `Work/Vaimo/Meeting notes/<subfolder>/`
  - Direct report 1-1s → `Direct reports 1-1s/`
  - Other non-project subfolders keep their plain names (e.g. `EME all-hands meetings`, `EME Engineering Leadership and Strategy Discussions`)

Decision rule:
- If the meeting is clearly scoped to a known project (ARB, SunnyEurope, SwissSense, Elon, SOGESMA, etc.) → use the project's `meeting-notes/` folder
- If it's a leadership 1-1, EME-wide sync, direct report 1-1, or cross-project discussion → use `Work/Vaimo/Meeting notes/<subfolder>/`
- If the project is new (no folder exists yet) → propose creating `Work/Vaimo/projects/<NewProject>/meeting-notes/` along with `README.md` and `TASKS.md` per AGENTS.md conventions

Before writing, provide a very short meeting summary first (2-4 bullets) with the most important discussion points.
For this summary only, use `kevin-mode` communication style (very terse, high-signal phrasing).

Then propose:
1. suggested target path (full vault-root-relative path including filename)
2. short rationale
3. 1-3 alternatives

Ask user to approve the target. Do not write before approval.

## Step 5 — Related pages and contradictions

Search related context using layered strategy:

```bash
# Line-level context for key topics and decisions
obsidian search:context query="<project or topic> <key decision>"

# Tag-siblings for any project tag detected in Step 6
obsidian tag name="<prj-tag>" verbose

# Graph expansion for top hits
obsidian backlinks file="<top hit>"
```

For each relevant page:
- collect vault-root path for YAML `related`
- add natural markdown links `[label](vault/root/path.md)` where appropriate
- cap related-pages list at 5, ranked by overlap (tag matches + keyword matches)
- if contradictions are detected, stop and ask user how to proceed

## Step 6 — Derive tags

Apply `AGENTS.md` tagging rules.

Meeting pages must include:
- `work`
- `vaimo`
- `meeting`

Add when detected:
- participant tags (CamelCase)
- project tags (`prj-arb`, `prj-swisssense`, `prj-sunnyeurope`, etc)
- topic tags (`transcript`, `architecture`, `adr`, `decision`, `magento`, `docker`, `kubernetes`, `redis`, `newrelic`, `gcp`, `ai`)

## Step 7 — Confirm write plan

Default rule before any write, confirm:
- target path
- create or update action
- tags
- related pages summary

Meeting-note approval shortcut:
- if the user explicitly approves the proposed meeting-note filename/path, treat that as write approval for the meeting note file
- do not ask for an extra write-permission confirmation
- still stop and ask if contradictions were detected in Step 5

## Step 8 — Write/update meeting page

Path format (one of):
- Project meeting → `Work/Vaimo/projects/<ProjectName>/meeting-notes/YYYY-mm-dd <meeting title>.md`
- Non-project meeting → `Work/Vaimo/Meeting notes/<approved subfolder>/YYYY-mm-dd <meeting title>.md`

Rules:
- do not invoke `impersonator` for meeting transcripts
  _Why: a transcript's value is in the participants' actual words — rewriting in the user's voice would distort attribution._
- keep transcript body raw except checklist normalization (template at `assets/frontmatter-templates/meeting.md`)
- frontmatter follows `AGENTS.md` wiki format (`tags`, `created`, `updated`, `related`, `summary`)
- when content was imported from a Google Docs URL, add a `source` YAML property with the original document URL
- for updates: run `obsidian outline path="<file>"` first to get heading structure, then read and merge without duplication

Google Docs create flow (use `obsidian move`, not `mv`):

1. Start from the downloaded `_raw` file.
2. Prepend YAML frontmatter directly to that `_raw` file.
3. Move it to the approved final location using the CLI so wikilinks stay intact:

```bash
# Project meeting
obsidian move path="_raw/<doc-id>.md" to="Work/Vaimo/projects/<ProjectName>/meeting-notes/YYYY-mm-dd <meeting title>.md"

# Non-project meeting
obsidian move path="_raw/<doc-id>.md" to="Work/Vaimo/Meeting notes/<approved subfolder>/YYYY-mm-dd <meeting title>.md"
```

4. Call `obsidian reload` if the move was done via `mv` fallback (CLI unavailable).

For Google Docs updates:
- use `_raw` file as analysis input
- merge new content into the existing target meeting page
- do not replace the existing file via move

## Step 9 — Action points and TASKS.md

Keep action points in meeting note body as plain bullets.

Also extract todos assigned to Pavlo (or unassigned) and prepare TASKS.md-ready entries with meeting context and due date when available.

Show a concrete preview and ask approval before touching `TASKS.md`.
Only modify `TASKS.md` after explicit user approval.

To mark a previously captured action item done in an old meeting note without rewriting the file:
```bash
obsidian task ref="<relative/path/to/note.md>:<line>" done
```

## Step 10 — Confirm result

Report:
- page path created/updated
- action points captured in note as plain bullets
- TASKS.md preview shown (and changed only if approved)
- related pages linked

Optionally offer to open the page in Obsidian.

## Recovery rule — note saved too early

If a meeting note is accidentally saved before subfolder approval:

1. Immediately print a short `kevin-mode` summary of the most important discussed points (2-4 bullets).
2. Ask user to confirm if current folder is correct.
3. If folder is wrong, move the file using `obsidian move path="<current>" to="<approved>"` (keeps wikilinks intact) and confirm final path.

## Cleanup example: transcript wall-of-text → paragraphs

A worked example of Step 2 body cleanup. The input is the kind of run-on
text a Granola or Google Meet transcript produces; the output is what
should land in the meeting note body.

**Input (raw transcript paragraph):**

```
Me: Hey Mohammed thanks for jumping on. So the marketplace cutover - we've been seeing rounding errors on multi-vendor carts again. Webkul confirmed it's their core. Mohammed: yeah I saw the ticket. ETA on the patch? Me: two weeks at least according to Ivan. So I want to push the cutover to next sprint, let the patch land in UAT first. Mohammed: makes sense. I'll let the steerco know. Anything else? Me: yeah - I also want to talk about the runbook. Max owes us a draft. https://granola.ai/meet/abc-123
```

**Output (cleaned, paragraphed, with attribution where explicit):**

```markdown
Me: Hey Mohammed thanks for jumping on. So the marketplace cutover — we've been seeing rounding errors on multi-vendor carts again. Webkul confirmed it's their core.

Mohammed: yeah I saw the ticket. ETA on the patch?

Me: two weeks at least according to Ivan. So I want to push the cutover to next sprint, let the patch land in UAT first.

Mohammed: makes sense. I'll let the steerco know. Anything else?

Me: yeah — I also want to talk about the runbook. Max owes us a draft.
```

What changed:
- Granola URL removed (private link, expires)
- Wall of text split on speaker shifts; one idea per paragraph
- `Me:` / `Mohammed:` labels preserved verbatim — both speakers are explicitly named in-line so attribution is safe
- No content paraphrased, no tone changes
- No action items extracted in body — Step 9 handles those
