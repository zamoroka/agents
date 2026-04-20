import type { JiraAuthType, JiraIssue } from '../types/index.js';
import { getJiraIssue } from './jiraApiClient.js';
import { summarizeJiraIssue } from './summarizeJiraIssue.js';

type ProcessIssueSummaryInput = {
  issueKey: string;
  jiraBaseUrl: string;
  jiraApiToken: string;
  jiraEmail: string;
  jiraAuthType: JiraAuthType;
  openaiApiKey: string;
  openaiModel: string;
};

type ProcessIssueSummaryOutput = {
  issue: JiraIssue;
  summary: string;
};

export const processIssueSummary = async ({
  issueKey,
  jiraBaseUrl,
  jiraApiToken,
  jiraEmail,
  jiraAuthType,
  openaiApiKey,
  openaiModel,
}: ProcessIssueSummaryInput): Promise<ProcessIssueSummaryOutput> => {
  const issue = await getJiraIssue({
    baseUrl: jiraBaseUrl,
    issueKey,
    token: jiraApiToken,
    email: jiraEmail,
    jiraAuthType,
  });

  const summary = await summarizeJiraIssue({
    jiraIssue: issue,
    openaiApiKey,
    openaiModel,
  });

  return { issue, summary };
};
