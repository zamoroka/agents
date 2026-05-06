from __future__ import annotations

import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

LOGGER = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def load_credentials(token_path: Path) -> Credentials | None:
    if not token_path.exists():
        return None

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json())
    return creds


def authorize(credentials_path: Path, token_path: Path) -> Credentials:
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"OAuth client credentials not found: {credentials_path}. "
            "Create an OAuth desktop client in Google Cloud and set GOOGLE_OAUTH_CREDENTIALS_FILE."
        )

    token_path.parent.mkdir(parents=True, exist_ok=True)
    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json())
    LOGGER.info("Saved OAuth token to %s", token_path)
    return creds


def get_or_authorize(credentials_path: Path, token_path: Path) -> Credentials:
    creds = load_credentials(token_path)
    if creds:
        return creds
    return authorize(credentials_path=credentials_path, token_path=token_path)
