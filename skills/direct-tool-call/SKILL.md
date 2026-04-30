---
name: direct-tool-call
description: Calls any stdio MCP server tool directly via a Node.js or Python/uv script only when the live MCP server is unavailable in the current session. Use this fallback instead of web_fetch when MCP access is missing.
---

# Direct Tool Call

Use this skill as a **fallback only** when a live MCP server tool, prompt, or resource is unavailable.
Do **not** use `web_fetch` as a substitute for MCP tool calls.

## Script locations

| Runtime | Path |
|---|---|
| Python (uv) | `~/.agents/skills/direct-tool-call/direct-tool-call.py` |

**Prefer the Python script** — it has no local SDK dependency and runs fully self-contained via `uv`.

## Usage

```bash
uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \
  --server-command '<command>' \
  --server-args '<json-array-of-args>' \
  --cwd '<server-working-dir>' \
  (--tool '<tool_name>' | --prompt '<prompt_name>' | --resource '<resource_uri>') \
  --args '<json>'
```

For prompts, `--args` should be a JSON object. Non-string values are JSON-stringified before sending.
For resources, `--resource` is required and `--args` is ignored.

> All three flags (`--server-command`, `--server-args`, `--cwd`) are required. Look them up in
> `~/.agents/skills/direct-tool-call/mcp-config.json` before running the script (see below).

## Resolving server flags from `mcp-config.json`

**Always read `~/.agents/skills/direct-tool-call/mcp-config.json` first** to get the correct
`command`, `args`, and working directory for the target server.

| `mcpServers` key | `--server-command` | `--server-args`                                                                                 | `--cwd` |
|---|---|-------------------------------------------------------------------------------------------------|---|
| `jira` | `uv` | `["--directory","~/.agents/mcp/jira-mcp","run","jira-mcp"]`                                  | `~/.agents/mcp/jira-mcp` |
| `chrome-devtools` | `npx` | `["-y","chrome-devtools-mcp@latest"]`                                                           | _(any)_ |
| `google-drive` | `uv` | `["--directory","~/.agents/mcp/google-drive-mcp","run","google-drive-mcp"]` | `~/.agents/mcp/google-drive-mcp` |
| `magento2-lsp-mcp` | `magento2-lsp-mcp` | `[]`                                                                                            | _(any)_ |

**Mapping rules:**
- `command` → `--server-command`
- `args` → `--server-args` (pass as a JSON array string)
- For servers whose args contain an absolute path to a file or `--directory <path>`, use that directory as `--cwd`. For servers with no local path (e.g. `npx`), you may pass any writable directory (e.g. `/tmp`).

## Examples

**Jira:**

```bash
uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \
  --server-command uv \
  --server-args '["--directory","~/.agents/mcp/jira-mcp","run","jira-mcp"]' \
  --cwd ~/.agents/mcp/jira-mcp \
  --tool fetch_jira_issue_details \
  --args '{"issueKey":"SUNNYR-64"}'
```

**Jira prompt (AI summary):**

```bash
uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \
  --server-command uv \
  --server-args '["--directory","~/.agents/mcp/jira-mcp","run","jira-mcp"]' \
  --cwd ~/.agents/mcp/jira-mcp \
  --prompt jira_issue_summary_prompt \
  --args '{"issueKey":"SUNNYR-64"}'
```

**Resource read:**

```bash
uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \
  --server-command '<command>' \
  --server-args '<json-array-of-args>' \
  --cwd '<server-working-dir>' \
  --resource '<resource_uri>' \
  --args '{}'
```

**Chrome DevTools — list pages:**

```bash
uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \
  --server-command npx \
  --server-args '["-y","chrome-devtools-mcp@latest"]' \
  --cwd /tmp \
  --tool list_pages \
  --args '{}'
```

**Chrome DevTools — open URL:**

```bash
uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \
  --server-command npx \
  --server-args '["-y","chrome-devtools-mcp@latest"]' \
  --cwd /tmp \
  --tool new_page \
  --args '{"url":"https://google.com","timeout":60000}'
```

**Google Drive:**

```bash
uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \
  --server-command uv \
  --server-args '["--directory","~/.agents/mcp/google-drive-mcp","run","google-drive-mcp"]' \
  --cwd ~/.agents/mcp/google-drive-mcp \
  --tool '<tool_name>' \
  --args '{}'
```

**Magento 2 LSP:**

```bash
uv run ~/.agents/skills/direct-tool-call/direct-tool-call.py \
  --server-command magento2-lsp-mcp \
  --server-args '[]' \
  --cwd /tmp \
  --tool '<tool_name>' \
  --args '{}'
```
