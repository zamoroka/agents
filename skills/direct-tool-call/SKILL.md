---
name: direct-tool-call
description: Calls any stdio MCP server tool directly via a Node.js script when the live MCP server is unavailable in the current session. Use when an MCP tool call fails or the server is not connected.
---

# Direct Tool Call

Use this skill as a **fallback only** when a live MCP server tool is unavailable.

## Script location

`~/.agents/skills/direct-tool-call/direct-tool-call.mjs`

## Usage

```bash
node ~/.agents/skills/direct-tool-call/direct-tool-call.mjs \
  --server-command '<command>' \
  --server-args '<json-array-of-args>' \
  --cwd '<server-working-dir>' \
  --tool '<tool_name>' \
  --args '<json>'
```

### Defaults (Jira MCP)

| Flag | Default |
|---|---|
| `--server-command` | `node` |
| `--server-args` | `["dist/function.js"]` |
| `--cwd` | `~/.agents/mcp/jira-mcp` |
| `--sdk-dir` | `~/.agents/mcp/jira-mcp/node_modules/@modelcontextprotocol/sdk` |

## Known servers (`mcp-config.json`)

Config: `~/.agents/skills/direct-tool-call/mcp-config.json`

| Server key | command | args |
|---|---|---|
| `jira` | `node` | `/Users/zamoroka_pavlo/.agents/mcp/jira-mcp/dist/function.js` |
| `chrome-devtools` | `npx` | `-y chrome-devtools-mcp@latest` |
| `google-drive` | `uv` | `--directory /Users/zamoroka_pavlo/.agents/mcp/google-drive-mcp run google-drive-mcp` |
| `magento2-lsp-mcp` | `magento2-lsp-mcp` | _(none)_ |

Translate the config entry directly into `--server-command` / `--server-args` / `--cwd` flags.

## Examples

**Jira** (uses all defaults):

```bash
node ~/.agents/skills/direct-tool-call/direct-tool-call.mjs \
  --tool fetch_jira_issue_details \
  --args '{"issueKey":"SUNNYR-64"}'
```

**Chrome DevTools — list pages:**

```bash
node ~/.agents/skills/direct-tool-call/direct-tool-call.mjs \
  --server-command npx \
  --server-args '["-y","chrome-devtools-mcp@latest"]' \
  --tool list_pages \
  --args '{}'
```

**Chrome DevTools — open URL:**

```bash
node ~/.agents/skills/direct-tool-call/direct-tool-call.mjs \
  --server-command npx \
  --server-args '["-y","chrome-devtools-mcp@latest"]' \
  --tool new_page \
  --args '{"url":"https://google.com","timeout":60000}'
```

**Google Drive:**

```bash
node ~/.agents/skills/direct-tool-call/direct-tool-call.mjs \
  --server-command uv \
  --server-args '["--directory","/Users/zamoroka_pavlo/.agents/mcp/google-drive-mcp","run","google-drive-mcp"]' \
  --tool '<tool_name>' \
  --args '{}'
```

**Magento 2 LSP:**

```bash
node ~/.agents/skills/direct-tool-call/direct-tool-call.mjs \
  --server-command magento2-lsp-mcp \
  --server-args '[]' \
  --tool '<tool_name>' \
  --args '{}'
```

**No MCP SDK in server's `node_modules`** — pass `--sdk-dir`:

```bash
--sdk-dir ~/.agents/mcp/jira-mcp/node_modules/@modelcontextprotocol/sdk
```

