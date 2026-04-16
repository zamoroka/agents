export type Config = {
  bitbucketEmail: string;
  bitbucketToken: string;
};

export type ParsedPrUrl = {
  provider: 'bitbucket' | 'github';
  workspace?: string;
  repo?: string;
  prNumber: string;
  originalUrl: string;
};

export type PullRequest = {
  title?: string;
  description?: string;
  state?: string;
  created_on?: string;
  updated_on?: string;
  author?: {
    display_name?: string;
  };
  source?: {
    branch?: {
      name?: string;
    };
  };
  destination?: {
    branch?: {
      name?: string;
    };
  };
  links?: {
    diff?: { href?: string };
    diffstat?: { href?: string };
  };
};

export type PullRequestComment = {
  user?: {
    display_name?: string;
  };
  content?: {
    raw?: string;
  };
  created_on?: string;
  updated_on?: string;
  deleted?: boolean;
  inline?: {
    path?: string;
    to?: number;
    from?: number;
  };
};

export type PullRequestCommentsResponse = {
  values?: PullRequestComment[];
  next?: string;
};

export type DiffStatResponse = {
  values?: Array<{
    status?: string;
    lines_added?: number;
    lines_removed?: number;
    old?: { path?: string };
    new?: { path?: string };
  }>;
};
