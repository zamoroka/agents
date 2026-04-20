import { request as httpRequest } from 'node:http';
import { request as httpsRequest } from 'node:https';
import type { JiraAuthType, JiraIssue } from '../types/index.js';

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

const fetchJson = async ({
  url,
  headers,
  redirectCount = 0,
}: {
  url: URL;
  headers: Record<string, string>;
  redirectCount?: number;
}): Promise<JiraIssue> => {
  if (redirectCount > 5) {
    throw new Error('Jira issue fetch failed: too many redirects');
  }

  const requestImpl = url.protocol === 'https:' ? httpsRequest : httpRequest;

  return new Promise<JiraIssue>((resolve, reject) => {
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
            fetchJson({ url: redirectedUrl, headers, redirectCount: redirectCount + 1 }).then(resolve).catch(reject);
            return;
          }

          if (statusCode < 200 || statusCode >= 300) {
            reject(new JiraHttpError(`Jira issue fetch failed: ${statusCode} ${response.statusMessage || ''} ${body}`.trim(), statusCode));
            return;
          }

          try {
            resolve(JSON.parse(body) as JiraIssue);
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

export const getJiraIssue = async ({ baseUrl, issueKey, token, email, jiraAuthType }: GetJiraIssueInput): Promise<JiraIssue> => {
  const url = new URL(`${normalizeBaseUrl(baseUrl)}/rest/api/2/issue/${encodeURIComponent(issueKey)}?expand=renderedFields`);
  const baseHeaders = {
    Accept: 'application/json',
  };

  if (jiraAuthType === 'bearer') {
    return fetchJson({
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

    return fetchJson({
      url,
      headers: {
        ...baseHeaders,
        Authorization: getBasicAuthHeader(email, token),
      },
    });
  }

  try {
    return await fetchJson({
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

  return fetchJson({
    url,
    headers: {
      ...baseHeaders,
      Authorization: getBasicAuthHeader(email, token),
    },
  });
};
