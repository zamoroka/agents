import { createOpenAI } from '@ai-sdk/openai';
import { generateText } from 'ai';
import type { JiraIssue } from '../types/index.js';

const systemPrompt =
  'You summarize Jira tickets for pull request review. Be precise, concise, and avoid guessing.';

const buildPayload = (jiraIssue: JiraIssue) => ({
  key: jiraIssue.key,
  id: jiraIssue.id,
  self: jiraIssue.self,
  fields: {
    summary: jiraIssue.fields?.summary || '',
    status: jiraIssue.fields?.status?.name || '',
    priority: jiraIssue.fields?.priority?.name || '',
    issueType: jiraIssue.fields?.issuetype?.name || '',
    assignee: jiraIssue.fields?.assignee?.displayName || '',
    reporter: jiraIssue.fields?.reporter?.displayName || '',
    created: jiraIssue.fields?.created || '',
    updated: jiraIssue.fields?.updated || '',
    labels: jiraIssue.fields?.labels || [],
    components: (jiraIssue.fields?.components || []).map((item) => item?.name).filter(Boolean),
    fixVersions: (jiraIssue.fields?.fixVersions || []).map((item) => item?.name).filter(Boolean),
    description: jiraIssue.fields?.description || '',
    renderedDescription: jiraIssue.renderedFields?.description || '',
    comments: (jiraIssue.fields?.comment?.comments || []).map((comment) => ({
      author: comment?.author?.displayName || '',
      created: comment?.created || '',
      body: comment?.body || '',
      renderedBody: comment?.renderedBody || '',
    })),
    attachments: (jiraIssue.fields?.attachment || []).map((attachment) => ({
      filename: attachment?.filename || '',
      mimeType: attachment?.mimeType || '',
      size: attachment?.size || 0,
      created: attachment?.created || '',
      content: attachment?.content || '',
    })),
  },
});

const buildUserPrompt = (payload: ReturnType<typeof buildPayload>): string => `Read this Jira issue payload and produce a markdown summary for code reviewers.

Requirements:
- Use only information from payload.
- If data is missing, write "Not provided".
- Keep output concise and actionable.
- Include these sections in this order:
  1) Ticket
  2) Problem to solve
  3) Scope requirements
  4) Acceptance criteria or verification notes
  5) Constraints and dependencies
  6) Open questions
  7) Reviewer checklist

Payload JSON:
${JSON.stringify(payload, null, 2)}
`;

type SummarizeJiraIssueInput = {
  jiraIssue: JiraIssue;
  openaiApiKey: string;
  openaiModel: string;
};

export const summarizeJiraIssue = async ({ jiraIssue, openaiApiKey, openaiModel }: SummarizeJiraIssueInput): Promise<string> => {
  const payload = buildPayload(jiraIssue);
  const openai = createOpenAI({ apiKey: openaiApiKey });

  const result = await generateText({
    model: openai(openaiModel),
    system: systemPrompt,
    prompt: buildUserPrompt(payload),
    temperature: 0.1,
  });

  return result.text.trim();
};
