"""Pydantic models for the Notes API."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class NoteBase(BaseModel):
    """Shared fields for note creation and updates."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Short title for the note (1-200 chars).",
        examples=["Shopping list"],
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Full note content (1-10000 chars).",
        examples=["Milk\nEggs\nBread"],
    )

    @field_validator("title", "content")
    @classmethod
    def _strip_and_validate_non_empty(cls, v: str) -> str:
        # Ensure whitespace-only strings are rejected even if min_length passes.
        stripped = v.strip()
        if not stripped:
            raise ValueError("Must not be empty or whitespace.")
        return stripped


class NoteCreate(NoteBase):
    """Request payload for creating a note."""


class NoteUpdate(NoteBase):
    """Request payload for updating a note."""


class NoteRead(NoteBase):
    """Response payload for a note."""

    id: int = Field(..., description="Note id.")
    created_at: str = Field(..., description="Creation timestamp (SQLite text).")
    updated_at: str = Field(..., description="Last update timestamp (SQLite text).")


class DeleteResult(BaseModel):
    """Response payload for successful deletion."""

    deleted: bool = Field(..., description="Whether the note was deleted.")
