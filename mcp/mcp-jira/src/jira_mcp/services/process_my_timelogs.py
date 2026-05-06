from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jira_mcp.config import JiraAuthType
from jira_mcp.services.jira_api_client import (
    get_current_jira_user,
    get_jira_issue_worklogs,
    search_jira_issues,
)

JsonDict = dict[str, Any]


def _format_duration(total_seconds: int) -> str:
    if total_seconds <= 0:
        return "0m"

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours == 0:
        return f"{minutes}m"
    if minutes == 0:
        return f"{hours}h"
    return f"{hours}h {minutes}m"


def _extract_text_from_adf_node(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return ""

    text = value.get("text") if isinstance(value.get("text"), str) else ""
    content = value.get("content")
    if not isinstance(content, list):
        return text.strip()

    nested = " ".join(_extract_text_from_adf_node(item) for item in content).strip()
    return f"{text} {nested}".strip()


def _get_comment_text(comment: Any) -> str:
    if not comment:
        return ""
    if isinstance(comment, str):
        return comment.strip()
    return " ".join(_extract_text_from_adf_node(comment).split())


def _is_same_user(user: JsonDict, author: JsonDict | None) -> bool:
    if not author:
        return False

    user_account_id = user.get("accountId")
    author_account_id = author.get("accountId")
    if user_account_id and author_account_id:
        return user_account_id == author_account_id

    user_email = user.get("emailAddress")
    author_email = author.get("emailAddress")
    if isinstance(user_email, str) and isinstance(author_email, str):
        return user_email.lower() == author_email.lower()

    user_name = user.get("displayName")
    author_name = author.get("displayName")
    if isinstance(user_name, str) and isinstance(author_name, str):
        return user_name.lower() == author_name.lower()

    return False


def _parse_jira_datetime(value: str) -> datetime | None:
    try:
        normalized = value
        if len(normalized) >= 5 and normalized[-5] in {"+", "-"} and normalized[-3] != ":":
            normalized = f"{normalized[:-2]}:{normalized[-2:]}"
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _sort_timestamp(value: str) -> float:
    parsed = _parse_jira_datetime(value)
    if not parsed:
        return 0.0
    return parsed.timestamp()


def _build_markdown_summary(report: JsonDict) -> str:
    lines: list[str] = []
    period = report["period"]
    author = report["author"]
    projects = report["projects"]
    details = report["details"]
    entries_count = report["entriesCount"]

    lines.append("# Jira timelog summary")
    lines.append("")
    lines.append(f"- Period: {period['from']} to {period['to']} ({period['days']} days)")
    lines.append(f"- User: {author['displayName'] or 'Unknown user'}")
    lines.append(
        f"- Total logged: {report['totalTime']} across {len(projects)} project(s) "
        f"and {entries_count} worklog entr{'y' if entries_count == 1 else 'ies'}"
    )
    lines.append("")

    if not projects:
        lines.append("No timelogs found for the selected period.")
        return "\n".join(lines)

    lines.append("## Projects")
    lines.append("")
    for project in projects:
        lines.append(f"### {project['projectKey']} - {project['projectName']} ({project['totalTime']})")
        for issue in project["issues"]:
            lines.append(f"- {issue['issueKey']} ({issue['totalTime']}): {issue['issueSummary']}")
        lines.append("")

    lines.append("## Detailed work")
    lines.append("")
    for item in details:
        lines.append(
            f"- {item['date']} | {item['projectKey']} | {item['issueKey']} | "
            f"{item['timeSpent']} | {item['workDescription']}"
        )

    return "\n".join(lines).strip()


async def _get_all_candidate_issues(
    *,
    jira_base_url: str,
    jira_api_token: str,
    jira_email: str,
    jira_auth_type: JiraAuthType,
    days: int,
) -> list[JsonDict]:
    jql = f"worklogAuthor = currentUser() AND worklogDate >= -{days}d ORDER BY updated DESC"
    issues: list[JsonDict] = []
    start_at = 0

    while True:
        page = await search_jira_issues(
            base_url=jira_base_url,
            token=jira_api_token,
            email=jira_email,
            jira_auth_type=jira_auth_type,
            jql=jql,
            fields=["summary", "project"],
            start_at=start_at,
            max_results=100,
        )

        page_issues = page.get("issues") or []
        issues.extend(page_issues)

        page_size = int(page.get("maxResults") or len(page_issues))
        next_start_at = start_at + page_size
        total = int(page.get("total") or len(issues))

        if not page_issues or next_start_at >= total or page_size == 0:
            break
        start_at = next_start_at

    return issues


async def _get_issue_worklogs(
    *,
    jira_base_url: str,
    jira_api_token: str,
    jira_email: str,
    jira_auth_type: JiraAuthType,
    issue_key: str,
) -> list[JsonDict]:
    worklogs: list[JsonDict] = []
    start_at = 0

    while True:
        page = await get_jira_issue_worklogs(
            base_url=jira_base_url,
            token=jira_api_token,
            email=jira_email,
            jira_auth_type=jira_auth_type,
            issue_key=issue_key,
            start_at=start_at,
            max_results=100,
        )

        page_worklogs = page.get("worklogs") or []
        worklogs.extend(page_worklogs)

        page_size = int(page.get("maxResults") or len(page_worklogs))
        next_start_at = start_at + page_size
        total = int(page.get("total") or len(worklogs))

        if not page_worklogs or next_start_at >= total or page_size == 0:
            break
        start_at = next_start_at

    return worklogs


async def process_my_timelogs(
    *,
    jira_base_url: str,
    jira_api_token: str,
    jira_email: str,
    jira_auth_type: JiraAuthType,
    days: int,
) -> JsonDict:
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=days)

    me = await get_current_jira_user(
        base_url=jira_base_url,
        token=jira_api_token,
        email=jira_email,
        jira_auth_type=jira_auth_type,
    )

    candidate_issues = await _get_all_candidate_issues(
        jira_base_url=jira_base_url,
        jira_api_token=jira_api_token,
        jira_email=jira_email,
        jira_auth_type=jira_auth_type,
        days=days,
    )

    details: list[JsonDict] = []
    for issue in candidate_issues:
        issue_key = issue.get("key")
        if not issue_key:
            continue

        issue_fields = issue.get("fields") or {}
        issue_summary = issue_fields.get("summary") or "No issue summary"
        project = issue_fields.get("project") or {}
        project_key = project.get("key") or "UNKNOWN"
        project_name = project.get("name") or "Unknown project"

        issue_worklogs = await _get_issue_worklogs(
            jira_base_url=jira_base_url,
            jira_api_token=jira_api_token,
            jira_email=jira_email,
            jira_auth_type=jira_auth_type,
            issue_key=issue_key,
        )

        for worklog in issue_worklogs:
            started = worklog.get("started")
            time_spent_seconds = int(worklog.get("timeSpentSeconds") or 0)
            if not isinstance(started, str) or time_spent_seconds <= 0:
                continue

            started_at = _parse_jira_datetime(started)
            if not started_at or started_at < period_start or started_at > now:
                continue

            if not _is_same_user(me, worklog.get("author")):
                continue

            comment_text = _get_comment_text(worklog.get("comment"))
            details.append(
                {
                    "started": started,
                    "date": started[:10],
                    "projectKey": project_key,
                    "projectName": project_name,
                    "issueKey": issue_key,
                    "issueSummary": issue_summary,
                    "timeSpentSeconds": time_spent_seconds,
                    "timeSpent": _format_duration(time_spent_seconds),
                    "workDescription": comment_text or issue_summary,
                }
            )

    details.sort(key=lambda item: _sort_timestamp(item["started"]), reverse=True)

    projects_map: dict[str, JsonDict] = {}
    total_time_seconds = 0

    for detail in details:
        total_time_seconds += int(detail["timeSpentSeconds"])
        project_id = f"{detail['projectKey']}::{detail['projectName']}"

        project = projects_map.get(project_id)
        if not project:
            project = {
                "projectKey": detail["projectKey"],
                "projectName": detail["projectName"],
                "totalTimeSeconds": 0,
                "totalTime": "0m",
                "issues": [],
            }

        project["totalTimeSeconds"] = int(project["totalTimeSeconds"]) + int(detail["timeSpentSeconds"])

        issue_summary = None
        for item in project["issues"]:
            if item["issueKey"] == detail["issueKey"]:
                issue_summary = item
                break

        if not issue_summary:
            issue_summary = {
                "issueKey": detail["issueKey"],
                "issueSummary": detail["issueSummary"],
                "totalTimeSeconds": 0,
                "totalTime": "0m",
                "entries": [],
            }
            project["issues"].append(issue_summary)

        issue_summary["totalTimeSeconds"] = int(issue_summary["totalTimeSeconds"]) + int(detail["timeSpentSeconds"])
        issue_summary["entries"].append(detail)
        projects_map[project_id] = project

    projects: list[JsonDict] = []
    for project in projects_map.values():
        project["totalTime"] = _format_duration(int(project["totalTimeSeconds"]))
        normalized_issues: list[JsonDict] = []
        for issue in project["issues"]:
            issue["totalTime"] = _format_duration(int(issue["totalTimeSeconds"]))
            issue["entries"].sort(
                key=lambda item: _sort_timestamp(item["started"]),
                reverse=True,
            )
            normalized_issues.append(issue)
        normalized_issues.sort(key=lambda item: int(item["totalTimeSeconds"]), reverse=True)
        project["issues"] = normalized_issues
        projects.append(project)

    projects.sort(key=lambda item: int(item["totalTimeSeconds"]), reverse=True)

    report: JsonDict = {
        "period": {
            "days": days,
            "from": period_start.date().isoformat(),
            "to": now.date().isoformat(),
        },
        "author": {
            "accountId": me.get("accountId") or "",
            "displayName": me.get("displayName") or "Unknown user",
            "emailAddress": me.get("emailAddress") or "",
        },
        "totalTimeSeconds": total_time_seconds,
        "totalTime": _format_duration(total_time_seconds),
        "entriesCount": len(details),
        "projects": projects,
        "details": details,
    }
    report["markdownSummary"] = _build_markdown_summary(report)
    return report
