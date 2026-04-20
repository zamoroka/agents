import { request as httpRequest } from 'node:http';
import { request as httpsRequest } from 'node:https';
import type { JiraAuthType, JiraIssue, JiraIssueWorklogPage, JiraSearchResult, JiraUser } from '../types/index.js';

const normalizeBaseUrl = (value: string): string => value.replace(/\/$/, '');

class JiraHttpError extends Error {
  constructor(
    message: string,
    public readonly statusCode: number,
  ) {
    super(message);
    this.name = 'JiraHttpError';
  }
}

const getBearerAuthHeader = (token: string): string => `Bearer ${token}`;
const getBasicAuthHeader = (email: string, token: string): string => `Basic ${Buffer.from(`${email}:${token}`).toString('base64')}`;

type GetJiraIssueInput = {
  baseUrl: string;
  issueKey: string;
  token: string;
  email: string;
  jiraAuthType: JiraAuthType;
};

type JiraAuthInput = {
  token: string;
  email: string;
  jiraAuthType: JiraAuthType;
};

type JiraPaginatedInput = {
  startAt?: number;
  maxResults?: number;
};

const fetchJson = async <T>({
  url,
  headers,
  redirectCount = 0,
}: {
  url: URL;
  headers: Record<string, string>;
  redirectCount?: number;
}): Promise<T> => {
  if (redirectCount > 5) {
    throw new Error('Jira issue fetch failed: too many redirects');
  }

  const requestImpl = url.protocol === 'https:' ? httpsRequest : httpRequest;

  return new Promise<T>((resolve, reject) => {
    const req = requestImpl(
      url,
      {
        method: 'GET',
        headers,
      },
      (response) => {
        let body = '';

        response.setEncoding('utf8');
        response.on('data', (chunk) => {
          body += chunk;
        });
        response.on('end', () => {
          const statusCode = response.statusCode ?? 0;
          if ([301, 302, 303, 307, 308].includes(statusCode)) {
            const location = response.headers.location;
            if (!location) {
              reject(new Error(`Jira issue fetch failed: ${statusCode} redirect without location header`));
              return;
            }

            const redirectedUrl = new URL(location, url);
            fetchJson<T>({ url: redirectedUrl, headers, redirectCount: redirectCount + 1 }).then(resolve).catch(reject);
            return;
          }

          if (statusCode < 200 || statusCode >= 300) {
            reject(new JiraHttpError(`Jira issue fetch failed: ${statusCode} ${response.statusMessage || ''} ${body}`.trim(), statusCode));
            return;
          }

          try {
            resolve(JSON.parse(body) as T);
          } catch (error) {
            reject(new Error(`Failed to parse Jira response JSON: ${error instanceof Error ? error.message : String(error)}`));
          }
        });
      },
    );

    req.on('error', (error) => {
      reject(error);
    });

    req.end();
  });
};

const fetchJiraWithAuth = async <T>({ url, token, email, jiraAuthType }: { url: URL } & JiraAuthInput): Promise<T> => {
  const baseHeaders = {
    Accept: 'application/json',
  };

  if (jiraAuthType === 'bearer') {
    return fetchJson<T>({
      url,
      headers: {
        ...baseHeaders,
        Authorization: getBearerAuthHeader(token),
      },
    });
  }

  if (jiraAuthType === 'basic') {
    if (!email) {
      throw new Error('jiraAuthType is basic but jiraEmail is not set. Set JIRA_EMAIL in .env or pass jiraEmail to the tool call.');
    }

    return fetchJson<T>({
      url,
      headers: {
        ...baseHeaders,
        Authorization: getBasicAuthHeader(email, token),
      },
    });
  }

  try {
    return await fetchJson<T>({
      url,
      headers: {
        ...baseHeaders,
        Authorization: getBearerAuthHeader(token),
      },
    });
  } catch (error) {
    if (!(error instanceof JiraHttpError) || error.statusCode !== 401 || !email) {
      throw error;
    }
  }

  return fetchJson<T>({
    url,
    headers: {
      ...baseHeaders,
      Authorization: getBasicAuthHeader(email, token),
    },
  });
};

export const getJiraIssue = async ({ baseUrl, issueKey, token, email, jiraAuthType }: GetJiraIssueInput): Promise<JiraIssue> => {
  const url = new URL(`${normalizeBaseUrl(baseUrl)}/rest/api/2/issue/${encodeURIComponent(issueKey)}?expand=renderedFields`);
  return fetchJiraWithAuth<JiraIssue>({ url, token, email, jiraAuthType });
};

export const getCurrentJiraUser = async ({
  baseUrl,
  token,
  email,
  jiraAuthType,
}: {
  baseUrl: string;
} & JiraAuthInput): Promise<JiraUser> => {
  const url = new URL(`${normalizeBaseUrl(baseUrl)}/rest/api/2/myself`);
  return fetchJiraWithAuth<JiraUser>({ url, token, email, jiraAuthType });
};

export const searchJiraIssues = async ({
  baseUrl,
  token,
  email,
  jiraAuthType,
  jql,
  fields,
  startAt,
  maxResults,
}: {
  baseUrl: string;
  jql: string;
  fields?: string[];
} & JiraAuthInput & JiraPaginatedInput): Promise<JiraSearchResult> => {
  const url = new URL(`${normalizeBaseUrl(baseUrl)}/rest/api/2/search`);
  url.searchParams.set('jql', jql);
  url.searchParams.set('maxResults', String(maxResults ?? 100));
  url.searchParams.set('startAt', String(startAt ?? 0));

  if (fields && fields.length > 0) {
    url.searchParams.set('fields', fields.join(','));
  }

  return fetchJiraWithAuth<JiraSearchResult>({ url, token, email, jiraAuthType });
};

export const getJiraIssueWorklogs = async ({
  baseUrl,
  token,
  email,
  jiraAuthType,
  issueKey,
  startAt,
  maxResults,
}: {
  baseUrl: string;
  issueKey: string;
} & JiraAuthInput & JiraPaginatedInput): Promise<JiraIssueWorklogPage> => {
  const url = new URL(`${normalizeBaseUrl(baseUrl)}/rest/api/2/issue/${encodeURIComponent(issueKey)}/worklog`);
  url.searchParams.set('maxResults', String(maxResults ?? 100));
  url.searchParams.set('startAt', String(startAt ?? 0));

  return fetchJiraWithAuth<JiraIssueWorklogPage>({ url, token, email, jiraAuthType });
};
