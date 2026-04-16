# Review guardrails

Apply these rules in Step 5.

## Behavior-claim evidence rule

For claims like "won't work", "breaks X", or "overrides Y":

- Read the actual implementation in this codebase before flagging (including `vendor/` or module internals when relevant).
- If the issue depends on framework/library behavior, include a verbatim proof snippet with file path and line range.
- If you cannot verify the claim with source evidence, drop the issue.

## Reviewer scopes

- `pr-ticket-alignment-checker`: compare PR diff against `YYYY-mm-dd-pr-{REPO_SLUG}-{PR_NUMBER}-issue-summary.md`; flag missing ticket requirements or out-of-scope implementation.
- `code-quality-pragmalist`: correctness, runtime risk, logic defects, API misuse, and missing edge-case handling.
- `claude-md-compliance-checker`: compliance with `AGENTS.md` rules, required project conventions, and mandated file/format patterns.

## False-positive filters

Do NOT flag:

- Pre-existing issues or intentionally correct behavior.
- Pedantic nits that a senior engineer would ignore.
- Lint-only issues or broad quality/security concerns unless explicitly required in `AGENTS.md`.
- Rules explicitly silenced in code (for example via lint ignore comments).
