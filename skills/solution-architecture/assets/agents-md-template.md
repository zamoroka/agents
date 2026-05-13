# AGENTS.md

> Single source of truth for any AI agent working in this repository. Keep it tight; move detail to linked notes when sections grow past a screen.

## 1. Project overview

- **Name:** <project name>
- **Purpose / business goal:** <one sentence — what this codebase delivers to whom>
- **Stage:** <PoC / MVP / Production / Maintenance / Sunset>
- **Primary stakeholders:** <client, internal product owner, key vendor>
- **Vault project folder:** <vault-root-relative path to `Work/<persona>/projects/<Project>/`>

## 2. Tech stack

- **Language(s):** <e.g. PHP 8.2, JavaScript (Magento UI components)>
- **Framework / platform:** <e.g. Magento 2.4.6-p3 with Adobe Commerce>
- **Datastore(s):** <e.g. MySQL 8, Redis (cache + session)>
- **Build / package managers:** <e.g. Composer, npm>
- **Other key libraries:** <list only the ones a new contributor would not guess from the manifest>

## 3. Repository layout

Top-level directories and what lives in them. Skip generic ones (e.g. `node_modules`).

| Path | Purpose |
|---|---|
| `app/code/<Vendor>/<Module>` | <description> |
| … | … |

## 4. How to run

Minimal commands a fresh clone needs to become productive. Prefer copy-pasteable.

```bash
# install
…

# run
…

# test
…
```

Note any environment that is not obvious (Docker stack, required env vars, secrets file location).

## 5. Conventions

Project-specific rules that override or extend any framework defaults. Examples:

- Coding style deviations from the framework default
- Branching / commit / PR conventions
- Test layout, naming, fixture conventions
- Logging / telemetry expectations
- Dependency-injection / extension patterns (e.g. Magento plugins vs preferences)

## 6. Domain concepts

Glossary of terms that recur in code and in stakeholder conversations. Two-column table is enough.

| Term | Meaning |
|---|---|
| <term> | <definition + where it appears in code> |

## 7. Integrations

External systems this project talks to (inbound and outbound). One row per integration.

| System | Direction | Transport | Auth | Notes |
|---|---|---|---|---|
| <name> | <inbound/outbound/both> | <REST/SOAP/MQ/file/SDK> | <type> | <link to summary, contract, or vendor docs> |

## 8. Knowledge base

Pointers to long-form context. Prefer vault-root-relative paths for Obsidian notes.

- **Project summaries (Obsidian):** `Work/<persona>/projects/<Project>/summaries/`
- **README / TASKS:** `Work/<persona>/projects/<Project>/README.md`, `…/TASKS.md`
- **External docs:** <vendor portals, Confluence, Google Drive folders — use full URLs>

## 9. Open architecture questions

Known unknowns at the architecture level. Move resolved entries to a decision row in the relevant project summary, then delete from here.

| Question | Why it matters | Awaiting |
|---|---|---|
| <question> | <impact on design> | <stakeholder / source> |

## 10. Change log

| Date | Change | By |
|---|---|---|
| <YYYY-MM-DD> | Initial AGENTS.md bootstrapped from source code + vault project folder | solution-architecture skill |
