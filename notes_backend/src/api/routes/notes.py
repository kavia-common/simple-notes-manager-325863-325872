"""Notes API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.api.core.config import Settings, get_settings
from src.api.core.errors import ApiError, not_found
from src.api.flows.notes_flow import NotesFlow
from src.api.models.notes import DeleteResult, NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def _get_flow(settings: Settings = Depends(get_settings)) -> NotesFlow:
    flow = NotesFlow(db_path=settings.sqlite_db_path)
    flow.ensure_ready()
    return flow


@router.get(
    "",
    response_model=list[NoteRead],
    summary="List notes",
    description="Returns all notes ordered by most recently updated first.",
    responses={
        400: {"model": ApiError, "description": "Database or request error"},
    },
    operation_id="list_notes",
)
# PUBLIC_INTERFACE
def list_notes(flow: NotesFlow = Depends(_get_flow)) -> list[NoteRead]:
    """List all notes."""
    notes = flow.list_notes()
    return [NoteRead(**n.__dict__) for n in notes]


@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Creates a new note with a title and content.",
    responses={
        400: {"model": ApiError, "description": "Database or request error"},
        422: {"description": "Validation error"},
    },
    operation_id="create_note",
)
# PUBLIC_INTERFACE
def create_note(payload: NoteCreate, flow: NotesFlow = Depends(_get_flow)) -> NoteRead:
    """Create a new note."""
    created = flow.create_note(title=payload.title, content=payload.content)
    return NoteRead(**created.__dict__)


@router.get(
    "/{note_id}",
    response_model=NoteRead,
    summary="Get note",
    description="Fetch a single note by id.",
    responses={
        404: {"model": ApiError, "description": "Note not found"},
        400: {"model": ApiError, "description": "Database or request error"},
    },
    operation_id="get_note",
)
# PUBLIC_INTERFACE
def get_note(note_id: int, flow: NotesFlow = Depends(_get_flow)) -> NoteRead:
    """Get a note by id."""
    note = flow.get_note(note_id)
    if note is None:
        raise not_found("Note", note_id)
    return NoteRead(**note.__dict__)


@router.put(
    "/{note_id}",
    response_model=NoteRead,
    summary="Update note",
    description="Replace the title/content of an existing note.",
    responses={
        404: {"model": ApiError, "description": "Note not found"},
        400: {"model": ApiError, "description": "Database or request error"},
        422: {"description": "Validation error"},
    },
    operation_id="update_note",
)
# PUBLIC_INTERFACE
def update_note(note_id: int, payload: NoteUpdate, flow: NotesFlow = Depends(_get_flow)) -> NoteRead:
    """Update a note."""
    updated = flow.update_note(note_id=note_id, title=payload.title, content=payload.content)
    if updated is None:
        raise not_found("Note", note_id)
    return NoteRead(**updated.__dict__)


@router.delete(
    "/{note_id}",
    response_model=DeleteResult,
    summary="Delete note",
    description="Deletes a note by id.",
    responses={
        404: {"model": ApiError, "description": "Note not found"},
        400: {"model": ApiError, "description": "Database or request error"},
    },
    operation_id="delete_note",
)
# PUBLIC_INTERFACE
def delete_note(note_id: int, flow: NotesFlow = Depends(_get_flow)) -> DeleteResult:
    """Delete a note."""
    deleted = flow.delete_note(note_id=note_id)
    if not deleted:
        raise not_found("Note", note_id)
    return DeleteResult(deleted=True)
