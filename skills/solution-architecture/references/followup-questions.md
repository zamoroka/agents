# Follow-up questions mode — append clarifications to a project summary

Goal: turn the gap between *what we know* (project AGENTS.md + the current project summary) and *what we need to know* (to design or build) into a set of concrete, well-scoped questions to ask a client, vendor, or other third party — and append them under the **Open Questions** section of the project summary in the Obsidian vault.

_Why append rather than replace: Open Questions is the canonical backlog of stakeholder-blocking unknowns for the project. Wiping or restructuring it would erase historical context and may silently re-ask questions that were already answered. New questions go after the existing rows; resolved questions are pruned by the user, not by us._

_Why route through the project summary, not a fresh note: the summary is already the place that downstream skills (`obsidian-note` summary mode, future steerco prep) read for project state. Keeping all open questions there avoids fragmenting the source of truth._

## Preconditions

- The user wants questions for an **external** party (client, vendor, integrator, regulator). For internal-team questions, prefer adding a `TASKS.md` entry instead — open questions on the summary are a stakeholder-facing artifact.
- A project summary exists in the Obsidian vault. If it doesn't, ask the user whether to create one first via `obsidian-note` summary mode, then resume.
- `$PROJECT_ROOT/AGENTS.md` is helpful but not strictly required. If it doesn't exist, the skill can still run using only the summary plus the repo source code — note this in the proposal so the user knows the question set may be shallower.

## Step 1 — Resolve the target summary

Resolution order:

1. If the user named a specific summary file or topic, use it directly. Confirm the path with `obsidian files folder="<summaries-folder>"` before reading.
2. Otherwise resolve the matching vault project folder (see main SKILL.md — *Identifying the matching vault project*), then:
   ```bash
   obsidian files folder="Work/<persona>/projects/<Project>/summaries"
   ```
3. If there are multiple summaries, list them with their `summary` frontmatter line and ask the user which one to target. Do not guess.

Store the resolved path as `SUMMARY_PATH`.

## Step 2 — Read project knowledge

Read in this order, lightest to heaviest:

1. **Summary outline** — `obsidian outline path="$SUMMARY_PATH"` to map sections.
2. **Summary body** — full read of the summary file. Pay particular attention to:
   - `Problem Statement`
   - `Solution Description`
   - `Assumptions`
   - `Solution Architecture` (especially `Key Components` and `Inbound/Outbound API Calls`)
   - The existing `Open Questions` table — every row here is a question that already exists, *do not duplicate*.
   - `Decision Log` — context for why some directions were chosen, useful when phrasing follow-ups.
3. **Project AGENTS.md** at `$PROJECT_ROOT/AGENTS.md` (if it exists) — additional context, especially **Section 9 — Open architecture questions**. Treat those as candidate sources too; some of them may be the same question already, others may be net-new.
4. **Recent project notes** — only if Steps 2.2/2.3 leave large gaps. Use `obsidian search:context` against the project tag for recent meeting notes or communications, but stop once you have enough to write good questions. Reading every related note is not the goal.

## Step 3 — Generate question candidates

Generate questions from **gaps**, not from generic checklists. Each question should be one that, if answered, would unblock a concrete decision.

Question sources, in priority order:

1. **Assumptions** — every assumption is a candidate question of the form "Can you confirm <assumption>?", especially when the assumption could plausibly be wrong.
2. **Solution Architecture gaps** — missing data formats, missing auth flows, missing failure modes, missing volume/SLA numbers, missing ownership boundaries.
3. **Inbound/Outbound API Calls** — for each integration referenced, check whether contract, auth, error-handling, idempotency, rate limits, and sandbox availability are documented. Each missing one is a question.
4. **Decision Log** — decisions taken on incomplete information; ask the questions that would let them be revisited or ratified.
5. **AGENTS.md Section 9 — Open architecture questions** — promote unresolved ones to the summary if they are stakeholder-blocking and not yet present in the summary's Open Questions table.

Tag each candidate question internally with:

- **Audience** — who is being asked: `client`, `vendor:<name>`, `integrator:<name>`, `regulator`, etc.
- **Blocking** — `yes` / `no` — is a project step blocked until this is answered.
- **Linked-from** — pointer back to the assumption / gap / decision that generated it.

## Step 4 — Quality filter

Before proposing the list, prune. Drop a question if any of these apply:

- The answer is already in the summary, in `AGENTS.md`, or in a linked note (you missed it on first read — re-read the cited section).
- It is a near-duplicate of an existing row in the summary's Open Questions table. Phrase variants don't count; if the underlying ask is the same, drop it.
- It's not actually actionable for an external party (e.g. "should we refactor this internally" — that's a TASKS entry, not an external question).
- It's framed too vaguely to get a useful answer ("what about scalability"). Re-phrase or drop.

Aim for **5–10 high-signal questions** per round. If you have 20 candidates after filtering, ask the user whether to send everything or pick the top N — do not silently truncate.

Style rules (the questions will go to a third party in the user's name):

- Invoke `impersonator` before drafting the final prose for each question.
- One question per row. Multi-part questions splinter ownership and slow responses.
- State context just enough for the recipient to answer without reading the summary themselves. A typical question is 1–3 sentences: context, then the ask.
- Lead with the most blocking questions; the recipient may only answer the first few.

## Step 5 — Proposal

Present the proposal in two parts:

1. **Existing Open Questions** in the summary — list current rows in a short summary line each, so the user can see what's already there.
2. **Proposed additions** — for each new question, show the audience, the blocking flag, the question text, and a one-line trace back to the source (assumption #, architecture gap, etc.).

End with: *"Approve which to append? Edit any wording first?"* — and wait for explicit approval. Partial approval is fine.

## Step 6 — Append to the summary

The Open Questions table in the summary is a log of questions that have already surfaced from discussions, documents, or stakeholder interactions. **Do not append AI-generated questions into this table.**

Instead, write approved questions into a dedicated subsection directly below the Open Questions table:

```markdown
### AI Proposed questions

Questions generated from codebase analysis and document gaps, not yet raised with ARB.

- <question text>. *(Audience)*
- ...
```

Rules for this subsection:
- One bullet per question.
- Append audience in italics at the end of the bullet: `*(ARB SA)*`, `*(ARB BA + E-Business)*`, etc.
- If the subsection already exists, append new bullets at the bottom. Do not restructure or reorder existing bullets.
- If no questions were approved, do not create the subsection.

After writing:

1. Bump frontmatter:
   ```bash
   obsidian property:set name="updated" value="<ISO datetime>" type=datetime path="$SUMMARY_PATH"
   ```
2. If new sources were used that aren't yet in `related`, merge them in:
   ```bash
   obsidian property:read name="related" path="$SUMMARY_PATH"
   obsidian property:set name="related" value="..." type=list path="$SUMMARY_PATH"
   ```
3. Call `obsidian reload` so Obsidian's index picks up the change immediately.

## Step 7 — Confirm and suggest next step

Report:

- Summary path updated.
- Number of rows appended, grouped by audience.
- Anything that was filtered out at Step 4 (one line per dropped candidate, so the user can override).

Optional next step suggestion when relevant:

- If many new questions point at the same stakeholder, suggest drafting a single outbound email/Slack message that bundles them. That draft belongs to a different skill — `impersonator` for tone, `obsidian-note` to file the sent thread under Communications — this skill stops at the summary update.

## Anti-patterns

- **Don't write questions you can answer from the code.** If `composer.json` already says PHP 8.3, asking "what PHP version do you use" wastes the stakeholder's time and signals we didn't read.
- **Don't bundle multiple asks into one row.** "What is the auth, error handling, and rate limit?" is three questions; the answer will be incomplete on at least one. Split.
- **Don't add AI-generated questions to the Open Questions table.** That table is for questions already surfaced in discussions or documents. AI-proposed questions go in the `### AI Proposed questions` subsection below it.
- **Don't generate questions for internal-only unknowns.** Open Questions on the summary are stakeholder-facing — internal grooming goes elsewhere.
