from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

SYSTEM_PROMPT = "You summarize Jira tickets for pull request review. Be precise, concise, and avoid guessing."

JsonDict = dict[str, Any]


def _extract_adf_text(node: Any) -> str:
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_extract_adf_text(item) for item in node)
    if not isinstance(node, dict):
        return ""

    node_type = node.get("type")
    if node_type == "text":
        return str(node.get("text") or "")
    if node_type == "hardBreak":
        return "\n"

    content = node.get("content")
    text = _extract_adf_text(content)
    if node_type in {"paragraph", "heading", "listItem", "tableRow"} and text:
        return f"{text}\n"
    return text


def _coerce_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        return _extract_adf_text(value).strip()
    return ""


def _build_payload(jira_issue: JsonDict) -> JsonDict:
    fields = jira_issue.get("fields") or {}
    rendered_fields = jira_issue.get("renderedFields") or {}
    comments = ((fields.get("comment") or {}).get("comments") or [])
    attachments = fields.get("attachment") or []

    return {
        "key": jira_issue.get("key") or "",
        "id": jira_issue.get("id") or "",
        "self": jira_issue.get("self") or "",
        "fields": {
            "summary": fields.get("summary") or "",
            "status": ((fields.get("status") or {}).get("name") or ""),
            "priority": ((fields.get("priority") or {}).get("name") or ""),
            "issueType": ((fields.get("issuetype") or {}).get("name") or ""),
            "assignee": ((fields.get("assignee") or {}).get("displayName") or ""),
            "reporter": ((fields.get("reporter") or {}).get("displayName") or ""),
            "created": fields.get("created") or "",
            "updated": fields.get("updated") or "",
            "labels": fields.get("labels") or [],
            "components": [
                (item or {}).get("name")
                for item in (fields.get("components") or [])
                if (item or {}).get("name")
            ],
            "fixVersions": [
                (item or {}).get("name")
                for item in (fields.get("fixVersions") or [])
                if (item or {}).get("name")
            ],
            "description": fields.get("description") or "",
            "renderedDescription": rendered_fields.get("description") or "",
            "comments": [
                {
                    "author": ((comment or {}).get("author") or {}).get("displayName") or "",
                    "created": (comment or {}).get("created") or "",
                    "body": (comment or {}).get("body") or "",
                    "renderedBody": (comment or {}).get("renderedBody") or "",
                    "text": _coerce_text((comment or {}).get("renderedBody"))
                    or _coerce_text((comment or {}).get("body")),
                }
                for comment in comments
            ],
            "attachments": [
                {
                    "filename": (attachment or {}).get("filename") or "",
                    "mimeType": (attachment or {}).get("mimeType") or "",
                    "size": (attachment or {}).get("size") or 0,
                    "created": (attachment or {}).get("created") or "",
                    "content": (attachment or {}).get("content") or "",
                }
                for attachment in attachments
            ],
        },
    }


def _build_user_prompt(payload: JsonDict) -> str:
    return (
        "Read this Jira issue payload and produce a markdown summary for code reviewers.\n\n"
        "Requirements:\n"
        "- Use only information from payload.\n"
        "- If data is missing, write \"Not provided\".\n"
        "- Keep output concise and actionable.\n"
        "- Explicitly account for issue comments when identifying scope, constraints, and open questions.\n"
        "- Include these sections in this order:\n"
        "  1) Ticket\n"
        "  2) Problem to solve\n"
        "  3) Scope requirements\n"
        "  4) Acceptance criteria or verification notes\n"
        "  5) Constraints and dependencies\n"
        "  6) Open questions\n"
        "  7) Reviewer checklist\n\n"
        "Payload JSON:\n"
        f"{json.dumps(payload, indent=2)}\n"
    )


async def summarize_jira_issue(*, jira_issue: JsonDict, openai_api_key: str, openai_model: str) -> str:
    payload = _build_payload(jira_issue)
    client = AsyncOpenAI(api_key=openai_api_key)

    response = await client.chat.completions.create(
        model=openai_model,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(payload)},
        ],
    )

    text = response.choices[0].message.content or ""
    return text.strip()
