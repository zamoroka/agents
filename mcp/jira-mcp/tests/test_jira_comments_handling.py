from __future__ import annotations

import asyncio
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from jira_mcp.services import jira_api_client
from jira_mcp.services.summarize_jira_issue import _build_payload, _build_user_prompt


def _load_fixture() -> dict:
    fixture_path = Path(__file__).parent / "fixtures" / "swisssp_168_sanitized.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def test_get_jira_issue_fetches_all_comments_with_rendered_body(monkeypatch) -> None:
    fixture = _load_fixture()
    comment_one, comment_two = fixture["fields"]["comment"]["comments"]
    captured_urls: list[str] = []

    async def fake_request_with_auth(**kwargs):
        url = kwargs["url"]
        captured_urls.append(url)

        if url.endswith("/rest/api/2/issue/SWISSSP-168?expand=renderedFields"):
            issue = {
                "key": fixture["key"],
                "id": fixture["id"],
                "self": fixture["self"],
                "fields": {
                    "summary": fixture["fields"]["summary"],
                    "status": fixture["fields"]["status"],
                    "priority": fixture["fields"]["priority"],
                },
                "renderedFields": fixture["renderedFields"],
            }
            return issue

        parsed = urlparse(url)
        if parsed.path.endswith("/rest/api/2/issue/SWISSSP-168/comment"):
            params = parse_qs(parsed.query)
            start_at = int(params["startAt"][0])
            if start_at == 0:
                return {"comments": [comment_one], "total": 2}
            if start_at == 1:
                return {"comments": [comment_two], "total": 2}

        raise AssertionError(f"Unexpected URL requested: {url}")

    monkeypatch.setattr(jira_api_client, "_request_with_auth", fake_request_with_auth)

    issue = asyncio.run(
        jira_api_client.get_jira_issue(
            base_url="https://jira.example.invalid",
            issue_key="SWISSSP-168",
            token="token",
            email="",
            jira_auth_type="bearer",
        )
    )

    comment_field = issue["fields"]["comment"]
    assert comment_field["total"] == 2
    assert len(comment_field["comments"]) == 2
    assert comment_field["comments"][0]["renderedBody"] == "<p>Investigation in progress</p>"

    comment_urls = [
        requested
        for requested in captured_urls
        if "/rest/api/2/issue/SWISSSP-168/comment" in requested
    ]
    assert comment_urls
    for requested in comment_urls:
        parsed = urlparse(requested)
        params = parse_qs(parsed.query)
        assert params["expand"] == ["renderedBody"]


def test_build_payload_uses_sanitized_fixture_comments() -> None:
    fixture = _load_fixture()

    payload = _build_payload(fixture)
    comments = payload["fields"]["comments"]

    assert len(comments) == 2
    assert comments[0]["author"] == "Support Bot"
    assert comments[0]["text"] == "<p>Investigation in progress</p>"
    assert comments[1]["author"] == "On-call Engineer"
    assert comments[1]["text"] == "Cart is slower than usual\nCheckout otherwise works"


def test_user_prompt_explicitly_mentions_comments() -> None:
    fixture = _load_fixture()
    payload = _build_payload(fixture)

    prompt = _build_user_prompt(payload)

    assert "Explicitly account for issue comments" in prompt
