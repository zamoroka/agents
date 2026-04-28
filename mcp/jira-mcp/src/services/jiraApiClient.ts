import { request as httpRequest } from 'node:http';
import { request as httpsRequest } from 'node:https';
import type {
  JiraAuthType,
  JiraIssue,
  JiraIssueComment,
  JiraIssueCommentPage,
  JiraIssueWorklogPage,
  JiraSearchResult,
  JiraUser,
  JiraWorklog,
} from '../types/index.js';

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

const requestJson = async <T>({
  url,
  method,
  headers,
  body,
  redirectCount = 0,
}: {
  url: URL;
  method: 'GET' | 'POST';
  headers: Record<string, string>;
  body?: unknown;
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
        method,
        headers,
      },
      (response) => {
        let responseBody = '';

        response.setEncoding('utf8');
        response.on('data', (chunk) => {
          responseBody += chunk;
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
            requestJson<T>({ url: redirectedUrl, method, headers, body, redirectCount: redirectCount + 1 }).then(resolve).catch(reject);
            return;
          }

          if (statusCode < 200 || statusCode >= 300) {
            reject(new JiraHttpError(`Jira issue fetch failed: ${statusCode} ${response.statusMessage || ''} ${responseBody}`.trim(), statusCode));
            return;
          }

          try {
            resolve(JSON.parse(responseBody) as T);
          } catch (error) {
            reject(new Error(`Failed to parse Jira response JSON: ${error instanceof Error ? error.message : String(error)}`));
          }
        });
      },
    );

    req.on('error', (error) => {
      reject(error);
    });

    if (method === 'POST' && body !== undefined) {
      req.write(JSON.stringify(body));
    }

    req.end();
  });
};

const fetchJson = async <T>({
  url,
  headers,
  redirectCount = 0,
}: {
  url: URL;
  headers: Record<string, string>;
  redirectCount?: number;
}): Promise<T> => requestJson<T>({ url, method: 'GET', headers, redirectCount });

const postJson = async <T>({
  url,
  headers,
  body,
  redirectCount = 0,
}: {
  url: URL;
  headers: Record<string, string>;
  body: unknown;
  redirectCount?: number;
}): Promise<T> => requestJson<T>({ url, method: 'POST', headers, body, redirectCount });

const fetchJiraWithAuth = async <T>({
  url,
  token,
  email,
  jiraAuthType,
  method = 'GET',
  body,
}: {
  url: URL;
  method?: 'GET' | 'POST';
  body?: unknown;
} & JiraAuthInput): Promise<T> => {
  const baseHeaders = {
    Accept: 'application/json',
    ...(method === 'POST' ? { 'Content-Type': 'application/json' } : {}),
  };

  const requestWithAuth = (authHeader: string): Promise<T> => {
    if (method === 'POST') {
      return postJson<T>({
        url,
        body,
        headers: {
          ...baseHeaders,
          Authorization: authHeader,
        },
      });
    }

    return fetchJson<T>({
      url,
      headers: {
        ...baseHeaders,
        Authorization: authHeader,
      },
    });
  };

  if (jiraAuthType === 'bearer') {
    return requestWithAuth(getBearerAuthHeader(token));
  }

  if (jiraAuthType === 'basic') {
    if (!email) {
      throw new Error('jiraAuthType is basic but jiraEmail is not set. Set JIRA_EMAIL in .env or pass jiraEmail to the tool call.');
    }

    return requestWithAuth(getBasicAuthHeader(email, token));
  }

  try {
    return await requestWithAuth(getBearerAuthHeader(token));
  } catch (error) {
    if (!(error instanceof JiraHttpError) || error.statusCode !== 401 || !email) {
      throw error;
    }
  }

  return requestWithAuth(getBasicAuthHeader(email, token));
};

export const getJiraIssue = async ({ baseUrl, issueKey, token, email, jiraAuthType }: GetJiraIssueInput): Promise<JiraIssue> => {
  const url = new URL(`${normalizeBaseUrl(baseUrl)}/rest/api/2/issue/${encodeURIComponent(issueKey)}?expand=renderedFields`);
  const issue = await fetchJiraWithAuth<JiraIssue>({ url, token, email, jiraAuthType });
  const comments = await getAllJiraIssueComments({ baseUrl, issueKey, token, email, jiraAuthType });

  issue.fields = issue.fields || {};
  issue.fields.comment = {
    startAt: 0,
    maxResults: comments.length,
    total: comments.length,
    comments,
  };

  return issue;
};

const getJiraIssueCommentsPage = async ({
  baseUrl,
  issueKey,
  token,
  email,
  jiraAuthType,
  startAt,
  maxResults,
}: {
  baseUrl: string;
  issueKey: string;
} & JiraAuthInput & JiraPaginatedInput): Promise<JiraIssueCommentPage> => {
  const url = new URL(`${normalizeBaseUrl(baseUrl)}/rest/api/2/issue/${encodeURIComponent(issueKey)}/comment`);
  url.searchParams.set('maxResults', String(maxResults ?? 100));
  url.searchParams.set('startAt', String(startAt ?? 0));

  return fetchJiraWithAuth<JiraIssueCommentPage>({ url, token, email, jiraAuthType });
};

const getAllJiraIssueComments = async ({
  baseUrl,
  issueKey,
  token,
  email,
  jiraAuthType,
}: {
  baseUrl: string;
  issueKey: string;
} & JiraAuthInput): Promise<JiraIssueComment[]> => {
  const maxResults = 100;
  const comments: JiraIssueComment[] = [];
  let startAt = 0;

  while (true) {
    const page = await getJiraIssueCommentsPage({
      baseUrl,
      issueKey,
      token,
      email,
      jiraAuthType,
      startAt,
      maxResults,
    });

    const pageComments = page.comments || [];
    comments.push(...pageComments);

    const total = page.total ?? comments.length;
    startAt += pageComments.length;

    if (pageComments.length === 0 || startAt >= total) {
      break;
    }
  }

  return comments;
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

export const addJiraIssueWorklog = async ({
  baseUrl,
  token,
  email,
  jiraAuthType,
  issueKey,
  timeSpent,
  timeSpentSeconds,
  comment,
  started,
}: {
  baseUrl: string;
  issueKey: string;
  timeSpent?: string;
  timeSpentSeconds?: number;
  comment?: string;
  started?: string;
} & JiraAuthInput): Promise<JiraWorklog> => {
  const url = new URL(`${normalizeBaseUrl(baseUrl)}/rest/api/2/issue/${encodeURIComponent(issueKey)}/worklog`);
  const payload: Record<string, unknown> = {};

  if (typeof timeSpent === 'string' && timeSpent.trim()) {
    payload.timeSpent = timeSpent.trim();
  }

  if (typeof timeSpentSeconds === 'number' && Number.isFinite(timeSpentSeconds) && timeSpentSeconds > 0) {
    payload.timeSpentSeconds = Math.floor(timeSpentSeconds);
  }

  if (typeof comment === 'string' && comment.trim()) {
    payload.comment = comment.trim();
  }

  if (typeof started === 'string' && started.trim()) {
    payload.started = started.trim();
  }

  return fetchJiraWithAuth<JiraWorklog>({
    url,
    token,
    email,
    jiraAuthType,
    method: 'POST',
    body: payload,
  });
};
