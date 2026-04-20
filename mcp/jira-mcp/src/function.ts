#!/usr/bin/env node

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { getConfig, logger } from './common/index.js';
import { getJiraIssue } from './services/jiraApiClient.js';
import { processIssueSummary } from './services/processIssueSummary.js';

const server = new McpServer({
  name: 'jira-mcp',
  version: '1.0.0',
});

server.registerTool(
  'fetch_jira_issue_details',
  {
    description: 'Fetch Jira issue details by issue key.',
    inputSchema: {
      issueKey: z.string().min(1),
      jiraBaseUrl: z.string().url().optional(),
      jiraApiToken: z.string().min(1).optional(),
      jiraEmail: z.string().email().optional(),
      jiraAuthType: z.enum(['auto', 'bearer', 'basic']).optional(),
    },
  },
  async ({ issueKey, jiraBaseUrl, jiraApiToken, jiraEmail, jiraAuthType }) => {
    const config = await getConfig({ jiraBaseUrl, jiraApiToken, jiraEmail, jiraAuthType });
    const issue = await getJiraIssue({
      baseUrl: config.jiraBaseUrl,
      issueKey,
      token: config.jiraApiToken,
      email: config.jiraEmail,
      jiraAuthType: config.jiraAuthType,
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(issue, null, 2),
        },
      ],
    };
  },
);

server.registerTool(
  'fetch_jira_issue_ai_summary',
  {
    description: 'Fetch Jira issue details and return an AI markdown summary.',
    inputSchema: {
      issueKey: z.string().min(1),
      jiraBaseUrl: z.string().url().optional(),
      jiraApiToken: z.string().min(1).optional(),
      jiraEmail: z.string().email().optional(),
      jiraAuthType: z.enum(['auto', 'bearer', 'basic']).optional(),
      openaiApiKey: z.string().min(1).optional(),
      openaiModel: z.string().min(1).optional(),
    },
  },
  async ({ issueKey, jiraBaseUrl, jiraApiToken, jiraEmail, jiraAuthType, openaiApiKey, openaiModel }) => {
    const config = await getConfig({
      jiraBaseUrl,
      jiraApiToken,
      jiraEmail,
      jiraAuthType,
      openaiApiKey,
      openaiModel,
    });

    if (!config.openaiApiKey) {
      throw new Error('Missing OPENAI_API_KEY. Set it in .env or pass openaiApiKey to the tool call.');
    }

    const result = await processIssueSummary({
      issueKey,
      jiraBaseUrl: config.jiraBaseUrl,
      jiraApiToken: config.jiraApiToken,
      jiraEmail: config.jiraEmail,
      jiraAuthType: config.jiraAuthType,
      openaiApiKey: config.openaiApiKey,
      openaiModel: config.openaiModel,
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(
            {
              issueKey: result.issue.key || issueKey,
              model: config.openaiModel,
              summary: result.summary,
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
