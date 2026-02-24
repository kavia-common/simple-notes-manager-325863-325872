"""NotesFlow: reusable orchestration for notes CRUD.

This is the single canonical entrypoint for note operations used by all API routes.
"""

from __future__ import annotations

import logging
import sqlite3

from src.api.adapters import sqlite_db
from src.api.core.errors import bad_request

logger = logging.getLogger(__name__)


class NotesFlow:
    """Orchestration layer for notes use-cases."""

    def __init__(self, *, db_path: str):
        self._db_path = db_path

    # PUBLIC_INTERFACE
    def ensure_ready(self) -> None:
        """Ensure DB schema exists.

        Contract:
          Inputs:
            - None (uses configured db_path)

          Outputs:
            - None

          Errors:
            - Raises sqlite3.Error on DB errors.

          Side effects:
            - May create tables/indexes.
        """
        sqlite_db.init_schema(self._db_path)

    # PUBLIC_INTERFACE
    def list_notes(self) -> list[sqlite_db.NoteRow]:
        """List notes."""
        logger.info("NotesFlow.list_notes start")
        try:
            notes = sqlite_db.list_notes(self._db_path)
            logger.info("NotesFlow.list_notes success count=%s", len(notes))
            return notes
        except sqlite3.Error as e:
            logger.exception("NotesFlow.list_notes failed db_path=%s", self._db_path)
            raise bad_request("Database error while listing notes.") from e

    # PUBLIC_INTERFACE
    def get_note(self, note_id: int) -> sqlite_db.NoteRow | None:
        """Get note by id."""
        logger.info("NotesFlow.get_note start id=%s", note_id)
        try:
            note = sqlite_db.get_note(self._db_path, note_id)
            logger.info("NotesFlow.get_note end id=%s found=%s", note_id, bool(note))
            return note
        except sqlite3.Error as e:
            logger.exception("NotesFlow.get_note failed id=%s db_path=%s", note_id, self._db_path)
            raise bad_request("Database error while fetching note.", {"id": note_id}) from e

    # PUBLIC_INTERFACE
    def create_note(self, *, title: str, content: str) -> sqlite_db.NoteRow:
        """Create a note and return it."""
        logger.info("NotesFlow.create_note start title_len=%s content_len=%s", len(title), len(content))
        try:
            created = sqlite_db.create_note(self._db_path, title=title, content=content)
            logger.info("NotesFlow.create_note success id=%s", created.id)
            return created
        except sqlite3.Error as e:
            logger.exception("NotesFlow.create_note failed db_path=%s", self._db_path)
            raise bad_request("Database error while creating note.") from e

    # PUBLIC_INTERFACE
    def update_note(self, *, note_id: int, title: str, content: str) -> sqlite_db.NoteRow | None:
        """Update a note. Returns None if the note does not exist."""
        logger.info("NotesFlow.update_note start id=%s", note_id)
        try:
            updated = sqlite_db.update_note(self._db_path, note_id=note_id, title=title, content=content)
            logger.info("NotesFlow.update_note end id=%s updated=%s", note_id, bool(updated))
            return updated
        except sqlite3.Error as e:
            logger.exception("NotesFlow.update_note failed id=%s db_path=%s", note_id, self._db_path)
            raise bad_request("Database error while updating note.", {"id": note_id}) from e

    # PUBLIC_INTERFACE
    def delete_note(self, *, note_id: int) -> bool:
        """Delete a note. Returns True if deleted, False if not found."""
        logger.info("NotesFlow.delete_note start id=%s", note_id)
        try:
            deleted = sqlite_db.delete_note(self._db_path, note_id=note_id)
            logger.info("NotesFlow.delete_note end id=%s deleted=%s", note_id, deleted)
            return deleted
        except sqlite3.Error as e:
            logger.exception("NotesFlow.delete_note failed id=%s db_path=%s", note_id, self._db_path)
            raise bad_request("Database error while deleting note.", {"id": note_id}) from e
