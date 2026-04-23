#!/usr/bin/env node

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { getConfig, logger } from './common/index.js';
import { addJiraIssueWorklog, getJiraIssue } from './services/jiraApiClient.js';
import { processMyTimelogs } from './services/processMyTimelogs.js';
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
  'add_jira_timelog',
  {
    description: 'Add a worklog entry to a Jira issue.',
    inputSchema: {
      issueKey: z.string().min(1),
      timeSpent: z.string().min(1).optional(),
      timeSpentSeconds: z.number().int().positive().optional(),
      comment: z.string().min(1).optional(),
      started: z.string().min(1).optional(),
      jiraBaseUrl: z.string().url().optional(),
      jiraApiToken: z.string().min(1).optional(),
      jiraEmail: z.string().email().optional(),
      jiraAuthType: z.enum(['auto', 'bearer', 'basic']).optional(),
    },
  },
  async ({ issueKey, timeSpent, timeSpentSeconds, comment, started, jiraBaseUrl, jiraApiToken, jiraEmail, jiraAuthType }) => {
    if (!timeSpent && !timeSpentSeconds) {
      throw new Error('Missing time value. Provide either timeSpent (for example "15m") or timeSpentSeconds.');
    }

    const config = await getConfig({ jiraBaseUrl, jiraApiToken, jiraEmail, jiraAuthType });
    const worklog = await addJiraIssueWorklog({
      baseUrl: config.jiraBaseUrl,
      issueKey,
      timeSpent,
      timeSpentSeconds,
      comment,
      started,
      token: config.jiraApiToken,
      email: config.jiraEmail,
      jiraAuthType: config.jiraAuthType,
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(worklog, null, 2),
        },
      ],
    };
  },
);

server.registerTool(
  'fetch_jira_my_timelogs',
  {
    description: 'Fetch and summarize current user Jira timelogs for the last N days.',
    inputSchema: {
      days: z.number().int().min(1).max(365).optional(),
      jiraBaseUrl: z.string().url().optional(),
      jiraApiToken: z.string().min(1).optional(),
      jiraEmail: z.string().email().optional(),
      jiraAuthType: z.enum(['auto', 'bearer', 'basic']).optional(),
    },
  },
  async ({ days, jiraBaseUrl, jiraApiToken, jiraEmail, jiraAuthType }) => {
    const config = await getConfig({ jiraBaseUrl, jiraApiToken, jiraEmail, jiraAuthType });
    const report = await processMyTimelogs({
      jiraBaseUrl: config.jiraBaseUrl,
      jiraApiToken: config.jiraApiToken,
      jiraEmail: config.jiraEmail,
      jiraAuthType: config.jiraAuthType,
      days: days ?? 30,
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(report, null, 2),
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
