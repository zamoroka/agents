import type { JiraIssue } from '../types/index.js';

const normalizeBaseUrl = (value: string): string => value.replace(/\/$/, '');

const getAuthHeader = (email: string, token: string): string => {
  if (email) {
    return `Basic ${Buffer.from(`${email}:${token}`).toString('base64')}`;
  }
  return `Bearer ${token}`;
};

type GetJiraIssueInput = {
  baseUrl: string;
  issueKey: string;
  token: string;
  email: string;
};

export const getJiraIssue = async ({ baseUrl, issueKey, token, email }: GetJiraIssueInput): Promise<JiraIssue> => {
  const response = await fetch(
    `${normalizeBaseUrl(baseUrl)}/rest/api/2/issue/${encodeURIComponent(issueKey)}?expand=renderedFields`,
    {
      headers: {
        Accept: 'application/json',
        Authorization: getAuthHeader(email, token),
      },
    },
  );

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Jira issue fetch failed: ${response.status} ${response.statusText} ${body}`);
  }

  return (await response.json()) as JiraIssue;
};
