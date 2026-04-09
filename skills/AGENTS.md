# AGENTS.md

This file defines how to create and modify skills in this repository.

## Scope

- Applies to every skill directory under `skills/`.
- A "skill" is a directory that contains a `SKILL.md` file (plus optional reference files/scripts).

## Source of truth

- Follow `best-practices.md` as the primary guidance for structure, naming, descriptions, and progressive disclosure.
- Keep instructions concise and high signal; avoid adding explanation the model already knows.

## Required skill structure

- Each skill must have `SKILL.md` with YAML frontmatter.
- Frontmatter must include:
  - `name`: lowercase letters/numbers/hyphens only, <= 64 chars, no reserved words (`anthropic`, `claude`).
  - `description`: non-empty, <= 1024 chars, written in third person, states what the skill does and when to use it.
- Keep `SKILL.md` focused as an overview; move deep details to referenced files when needed.

## Creating a new skill

1. Create a new folder named after the skill.
2. Add `SKILL.md` with valid frontmatter and concise usage instructions.
3. Add supplemental files only when they reduce `SKILL.md` size and improve clarity.
4. Ensure referenced files are linked directly from `SKILL.md` (avoid deep nested references).

## Modifying an existing skill

1. Preserve intent and triggering behavior unless change request explicitly says otherwise.
2. Keep naming and tone consistent with existing repository patterns.
3. Update linked references when sections are moved or renamed.
4. Prefer small, focused edits over broad rewrites.

## Mandatory verification

After every create or modify action on a skill, run verification from that skill's directory:

```bash
npx tessl skill review SKILL.md
```

Rules:

- This check is required; do not skip it.
- If multiple skills were changed, run it once per changed `SKILL.md`.
- Treat warnings/errors as actionable: fix and rerun until clean (or document why not fixable).

## Quality checklist before finishing

- Frontmatter is valid and constraints are met.
- Description is specific and includes usage triggers.
- Instructions are concise and actionable.
- References are one level deep from `SKILL.md`.
- Examples/commands are correct and minimal.
- `npx tessl skill review SKILL.md` has been run successfully.
