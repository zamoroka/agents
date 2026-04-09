#!/bin/bash

# Bitbucket PR Review Script
# Usage: PROJECT_ROOT=/path/to/project bitbucket-fetch-pr.sh <PR_NUMBER>

set -e

if [ -z "$PROJECT_ROOT" ]; then
    echo "Error: PROJECT_ROOT env var is not set"
    exit 1
fi

ENV_FILE="$PROJECT_ROOT/.env.local"
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env.local not found at $ENV_FILE"
    echo "Create it with: AGENT_CODEREVIEW_BITBUCKET_EMAIL, AGENT_CODEREVIEW_BITBUCKET_TOKEN, AGENT_CODEREVIEW_BITBUCKET_WORKSPACE, AGENT_CODEREVIEW_BITBUCKET_REPO"
    exit 1
fi

source "$ENV_FILE"

BITBUCKET_EMAIL="$AGENT_CODEREVIEW_BITBUCKET_EMAIL"
BITBUCKET_TOKEN="$AGENT_CODEREVIEW_BITBUCKET_TOKEN"
BITBUCKET_WORKSPACE="$AGENT_CODEREVIEW_BITBUCKET_WORKSPACE"
BITBUCKET_REPO="$AGENT_CODEREVIEW_BITBUCKET_REPO"

if [ -z "$BITBUCKET_EMAIL" ] || [ -z "$BITBUCKET_TOKEN" ] || [ -z "$BITBUCKET_WORKSPACE" ] || [ -z "$BITBUCKET_REPO" ]; then
    echo "Error: One or more required AGENT_CODEREVIEW_BITBUCKET_* variables are missing in $ENV_FILE"
    exit 1
fi

if [ -z "$1" ]; then
    echo "Usage: PROJECT_ROOT=/path/to/project bitbucket-fetch-pr.sh <PR_NUMBER>"
    exit 1
fi

PR_NUMBER="$1"
API_BASE="https://api.bitbucket.org/2.0"
REPO_URL="$API_BASE/repositories/$BITBUCKET_WORKSPACE/$BITBUCKET_REPO"

echo "=========================================="
echo "Fetching PR #$PR_NUMBER from $BITBUCKET_WORKSPACE/$BITBUCKET_REPO"
echo "=========================================="
echo ""

PR_DATA=$(mktemp)
curl -s -u "$BITBUCKET_EMAIL:$BITBUCKET_TOKEN" \
    "$REPO_URL/pullrequests/$PR_NUMBER" > "$PR_DATA"

if [ $(jq -r '.type' "$PR_DATA") == "error" ]; then
    echo "Error: $(jq -r '.error.message' "$PR_DATA")"
    rm "$PR_DATA"
    exit 1
fi

echo "--- PR DETAILS ---"
jq -r '"Title: " + .title, "Author: " + .author.display_name, "State: " + .state, "Source: " + .source.branch.name, "Destination: " + .destination.branch.name, "Created: " + .created_on, "Updated: " + .updated_on, "", "Description:", .description' "$PR_DATA"

DIFFSTAT_URL=$(jq -r '.links.diffstat.href' "$PR_DATA")
DIFF_URL=$(jq -r '.links.diff.href' "$PR_DATA")

echo ""
echo "--- FILES CHANGED ---"
curl -s -u "$BITBUCKET_EMAIL:$BITBUCKET_TOKEN" "$DIFFSTAT_URL" | \
    jq -r '.values[] | "  " + .status + " | " + (.lines_added|tostring) + " + | " + (.lines_removed|tostring) + " - | " + (.old.path // .new.path)'

echo ""
echo "--- DIFF ---"
curl -s -u "$BITBUCKET_EMAIL:$BITBUCKET_TOKEN" "$DIFF_URL"

rm "$PR_DATA"

echo ""
echo "=========================================="
echo "PR #$PR_NUMBER fetched successfully!"
echo "=========================================="
