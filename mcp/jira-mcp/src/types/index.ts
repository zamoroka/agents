export type JiraAuthType = 'auto' | 'bearer' | 'basic';

export type Config = {
  jiraBaseUrl: string;
  jiraApiToken: string;
  jiraEmail: string;
  jiraAuthType: JiraAuthType;
  openaiApiKey: string;
  openaiModel: string;
};

export type JiraIssue = {
  key?: string;
  id?: string;
  self?: string;
  renderedFields?: {
    description?: string;
  };
  fields?: {
    summary?: string;
    description?: string;
    created?: string;
    updated?: string;
    labels?: string[];
    status?: { name?: string };
    priority?: { name?: string };
    issuetype?: { name?: string };
    assignee?: { displayName?: string };
    reporter?: { displayName?: string };
    components?: Array<{ name?: string }>;
    fixVersions?: Array<{ name?: string }>;
    comment?: {
      startAt?: number;
      maxResults?: number;
      total?: number;
      comments?: JiraIssueComment[];
    };
    attachment?: Array<{
      filename?: string;
      mimeType?: string;
      size?: number;
      created?: string;
      content?: string;
    }>;
  };
};

export type JiraIssueComment = {
  id?: string;
  author?: { displayName?: string };
  created?: string;
  body?: string;
  renderedBody?: string;
};

export type JiraUser = {
  accountId?: string;
  displayName?: string;
  emailAddress?: string;
};

export type JiraWorklog = {
  id?: string;
  started?: string;
  timeSpentSeconds?: number;
  comment?: unknown;
  author?: JiraUser;
};

export type JiraIssueSearchItem = {
  id?: string;
  key?: string;
  fields?: {
    summary?: string;
    project?: {
      key?: string;
      name?: string;
    };
  };
};

export type JiraSearchResult = {
  startAt?: number;
  maxResults?: number;
  total?: number;
  issues?: JiraIssueSearchItem[];
};

export type JiraIssueWorklogPage = {
  startAt?: number;
  maxResults?: number;
  total?: number;
  worklogs?: JiraWorklog[];
};

export type JiraIssueCommentPage = {
  startAt?: number;
  maxResults?: number;
  total?: number;
  comments?: JiraIssueComment[];
};
