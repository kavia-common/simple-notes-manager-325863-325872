"""Configuration for the notes backend.

Centralizes environment variable parsing so deeper layers never read env vars
directly (keeps flows testable and predictable).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Typed settings for the application."""

    sqlite_db_path: str


def _default_sqlite_db_path() -> str:
    """Return the default SQLite DB path used by the database container.

    Contract:
      Inputs:
        - None

      Outputs:
        - Absolute path to database/myapp.db in the sibling database workspace if it exists.
        - Otherwise, a conservative relative fallback ("myapp.db") to keep local dev working.

      Errors:
        - None

      Side effects:
        - Reads filesystem to check for default DB path.
    """
    # This backend container is typically a sibling of the `simple-notes-manager-.../database`
    # folder at:
    #   .../simple-notes-manager-325863-325873/database/myapp.db
    # We derive it from *this file's* location to avoid brittle absolute constants.
    this_file = Path(__file__).resolve()
    # .../notes_backend/src/api/core/config.py -> .../notes_backend
    notes_backend_root = this_file.parents[4]

    workspace_root = notes_backend_root.parent
    candidate = workspace_root / "simple-notes-manager-325863-325873" / "database" / "myapp.db"
    if candidate.exists():
        return str(candidate)

    # If the expected workspace structure is different, fall back to a local file.
    return "myapp.db"


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Load settings from environment variables.

    Contract:
      Inputs:
        - Reads environment variable SQLITE_DB if set (provided by the database container).

      Outputs:
        - Settings with `sqlite_db_path` set to a filesystem path.

      Errors:
        - None (always returns a Settings object).

      Side effects:
        - Reads environment variables and checks for default DB path on disk.

    Required env vars (recommended):
      - SQLITE_DB: Absolute path to the SQLite database file (e.g. database container path).
    """
    sqlite_db_path = os.getenv("SQLITE_DB") or _default_sqlite_db_path()
    return Settings(sqlite_db_path=sqlite_db_path)
