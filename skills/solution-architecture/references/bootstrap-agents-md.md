# Bootstrap mode — create the project AGENTS.md

Goal: produce the first `$PROJECT_ROOT/AGENTS.md` for a repository, derived from source-code evidence and the matching Obsidian-vault project folder. After this runs once, the file is owned by **update mode** for the rest of the project's life.

_Why two distinct inputs (code + vault): code is precise about *what is*, but says little about *why*. The vault holds business goals, stakeholders, decisions, vendor context. Combining both keeps `AGENTS.md` accurate AND useful for downstream skills like `review-pr`._

## Preconditions

- `PROJECT_ROOT` is resolved (see main SKILL.md — shared context).
- `$PROJECT_ROOT/AGENTS.md` does **not** already exist. If it does, switch to update mode and tell the user — never silently overwrite.

## Step 1 — Source-code scan

Read with intent: skim, don't load the whole tree. Aim for "enough evidence to write a one-paragraph overview", not exhaustive cataloging.

Cover, in order:

1. **Top-level descriptor files** (whichever exist): `README.md`, `composer.json`, `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `Dockerfile`, `docker-compose.yml`, `.env.example`.
2. **Top-level directory listing** (one level deep): record names + a one-line guess at purpose for each.
3. **Platform hints** — explicit markers that pin the tech stack:
   - `app/code/<Vendor>/<Module>/etc/module.xml` → Magento 2
   - `wp-config-sample.php` / `wp-content/themes/` → WordPress
   - `manage.py` + `settings.py` → Django
   - `next.config.js` / `nuxt.config.ts` → Next/Nuxt
   - `pubspec.yaml` → Flutter
4. **Existing nested `AGENTS.md` / `CLAUDE.md` files** anywhere in the repo — these are pre-existing knowledge to *preserve*, not replace. Note their paths so the root `AGENTS.md` can link to them.
5. **CI configs** (`.github/workflows/`, `bitbucket-pipelines.yml`, `.gitlab-ci.yml`) — surface the canonical build/test/deploy commands.

Skip generated dirs by default (`node_modules`, `vendor`, `__pycache__`, build outputs, anything in `.gitignore`).

## Step 2 — Vault project scan

1. Resolve the matching vault project folder (see main SKILL.md — *Identifying the matching vault project*).
2. Once a folder is confirmed, read in this order (each call is cheap):
   ```bash
   obsidian outline path="Work/<persona>/projects/<Project>/README.md"
   obsidian outline path="Work/<persona>/projects/<Project>/TASKS.md"
   obsidian files folder="Work/<persona>/projects/<Project>/summaries"
   ```
3. For each summary in the summaries folder:
   ```bash
   obsidian outline path="Work/<persona>/projects/<Project>/summaries/<file>.md"
   ```
   Read full content only for summaries whose outline looks load-bearing for the architecture overview (e.g. a primary integration design doc), not for routine status pages.
4. Skim the Communications folder briefly via `obsidian search:context` for terms like `stakeholder`, `client`, `vendor`, `contact` if Step 2.2 didn't already surface them.

If no vault project folder exists, ask the user once whether to skip the vault step or pause until they create the folder. Do not fabricate stakeholder names or business goals.

## Step 3 — Compose the draft

Start from [../assets/agents-md-template.md](../assets/agents-md-template.md) and fill each section using the evidence collected:

| Section | Primary evidence source |
|---|---|
| 1. Project overview | Vault README + project summaries (stage, stakeholders, goal) |
| 2. Tech stack | Source-code descriptors (composer/package/pyproject) + platform hints |
| 3. Repository layout | Top-level directory listing |
| 4. How to run | README + CI configs + Dockerfile/compose |
| 5. Conventions | Nested AGENTS.md/CLAUDE.md files, linter configs, README |
| 6. Domain concepts | Vault summaries — pull recurring terms |
| 7. Integrations | Vault summaries (especially integration design docs) + `.env.example` |
| 8. Knowledge base | Vault paths + external links found in README/summaries |
| 9. Open architecture questions | Open Questions tables across vault summaries |
| 10. Change log | Today's date + "Initial AGENTS.md bootstrapped from source code + vault project folder" |

Rules while composing:

- **Cite, don't invent.** If a field has no evidence, leave it as a single placeholder line (`<unknown — confirm with PO>`) rather than guessing.
- **One screen per section.** If a section is overflowing, move detail to a linked note inside the repo (e.g. `docs/integrations.md`) and keep `AGENTS.md` as the index.
- Invoke `impersonator` before drafting prose (overview, conventions, domain concepts). Skip it for tables of literal values.
- Match the project's primary language for prose where the repo is already mostly that language; otherwise default to English.

## Step 4 — Proposal and approval

Present to the user:

1. Target path: `$PROJECT_ROOT/AGENTS.md`.
2. **Inline preview of the full file** (not just a table of contents) — `AGENTS.md` is short enough to read in one pass, and the user needs to audit every claim.
3. Highlight which sections came from source code versus vault, so the user knows where to push back. A short legend at the top of the preview is enough — `[code]`, `[vault]`, `[unknown]`.
4. Ask: *"Proceed to write, or which sections should I revise first?"*

Wait for explicit approval. If the user revises, redraft and re-present — don't write a half-approved version "as a starting point".

## Step 5 — Write

Once approved:

1. Write `$PROJECT_ROOT/AGENTS.md`.
2. If the repo is a git working tree, do **not** auto-commit. The user controls commit framing.
3. Report:
   - File path written.
   - Section count and any sections still marked `<unknown — confirm with PO>` (these are the prompts for the user's next stakeholder conversation).
   - Suggested next step: run **follow-up questions mode** if there are open unknowns and a vault project summary exists.

## Anti-patterns

- **Don't dump the file tree.** Listing every directory makes `AGENTS.md` a worse index. Group and explain.
- **Don't pull in implementation detail.** Patterns, not method signatures. Implementation belongs in the code; `AGENTS.md` is the map.
- **Don't restate framework defaults.** Magento has a layout; you don't need to re-explain it. Only document what is *specific to this project*.
- **Don't promote speculation.** If the vault notes say "exploring vendor X", that is an open question — not the stack.
