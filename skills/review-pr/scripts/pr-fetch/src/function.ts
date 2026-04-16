#!/usr/bin/env node

import { processPr } from './services/processPr.js';

const provider = process.argv[2];
const prUrl = process.argv[3];

if (!provider || !prUrl) {
  process.stderr.write('Usage: PROJECT_ROOT=/path/to/project npm --workspace pr-fetch run fetch:pr -- <bitbucket|github> <PR_URL>\n');
  process.exit(1);
}

try {
  await processPr({ provider, prUrl });
} catch (error) {
  process.stderr.write(`[revew-pr] PR fetch failed: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exit(1);
}
