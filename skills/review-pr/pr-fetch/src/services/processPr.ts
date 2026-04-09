import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { getConfig } from '../common/index.js';
import { getProjectRoot } from '../common/index.js';
import type { ParsedPrUrl } from '../types/index.js';
import { getDiff, getDiffStat, getPullRequest, getPullRequestComments } from './bitbucketApiClient.js';

const line = '==========================================';

const parsePrUrl = (provider: string, prUrl: string): ParsedPrUrl => {
  if (provider === 'github') {
    const githubMatch = prUrl.match(/^https?:\/\/github\.com\/[^/]+\/[^/]+\/pull\/(\d+)(?:\/.*)?$/i);
    if (!githubMatch) {
      throw new Error('Invalid GitHub PR URL. Expected format: https://github.com/<owner>/<repo>/pull/<number>');
    }

    return { provider: 'github', prNumber: githubMatch[1], originalUrl: prUrl };
  }

  if (provider !== 'bitbucket') {
    throw new Error(`Unsupported provider '${provider}'. Use 'bitbucket' or 'github'.`);
  }

  const bitbucketMatch = prUrl.match(/^https?:\/\/bitbucket\.org\/([^/]+)\/([^/]+)\/pull-requests\/(\d+)(?:\/.*)?$/i);
  if (!bitbucketMatch) {
    throw new Error('Invalid Bitbucket PR URL. Expected format: https://bitbucket.org/<workspace>/<repo>/pull-requests/<number>');
  }

  return {
    provider: 'bitbucket',
    workspace: bitbucketMatch[1],
    repo: bitbucketMatch[2],
    prNumber: bitbucketMatch[3],
    originalUrl: prUrl,
  };
};

const printPrDetails = (pr: Awaited<ReturnType<typeof getPullRequest>>, parsed: ParsedPrUrl): void => {
  process.stdout.write('--- PR DETAILS ---\n');
  process.stdout.write(`URL: ${parsed.originalUrl}\n`);
  process.stdout.write(`Provider: ${parsed.provider}\n`);
  process.stdout.write(`Title: ${pr.title || ''}\n`);
  process.stdout.write(`Author: ${pr.author?.display_name || ''}\n`);
  process.stdout.write(`State: ${pr.state || ''}\n`);
  process.stdout.write(`Source: ${pr.source?.branch?.name || ''}\n`);
  process.stdout.write(`Destination: ${pr.destination?.branch?.name || ''}\n`);
  process.stdout.write(`Created: ${pr.created_on || ''}\n`);
  process.stdout.write(`Updated: ${pr.updated_on || ''}\n\n`);
  process.stdout.write('Description:\n');
  process.stdout.write(`${pr.description || ''}\n`);
};

const printDiffStat = (diffStat: Awaited<ReturnType<typeof getDiffStat>>): void => {
  process.stdout.write('\n--- FILES CHANGED ---\n');
  for (const file of diffStat.values || []) {
    const status = file.status || 'modified';
    const added = file.lines_added ?? 0;
    const removed = file.lines_removed ?? 0;
    const path = file.old?.path || file.new?.path || 'unknown';
    process.stdout.write(`  ${status} | ${added} + | ${removed} - | ${path}\n`);
  }
};

const printComments = (comments: Awaited<ReturnType<typeof getPullRequestComments>>): void => {
  process.stdout.write('\n--- PR COMMENTS ---\n');
  if (!comments?.length) {
    process.stdout.write('No comments found.\n');
    return;
  }

  for (const comment of comments) {
    if (comment.deleted) {
      continue;
    }

    const author = comment.user?.display_name || 'unknown';
    const created = comment.created_on || '';
    const inlinePath = comment.inline?.path ? ` [${comment.inline.path}:${comment.inline.to ?? comment.inline.from ?? 0}]` : '';
    process.stdout.write(`- ${author}${inlinePath} (${created})\n`);
    process.stdout.write(`  ${comment.content?.raw || ''}\n`);
  }
};

const toCommentLines = (label: string, value: string): string[] => {
  if (!value) {
    return [`# ${label}:`];
  }

  const lines = value.split(/\r?\n/);
  if (lines.length === 1) {
    return [`# ${label}: ${lines[0]}`];
  }

  return [`# ${label}:`, ...lines.map((line) => `#   ${line}`)];
};

const buildPatchHeader = (pr: Awaited<ReturnType<typeof getPullRequest>>, parsed: ParsedPrUrl): string => {
  const headerLines = [
    '# Bitbucket PR metadata',
    `# URL: ${parsed.originalUrl}`,
    `# Provider: ${parsed.provider}`,
    `# Workspace: ${parsed.workspace || ''}`,
    `# Repository: ${parsed.repo || ''}`,
    `# PR Number: ${parsed.prNumber}`,
    `# Title: ${pr.title || ''}`,
    `# Author: ${pr.author?.display_name || ''}`,
    `# State: ${pr.state || ''}`,
    `# Source Branch: ${pr.source?.branch?.name || ''}`,
    `# Destination Branch: ${pr.destination?.branch?.name || ''}`,
    `# Created: ${pr.created_on || ''}`,
    `# Updated: ${pr.updated_on || ''}`,
    ...toCommentLines('Description', pr.description || ''),
    '# End Bitbucket PR metadata',
    '',
  ];

  return `${headerLines.join('\n')}\n`;
};

export const processPr = async ({ provider, prUrl }: { provider: string; prUrl: string }): Promise<void> => {
  const config = getConfig();
  const projectRoot = getProjectRoot();
  const parsed = parsePrUrl(provider, prUrl);

  if (parsed.provider === 'github') {
    throw new Error('GitHub PR review is not supported yet.');
  }

  const workspace = parsed.workspace as string;
  const repo = parsed.repo as string;

  process.stdout.write(`${line}\n`);
  process.stdout.write(`Fetching PR #${parsed.prNumber} from ${workspace}/${repo}\n`);
  process.stdout.write(`${line}\n\n`);

  const pr = await getPullRequest({
    workspace,
    repo,
    prNumber: parsed.prNumber,
    email: config.bitbucketEmail,
    token: config.bitbucketToken,
  });

  printPrDetails(pr, parsed);

  const diffStatUrl = pr.links?.diffstat?.href;
  if (diffStatUrl) {
    const diffStat = await getDiffStat({
      url: diffStatUrl,
      email: config.bitbucketEmail,
      token: config.bitbucketToken,
    });
    printDiffStat(diffStat);
  }

  const comments = await getPullRequestComments({
    workspace,
    repo,
    prNumber: parsed.prNumber,
    email: config.bitbucketEmail,
    token: config.bitbucketToken,
  });
  printComments(comments);

  const diffUrl = pr.links?.diff?.href;
  let diffContent = '';
  if (diffUrl) {
    diffContent = await getDiff({
      url: diffUrl,
      email: config.bitbucketEmail,
      token: config.bitbucketToken,
    });
    process.stdout.write('\n--- DIFF ---\n');
    process.stdout.write(diffContent);
    if (!diffContent.endsWith('\n')) {
      process.stdout.write('\n');
    }
  }

  const artifactsDir = join(projectRoot, '.agents', 'artifacts');
  const diffArtifactPath = join(artifactsDir, `pr-${parsed.prNumber}-diff.patch`);
  const patchHeader = buildPatchHeader(pr, parsed);
  const patchContent = `${patchHeader}${diffContent}`;
  try {
    await writeFile(diffArtifactPath, patchContent, 'utf8');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
      throw error;
    }

    await mkdir(artifactsDir, { recursive: true });
    await writeFile(diffArtifactPath, patchContent, 'utf8');
  }
  process.stdout.write(`Saved diff artifact: ${diffArtifactPath}\n`);

  process.stdout.write(`\n${line}\n`);
  process.stdout.write(`PR #${parsed.prNumber} fetched successfully!\n`);
  process.stdout.write(`${line}\n`);
};
