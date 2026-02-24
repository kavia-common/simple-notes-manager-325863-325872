"""SQLite adapter for notes persistence (I/O layer).

This module isolates all direct sqlite3 interactions behind small, well-defined
functions so the rest of the application can remain deterministic and easy to test.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NoteRow:
    """Row representation of a note as stored in the database."""

    id: int
    title: str
    content: str
    created_at: str
    updated_at: str


@contextmanager
def _connect(db_path: str) -> Iterator[sqlite3.Connection]:
    """Context manager for sqlite3 connection with consistent settings."""
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    finally:
        conn.close()


# PUBLIC_INTERFACE
def init_schema(db_path: str) -> None:
    """Ensure the DB schema for notes exists.

    Contract:
      Inputs:
        - db_path: path to SQLite DB file

      Outputs:
        - None

      Errors:
        - Raises sqlite3.Error if DDL fails.

      Side effects:
        - Creates tables/indexes if missing.
    """
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at)")
        conn.commit()


def _row_to_note(row: sqlite3.Row) -> NoteRow:
    return NoteRow(
        id=int(row["id"]),
        title=str(row["title"]),
        content=str(row["content"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


# PUBLIC_INTERFACE
def list_notes(db_path: str) -> list[NoteRow]:
    """List all notes ordered by updated_at DESC then id DESC."""
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            SELECT id, title, content, created_at, updated_at
            FROM notes
            ORDER BY datetime(updated_at) DESC, id DESC
            """
        )
        return [_row_to_note(r) for r in cur.fetchall()]


# PUBLIC_INTERFACE
def get_note(db_path: str, note_id: int) -> NoteRow | None:
    """Fetch one note by id."""
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            SELECT id, title, content, created_at, updated_at
            FROM notes
            WHERE id = ?
            """,
            (note_id,),
        )
        row = cur.fetchone()
        return _row_to_note(row) if row else None


# PUBLIC_INTERFACE
def create_note(db_path: str, title: str, content: str) -> NoteRow:
    """Insert a note and return the created row.

    Invariant: title/content are assumed already validated by API layer.
    """
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO notes (title, content, created_at, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (title, content),
        )
        note_id = int(cur.lastrowid)
        conn.commit()

        created = get_note(db_path, note_id)
        if created is None:
            # Extremely unlikely, but keep behavior deterministic and debuggable.
            logger.error("create_note: inserted id=%s but row could not be reloaded", note_id)
            raise sqlite3.DatabaseError("Inserted note could not be reloaded.")
        return created


# PUBLIC_INTERFACE
def update_note(db_path: str, note_id: int, title: str, content: str) -> NoteRow | None:
    """Update note fields, return updated row, or None if not found."""
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            UPDATE notes
            SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title, content, note_id),
        )
        conn.commit()

        if cur.rowcount == 0:
            return None
        return get_note(db_path, note_id)


# PUBLIC_INTERFACE
def delete_note(db_path: str, note_id: int) -> bool:
    """Delete note by id. Returns True if deleted, False if not found."""
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return cur.rowcount > 0
