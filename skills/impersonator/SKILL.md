---
name: impersonator
version: 1.0.0
description: "Preserves tone of voice and writing style when creating or modifying wiki pages in the Obsidian vault. Invoke whenever content needs to be written or edited to match the vault owner's style."
metadata:
  openclaw:
    category: "productivity"
---

# impersonator

Preserve the vault owner's tone, voice, and writing style when creating or modifying wiki page content. This skill is the authoritative reference for how content should sound. Update the **Detected Patterns** section whenever new style patterns are observed during a conversation.

## When to use

Invoke this skill:
- Before writing any new wiki page content
- Before modifying existing page content
- When summarising, paraphrasing, or expanding notes
- When generating the `summary` YAML property

Do NOT apply this skill to:
- YAML frontmatter (tags, values — keep those structured)
- Code blocks, CLI commands, configs
- Table data, URLs, filenames

---

## Core style profile

### Language

- **Mix Ukrainian and English freely** in personal sections — whichever word/phrase fits naturally
- **English-dominant** in Work/Dev sections; Ukrainian may appear in informal comments or TODOs
- YAML tags always in English regardless of note language

### Tone

- Informal, direct, conversational
- Short sentences — one idea per sentence
- No filler words, no fluff
- Think "smart colleague explaining something quickly", not "documentation writer"
- Opinionated — it's a personal wiki, not a reference manual

### What to avoid

- **No long dashes (—)** in body text — use a comma, period, or rewrite the sentence instead
- No formal transitions ("Furthermore", "In conclusion", "It is worth noting")
- No passive voice if active fits
- No over-explaining — if it's obvious, skip it
- No bullet points that are just restated headings

### Grammar

- Fix spelling and grammar errors silently
- Keep casual phrasing even after grammar fix ("gonna" → "going to", but "it works" stays "it works", not "it functions correctly")
- Preserve sentence structure unless it's genuinely broken

### Formatting

- **Headings:** `#` main → `##` sections → `###` subsections — consistent nesting, don't skip levels
- **Bullets:** `-` for most lists; `*` acceptable if file already uses it; `[ ]` for tasks
- **Bold:** `**word**` for emphasis, sparingly — not whole sentences
- **Emoji:** titles and section headers only; never mid-sentence in body text
- **URLs:** inline markdown `[text](url)` — not bare URLs (except in Wishlist)
- **Tables:** use for structured data (quick links, comparisons) — not for narrative content
- **Code:** backticks for inline; fenced blocks for multi-line

### Content placement

- When adding context to an existing page: insert in the most relevant existing section, not at the bottom
- When structure allows, group related ideas under the same heading
- Don't duplicate content that already exists — merge instead

### Writing new content from scratch

- Use the most relevant existing page as a structural template
- Match heading depth, bullet style, and tone of that page
- The result should feel like it could have been written by the same person on the same day

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

> "This needs careful thought — the current architecture has some hard limits."

Wait, no long dash:

> "This needs careful thought. The current architecture has some hard limits."

---

### ❌ Over-explained bullet

> - **Redis caching** — Redis is an in-memory data structure store that can be used as a caching layer to improve application performance

### ✅ Direct bullet

> - Redis caching — speeds up repeated queries

Still has a dash — fix:

> - Redis caching: speeds up repeated queries

---

## Detected Patterns

> Agents: append new tone/style observations here when discovered during a conversation. Include date and brief example.

- `2026-04-23` — No long dashes (—) in body text; user explicitly requested this. Use comma, period, or rewrite.
- `2026-04-23` — Mixed Ukrainian/English is natural and intentional, not a mistake to fix.
- `2026-04-23` — Content is terse and practical; avoid adding explanatory padding when the point is clear.
