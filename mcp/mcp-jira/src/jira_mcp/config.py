from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

JiraAuthType = Literal["auto", "bearer", "basic"]

ENV_PLACEHOLDER = """# Jira MCP configuration
# Fill these values with your Jira credentials and instance URL.
JIRA_URL=
JIRA_TOKEN=
JIRA_EMAIL=
JIRA_AUTH_TYPE=auto
"""


@dataclass(frozen=True)
class Settings:
    jira_base_url: str
    jira_api_token: str
    jira_email: str
    jira_auth_type: JiraAuthType


@dataclass(frozen=True)
class ConfigOverrides:
    jira_base_url: str | None = None
    jira_api_token: str | None = None
    jira_email: str | None = None
    jira_auth_type: str | None = None


def _env_file_path() -> Path:
    return Path(__file__).resolve().parents[2] / ".env"


def ensure_env_file() -> Path:
    env_path = _env_file_path()
    if not env_path.exists():
        env_path.write_text(ENV_PLACEHOLDER, encoding="utf-8")
    return env_path


def _parse_env_file(file_path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not file_path.exists():
        return result

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()

    return result


def _parse_auth_type(value: str | None) -> JiraAuthType:
    normalized = (value or "auto").lower().strip()
    if normalized in {"auto", "bearer", "basic"}:
        return cast(JiraAuthType, normalized)
    raise ValueError("Invalid JIRA_AUTH_TYPE. Expected one of: auto, bearer, basic.")


def _read_env_value(key: str, file_values: dict[str, str]) -> str:
    return os.getenv(key, file_values.get(key, ""))


def load_settings(overrides: ConfigOverrides | None = None) -> Settings:
    env_path = ensure_env_file()
    env_values = _parse_env_file(env_path)
    overrides = overrides or ConfigOverrides()

    jira_base_url = (overrides.jira_base_url or _read_env_value("JIRA_URL", env_values)).strip()
    jira_api_token = (overrides.jira_api_token or _read_env_value("JIRA_TOKEN", env_values)).strip()
    jira_email = (overrides.jira_email if overrides.jira_email is not None else _read_env_value("JIRA_EMAIL", env_values)).strip()
    jira_auth_type = _parse_auth_type(overrides.jira_auth_type) if overrides.jira_auth_type is not None else _parse_auth_type(_read_env_value("JIRA_AUTH_TYPE", env_values))
    if not jira_base_url:
        raise ValueError("Missing Jira base URL. Set JIRA_URL in .env or pass jiraBaseUrl to the tool call.")
    if not jira_api_token:
        raise ValueError("Missing Jira API token. Set JIRA_TOKEN in .env or pass jiraApiToken to the tool call.")

    return Settings(
        jira_base_url=jira_base_url,
        jira_api_token=jira_api_token,
        jira_email=jira_email,
        jira_auth_type=jira_auth_type,
    )
