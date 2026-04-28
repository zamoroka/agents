#!/usr/bin/env node

import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import fs from 'node:fs';

const THIS_DIR = path.dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const parsed = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) continue;
    const key = token.slice(2);
    const value = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : 'true';
    parsed[key] = value;
  }
  return parsed;
}

function printHelp() {
  console.log(
    [
      'Usage:',
      "  node ~/.agents/mcp/direct-tool-call.mjs --tool <tool_name> [--args '<json>']",
      "    [--server-command '<cmd>'] [--server-args '<json-array>'] [--cwd '<path>'] [--sdk-dir '<path>']",
      '',
      'Defaults:',
      "  --server-command 'node'",
      "  --server-args '[\"dist/function.js\"]'",
      "  --cwd '~/.agents/mcp/jira-mcp'",
      "  --sdk-dir '~/.agents/mcp/jira-mcp/node_modules/@modelcontextprotocol/sdk'",
      '',
      'Examples (Jira):',
      "  node ~/.agents/mcp/direct-tool-call.mjs --tool fetch_jira_issue_details --args '{\"issueKey\":\"SUNNYR-64\"}'",
      '',
      'Example (Chrome MCP):',
      "  node ~/.agents/mcp/direct-tool-call.mjs --server-command node --server-args '[\"build/src/index.js\"]' --cwd '~/.agents/mcp/chrome-devtools-mcp' --tool list_pages --args '{}'",
    ].join('\n'),
  );
}

async function loadSdk(sdkDir) {
  const esmClient = path.join(sdkDir, 'dist/esm/client/index.js');
  const esmStdio = path.join(sdkDir, 'dist/esm/client/stdio.js');
  const legacyClient = path.join(sdkDir, 'client/index.js');
  const legacyStdio = path.join(sdkDir, 'client/stdio.js');
  const clientPath = fs.existsSync(esmClient) ? esmClient : legacyClient;
  const stdioPath = fs.existsSync(esmStdio) ? esmStdio : legacyStdio;
  const clientModuleUrl = pathToFileURL(clientPath).href;
  const stdioModuleUrl = pathToFileURL(stdioPath).href;
  const [{ Client }, { StdioClientTransport }] = await Promise.all([import(clientModuleUrl), import(stdioModuleUrl)]);
  return { Client, StdioClientTransport };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help === 'true' || !args.tool) {
    printHelp();
    return;
  }

  let toolArgs = {};
  if (args.args) {
    try {
      toolArgs = JSON.parse(args.args);
    } catch (error) {
      throw new Error(`Invalid JSON in --args: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  let serverArgs = ['dist/function.js'];
  if (args['server-args']) {
    try {
      const parsed = JSON.parse(args['server-args']);
      if (!Array.isArray(parsed) || parsed.some((item) => typeof item !== 'string')) {
        throw new Error('Expected JSON array of strings.');
      }
      serverArgs = parsed;
    } catch (error) {
      throw new Error(`Invalid JSON in --server-args: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  const serverCommand = args['server-command'] || 'node';
  const serverCwd = args.cwd ? path.resolve(args.cwd.replace(/^~(?=\/)/, process.env.HOME || '~')) : path.join(THIS_DIR, 'jira-mcp');
  const sdkDir = args['sdk-dir']
    ? path.resolve(args['sdk-dir'].replace(/^~(?=\/)/, process.env.HOME || '~'))
    : path.join(THIS_DIR, 'jira-mcp', 'node_modules', '@modelcontextprotocol', 'sdk');

  const { Client, StdioClientTransport } = await loadSdk(sdkDir);
  const client = new Client({ name: 'mcp-direct-call', version: '1.2.0' }, { capabilities: {} });
  const transport = new StdioClientTransport({
    command: serverCommand,
    args: serverArgs,
    cwd: serverCwd,
  });

  try {
    await client.connect(transport);
    const result = await client.callTool({
      name: args.tool,
      arguments: toolArgs,
    });
    console.log(result?.content?.[0]?.text ?? JSON.stringify(result, null, 2));
  } finally {
    await client.close();
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
