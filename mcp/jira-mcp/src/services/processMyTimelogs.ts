import type { JiraAuthType, JiraIssueSearchItem, JiraUser, JiraWorklog } from '../types/index.js';
import { getCurrentJiraUser, getJiraIssueWorklogs, searchJiraIssues } from './jiraApiClient.js';

const DAY_IN_MS = 24 * 60 * 60 * 1000;

const formatDuration = (totalSeconds: number): string => {
  if (totalSeconds <= 0) {
    return '0m';
  }

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);

  if (hours === 0) {
    return `${minutes}m`;
  }

  if (minutes === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${minutes}m`;
};

const extractTextFromAdfNode = (value: unknown): string => {
  if (typeof value === 'string') {
    return value;
  }

  if (!value || typeof value !== 'object') {
    return '';
  }

  const node = value as {
    text?: unknown;
    content?: unknown;
  };

  const text = typeof node.text === 'string' ? node.text : '';
  const content = Array.isArray(node.content)
    ? node.content
        .map((item) => extractTextFromAdfNode(item))
        .filter(Boolean)
        .join(' ')
    : '';

  return `${text} ${content}`.trim();
};

const getCommentText = (comment: unknown): string => {
  if (!comment) {
    return '';
  }

  if (typeof comment === 'string') {
    return comment.trim();
  }

  return extractTextFromAdfNode(comment).replace(/\s+/g, ' ').trim();
};

const isSameUser = (user: JiraUser, author: JiraUser | undefined): boolean => {
  if (!author) {
    return false;
  }

  if (user.accountId && author.accountId) {
    return user.accountId === author.accountId;
  }

  if (user.emailAddress && author.emailAddress) {
    return user.emailAddress.toLowerCase() === author.emailAddress.toLowerCase();
  }

  if (user.displayName && author.displayName) {
    return user.displayName.toLowerCase() === author.displayName.toLowerCase();
  }

  return false;
};

type TimelogEntry = {
  started: string;
  date: string;
  projectKey: string;
  projectName: string;
  issueKey: string;
  issueSummary: string;
  timeSpentSeconds: number;
  timeSpent: string;
  workDescription: string;
};

type TimelogIssueSummary = {
  issueKey: string;
  issueSummary: string;
  totalTimeSeconds: number;
  totalTime: string;
  entries: TimelogEntry[];
};

type TimelogProjectSummary = {
  projectKey: string;
  projectName: string;
  totalTimeSeconds: number;
  totalTime: string;
  issues: TimelogIssueSummary[];
};

export type TimelogReport = {
  period: {
    days: number;
    from: string;
    to: string;
  };
  author: {
    accountId: string;
    displayName: string;
    emailAddress: string;
  };
  totalTimeSeconds: number;
  totalTime: string;
  entriesCount: number;
  projects: TimelogProjectSummary[];
  details: TimelogEntry[];
  markdownSummary: string;
};

const buildMarkdownSummary = (report: Omit<TimelogReport, 'markdownSummary'>): string => {
  const lines: string[] = [];

  lines.push('# Jira timelog summary');
  lines.push('');
  lines.push(`- Period: ${report.period.from} to ${report.period.to} (${report.period.days} days)`);
  lines.push(`- User: ${report.author.displayName || 'Unknown user'}`);
  lines.push(`- Total logged: ${report.totalTime} across ${report.projects.length} project(s) and ${report.entriesCount} worklog entr${report.entriesCount === 1 ? 'y' : 'ies'}`);
  lines.push('');

  if (report.projects.length === 0) {
    lines.push('No timelogs found for the selected period.');
    return lines.join('\n');
  }

  lines.push('## Projects');
  lines.push('');

  for (const project of report.projects) {
    lines.push(`### ${project.projectKey} - ${project.projectName} (${project.totalTime})`);
    for (const issue of project.issues) {
      lines.push(`- ${issue.issueKey} (${issue.totalTime}): ${issue.issueSummary}`);
    }
    lines.push('');
  }

  lines.push('## Detailed work');
  lines.push('');

  for (const item of report.details) {
    lines.push(`- ${item.date} | ${item.projectKey} | ${item.issueKey} | ${item.timeSpent} | ${item.workDescription}`);
  }

  return lines.join('\n').trim();
};

const getAllCandidateIssues = async ({
  jiraBaseUrl,
  jiraApiToken,
  jiraEmail,
  jiraAuthType,
  days,
}: {
  jiraBaseUrl: string;
  jiraApiToken: string;
  jiraEmail: string;
  jiraAuthType: JiraAuthType;
  days: number;
}): Promise<JiraIssueSearchItem[]> => {
  const jql = `worklogAuthor = currentUser() AND worklogDate >= -${days}d ORDER BY updated DESC`;
  const issues: JiraIssueSearchItem[] = [];
  let startAt = 0;

  while (true) {
    const page = await searchJiraIssues({
      baseUrl: jiraBaseUrl,
      token: jiraApiToken,
      email: jiraEmail,
      jiraAuthType,
      jql,
      fields: ['summary', 'project'],
      maxResults: 100,
      startAt,
    });

    const pageIssues = page.issues || [];
    issues.push(...pageIssues);

    const pageSize = page.maxResults && page.maxResults > 0 ? page.maxResults : pageIssues.length;
    const nextStartAt = startAt + pageSize;
    const total = page.total || issues.length;

    if (pageIssues.length === 0 || nextStartAt >= total || pageSize === 0) {
      break;
    }

    startAt = nextStartAt;
  }

  return issues;
};

const getIssueWorklogs = async ({
  jiraBaseUrl,
  jiraApiToken,
  jiraEmail,
  jiraAuthType,
  issueKey,
}: {
  jiraBaseUrl: string;
  jiraApiToken: string;
  jiraEmail: string;
  jiraAuthType: JiraAuthType;
  issueKey: string;
}): Promise<JiraWorklog[]> => {
  const worklogs: JiraWorklog[] = [];
  let startAt = 0;

  while (true) {
    const page = await getJiraIssueWorklogs({
      baseUrl: jiraBaseUrl,
      token: jiraApiToken,
      email: jiraEmail,
      jiraAuthType,
      issueKey,
      maxResults: 100,
      startAt,
    });

    const pageWorklogs = page.worklogs || [];
    worklogs.push(...pageWorklogs);

    const pageSize = page.maxResults && page.maxResults > 0 ? page.maxResults : pageWorklogs.length;
    const nextStartAt = startAt + pageSize;
    const total = page.total || worklogs.length;

    if (pageWorklogs.length === 0 || nextStartAt >= total || pageSize === 0) {
      break;
    }

    startAt = nextStartAt;
  }

  return worklogs;
};

type ProcessMyTimelogsInput = {
  jiraBaseUrl: string;
  jiraApiToken: string;
  jiraEmail: string;
  jiraAuthType: JiraAuthType;
  days: number;
};

export const processMyTimelogs = async ({
  jiraBaseUrl,
  jiraApiToken,
  jiraEmail,
  jiraAuthType,
  days,
}: ProcessMyTimelogsInput): Promise<TimelogReport> => {
  const now = new Date();
  const periodStart = new Date(now.getTime() - days * DAY_IN_MS);
  const me = await getCurrentJiraUser({
    baseUrl: jiraBaseUrl,
    token: jiraApiToken,
    email: jiraEmail,
    jiraAuthType,
  });

  const candidateIssues = await getAllCandidateIssues({
    jiraBaseUrl,
    jiraApiToken,
    jiraEmail,
    jiraAuthType,
    days,
  });

  const details: TimelogEntry[] = [];

  for (const issue of candidateIssues) {
    if (!issue.key) {
      continue;
    }

    const issueKey = issue.key;
    const issueSummary = issue.fields?.summary || 'No issue summary';
    const projectKey = issue.fields?.project?.key || 'UNKNOWN';
    const projectName = issue.fields?.project?.name || 'Unknown project';

    const issueWorklogs = await getIssueWorklogs({
      jiraBaseUrl,
      jiraApiToken,
      jiraEmail,
      jiraAuthType,
      issueKey,
    });

    for (const worklog of issueWorklogs) {
      const started = worklog.started;
      const timeSpentSeconds = worklog.timeSpentSeconds || 0;

      if (!started || timeSpentSeconds <= 0) {
        continue;
      }

      const startedAt = new Date(started);
      if (Number.isNaN(startedAt.getTime()) || startedAt < periodStart || startedAt > now) {
        continue;
      }

      if (!isSameUser(me, worklog.author)) {
        continue;
      }

      const commentText = getCommentText(worklog.comment);

      details.push({
        started,
        date: started.slice(0, 10),
        projectKey,
        projectName,
        issueKey,
        issueSummary,
        timeSpentSeconds,
        timeSpent: formatDuration(timeSpentSeconds),
        workDescription: commentText || issueSummary,
      });
    }
  }

  details.sort((a, b) => new Date(b.started).getTime() - new Date(a.started).getTime());

  const projectsMap = new Map<string, TimelogProjectSummary>();
  let totalTimeSeconds = 0;

  for (const detail of details) {
    totalTimeSeconds += detail.timeSpentSeconds;

    const projectId = `${detail.projectKey}::${detail.projectName}`;
    const existingProject = projectsMap.get(projectId);
    const project =
      existingProject ||
      {
        projectKey: detail.projectKey,
        projectName: detail.projectName,
        totalTimeSeconds: 0,
        totalTime: '0m',
        issues: [],
      };

    project.totalTimeSeconds += detail.timeSpentSeconds;

    let issue = project.issues.find((item) => item.issueKey === detail.issueKey);
    if (!issue) {
      issue = {
        issueKey: detail.issueKey,
        issueSummary: detail.issueSummary,
        totalTimeSeconds: 0,
        totalTime: '0m',
        entries: [],
      };
      project.issues.push(issue);
    }

    issue.totalTimeSeconds += detail.timeSpentSeconds;
    issue.entries.push(detail);
    projectsMap.set(projectId, project);
  }

  const projects = [...projectsMap.values()]
    .map((project) => ({
      ...project,
      totalTime: formatDuration(project.totalTimeSeconds),
      issues: project.issues
        .map((issue) => ({
          ...issue,
          totalTime: formatDuration(issue.totalTimeSeconds),
          entries: issue.entries.sort((a, b) => new Date(b.started).getTime() - new Date(a.started).getTime()),
        }))
        .sort((a, b) => b.totalTimeSeconds - a.totalTimeSeconds),
    }))
    .sort((a, b) => b.totalTimeSeconds - a.totalTimeSeconds);

  const reportWithoutMarkdown: Omit<TimelogReport, 'markdownSummary'> = {
    period: {
      days,
      from: periodStart.toISOString().slice(0, 10),
      to: now.toISOString().slice(0, 10),
    },
    author: {
      accountId: me.accountId || '',
      displayName: me.displayName || 'Unknown user',
      emailAddress: me.emailAddress || '',
    },
    totalTimeSeconds,
    totalTime: formatDuration(totalTimeSeconds),
    entriesCount: details.length,
    projects,
    details,
  };

  return {
    ...reportWithoutMarkdown,
    markdownSummary: buildMarkdownSummary(reportWithoutMarkdown),
  };
};
