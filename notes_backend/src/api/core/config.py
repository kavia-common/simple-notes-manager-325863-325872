"""Configuration for the notes backend.

Centralizes environment variable parsing so deeper layers never read env vars
directly (keeps flows testable and predictable).
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Typed settings for the application."""

    sqlite_db_path: str


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Load settings from environment variables.

    Contract:
      Inputs:
        - Reads environment variable SQLITE_DB if set (provided by the database container).

      Outputs:
        - Settings with `sqlite_db_path` set to an absolute/relative filesystem path.

      Errors:
        - None (always returns a Settings object). If SQLITE_DB is missing, falls back
          to the known default path used by the database container tooling.

      Side effects:
        - Reads environment variables.

    Note:
      The database container in this workspace documents the DB file at:
      /home/kavia/workspace/code-generation/simple-notes-manager-325863-325873/database/myapp.db
    """
    sqlite_db_path = os.getenv(
        "SQLITE_DB",
        "/home/kavia/workspace/code-generation/simple-notes-manager-325863-325873/database/myapp.db",
    )
    return Settings(sqlite_db_path=sqlite_db_path)
