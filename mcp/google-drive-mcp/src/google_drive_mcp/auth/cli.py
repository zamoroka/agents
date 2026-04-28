from __future__ import annotations

import logging

from google_drive_mcp.auth.oauth import authorize
from google_drive_mcp.config import load_settings


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO)


def main() -> None:
    configure_logging()
    settings = load_settings()
    authorize(settings.credentials_path, settings.token_path)
    logging.getLogger(__name__).info("Authorization complete.")


if __name__ == "__main__":
    main()
