import { join, resolve } from 'node:path';
import { config as dotenvConfig } from 'dotenv';
import env from 'env-var';
import type { Config } from '../types/index.js';

let configCache: Config | undefined;

export const getProjectRoot = (): string => {
  const projectRoot = process.env.PROJECT_ROOT;
  if (!projectRoot) {
    throw new Error('PROJECT_ROOT env var is not set');
  }
  return resolve(projectRoot);
};

const loadEnvFile = (projectRoot: string): void => {
  dotenvConfig({ path: join(projectRoot, '.env.local') });
};

export const getConfig = (): Config => {
  if (configCache) {
    return configCache;
  }

  loadEnvFile(getProjectRoot());

  configCache = {
    jiraBaseUrl: env.get('AGENT_CODEREVIEW_JIRA_URL').required().asString(),
    jiraApiToken: env.get('AGENT_CODEREVIEW_JIRA_TOKEN').required().asString(),
    jiraEmail: env.get('AGENT_CODEREVIEW_JIRA_EMAIL').default('').asString(),
    openaiApiKey: env.get('OPENAI_API_KEY').required().asString(),
    openaiModel: env.get('AGENT_CODEREVIEW_OPENAI_MODEL').default('gpt-5.4-nano').asString(),
  };

  return configCache;
};
