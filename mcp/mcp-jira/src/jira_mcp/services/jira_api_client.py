from __future__ import annotations

import base64
from typing import Any
from urllib.parse import quote

import httpx

from jira_mcp.config import JiraAuthType

JsonDict = dict[str, Any]


class JiraHttpError(RuntimeError):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


def _normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def _bearer_auth_header(token: str) -> str:
    return f"Bearer {token}"


def _basic_auth_header(email: str, token: str) -> str:
    raw = f"{email}:{token}".encode("utf-8")
    return f"Basic {base64.b64encode(raw).decode('ascii')}"


async def _request_with_auth(
    *,
    method: str,
    url: str,
    token: str,
    email: str,
    jira_auth_type: JiraAuthType,
    payload: JsonDict | None = None,
) -> JsonDict:
    headers = {
        "Accept": "application/json",
        **({"Content-Type": "application/json"} if method == "POST" else {}),
    }

    async def call_with_auth(auth_header: str) -> JsonDict:
        request_headers = {
            **headers,
            "Authorization": auth_header,
        }
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.request(method, url, headers=request_headers, json=payload)

        if response.status_code < 200 or response.status_code >= 300:
            raise JiraHttpError(
                f"Jira request failed: {response.status_code} {response.text}".strip(),
                response.status_code,
            )

        return response.json()

    if jira_auth_type == "bearer":
        return await call_with_auth(_bearer_auth_header(token))

    if jira_auth_type == "basic":
        if not email:
            raise ValueError(
                "jiraAuthType is basic but jiraEmail is not set. "
                "Set JIRA_EMAIL in .env or pass jiraEmail to the tool call."
            )
        return await call_with_auth(_basic_auth_header(email, token))

    try:
        return await call_with_auth(_bearer_auth_header(token))
    except JiraHttpError as error:
        if error.status_code != 401 or not email:
            raise

    return await call_with_auth(_basic_auth_header(email, token))


async def _get_issue_comments_page(
    *,
    base_url: str,
    issue_key: str,
    token: str,
    email: str,
    jira_auth_type: JiraAuthType,
    start_at: int = 0,
    max_results: int = 100,
) -> JsonDict:
    url = httpx.URL(
        f"{_normalize_base_url(base_url)}/rest/api/2/issue/{quote(issue_key, safe='')}/comment",
        params={
            "maxResults": str(max_results),
            "startAt": str(start_at),
            "expand": "renderedBody",
        },
    )
    return await _request_with_auth(
        method="GET",
        url=str(url),
        token=token,
        email=email,
        jira_auth_type=jira_auth_type,
    )


async def _get_all_issue_comments(
    *,
    base_url: str,
    issue_key: str,
    token: str,
    email: str,
    jira_auth_type: JiraAuthType,
) -> list[JsonDict]:
    comments: list[JsonDict] = []
    start_at = 0
    max_results = 100

    while True:
        page = await _get_issue_comments_page(
            base_url=base_url,
            issue_key=issue_key,
            token=token,
            email=email,
            jira_auth_type=jira_auth_type,
            start_at=start_at,
            max_results=max_results,
        )
        page_comments = page.get("comments") or []
        comments.extend(page_comments)
        total = int(page.get("total") or len(comments))
        start_at += len(page_comments)
        if not page_comments or start_at >= total:
            break

    return comments


async def get_jira_issue(*, base_url: str, issue_key: str, token: str, email: str, jira_auth_type: JiraAuthType) -> JsonDict:
    escaped_issue_key = quote(issue_key, safe="")
    url = f"{_normalize_base_url(base_url)}/rest/api/2/issue/{escaped_issue_key}?expand=renderedFields"
    issue = await _request_with_auth(
        method="GET",
        url=url,
        token=token,
        email=email,
        jira_auth_type=jira_auth_type,
    )

    comments = await _get_all_issue_comments(
        base_url=base_url,
        issue_key=issue_key,
        token=token,
        email=email,
        jira_auth_type=jira_auth_type,
    )

    fields = issue.setdefault("fields", {})
    fields["comment"] = {
        "startAt": 0,
        "maxResults": len(comments),
        "total": len(comments),
        "comments": comments,
    }
    return issue


async def get_current_jira_user(*, base_url: str, token: str, email: str, jira_auth_type: JiraAuthType) -> JsonDict:
    url = f"{_normalize_base_url(base_url)}/rest/api/2/myself"
    return await _request_with_auth(
        method="GET",
        url=url,
        token=token,
        email=email,
        jira_auth_type=jira_auth_type,
    )


async def search_jira_issues(
    *,
    base_url: str,
    token: str,
    email: str,
    jira_auth_type: JiraAuthType,
    jql: str,
    fields: list[str] | None = None,
    start_at: int = 0,
    max_results: int = 100,
) -> JsonDict:
    params: dict[str, str] = {
        "jql": jql,
        "maxResults": str(max_results),
        "startAt": str(start_at),
    }
    if fields:
        params["fields"] = ",".join(fields)

    url = httpx.URL(f"{_normalize_base_url(base_url)}/rest/api/2/search", params=params)
    return await _request_with_auth(
        method="GET",
        url=str(url),
        token=token,
        email=email,
        jira_auth_type=jira_auth_type,
    )


async def get_jira_issue_worklogs(
    *,
    base_url: str,
    token: str,
    email: str,
    jira_auth_type: JiraAuthType,
    issue_key: str,
    start_at: int = 0,
    max_results: int = 100,
) -> JsonDict:
    escaped_issue_key = quote(issue_key, safe="")
    url = (
        f"{_normalize_base_url(base_url)}/rest/api/2/issue/{escaped_issue_key}/worklog"
        f"?maxResults={max_results}&startAt={start_at}"
    )
    return await _request_with_auth(
        method="GET",
        url=url,
        token=token,
        email=email,
        jira_auth_type=jira_auth_type,
    )


async def add_jira_issue_worklog(
    *,
    base_url: str,
    token: str,
    email: str,
    jira_auth_type: JiraAuthType,
    issue_key: str,
    time_spent: str | None = None,
    time_spent_seconds: int | None = None,
    comment: str | None = None,
    started: str | None = None,
) -> JsonDict:
    escaped_issue_key = quote(issue_key, safe="")
    url = f"{_normalize_base_url(base_url)}/rest/api/2/issue/{escaped_issue_key}/worklog"

    payload: JsonDict = {}
    if time_spent and time_spent.strip():
        payload["timeSpent"] = time_spent.strip()
    if isinstance(time_spent_seconds, int) and time_spent_seconds > 0:
        payload["timeSpentSeconds"] = int(time_spent_seconds)
    if comment and comment.strip():
        payload["comment"] = comment.strip()
    if started and started.strip():
        payload["started"] = started.strip()

    return await _request_with_auth(
        method="POST",
        url=url,
        token=token,
        email=email,
        jira_auth_type=jira_auth_type,
        payload=payload,
    )
