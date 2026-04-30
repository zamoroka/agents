from __future__ import annotations

import json
from typing import Any

SYSTEM_PROMPT = (
    "You are a senior engineering assistant that summarizes Jira tickets for pull request review.\n"
    "\n"
    "Operating rules:\n"
    "- Ground every statement in the supplied payload. Never infer, assume, or fabricate facts that are not present.\n"
    "- If a required detail is missing, write \"Not specified\" instead of guessing.\n"
    "- Prefer precise, technical language over marketing or narrative phrasing.\n"
    "- Stay concise: short sentences, bullet points, no filler, no restating the prompt.\n"
    "- Preserve identifiers (ticket keys, file paths, class/method names, URLs) verbatim.\n"
    "- Do not include private metadata, internal IDs, avatars, or system fields that do not help a reviewer.\n"
    "- Output must be valid GitHub-flavored Markdown only — no preamble, no closing remarks, no code fences around the whole response."
)

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
        "# Task\n"
        "Transform the Jira issue JSON below into a concise Markdown briefing that helps a reviewer understand a pull "
        "request linked to this ticket.\n"
        "\n"
        "# Inputs\n"
        "The `<payload_json>` block contains a normalized subset of the Jira REST API response: "
        "core fields, the rendered description, comments (rendered HTML, ADF body, and a flattened `text` field), "
        "and attachment metadata.\n"
        "\n"
        "# Method\n"
        "1. Read the description, then every comment in chronological order. Treat later comments as authoritative "
        "when they refine or override earlier scope.\n"
        "2. Extract concrete requirements, decisions, constraints, and open questions. Quote short critical phrases "
        "verbatim when wording matters (e.g. acceptance criteria).\n"
        "3. Drop duplicated, obsolete, or purely conversational content. Collapse repeated points.\n"
        "4. If the payload contains no information for a section, write `- Not specified` under it. Do not omit sections.\n"
        "\n"
        "# Output format\n"
        "Return Markdown with exactly these top-level sections, in this order, using `##` headings:\n"
        "\n"
        "## Ticket\n"
        "One-line summary: `KEY — summary` followed by a compact bullet list of `status`, `type`, `priority`, "
        "`assignee`, `reporter`, `components`, `fixVersions`, `labels` (omit individual bullets that are empty).\n"
        "\n"
        "## Problem to solve\n"
        "2–5 sentences describing the user/business problem and why the change is needed.\n"
        "\n"
        "## Scope requirements\n"
        "Bulleted list of in-scope work items derived from the description and comments. Mark anything explicitly "
        "out of scope as `- Out of scope: ...`.\n"
        "\n"
        "## Acceptance criteria or verification notes\n"
        "Bulleted, testable checks. Use the ticket's wording when provided; otherwise synthesize from scope.\n"
        "\n"
        "## Constraints and dependencies\n"
        "Technical constraints, blocked-by/blocks links, environments, feature flags, data migrations, "
        "third-party services, performance/security requirements.\n"
        "\n"
        "## Open questions\n"
        "Unresolved questions raised in comments or implied by missing information. If none, write `- None`.\n"
        "\n"
        "## Reviewer checklist\n"
        "Actionable bullets a PR reviewer should verify against the diff (behavior, tests, edge cases, telemetry, "
        "docs, backwards compatibility). Each bullet phrased as an imperative starting with a verb.\n"
        "\n"
        "# Hard constraints\n"
        "- Use only facts present in `<payload_json>`.\n"
        "- Do not invent ticket links, people, dates, or version numbers.\n"
        "- Do not include the raw JSON, IDs, URLs to avatars, or internal Jira system fields.\n"
        "- Do not add sections beyond the seven above.\n"
        "- Do not wrap the entire answer in a code block.\n"
        "\n"
        "<payload_json>\n"
        f"{json.dumps(payload, indent=2, ensure_ascii=False)}\n"
        "</payload_json>\n"
    )


def build_summary_prompt_messages(*, jira_issue: JsonDict) -> list[JsonDict]:
    payload = _build_payload(jira_issue)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(payload)},
    ]
