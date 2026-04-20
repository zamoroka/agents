import { access, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { config as dotenvConfig } from 'dotenv';
import type { Config, JiraAuthType } from '../types/index.js';

let configCache: Config | undefined;
const envFilePath = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '.env');

const envPlaceholder = `# Jira MCP configuration\n# Fill these values with your Jira credentials and instance URL.\nJIRA_URL=\nJIRA_TOKEN=\nJIRA_EMAIL=\nJIRA_AUTH_TYPE=auto\nOPENAI_API_KEY=\nJIRA_SUMMARY_OPENAI_MODEL=gpt-5.4-nano\n`;

const ensureEnvFile = async (): Promise<void> => {
  try {
    await access(envFilePath);
  } catch {
    await writeFile(envFilePath, envPlaceholder, 'utf8');
  }
};

const loadEnvFile = (): void => {
  dotenvConfig({ path: envFilePath });
};

type ConfigOverrides = {
  jiraBaseUrl?: string;
  jiraApiToken?: string;
  jiraEmail?: string;
  jiraAuthType?: JiraAuthType;
  openaiApiKey?: string;
  openaiModel?: string;
};

const parseJiraAuthType = (value: string): JiraAuthType => {
  if (!value) {
    return 'auto';
  }

  const normalized = value.toLowerCase();
  if (normalized === 'auto' || normalized === 'bearer' || normalized === 'basic') {
    return normalized;
  }

  throw new Error('Invalid JIRA_AUTH_TYPE. Expected one of: auto, bearer, basic.');
};

const readConfigFromEnv = (): Config => {
  if (!configCache) {
    loadEnvFile();

    configCache = {
      jiraBaseUrl: process.env.JIRA_URL || '',
      jiraApiToken: process.env.JIRA_TOKEN || '',
      jiraEmail: process.env.JIRA_EMAIL || '',
      jiraAuthType: parseJiraAuthType(process.env.JIRA_AUTH_TYPE || ''),
      openaiApiKey: process.env.OPENAI_API_KEY || '',
      openaiModel: process.env.JIRA_SUMMARY_OPENAI_MODEL || 'gpt-5.4-nano',
    };
  }

  return configCache;
};

export const getConfig = async (overrides?: ConfigOverrides): Promise<Config> => {
  await ensureEnvFile();

  const envConfig = readConfigFromEnv();

  const mergedConfig = {
    jiraBaseUrl: overrides?.jiraBaseUrl || envConfig.jiraBaseUrl,
    jiraApiToken: overrides?.jiraApiToken || envConfig.jiraApiToken,
    jiraEmail: overrides?.jiraEmail ?? envConfig.jiraEmail,
    jiraAuthType: overrides?.jiraAuthType || envConfig.jiraAuthType,
    openaiApiKey: overrides?.openaiApiKey || envConfig.openaiApiKey,
    openaiModel: overrides?.openaiModel || envConfig.openaiModel,
  };

  if (!mergedConfig.jiraBaseUrl) {
    throw new Error('Missing Jira base URL. Set JIRA_URL in .env or pass jiraBaseUrl to the tool call.');
  }

  if (!mergedConfig.jiraApiToken) {
    throw new Error('Missing Jira API token. Set JIRA_TOKEN in .env or pass jiraApiToken to the tool call.');
  }

  return mergedConfig;
};
