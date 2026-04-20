#!/usr/bin/env node

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { getProjectRoot, logger } from './common/index.js';
import { processIssueSummary } from './services/processIssueSummary.js';

const server = new McpServer({
  name: 'jira-mcp',
  version: '1.0.0',
});

server.tool(
  'get_jira_issue_details',
  'Fetches Jira issue details, writes an issue summary artifact, and returns summary location.',
  {
    repoSlug: z.string().min(1),
    prNumber: z.string().min(1),
    issueKey: z.string().min(1),
  },
  async ({ repoSlug, prNumber, issueKey }) => {
    const projectRoot = getProjectRoot();
    const result = await processIssueSummary({ repoSlug, prNumber, issueKey, projectRoot });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(
            {
              issueKey: result.issueKey,
              outputPath: result.outputPath,
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

try {
  const transport = new StdioServerTransport();
  await server.connect(transport);
} catch (error) {
  logger.error('jira-mcp server failed', { error: error instanceof Error ? error.message : String(error) });
  process.exit(1);
}
