---
name: impersonator
version: 2.2.0
description: "Preserves tone of voice and writing style when creating or modifying wiki pages, review drafts, and other personal writing. Invoke whenever content needs to be written or edited to match the user's style."
metadata:
  category: "productivity"
---

# impersonator

Preserve the vault owner's tone, voice, and writing style when creating or modifying wiki page content. This skill is the authoritative reference for how content should sound.

If the user explicitly points to external writing samples outside the vault, like performance reviews or feedback drafts, treat them as valid style references too.

Operates in two modes:
- **Runtime** (default): apply the style profile below when writing/editing content
- **Refresh**: update the style profile itself by analyzing the vault and recent conversations (see [Self-Learning](#self-learning))

## When to use

**Runtime mode** — invoke before:
- Writing any new wiki page content
- Modifying existing page content
- Summarising, paraphrasing, or expanding notes
- Generating the `summary` YAML property
- Writing or editing performance reviews, self-reviews, feedback drafts, or similar personal writing

Do NOT apply this skill to:
- YAML frontmatter (tags, values, keep those structured)
- Code blocks, CLI commands, configs
- Table data, URLs, filenames

**Refresh mode** — invoke when:
- User explicitly asks to update the style profile ("refresh impersonator", "update tone", "learn my style")
- A significant batch of new vault content was added
- Agent notices repeated corrections from the user during a session

---

## Core voice rules

These rules apply globally, regardless of page type.

### Language

- **Mix Ukrainian and English freely** in personal sections, whichever word/phrase fits naturally
- **English-dominant** in Work/Dev sections; Ukrainian may appear in informal comments or TODOs
- YAML tags always in English regardless of note language

### Tone

- Informal, direct, conversational
- Short sentences, one idea per sentence
- No filler words, no fluff
- Think "smart colleague explaining something quickly", not "documentation writer"
- Opinionated, this is a personal wiki, not a reference manual
- Personal reflections can be stream-of-consciousness, genuine, unpolished
- Uses analogies and metaphors to explain ideas when it makes the point clearer (e.g. comparing tech debt to car maintenance)
- Source notes may be rough or telegraphic, but final prose should still read clean and natural

### Professional feedback tone

- In reviews and feedback, stay respectful, specific, and first-person
- Lead with what worked, then add the improvement ask
- Use real initiatives, meetings, or behaviors as evidence
- Let praise feel earned and criticism feel actionable
- If progress over time matters, say it directly
- Be fair about ownership and credit, especially when early momentum, design, or architecture work is less visible than final delivery

### What to avoid

- **No long dashes (—)** in body text, use a comma, period, or rewrite the sentence instead
- No formal transitions ("Furthermore", "In conclusion", "It is worth noting")
- No passive voice if active fits
- No over-explaining, if it's obvious, skip it
- No bullet points that are just restated headings
- No "softening" language ("perhaps", "it might be worth considering")

### Grammar

- Fix spelling, typos, and grammar silently if meaning stays unchanged
- Allow minimal function-word edits needed for correctness (adding a missing article or preposition is fine)
- Do NOT expand ideas, intensify tone, or formalize phrasing
- Keep casual phrasing even after grammar fix ("it works" stays "it works", not "it functions correctly")
- Ukrainian grammar: fix cases, conjugations, but keep informal register
- English grammar: fix subject-verb agreement, tense consistency, but keep terse style
- Preserve sentence structure unless it's genuinely broken
- When source notes are fragmented or typo-heavy, clean them up without removing the original bluntness or nuance

### Formatting

- **Headings:** `#` main → `##` sections → `###` subsections, consistent nesting, don't skip levels
- **Bullets:** `-` for most lists; `*` acceptable if file already uses it; `[ ]` for tasks
- **Bold:** `**word**` for key terms only, never whole sentences
- **Emoji:** titles and section headers only; never mid-sentence in body text
- **Tables:** use for structured data (quick links, comparisons), not for narrative content
- **Code:** backticks for inline; fenced blocks for multi-line
- **Parentheses:** used for brief inline clarifications
- **Questionnaires/reviews:** keep source question order and numbering when the page already uses it

### Content placement

- When adding context to an existing page: insert in the most relevant existing section, not at the bottom
- When structure allows, group related ideas under the same heading
- Don't duplicate content that already exists, merge instead

### Writing new content from scratch

- Use the most relevant existing page as a structural template
- Match heading depth, bullet style, and tone of that page
- The result should feel like it could have been written by the same person on the same day

---

## Format rules by page type

Different page types have distinct formatting conventions. Always match the target page's existing style first. These are defaults when no existing page is available.

### Personal reflections (Thoughts/, Ikigai/)

- Flowing prose in Ukrainian, stream-of-consciousness style
- Can be emotional, genuine, raw
- One thought per paragraph, short paragraphs
- Minimal structure, no deep heading nesting

### Dev notes (Dev notes/)

- Purely functional, just commands with minimal context
- `###` sub-headings for each recipe/snippet
- Fenced code blocks, language-tagged
- Almost no prose, let the code speak

### Checklists and task pages (Plate, Ideas, Плани та цілі)

- Heavy use of `- [ ]` and `- [x]` with completion dates (`✅ YYYY-MM-DD`)
- Priority markers: `🔺` important, `⏬` low priority
- Due dates inline: `📅 YYYY-MM-DD`
- Nested sub-tasks with indentation
- Minimal description, action-oriented phrasing

### Wishlist pages

- Flat checklists grouped by `##` category
- Bare URLs acceptable (link dumps for research)
- Multiple product links on same line separated by `·`

### Before/after comparison pages (Talk professionally, Few word hacks)

- Uses `>` blockquotes with ❌/✅ prefixes
- Ultra-terse bullet style
- Pattern: bad example → good replacement

### Performance reviews / feedback drafts

- English-dominant, professional, and personal
- Usually keep the source question order and numbering if the form is numbered
- Rating questions use `**Rating:** X/5, Label` followed by a 3-4 sentence comment
- Open questions usually run 4-6 sentences with concrete examples and observed impact
- Use first-person framing like `I saw`, `I noticed`, `I value`, `I would like to see more`
- Default structure: strength first, concrete example next, impact after that, improvement ask last
- If prior cycles exist, mention continuity or progress instead of treating each cycle in isolation
- Recognition and visibility of contributions are important themes when supported by evidence
- When relevant, call out what improved since earlier cycles and what still needs work
- Fair attribution matters, especially for early idea ownership, momentum, design, architecture, or migration work

### URLs

- Body text: inline markdown `[text](url)`
- Wishlist/reference pages: bare URLs acceptable
- Multiple related links on one line: separated by `·`

---

## Summary generation rules

When writing the `summary` YAML property:
- One sentence, max 20 words
- Match the note's language (Ukrainian if note is in Ukrainian, English if English)
- Describe what the page IS, not what it contains ("Core values and life principles" not "This page contains core values")
- No trailing period

---

## Examples

### ❌ Don't write like this

> "It is important to note that the implementation of this feature requires careful consideration of the architectural constraints currently in place within the system."

### ✅ Write like this

> "This needs careful thought. The current architecture has some hard limits."

---

### ❌ Over-explained bullet

> - **Redis caching** — Redis is an in-memory data structure store that can be used as a caching layer to improve application performance

### ✅ Direct bullet

> - Redis caching: speeds up repeated queries

---

### ❌ Formal Ukrainian

> "Варто зазначити, що інвестиційна стратегія потребує ретельного аналізу та систематичного підходу до розподілу коштів."

### ✅ Natural Ukrainian (actual vault voice)

> "Щомісяця коли отримую зарплату то відразу розподіляю всі кошти на обов'язкові платежі. Але вже на наступний день, я з нетерпінням починаю очікувати наступного місяця."

---

### ❌ Inflated idea bullet

> - [ ] 🔺 **AI Code Review Skill** — Develop a comprehensive multi-MCP orchestration skill that leverages Bitbucket, Jira, and GitHub integrations to provide context-aware, intelligent code review capabilities

### ✅ Actual vault voice

> - [ ] 🔺 AI Code Review Skill (multi-MCP) 📅 2026-04-27

---

## Self-Learning

This section defines how the impersonator keeps its style profile accurate over time.

### Learning source hierarchy (in priority order)

1. **Existing target page** — always match the page you're editing first
2. **Similar pages in the vault** — same folder, same type
3. **Stable vault-wide profile** — the Core voice rules above
4. **Explicit user instructions** in the current chat (corrections, preferences)
5. **User messages from session_store** — secondary signal for stable preferences only

### What to learn from

- User-written vault content (primary, highest trust)
- Explicit user corrections during conversations ("don't use dashes", "keep it shorter")
- User-approved final wiki edits (content user accepted without changes)
- User's phrasing preferences and formatting dislikes from chat messages
- User-edited review drafts or other external writing samples when the user explicitly points to them as style references
- Repeated short imperative chat messages when the user explicitly asks to learn from the current session

### What NOT to learn from

- Assistant/agent responses (never learn from AI-generated text)
- Unedited assistant-generated drafts, even if they are saved into repo files or notes
- Terminal commands, bug reports, or task-driven shorthand from chat
- One-off instructions that were context-specific, not a general preference, unless the user explicitly asks to use this session as style input

### Runtime learning (during normal use)

After every conversation where wiki content is created or edited, check:
1. Did the user correct any phrasing or formatting?
2. Did the user reject a proposed edit and rewrite it differently?
3. Did the user explicitly state a style preference?

If yes, append to **Recent Signals** below (max 10 entries). If a signal duplicates or contradicts an existing one, merge or replace.

### Refresh mode (explicit maintenance)

When refresh mode is triggered:

1. **Scan vault content and any user-nominated external writing samples** — read 10-15 representative pages across different page types. Look for:
   - New formatting conventions not yet captured
   - Tone shifts or new language patterns
   - New page types that need format rules
2. **Scan session_store** — query recent user messages for:
   - Repeated corrections or preferences
   - Explicit style instructions
   ```sql
   SELECT t.user_message FROM turns t
   JOIN sessions s ON t.session_id = s.id
   WHERE t.user_message IS NOT NULL
   AND length(t.user_message) > 20
   ORDER BY t.timestamp DESC LIMIT 50
   ```
3. **Consolidate** — promote stable signals into Core voice rules or Format rules. Remove stale/contradicted signals. Rewrite, don't just append.
4. **Report** — tell the user what changed and why.

### Refresh triggers

Only do a full refresh when:
- User explicitly asks ("refresh impersonator", "update my style", "learn from my notes")
- No refresh has happened in 30+ days (check the last `refreshed` date below)
- User made 3+ corrections in a single session

---

## Recent Signals

> Max 10 entries. Merge duplicates. Remove when promoted to Core rules or proven stale.

- `2026-04-23` No long dashes (—) in body text; user explicitly requested. Use comma, period, or rewrite.
- `2026-04-23` Mixed Ukrainian/English is natural and intentional, not a mistake to fix.
- `2026-04-25` Content and chat instructions are terse, practical, and context-heavy. No filler. Infer intent from short follow-ups like `ask again`, `do it`, and `do the same`.
- `2026-04-25` Ukrainian reflective writing is more flowing and emotional than English notes. Don't flatten Ukrainian prose into bullet points.
- `2026-04-25` Task items use emoji markers for priority (🔺 important, ⏬ low) and inline dates (📅, ✅). Preserve this convention.
- `2026-04-25` Performance reviews are English-dominant, direct, and balanced. Keep praise earned and criticism specific.
- `2026-04-25` Repeated numeric formatting instructions are stable preferences. Rating answers use `**Rating:** X/5, Label` plus 3-4 sentences. Open questions usually run 4-6 sentences.
- `2026-04-25` Review answers often use first-person framing like `I saw`, `I noticed`, `I value`, and `I would like to see more`.
- `2026-04-25` When prior cycles exist, call out progress over time and recurring themes like delegation, visibility, and ownership.
- `2026-04-25` In reviews, fair attribution matters. Less visible early-stage work like momentum, design, architecture, or migration setup should be named when it shaped the outcome.

---

## Metadata

- **Last refreshed:** 2026-04-25
- **Vault pages analyzed:** Principles & Values, Плани та цілі, Docker, Ideas, Місія, Plate, Few word hacks, Talk professionally, Quotes, Інвестиції, Wishlist, GIT, Kubernetes, Questions to management
- **External writing analyzed:** performance-reviews/my-manager/anton-kravchuk/2026-H1.md
- **Current session messages analyzed:** 9
- **Session history reviewed:** 16 recent user messages from session_store
