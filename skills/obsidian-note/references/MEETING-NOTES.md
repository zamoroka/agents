# Meeting Notes Workflow

Use this workflow when meeting signals are detected by `obsidian-note`.

## Scope

- Creates or updates pages under `Work/Vaimo/Meeting notes/`
- Works for pasted meeting notes and Google Docs transcripts
- For Google Docs, the download and content-type detection is handled by [google-drive-usage.md](./google-drive-usage.md); this workflow receives the staged `_raw` file as input
- Keeps transcript text mostly raw while enforcing meeting-note rules

## Step 1 — Gather missing context

If meeting content is missing, ask:
*"Please paste the meeting transcript or notes, and I'll handle the rest."*

If content exists but project context is unclear, ask:
*"Was this related to a Vaimo project? If yes, which one: ARB, SunnyEurope, SwissSense, Elon, SOGESMA, or general/none?"*

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
- convert checklist bullets (`- [ ]`, `- [x]`) to plain bullets (`- ...`)

## Step 3 — Find candidate page (create vs update)

Run focused searches:

```bash
obsidian search query="<meeting date> <participant> <project>"
```

Use 1-2 additional searches for aliases/date variants.

- If same-date page with overlapping participants exists -> update it
- Otherwise -> create a new page

## Step 4 — Propose subfolder (required)

Target root is always:
`Work/Vaimo/Meeting notes/`

Before writing, provide a very short meeting summary first (2-4 bullets) with the most important discussion points.
For this summary only, use `kevin-mode` communication style (very terse, high-signal phrasing).

Then propose:
1. suggested subfolder
2. short rationale
3. 1-3 alternatives

Ask user to approve the subfolder. Do not write before approval.

## Step 5 — Related pages and contradictions

Search related context:

```bash
obsidian search query="<project or topic> <key decision>"
```

For each relevant page:
- collect filename for YAML `related`
- add natural `[[wiki-links]]` where appropriate
- if contradictions are detected, stop and ask user how to proceed

## Step 6 — Derive tags

Apply `AGENTS.md` tagging rules.

Meeting pages must include:
- `work`
- `vaimo`
- `meeting`

Add when detected:
- participant tags (CamelCase)
- project tags (`al-rajhi-bank`, `swisssense`, `sunnyeurope`, `elon`, `sogesma`)
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

Path format:
`Work/Vaimo/Meeting notes/<approved subfolder>/YYYY-mm-dd <meeting title>.md`

Rules:
- do not invoke `impersonator` for meeting transcripts
- keep transcript body raw except checklist normalization
- frontmatter follows `AGENTS.md` wiki format (`tags`, `created`, `updated`, `related`, `summary`)
- when content was imported from a Google Docs URL, add a `source` YAML property with the original document URL
- for updates, read existing file first and merge without duplication

Google Docs create flow (must use `mv`):

1. Start from the downloaded `_raw` file.
2. Prepend YAML frontmatter directly to that file.
3. Move it into the approved final location using `mv`.

Example:

```bash
mv "VAULT_ROOT/_raw/<doc-id>.md" "VAULT_ROOT/Work/Vaimo/Meeting notes/<approved subfolder>/YYYY-mm-dd <meeting title>.md"
```

For Google Docs updates:
- use `_raw` file as analysis input
- merge new content into the existing target meeting page
- do not replace the existing file via `mv`

## Step 9 — Action points and TASKS.md

Keep action points in meeting note body as plain bullets.

Also extract todos assigned to Pavlo (or unassigned) and prepare TASKS.md-ready entries with meeting context and due date when available.

Show a concrete preview and ask approval before touching `TASKS.md`.
Only modify `TASKS.md` after explicit user approval.

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
3. If folder is wrong, move the file to the approved folder and confirm final path.
