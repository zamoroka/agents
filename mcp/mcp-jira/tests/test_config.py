from __future__ import annotations

import pytest

from jira_mcp.config import ConfigOverrides, load_settings


def test_load_settings_rejects_http_jira_base_url() -> None:
    with pytest.raises(ValueError, match="Invalid Jira base URL"):
        load_settings(
            ConfigOverrides(
                jira_base_url="http://jira.example.invalid",
                jira_api_token="token",
            )
        )


def test_load_settings_accepts_https_jira_base_url_and_trims_trailing_slash() -> None:
    settings = load_settings(
        ConfigOverrides(
            jira_base_url="https://jira.example.invalid/",
            jira_api_token="token",
        )
    )

    assert settings.jira_base_url == "https://jira.example.invalid"
