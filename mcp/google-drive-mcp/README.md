# Google Drive MCP (Python)

MCP server for Google Drive workflows with an extendable architecture.

Current functionality:
- Download a Google Doc by URL and save it as Markdown (`.md`) using Google export endpoint:
  `https://docs.google.com/document/d/{fileId}/export?format=md`

## Tech choices

- Python MCP SDK (`mcp[cli]`) with `FastMCP`
- STDIO transport for compatibility with desktop MCP clients
- Logging via `logging` (stderr-safe for STDIO servers)
- Modular tool registration for easy extension

## Project structure

```text
google-drive-mcp/
  src/google_drive_mcp/
    auth/
      cli.py              # Manual authorization command
      oauth.py            # Token load/refresh/authorize helpers
    services/
      google_docs.py      # URL parsing + markdown download + save
    tools/
      base.py             # ToolRegistrar abstraction
      google_docs.py      # MCP tool implementation
    config.py             # Env-based settings
    server.py             # MCP entrypoint
```

## Prerequisites

- Python 3.10+
- `uv` recommended (or use pip/venv)
- Google Cloud project with OAuth Desktop app credentials

## Setup

From this folder:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Google authorization (initial setup)

1. Open Google Cloud Console.
2. Enable **Google Drive API** for your project.
3. Create OAuth client credentials of type **Desktop app**.
4. Download the client secret JSON.
5. Save it as:
   - `./secrets/google-oauth-client.json`
   - or any path and set `GOOGLE_OAUTH_CREDENTIALS_FILE`

Then run initial authorization:

```bash
google-drive-mcp-auth
```

If you see `command not found: google-drive-mcp-auth`, run it via `uv` without installing scripts globally:

```bash
uv run google-drive-mcp-auth
```

Or install project scripts into a local virtual environment first:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
google-drive-mcp-auth
```

This opens a browser consent flow and stores token at:
- `./secrets/google-token.json` by default
- or path from `GOOGLE_OAUTH_TOKEN_FILE`

## Run MCP server

```bash
google-drive-mcp
```

If the command is not available in your shell, you can also run:

```bash
uv run google-drive-mcp
```

## Tool

### `doc_markdown_download`

Inputs:
- `doc_url` (required): full Google Doc URL, for example:
  `https://docs.google.com/document/d/1Ai0foyGv-fx8oNS9jkbK4OcxZ6cjc9tmJqrDk1MPSKU/edit?tab=t.mwaoa1bc87zx`
- `file_name` (optional): output file name (`.md` appended automatically if missing)
- `output_dir` (optional): output directory path (defaults to `GOOGLE_DOCS_DOWNLOAD_DIR` / `./downloads`)

Behavior:
- Extracts `{fileId}` from URL
- Downloads markdown export from Google Docs
- Saves file into `output_dir` when provided, otherwise into `./downloads` (or `GOOGLE_DOCS_DOWNLOAD_DIR`)
- Returns absolute output path and downloaded character count

### `doc_markdown_output_tty`

Inputs:
- `doc_url` (required): full Google Doc URL

Behavior:
- Extracts `{fileId}` from URL
- Downloads markdown export from Google Docs
- Returns markdown content directly to MCP client output (TTY) without saving to a file

## Environment variables

- `GOOGLE_OAUTH_CREDENTIALS_FILE` (default: `./secrets/google-oauth-client.json`)
- `GOOGLE_OAUTH_TOKEN_FILE` (default: `./secrets/google-token.json`)
- `GOOGLE_DOCS_DOWNLOAD_DIR` (default: `./downloads`)

## Example Claude Desktop config

```json
{
  "mcpServers": {
    "google-drive": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/google-drive-mcp",
        "run",
        "google-drive-mcp"
      ]
    }
  }
}
```
