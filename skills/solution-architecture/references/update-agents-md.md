# Update mode — merge new information into AGENTS.md

Goal: incrementally evolve `$PROJECT_ROOT/AGENTS.md` as the project's knowledge changes, without rewriting it from scratch and without silently flipping facts the user has already shipped downstream.

_Why incremental matters: every PR review, every onboarding doc, every agent that reads `AGENTS.md` treats it as ground truth. A silent overwrite that changes a single integration field can mislead all of them. Treat each update like an audited diff, not a rewrite._

## Preconditions

- `PROJECT_ROOT` is resolved and `$PROJECT_ROOT/AGENTS.md` already exists. If it does not, switch to bootstrap mode.
- The user has a concrete *source of new information*. Common sources, in rough order of frequency:
  1. A pasted meeting decision or transcript.
  2. A freshly-saved Obsidian note or refreshed project summary.
  3. A code change the user has already made or is about to make (renamed module, new integration, retired feature).
  4. A direct dictation from the user ("the cache layer is now Redis, not Memcached").

If the source is ambiguous, ask: *"What's the source of the update — a meeting note, an Obsidian summary, a code change, or something you want me to type in directly?"*

## Step 1 — Snapshot the current AGENTS.md

1. Read `$PROJECT_ROOT/AGENTS.md` in full.
2. Build a quick mental index of which facts live in which section. This is needed to (a) place additions in the right place and (b) detect contradictions.

## Step 2 — Extract candidate updates from the source

Convert the source into a flat list of **facts**, each one tagged with a target section in the template.

Format internally as:

```
[<section #>] <fact> (source: <pointer to where it came from>)
```

Examples:

```
[7] New integration: SSO via SAML 2.0 with vendor Okta (source: meeting note 2026-05-10 — SSO design)
[2] PHP version pinned to 8.3 (source: composer.json change)
[6] "Express checkout" now refers to the merchant-funded flow, not the platform-funded one (source: ARB-2026-05-08 review call)
```

If the source is long (a transcript, a full summary), don't try to keep every line — pull only what would change `AGENTS.md`. The user can always ask to add more later.

## Step 3 — Classify each candidate

For every candidate fact, classify it relative to the current `AGENTS.md`:

- **Addition** — new information; the section either is empty or doesn't cover this aspect. Action: add.
- **Refinement** — section already mentions this topic, but the new fact adds depth or correctness without contradicting. Action: rewrite the affected lines in place.
- **Contradiction** — new fact directly conflicts with what's there (different version, different vendor, different owner, different status). Action: flag for the user.
- **Duplicate** — already captured at equivalent depth. Action: skip; mention it in the proposal so the user can override if a nuance was missed.

If a contradiction looks like an obvious typo or wording fix, still treat it as a contradiction — let the user confirm.

## Step 4 — Decide structural moves (rare)

Most updates only touch existing sections. Restructure only when:

- A section has grown past one screen → propose moving detail to a linked note (`docs/<topic>.md`) and leave a one-paragraph summary in `AGENTS.md`.
- A new top-level concern needs its own section (e.g. the project just acquired a security review process) → propose inserting a new numbered section.

Do not renumber existing sections during a routine update. Renumbering breaks every external link to "AGENTS.md section 7". If a new section is needed in the middle, give it a sub-number (`7a`) or append at the end and let the user re-sequence later.

## Step 5 — Proposal

Present a structured proposal — the same shape used by `obsidian-note` summary updates, because it is the shape the user is already used to auditing.

```
## Additions
- [Section 7 — Integrations] Add row: Okta SSO (SAML 2.0), inbound, vendor-managed.
  Source: vault note Work/Vaimo/projects/ARB/Communications/2026-05-10 SSO design.md

## Refinements
- [Section 2 — Tech stack] Update PHP version 8.2 → 8.3.
  Source: composer.json (this PR).

## Contradictions (need decision)
- [Section 6 — Domain concepts] "Express checkout"
  Current AGENTS.md: "Express checkout = merchant-funded flow"
  New source: "Express checkout = platform-funded flow" (ARB call 2026-05-08)
  Question: which definition is correct now, or has the term split into two? If split, propose new term for the other meaning.

## Skipped duplicates
- [Section 1] Stage already says "Production". The source repeats this. Skipping.
```

End with: *"Approve all, approve a subset (call out which), or revise the contradictions before I write?"*

## Step 6 — Wait for explicit approval

Approval can be partial. If the user accepts the additions but defers a contradiction, write only the approved subset — leave the contradiction in the proposal log (see Step 8) for next round.

Do not write anything until the user has spoken. Silent "obviously safe" updates are exactly how `AGENTS.md` drifts from reality without anyone noticing.

## Step 7 — Write

For approved items only:

1. Apply each change in place. Match the existing structure exactly — heading depth, table column order, bullet style, tone.
2. Append a row to the **Change log** section at the bottom:
   ```
   | YYYY-MM-DD | <one-line summary of what changed> | solution-architecture skill |
   ```
   One row per update session, even when multiple facts are merged.
3. Do not auto-commit. The user controls commit framing.

## Step 8 — Leave a trace for next time

If any candidates were deferred (contradictions awaiting resolution, additions the user rejected for now), tell the user clearly which ones — so they can decide later whether the next update should reopen them.

Optional: if the user wants a persistent reminder, suggest appending to **Section 9 — Open architecture questions** as a real row. Don't append automatically; the open-questions row is for stakeholder-blocking questions, not internal review queue.

## Anti-patterns

- **Don't rewrite untouched sections.** A common failure mode is "while I'm in there, let me also tighten Section 5". That is a separate change with separate review needs. Resist.
- **Don't lose source attribution.** When the source was a vault note, the appended fact should be traceable back — either via a vault-relative link in the section it lands in, or via a clear note in the Change log row.
- **Don't treat code changes as authority over the vault, or vice versa.** If `composer.json` upgraded PHP but the vault summary still says the old version, surface the disagreement to the user — both might be right (rollout in progress) or both might be wrong (forgot to update one).
