# MCP Servers — Direct Run Guide

MCP servers in this folder communicate over
**newline-delimited JSON-RPC 2.0** via stdin/stdout (no HTTP, no Content-Length headers).

## Usage order

1. Use connected MCP server tools first (preferred path).
2. If server is not connected/unavailable in current session, use the `direct-tool-call` skill.

---

## Servers

### jira-mcp

**Location:** `~/.agents/mcp/jira-mcp`  
**Entry point:** `uv run jira-mcp`  
**Docs:** `jira-mcp/README.md`  
**Config:** `jira-mcp/.env`

Run:

```bash
uv run jira-mcp
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

## Direct-call workaround

When a live MCP tool is unavailable, use the **`direct-tool-call` skill** — see `~/.agents/skills/direct-tool-call/SKILL.md`.

---

## Rebuilding a server

If you modify source files, rebuild before running:

```bash
# jira-mcp
cd ~/.agents/mcp/jira-mcp && uv pip install -e .

# chrome-devtools-mcp
cd ~/.agents/mcp/chrome-devtools-mcp && npm run build
```
