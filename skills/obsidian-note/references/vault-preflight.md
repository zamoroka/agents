# Vault preflight

Shared setup steps that every `obsidian-note` workflow needs before writing.
Pulled out so each reference can point here instead of restating preconditions (which tend to drift out of sync).

## When to use

At the start of any workflow that may write to the vault. Skip in pure read-only flows (e.g. just answering "where is X").

## Steps

### 1. `VAULT_ROOT` is a constant

```
VAULT_ROOT=/Users/zamoroka_pavlo/Library/CloudStorage/GoogleDrive-zapashok0@gmail.com/My\ Drive/obsidian/zamoroka/
```

This is a personal skill — the path is fixed. Do not call `obsidian vault info=path` to "discover" it; that adds a tool round-trip with no benefit.

### 2. CLI is assumed available

The Obsidian app is always installed on this machine, so workflows can use `obsidian <command>` directly without a precheck. 
If a specific command errors out, handle that error in context — do not run a probe upfront.

### 3. Load vault conventions

Read `$VAULT_ROOT/AGENTS.md` before any write action. It is the source of truth for folder structure, personas, naming, and tagging.

A non-authoritative quick-reference (consult AGENTS.md for any decision that isn't obvious from this list):

| Path | Contents |
|---|---|
| `Work/Vaimo/` | work, professional, Vaimo-related content |
| `Work/Vaimo/Meeting notes/` | non-project meetings (leadership 1-1s, EME-wide, `Direct reports 1-1s/`) |
| `Work/Vaimo/projects/<ProjectName>/` | project-specific docs |
| `Work/Vaimo/projects/<ProjectName>/meeting-notes/` | project-specific meetings |
| `Work/Vaimo/projects/<ProjectName>/summaries/` | long-lived synthesis docs |
| `Work/Dev notes/` | technical references, runbooks, ADRs |
| `Personal/` | personal life, health, finance, goals |

If placement is ambiguous, ask before writing.

### 4. Template (when needed)

The canonical frontmatter template lives at `$VAULT_ROOT/_templates/page.md`.
Per-mode templates also live in this skill's `assets/frontmatter-templates/`(normal, meeting, email, summary, raw).
