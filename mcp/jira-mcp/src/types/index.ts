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
      comments?: Array<{
        author?: { displayName?: string };
        created?: string;
        body?: string;
        renderedBody?: string;
      }>;
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
