# MCP Servers — Direct Run Guide

MCP servers in this folder communicate over
**newline-delimited JSON-RPC 2.0** via stdin/stdout (no HTTP, no Content-Length headers).

## Usage order

1. Use connected MCP server tools first (preferred path).
2. If server is not connected/unavailable in current session, use the `direct-tool-call` skill.

---

## Servers

### mcp-jira

**Location:** `~/.agents/mcp/mcp-jira`  
**Entry point:** `uv run mcp-jira`  
**Docs:** `mcp-jira/README.md`  
**Config:** `mcp-jira/.env`

Run:

```bash
uv run mcp-jira
# from ~/.agents/mcp/mcp-jira
```

Tools: `fetch_jira_issue_details`, `fetch_jira_my_timelogs`, `add_jira_timelog`  
Prompts: `jira_issue_summary_prompt`

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
# mcp-jira
cd ~/.agents/mcp/mcp-jira && uv pip install -e .

# chrome-devtools-mcp
cd ~/.agents/mcp/chrome-devtools-mcp && npm run build
```
