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
    bitbucketEmail: env.get('AGENT_CODEREVIEW_BITBUCKET_EMAIL').required().asString(),
    bitbucketToken: env.get('AGENT_CODEREVIEW_BITBUCKET_TOKEN').required().asString(),
  };

  return configCache;
};
