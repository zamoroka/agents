#!/usr/bin/env node

import { getProjectRoot, logger } from './common/index.js';
import { processIssueSummary } from './services/processIssueSummary.js';

const repoSlug = process.argv[2];
const prNumber = process.argv[3];
const issueKey = process.argv[4];

if (!repoSlug || !prNumber || !issueKey) {
  logger.error('Usage: PROJECT_ROOT=/path/to/project npm --workspace jira-fetch run fetch:jira -- <REPO_SLUG> <PR_NUMBER> <ISSUE_KEY>');
  process.exit(1);
}

try {
  const projectRoot = getProjectRoot();
  const result = await processIssueSummary({ repoSlug, prNumber, issueKey, projectRoot });
  logger.info('Jira summary completed', { repoSlug, prNumber, issueKey: result.issueKey, outputPath: result.outputPath });
} catch (error) {
  logger.error('Jira summary failed', { error: error instanceof Error ? error.message : String(error) });
  process.exit(1);
}
