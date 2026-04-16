import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { getConfig, logger } from '../common/index.js';
import { getJiraIssue } from './jiraApiClient.js';
import { summarizeJiraIssue } from './summarizeJiraIssue.js';

const buildArtifactContent = ({ prNumber, issueKey, summary }: { prNumber: string; issueKey: string; summary: string }): string =>
  [`# PR ${prNumber} issue summary`, '', `Jira ticket: ${issueKey}`, '', summary, ''].join('\n');

export const processIssueSummary = async ({
  prNumber,
  issueKey,
  projectRoot,
}: {
  prNumber: string;
  issueKey: string;
  projectRoot: string;
}): Promise<{ issueKey: string; outputPath: string }> => {
  const config = getConfig();

  logger.info('Fetching Jira ticket', { issueKey });
  const jiraIssue = await getJiraIssue({
    baseUrl: config.jiraBaseUrl,
    issueKey,
    token: config.jiraApiToken,
    email: config.jiraEmail,
  });

  logger.info('Generating Jira ticket summary with OpenAI', { model: config.openaiModel });
  const summary = await summarizeJiraIssue({
    jiraIssue,
    openaiApiKey: config.openaiApiKey,
    openaiModel: config.openaiModel,
  });

  const artifactsDir = join(projectRoot, '.agents', 'artifacts');
  const outputPath = join(artifactsDir, `pr-${prNumber}-issue-summary.md`);
  const output = buildArtifactContent({ prNumber, issueKey, summary });

  try {
    await writeFile(outputPath, output, 'utf8');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
      throw error;
    }

    await mkdir(artifactsDir, { recursive: true });
    await writeFile(outputPath, output, 'utf8');
  }

  logger.info('Saved issue summary artifact', { outputPath });

  return { issueKey, outputPath };
};
