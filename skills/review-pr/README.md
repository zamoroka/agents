# Review

## Flow

- Agent always asks user to confirm project root, or asks for absolute project root path if it is not clear.
- Agent asks for PR URL.
- User provides PR URL.
- Agent validates URL shape, detects git provider, and runs `pr-fetch` with provider + PR URL for Bitbucket.
- If provider is GitHub, agent responds: `not supported yet`.
- `pr-fetch` returns PR details, comments, and full diff to the agent.
- Agent loads relevant `AGENTS.md` files, detects project type, and selects the LSP/MCP provider (before fetch).
- Agent launches isolated `changes-checker-agent` (with known project type) and continues the main flow in parallel.
- Agent determines Jira issue key from PR data.
- Agent always asks user to confirm detected Jira issue key.
- If key is not in PR details, agent asks user to provide one or confirm skipping Jira step when PR is not Jira-related.
- If Jira issue key is provided, agent launches isolated subagent `jira-agent` (`~/.agents/agents/jira-agent.md`) that fetches raw issue data via `fetch_jira_issue_details`, MUST call `jira_issue_summary_prompt`, and generates the summary from that returned prompt contract; main agent then saves only that subagent output to the issue-summary artifact file.
- After Jira summary is saved, agent launches another isolated subagent `functionality-checker-agent` (`~/.agents/agents/functionality-checker-agent.md`) to validate whether Jira requirements are already covered by existing/default project functionality. This subagent must not inspect PR diff and returns implementation status/explanation (with exact files) plus a project-specific `implementationProposal` when status is `not_implemented`; main agent appends that output to the issue-summary artifact.
- `changes-checker-agent` performs PR code review (quality, standards, architecture, bug risk, security) using guardrails/checklists.
- In review step (main agent only), agent cross-checks outputs from `changes-checker-agent`, `jira-agent`, and `functionality-checker-agent` for alignment/mismatches and better implementation options; if Jira is skipped, it judges based on `changes-checker-agent` only.
- Agent builds the PR summary from `changes-checker-agent` output.
- In artifact step (main agent only), agent saves final PR review artifact.

## Sequence diagram

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant M as Main review-pr agent
    participant BB as Bitbucket PR fetch
    participant CC as changes-checker-agent
    participant JA as jira-agent
    participant FC as functionality-checker-agent
    participant JM as mcp-jira/direct-tool-call
    participant MM as magento2-lsp-mcp
    participant FS as Artifacts filesystem

    U->>M: Provide PR URL
    M->>M: Validate URL, detect project root, ensure .env.local/.gitignore
    M->>M: Read AGENTS.md, detect project type and select LSP/MCP provider
    M->>BB: Fetch PR metadata + diff
    BB-->>M: PR details, comments, changed files, diff
    M->>FS: Save diff artifact
    M->>M: Load AGENTS.md from PR-modified directories

    M->>CC: Launch isolated changes checker (parallel)

    M->>M: Detect Jira issue key from PR data
    M->>U: Confirm key (or provide/skip)

    alt Jira linked
        M->>JA: Launch isolated Jira summarizer
        JA->>JM: fetch_jira_issue_details
        JA->>JM: jira_issue_summary_prompt
        JM-->>JA: Jira raw data + summary contract
        JA-->>M: JSON {issueKey, summary}
        M->>FS: Save issue-summary artifact
    else No Jira
        M->>M: Skip Jira summary and functionality check
    end

    alt Jira linked
        M->>FC: Check existing/default functionality (no diff access)
        FC->>FS: Read issue-summary artifact
        alt Magento project
            FC->>MM: Collect Magento evidence
            MM-->>FC: Project behavior evidence
        end
        FC-->>M: Decision/proposal
        M->>FS: Append "## Agent proposal implementation"
    end

    CC-->>M: Return summary + review findings
    alt Jira linked
        M->>M: Cross-check Jira summary vs PR changes
        M->>M: Cross-check functionality output vs PR changes
        M->>M: Add mismatch warnings and better-solution notes
    else No Jira
        M->>M: Judge quality from changes-checker output only
    end

    M->>M: Merge findings from existing subagent outputs
    M->>FS: Save final review artifact
    M-->>U: Return artifact path + issue count summary
```

### Agent dependencies

- Always spawned: `changes-checker-agent`.
- Jira flow only: `jira-agent`, `functionality-checker-agent`.
- Ordering constraints: `jira-agent` must finish before writing issue summary; issue summary write must finish before `functionality-checker-agent` starts.
- Timeout: all subagents have a 10-minute hard limit; main agent STOPs on timeout.
- Review ownership: code-review findings are produced by `changes-checker-agent`.
- Summary dependency: main agent uses `changes-checker-agent` summary fields.
- Step 8/9 rule: main agent does not launch extra subagents; it aggregates existing subagent outputs and writes final artifact.
- Artifact write failure: any write failure is a hard STOP — no retries, user re-runs the workflow.
- Conditional dependency: when project type is Magento 2, agents making Magento-specific claims must use `magento2-lsp-mcp` as evidence.
- Fallback dependency: `jira-agent` uses `mcp-jira` first, then `direct-tool-call` fallback when MCP is unavailable.

## Parallel execution timeline

> Represents the Jira-linked flow (longest path). No-Jira flow skips `jira-agent` and `functionality-checker-agent` rows.

```mermaid
gantt
    title review-pr — parallel execution
    dateFormat  X
    axisFormat  %s

    section Bootstrap
    Steps 0-2.1  root · env · project type      : 0, 3
    Step 3  fetch PR data                        : 3, 5
    Step 3.1  load AGENTS.md from PR-modified dirs : 5, 6

    section Main agent
    Step 5  detect + confirm Jira key            : 6, 7
    Step 6  launch + await jira-agent            : 7, 10
    Step 6.2  write issue-summary artifact       : 10, 11
    Step 7  launch + await functionality-checker : 11, 14
    Step 8  collect CC output + cross-check      : 14, 17
    Step 9  save review artifact                 : 17, 19

    section changes-checker-agent
    Step 4-8  code review (background)           : crit, 6, 14

    section jira-agent
    Step 6  fetch + summarize ticket             : 7, 10

    section functionality-checker-agent
    Step 7  check existing functionality         : 11, 14
```

## Artifact data flow

```mermaid
flowchart LR
    subgraph ext [External]
        BB[(Bitbucket PR)]
        JM[(Jira via mcp-jira)]
    end

    subgraph agents [Agents]
        M(Main agent)
        CC(changes-checker-agent)
        JA(jira-agent)
        FC(functionality-checker-agent)
    end

    subgraph files [Artifact files]
        DIFF[diff.patch]
        IS[issue-summary.md]
        RV[review.md]
    end

    BB -->|pr-fetch| DIFF
    DIFF -->|read| CC
    CC -->|JSON findings| M

    JM --> JA
    JA -->|JSON summary| M
    M -->|create| IS

    IS -->|read| FC
    FC -->|JSON proposal| M
    M -->|append proposal| IS

    M -->|merge + create| RV
```



- PR URL from user.
- Optional Jira issue key confirmation from user.
- Environment values in `$PROJECT_ROOT/.env.local` for Bitbucket fetch.
- Jira/LLM values in `~/.agents/mcp/mcp-jira/.env` (or passed as MCP tool arguments) when Jira summary step is used by the isolated Jira subagent.

## Token setup tip

- Bitbucket API token: generate at `https://id.atlassian.com/manage-profile/security/api-tokens`.
- Jira API token/PAT: use a **standard Atlassian API token** from `https://id.atlassian.com/manage-profile/security/api-tokens` (use the regular **Create API token** option, not **Create API token with scopes**, unless your org explicitly requires scoped tokens).

## Outputs

- PR review artifacts in `$PROJECT_ROOT/.agents/artifacts/`.

## Runtime notes

- Prefer execution-first flow: run the main command and remediate concrete failures (missing files/dirs/deps/env) instead of broad pre-check passes.
- `pr-fetch` requires a Node runtime with global `fetch` support (Node 18+).
- If the local default Node is older (for example Node 17) and commands fail with `fetch is not defined`, run PR fetch with Node 25 and run Jira via `uv`:
  - `PROJECT_ROOT="{PROJECT_ROOT}" npx -y node@25 --loader ts-node/esm src/function.ts bitbucket {PR_URL}` from `~/.agents/skills/review-pr/scripts/pr-fetch`
  - `uv run mcp-jira` from `~/.agents/mcp/mcp-jira`
- Jira summarization must attempt fallback when Jira MCP is unavailable: use `direct-tool-call` skill to call `fetch_jira_issue_details` before declaring Jira step failed.
- `magento2-lsp-mcp` is expected to be preinstalled in this environment; skip reinstall in standard review runs.
- If project type is Magento 2 / Adobe Commerce, isolated `functionality-checker-agent` should use `magento2-lsp-mcp` for Magento-specific claims.

## Jira isolation contract

- Main agent must use Jira context only from the isolated Jira subagent output.
- If subagent output is invalid JSON or missing required fields (`issueKey`, `summary`), stop and fail instead of continuing with partial Jira context.
- If `summary` is missing required `jira_issue_summary_prompt` headings, stop and fail instead of accepting partial structure.
- Main agent must not merge Jira facts from direct Jira tool calls after subagent launch.

### Artifact naming convention

- Format: `<YYYY>-<mm>-<dd>-pr-<repo_slug>-<number>-<artifact_type>`
- `repo_slug` is extracted from PR URL repo segment (example: `project_sunny-eu` from `https://bitbucket.org/vaimo/project_sunny-eu/pull-requests/726/`)
- `number` is extracted from PR URL PR number segment (example: `726`)
- `artifact_type` examples: `diff`, `issue-summary`, `review`

Examples in `$PROJECT_ROOT/.agents/artifacts/`:
- `YYYY-mm-dd-pr-<repo_slug>-<number>-diff.patch`
- `YYYY-mm-dd-pr-<repo_slug>-<number>-issue-summary.md`
- `YYYY-mm-dd-pr-<repo_slug>-<number>-review.md`

### Review artifact content

- Put the complete review into `-review.md`.
- Include findings, suggested fixes, and optional code snippets in the same file.
- Do not create a separate `-review-inline.json` artifact.
