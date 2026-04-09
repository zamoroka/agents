import type { DiffStatResponse, PullRequest, PullRequestCommentsResponse } from '../types/index.js';

const API_BASE = 'https://api.bitbucket.org/2.0';

const getRepoUrl = (workspace: string, repo: string): string => `${API_BASE}/repositories/${workspace}/${repo}`;

const buildHeaders = (email: string, token: string): HeadersInit => ({
  Authorization: `Basic ${Buffer.from(`${email}:${token}`).toString('base64')}`,
  Accept: 'application/json',
});

type ApiInput = {
  workspace: string;
  repo: string;
  email: string;
  token: string;
};

export const getPullRequest = async ({ workspace, repo, email, token, prNumber }: ApiInput & { prNumber: string }): Promise<PullRequest> => {
  const response = await fetch(`${getRepoUrl(workspace, repo)}/pullrequests/${prNumber}`, {
    headers: buildHeaders(email, token),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Bitbucket PR fetch failed: ${response.status} ${response.statusText} ${body}`);
  }

  return (await response.json()) as PullRequest;
};

export const getDiffStat = async ({ url, email, token }: { url: string; email: string; token: string }): Promise<DiffStatResponse> => {
  const response = await fetch(url, {
    headers: buildHeaders(email, token),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Bitbucket diffstat fetch failed: ${response.status} ${response.statusText} ${body}`);
  }

  return (await response.json()) as DiffStatResponse;
};

export const getDiff = async ({ url, email, token }: { url: string; email: string; token: string }): Promise<string> => {
  const response = await fetch(url, {
    headers: {
      Authorization: `Basic ${Buffer.from(`${email}:${token}`).toString('base64')}`,
      Accept: 'text/plain',
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Bitbucket diff fetch failed: ${response.status} ${response.statusText} ${body}`);
  }

  return response.text();
};

export const getPullRequestComments = async ({ workspace, repo, prNumber, email, token }: ApiInput & { prNumber: string }): Promise<PullRequestCommentsResponse['values']> => {
  const allComments: PullRequestCommentsResponse['values'] = [];
  let nextUrl: string | undefined = `${getRepoUrl(workspace, repo)}/pullrequests/${prNumber}/comments?pagelen=100`;

  while (nextUrl) {
    const response = await fetch(nextUrl, {
      headers: buildHeaders(email, token),
    });

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`Bitbucket comments fetch failed: ${response.status} ${response.statusText} ${body}`);
    }

    const payload = (await response.json()) as PullRequestCommentsResponse;
    if (payload.values?.length) {
      allComments.push(...payload.values);
    }

    nextUrl = payload.next;
  }

  return allComments;
};
