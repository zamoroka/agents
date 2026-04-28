# MCP Servers — Direct Run Guide

All MCP servers in this folder use **Node.js 25** and communicate over
**newline-delimited JSON-RPC 2.0** via stdin/stdout (no HTTP, no Content-Length headers).

## Usage order

1. Use connected MCP server tools first (preferred path).
2. If server is not connected/unavailable in current session, use direct-call workaround script.

---

## Servers

### jira-mcp

**Location:** `~/.agents/mcp/jira-mcp`  
**Entry point:** `dist/function.js` (pre-built)  
**Docs:** `jira-mcp/README.md`  
**Config:** `jira-mcp/.env`

Run:

```bash
node dist/function.js
# from ~/.agents/mcp/jira-mcp
```

Tools: `fetch_jira_issue_details`, `fetch_jira_my_timelogs`, `add_jira_timelog`, `fetch_jira_issue_ai_summary`

---

### chrome-devtools-mcp

**Location:** `~/.agents/mcp/chrome-devtools-mcp`  
**Entry point:** `build/src/bin/chrome-devtools-mcp.js` (pre-built, use this for direct calls)  
**Docs:** `chrome-devtools-mcp/README.md`

Run:

```bash
node build/src/bin/chrome-devtools-mcp.js
# from ~/.agents/mcp/chrome-devtools-mcp
```

Useful flags: `--no-usage-statistics`, `--no-performance-crux`

---

## Direct-call workaround script

Use one script for any stdio MCP server **only as fallback when live MCP is unavailable**:

```bash
node ~/.agents/mcp/direct-tool-call.mjs \
  --server-command '<command>' \
  --server-args '<json-array-of-args>' \
  --cwd '<server-working-dir>' \
  --tool '<tool_name>' \
  --args '<json>'
```

Jira example:

```bash
node ~/.agents/mcp/direct-tool-call.mjs \
  --tool fetch_jira_issue_details \
  --args '{"issueKey":"SUNNYR-64"}'
```

Chrome example:

```bash
node ~/.agents/mcp/direct-tool-call.mjs \
  --server-command node \
  --server-args '["build/src/bin/chrome-devtools-mcp.js","--no-usage-statistics","--no-performance-crux"]' \
  --cwd ~/.agents/mcp/chrome-devtools-mcp \
  --tool list_pages \
  --args '{}'
```

Chrome open URL example (reliable for page loads that need more time):

```bash
node ~/.agents/mcp/direct-tool-call.mjs \
  --server-command node \
  --server-args '["build/src/bin/chrome-devtools-mcp.js","--no-usage-statistics","--no-performance-crux"]' \
  --cwd ~/.agents/mcp/chrome-devtools-mcp \
  --tool new_page \
  --args '{"url":"https://google.com","timeout":60000}'
```

If a target server does not have MCP SDK in its own `node_modules`, pass:

```bash
--sdk-dir ~/.agents/mcp/jira-mcp/node_modules/@modelcontextprotocol/sdk
```

---

## Rebuilding a server

If you modify source files, rebuild before running:

```bash
# jira-mcp
cd ~/.agents/mcp/jira-mcp && npm run build

# chrome-devtools-mcp
cd ~/.agents/mcp/chrome-devtools-mcp && npm run build
```
