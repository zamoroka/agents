---
name: review-people-performance
version: 1.0.0
description: "Guides end-to-end writing and refinement of HiBob performance reviews with evidence-first guardrails, question handling, and workspace conventions."
metadata:
  category: "productivity"
---

# AGENTS.md — Performance Review Workspace

## Purpose

This repository is a workspace for drafting performance reviews used in **HiBob** review cycles at **Vaimo**.

- **Vaimo** is a global full-service digital experience agency (650+ team members, 15 markets, Scandinavian origin).
- **HiBob** ("Bob") is the HR platform Vaimo uses for performance management and review cycles.
- **Author role**: Engineering Lead & Technical Architect.

Reviews are written in Markdown, organized by review type and person, and refined iteratively with agent assistance.

---

## Workspace Location

Primary performance review workspace path:

`/Users/zamoroka_pavlo/Library/CloudStorage/GoogleDrive-zapashok0@gmail.com/My Drive/obsidian/zamoroka/Work/Vaimo/People/performance-reviews`

Use this as the default root for all review read/write operations unless the user explicitly overrides path.

---

## File Write Policy (Mandatory)

- For any create/update of review files, **always invoke `obsidian-note`**.
- Do **not** write review files directly via raw file edit/create tools when `obsidian-note` can perform the operation.
- Treat `obsidian-note` as the source of truth for page placement, update flow, and wiki integration behavior.

---

## Directory Structure

```
my-performance/          # Self-review (own performance)
my-team/                 # Reviews of direct reports
  ├── firstname-lastname/
my-peers/                # Peer reviews
  ├── firstname-lastname/
my-manager/              # My manager review (upward feedback)
  ├── firstname-lastname/
```

### Conventions

- **Person folders**: lowercase `firstname-lastname` (e.g., `john-doe`). One stable folder per person, reused across cycles, and reused across review-type directories when the same person appears in more than one category.
- **Timeframe files**: `YYYY-Hn.md` (e.g., `2026-H1.md`). One file per review cycle per person.
- **Disambiguation**: if two people share the same name, append a short disambiguator agreed with the user (e.g., `john-doe-backend`).
- **Self-review exception**: `my-performance/` has no person subfolder — files go directly inside (e.g., `my-performance/2026-H1.md`).

---

## Session Workflow

Every review-writing session follows this sequence:

### 1. Preflight — Identify & Confirm

Before any drafting, confirm with the user:

- **Review type** — which of the four categories
- **Person** — full name and folder name
- **Timeframe** — cycle identifier (e.g., `2026-H1`)
- **Destination path** — derived from above; confirm it
- **New or update** — creating a new file or editing an existing one
- **Questions** — the HiBob review questions to answer

### 2. Context Gathering

- Check if an **existing review file** is present at the destination path. If so, load it.
- Check the same person's folder in the current review-type directory for **previous review-cycle files**. If found, load them as historical context before drafting.
- Also check the other review-type directories for a folder with the same confirmed person slug (for example the same person may exist in both `my-peers/` and `my-manager/`). If matching files exist there, load them as cross-context too.
- Use previous reviews to identify recurring strengths, growth areas, unresolved themes, and places where the new review should be more specific or more complete than earlier cycles.
- Treat previous reviews, including files from other review-type directories, as **context**, not as automatic evidence for the current cycle. Reuse only what the user confirms or what is clearly still applicable, and adjust for the fact that question framing and tone may differ between peer, manager, team, and self reviews.
- Use the **`obsidian-note`** skill to search for prior context about the person (meeting notes, project work, 1:1 notes, past reviews). Skip if the user provides sufficient material or explicitly opts out.
- Present a summary of found context to the user for validation.

### 3. Targeted Follow-Up Questions

Start with **one general opening question** about the user's overall thoughts on the person and review cycle. Use that response to guide the rest of the conversation.

Only after the opening response, ask focused follow-up questions to fill evidence gaps. Target:

- **Rating questions first need scale clarity** — when a question uses a `1-5` scale, explicitly state that **1 is the lowest rating** and **5 is the highest rating**
- **Rating questions need justification** — collect the numeric score **and** a **3-4 sentence comment** grounded in observed behaviors, actions, or outcomes
- **Open questions need depth** — draft **4-6 sentences** by default, with concrete examples, impact, and clear observations
- **Question mapping** — identify which evidence points belong mainly to strengths, growth areas, overall rating, and "anything else" so answers stay distinct
- **Concrete examples** — specific projects, deliverables, incidents
- **Impact** — measurable outcomes, business value, team effect
- **Growth areas** — skills developed, challenges overcome
- **Collaboration signals** — how the person works with others
- **Development needs** — areas for improvement with specific observations

Do not proceed to drafting until there is sufficient evidence for each review question.

### 4. Draft Answers

- Use the **`impersonator`** skill for all authored review text to match the user's writing voice.
- Draft answers one question at a time or in batches as the user prefers.
- If previous reviews exist, make the new review more extensive where justified: add sharper examples, clearer rationale, and note meaningful changes since the last cycle instead of repeating old wording.
- Before writing, assign each key point to one primary answer. Do not repeat the same praise, critique, or example across multiple open questions unless the later question is explicitly a summary or adds a clearly different angle.
- Prefer complementary coverage across answers: strengths should focus on what the person is doing well, growth should focus on what should change or what support is needed, rating should briefly justify the score, and "anything else" should add net-new context such as recognition, trajectory, or final nuance.
- For rating questions, write a **3-4 sentence comment** after the score unless the user explicitly asks for a shorter format.
- For open questions, write **4-6 sentences** unless the user explicitly asks for a shorter format.
- Format: question as heading, drafted answer below.

### 5. Refine & Save

- Iterate on drafts based on user feedback.
- Save the final version to the confirmed destination path **via `obsidian-note` only**.
- Follow `obsidian-note` rules for confirmation before write and for update-vs-create handling.

---

## Obsidian Metadata and Linking Rules (Mandatory)

When saving through `obsidian-note`, enforce its standards for metadata and structure:

- Load vault `AGENTS.md` first for current tagging and formatting conventions.
- Apply mandatory folder/content tags per vault rules (minimum 2 tags when required by vault conventions).
- Keep/update `summary` in the expected format from vault rules (single concise sentence when required).
- Maintain/update `related` with valid wiki-links to discovered related pages.
- Update metadata fields like `updated` when content changes, preserving existing frontmatter structure.
- Keep review content and frontmatter compliant with vault conventions instead of ad-hoc formatting.

---

## Evidence & Safety Guardrails

These rules are **mandatory** and override all other instructions:

1. **No fabricated evidence.** Use only facts provided by the user or retrieved from context (Obsidian vault, existing files). Never invent examples, metrics, or events.
2. **Flag uncertainty.** If evidence for a question is weak or missing, explicitly tell the user and ask for more input. Mark uncertain statements with `[needs validation]`.
3. **No unsupported superlatives.** Avoid inflated praise or criticism without backing evidence.
4. **Balanced tone.** Be specific, evidence-based, and constructive. Include both strengths and development areas where appropriate.
5. **User owns the final text.** Every draft is a suggestion — the user decides what gets submitted to HiBob.
6. **Ratings need rationale.** Do not accept a bare `1-5` score. Every rating answer must include a **3-4 sentence comment** tied to real observations.
7. **Previous reviews are not proof by themselves.** They can guide continuity and depth, but current-cycle claims still need user confirmation or fresh supporting context.
8. **Open questions should not be underwritten.** Default to **4-6 sentences** with specific observations unless the user asks for a shorter response.
9. **Avoid duplicate padding.** Do not repeat the same feedback across multiple answers just to fill space. Reuse a point only when an overall or summary-style question needs a brief callback, or when the second mention adds a materially different angle.

---

## Review-Type Guidance

Each review type has different focus areas and tone:

### Self-Review (`my-performance/`)

- Focus: outcomes delivered, leadership demonstrated, measurable impact, professional growth
- Tone: confident but honest, reflective
- Include: concrete achievements, challenges overcome, areas for continued development

### Team Review (`my-team/`)

- Focus: individual strengths, growth areas, coaching opportunities, evidence of progress
- Tone: supportive, developmental, specific
- Include: what went well, where to improve, actionable next steps

### Peer Review (`my-peers/`)

- Focus: collaboration quality, reliability, influence, technical contribution
- Tone: collegial, constructive, honest
- Include: specific examples of working together, impact on shared goals

### Manager Review (`my-manager/`)

- Focus: support quality, clarity of direction, empowerment, feedback effectiveness
- Tone: respectful, constructive, specific
- Include: what works well in the relationship, what could improve, suggestions

---

## Example Q/A Format

For `1-5` rating questions, always make the scale explicit: **1 is the lowest rating and 5 is the highest rating**. Write a **3-4 sentence comment** for rating questions, and **4-6 sentences** for open questions, unless the user asks for a shorter format.

Example:

```markdown
## How would you rate your manager at encouraging and supporting your development? Over the last 6 months (1 = lowest, 5 = highest)

**Rating:** 4/5 — Great

**Justification:**
They have consistently provided opportunities for growth and have been proactive in offering guidance. I can point to several moments where they helped clarify next steps and supported learning. The support has been meaningful and visible over the cycle. I still see room for improvement in consistency and follow-through, which is why this is a 4 instead of a 5.
```

```markdown
## How has this person demonstrated leadership this cycle?

**Evidence:**
- Led the migration of payment service to new architecture (Q1), reducing deployment time by 40%
- Mentored two junior engineers through their first production releases
- Proactively identified and resolved cross-team dependency blockers on Project X

**Answer:**
[Drafted answer in the user's writing voice using impersonator skill]
```

If evidence is insufficient:

```markdown
## How has this person demonstrated leadership this cycle?

**Evidence:**
- [needs validation] — no specific examples found in context

**Follow-up needed:** Can you share specific examples of leadership this person showed? Think about project ownership, mentoring, or initiative.
```

---

## Required Skills

| Skill | When | Purpose |
|---|---|---|
| `impersonator` | All drafted review text | Match the user's writing voice and tone |
| `obsidian-note` | Context gathering and **all file create/update operations** (mandatory) | Discover prior notes, enforce tagging/summary/related rules, and safely create/update review pages |

---

## File Format

Review files are plain Markdown with this structure:

```markdown
# [Review Type]: [Person Name] — [Timeframe]

> Review cycle: [timeframe]. Generated with agent assistance.

## [Question 1 from HiBob]

[Answer]

## [Question 2 from HiBob]

[Answer]

...
```

For `1-5` rating questions, prefer this structure:

```markdown
## [Rating question text] (1 = lowest, 5 = highest)

**Rating:** [1-5]/5

[3-4 sentence comment]
```

For open questions, prefer a **4-6 sentence** answer with concrete examples and observed impact.
