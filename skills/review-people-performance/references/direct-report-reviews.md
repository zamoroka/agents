# Direct Report Reviews

Use this reference when preparing HiBob Direct Report Reviews for the user's team members under `my-team/`.

Naming convention:

- **Direct Report Review**: the review type stored under `my-team/`, where the user reviews a direct report/team member.
- **Manager review**: a section inside a Direct Report Review file, containing answers written by the user as the person's manager.
- **Upward Manager Review**: the review type stored under `my-manager/`, where the user gives feedback about their own manager. Do not use this reference for that workflow.

## Workspace

Default review root:

`/Users/zamoroka_pavlo/Library/CloudStorage/GoogleDrive-zapashok0@gmail.com/My Drive/obsidian/zamoroka/Work/Vaimo/People/performance-reviews`

Direct Report Reviews live under:

`my-team/<firstname-lastname>/<YYYY-Hn>.md`

Example current draft:

`my-team/oleksii-svystunov/2026-H1.md`

Direct Report Review drafts usually contain these sections:

- `Self review`
- `Goals`
- `Peers`
- `Direct reports` when the person is also a people lead
- `Manager review`
- `Reverse feedback`

## Preflight

Confirm or infer:

- Person and folder slug.
- Cycle, usually `YYYY-H1` or `YYYY-H2`.
- Destination file.
- Whether the task is to draft, refine, summarize evidence, or save changes.
- Whether the user wants direct HiBob-ready answers or an evidence map first.

If any path is ambiguous, derive it from the workspace conventions and ask only if multiple plausible matches exist.

## Context Collection

Load the current cycle file first. Then collect targeted supporting context:

- Prior review cycles for the same person in the same folder.
- Other review-type folders with the same slug if they exist.
- Relevant Obsidian pages, 1:1 notes, meeting notes, project notes, goals, and task/action records mentioning the person.
- Any direct user notes from this conversation.

Search terms to try:

- Full name and first name.
- Person slug.
- Current project/client names from the draft.
- Terms from goals, key results, and feedback themes.
- `1:1`, `one-to-one`, `feedback`, `goal`, `promotion`, `support`, `coaching`.

Use `obsidian-note` conventions when searching or writing in the vault. Read the vault `AGENTS.md` before any write action.

## Evidence Window

The review covers the last six months for the active cycle.

- For `H1`, prioritize January through June of that year.
- For `H2`, prioritize July through December of that year.
- If the cycle is still in progress, use the elapsed part of that half-year and say so when needed.

Use older review files to identify trajectory:

- Recurring strengths.
- Improvements since the previous cycle.
- Regressions or unresolved growth areas.
- Tone and answer-length examples that previously worked.

Do not use old claims as current facts unless the current draft, recent notes, or user confirms the behavior continued.

## Evidence Synthesis

Build a compact evidence map before drafting:

| Theme | Current evidence | Source | Confidence | Possible answer |
|---|---|---|---|---|
| Delivery/performance | Specific result or behavior | self/peer/goal/1:1/user | high/medium/low | question number |
| Collaboration/leadership | Specific result or behavior | peer/direct report/user | high/medium/low | question number |
| Growth area/support | Specific gap or opportunity | self/peer/manager/user | high/medium/low | question number |

Resolve repeated themes into one primary place. Avoid padding multiple answers with the same point.

Source weighting guidance:

- User-provided observations from the user as the person's manager are strongest for Direct Report Review wording.
- Goals and completed key results are strong for progress questions.
- Peer feedback is useful for collaboration, technical contribution, and external perception.
- Direct-report feedback is useful for leadership and people-management questions.
- Self-review is useful for motivation, self-awareness, goals, and support needs.
- Older reviews are trajectory context only.

If evidence conflicts, do not smooth it over. Tell the user the conflicting signals and ask how to interpret them.

## Drafting Standards

Use `impersonator` before writing or rewriting any Direct Report Review feedback. This applies to full HiBob answers, short feedback summaries, rating justifications, growth-area wording, and edits to user-provided draft text.

Keep the tone:

- Specific and developmental.
- Clear enough to paste into HiBob.
- Supportive without inflated praise.
- Direct about growth areas without sounding punitive.
- Written from the user's perspective as the direct report's manager.

Default answer lengths:

- Rating questions: rating plus 3-4 concise sentences.
- Open questions: 4-6 sentences when evidence supports it.
- Short fields: 2-3 sentences if the question is narrow.

For each answer:

- Start with the direct answer.
- Include concrete examples from the current cycle.
- Explain impact on team, client, delivery, quality, learning, or leadership.
- Add growth/support/focus recommendations where the question asks for them.
- Mark unsupported claims with `[needs validation]` or ask a follow-up before drafting final text.

## Common Direct Report Review Questions

Current `my-team/` drafts often include these questions in the `Manager review` section:

- `How would you rate their performance?`
- `Which areas do you feel have been going well for them?`
- `Which areas do you feel have not been going so well?`
- `How would you rate their progress on their goals?`
- `What support / coaching / training would they benefit from?`
- `What do you think they should focus on in the next 6 months?`
- `How would you rate their potential?`
- `Anything else you would like to share?`

Answer mapping:

- Performance rating: overall delivery, reliability, quality, scope, and impact.
- Going well: strengths, concrete outcomes, positive behaviors, growth demonstrated.
- Not going well: current-cycle friction, gaps, missed goals, risks, or underused opportunities.
- Goal progress: key-result completion and qualitative progress against stated goals.
- Support/coaching/training: what the user can provide, training needs, exposure, mentoring, feedback loops.
- Next six months: 2-4 focus areas tied to role growth and business needs.
- Potential: future scope, leadership, architecture, client ownership, mentoring, or role expansion.
- Anything else: net-new nuance, recognition, retention signal, or final manager perspective.

## Saving

Before saving:

- Show the section(s) that will change.
- Ask for confirmation if the user has not explicitly asked to apply the change.
- Use `obsidian-note` for the actual Obsidian file update.
- Preserve existing headings, question text, frontmatter, and section order.

When updating only the `Manager review` section, leave `Self review`, `Goals`, `Peers`, `Direct reports`, and `Reverse feedback` untouched unless explicitly asked.
