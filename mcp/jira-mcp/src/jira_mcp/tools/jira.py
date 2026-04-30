from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from jira_mcp.config import ConfigOverrides, load_settings
from jira_mcp.services.jira_api_client import add_jira_issue_worklog, get_jira_issue
from jira_mcp.services.process_issue_summary import process_issue_summary
from jira_mcp.services.process_my_timelogs import process_my_timelogs
from jira_mcp.tools.base import ToolRegistrar


class JiraTools(ToolRegistrar):
    def register(self, mcp: FastMCP) -> None:
        @mcp.tool(
            name="fetch_jira_issue_details",
            description="Fetch Jira issue details by issue key.",
        )
        async def fetch_jira_issue_details(
            issueKey: str,
            jiraBaseUrl: str | None = None,
            jiraApiToken: str | None = None,
            jiraEmail: str | None = None,
            jiraAuthType: str | None = None,
        ) -> str:
            settings = load_settings(
                ConfigOverrides(
                    jira_base_url=jiraBaseUrl,
                    jira_api_token=jiraApiToken,
                    jira_email=jiraEmail,
                    jira_auth_type=jiraAuthType,
                )
            )
            issue = await get_jira_issue(
                base_url=settings.jira_base_url,
                issue_key=issueKey,
                token=settings.jira_api_token,
                email=settings.jira_email,
                jira_auth_type=settings.jira_auth_type,
            )
            return json.dumps(issue, indent=2)

        @mcp.tool(
            name="fetch_jira_issue_ai_summary",
            description="Fetch Jira issue details and return an AI markdown summary.",
        )
        async def fetch_jira_issue_ai_summary(
            issueKey: str,
            jiraBaseUrl: str | None = None,
            jiraApiToken: str | None = None,
            jiraEmail: str | None = None,
            jiraAuthType: str | None = None,
            openaiApiKey: str | None = None,
            openaiModel: str | None = None,
        ) -> str:
            settings = load_settings(
                ConfigOverrides(
                    jira_base_url=jiraBaseUrl,
                    jira_api_token=jiraApiToken,
                    jira_email=jiraEmail,
                    jira_auth_type=jiraAuthType,
                    openai_api_key=openaiApiKey,
                    openai_model=openaiModel,
                )
            )

            if not settings.openai_api_key:
                raise ValueError(
                    "Missing OPENAI_API_KEY. Set it in .env or pass openaiApiKey to the tool call."
                )

            result = await process_issue_summary(
                issue_key=issueKey,
                jira_base_url=settings.jira_base_url,
                jira_api_token=settings.jira_api_token,
                jira_email=settings.jira_email,
                jira_auth_type=settings.jira_auth_type,
                openai_api_key=settings.openai_api_key,
                openai_model=settings.openai_model,
            )

            return json.dumps(
                {
                    "issueKey": (result["issue"].get("key") if isinstance(result["issue"], dict) else None)
                    or issueKey,
                    "model": settings.openai_model,
                    "summary": result["summary"],
                },
                indent=2,
            )

        @mcp.tool(
            name="add_jira_timelog",
            description="Add a worklog entry to a Jira issue.",
        )
        async def add_jira_timelog(
            issueKey: str,
            timeSpent: str | None = None,
            timeSpentSeconds: int | None = None,
            comment: str | None = None,
            started: str | None = None,
            jiraBaseUrl: str | None = None,
            jiraApiToken: str | None = None,
            jiraEmail: str | None = None,
            jiraAuthType: str | None = None,
        ) -> str:
            if not timeSpent and not timeSpentSeconds:
                raise ValueError(
                    'Missing time value. Provide either timeSpent (for example "15m") or timeSpentSeconds.'
                )

            settings = load_settings(
                ConfigOverrides(
                    jira_base_url=jiraBaseUrl,
                    jira_api_token=jiraApiToken,
                    jira_email=jiraEmail,
                    jira_auth_type=jiraAuthType,
                )
            )
            worklog = await add_jira_issue_worklog(
                base_url=settings.jira_base_url,
                token=settings.jira_api_token,
                email=settings.jira_email,
                jira_auth_type=settings.jira_auth_type,
                issue_key=issueKey,
                time_spent=timeSpent,
                time_spent_seconds=timeSpentSeconds,
                comment=comment,
                started=started,
            )
            return json.dumps(worklog, indent=2)

        @mcp.tool(
            name="fetch_jira_my_timelogs",
            description="Fetch and summarize current user Jira timelogs for the last N days.",
        )
        async def fetch_jira_my_timelogs(
            days: int = 30,
            jiraBaseUrl: str | None = None,
            jiraApiToken: str | None = None,
            jiraEmail: str | None = None,
            jiraAuthType: str | None = None,
        ) -> str:
            if days < 1 or days > 365:
                raise ValueError("days must be in range 1..365")

            settings = load_settings(
                ConfigOverrides(
                    jira_base_url=jiraBaseUrl,
                    jira_api_token=jiraApiToken,
                    jira_email=jiraEmail,
                    jira_auth_type=jiraAuthType,
                )
            )
            report = await process_my_timelogs(
                jira_base_url=settings.jira_base_url,
                jira_api_token=settings.jira_api_token,
                jira_email=settings.jira_email,
                jira_auth_type=settings.jira_auth_type,
                days=days,
            )
            return json.dumps(report, indent=2)
