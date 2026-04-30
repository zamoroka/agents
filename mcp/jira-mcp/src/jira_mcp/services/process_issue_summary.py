from __future__ import annotations

from typing import Any

from jira_mcp.config import JiraAuthType
from jira_mcp.services.jira_api_client import get_jira_issue
from jira_mcp.services.summarize_jira_issue import summarize_jira_issue

JsonDict = dict[str, Any]


async def process_issue_summary(
    *,
    issue_key: str,
    jira_base_url: str,
    jira_api_token: str,
    jira_email: str,
    jira_auth_type: JiraAuthType,
    openai_api_key: str,
    openai_model: str,
) -> JsonDict:
    issue = await get_jira_issue(
        base_url=jira_base_url,
        issue_key=issue_key,
        token=jira_api_token,
        email=jira_email,
        jira_auth_type=jira_auth_type,
    )

    summary = await summarize_jira_issue(
        jira_issue=issue,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
    )

    return {
        "issue": issue,
        "summary": summary,
    }
