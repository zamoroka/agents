from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    credentials_path: Path
    token_path: Path
    download_dir: Path


def load_settings() -> Settings:
    credentials_path = Path(
        os.getenv("GOOGLE_OAUTH_CREDENTIALS_FILE", "./secrets/google-oauth-client.json")
    ).expanduser()
    token_path = Path(os.getenv("GOOGLE_OAUTH_TOKEN_FILE", "./secrets/google-token.json")).expanduser()
    download_dir = Path(os.getenv("GOOGLE_DOCS_DOWNLOAD_DIR", "./downloads")).expanduser()

    return Settings(
        credentials_path=credentials_path,
        token_path=token_path,
        download_dir=download_dir,
    )
