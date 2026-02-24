"""Error utilities for consistent API responses."""

from __future__ import annotations

from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class ApiError(BaseModel):
    """Standard error response payload for this API."""

    error: str = Field(..., description="Stable error code identifier.")
    message: str = Field(..., description="Human readable description of the error.")
    details: dict | None = Field(
        default=None, description="Optional machine-readable error details."
    )


# PUBLIC_INTERFACE
def http_error(
    *,
    status_code: int,
    error: str,
    message: str,
    details: dict | None = None,
) -> HTTPException:
    """Create an HTTPException with the standard error payload.

    Contract:
      Inputs:
        - status_code: HTTP status code
        - error: stable error code
        - message: human readable message
        - details: optional dict with error context

      Outputs:
        - FastAPI HTTPException with `detail` set to ApiError-compatible dict.

      Errors:
        - None (always returns an exception object).

      Side effects:
        - None
    """
    payload = ApiError(error=error, message=message, details=details).model_dump()
    return HTTPException(status_code=status_code, detail=payload)


# PUBLIC_INTERFACE
def not_found(resource: str, resource_id: int) -> HTTPException:
    """404 helper."""
    return http_error(
        status_code=status.HTTP_404_NOT_FOUND,
        error="NOT_FOUND",
        message=f"{resource} {resource_id} was not found.",
        details={"id": resource_id},
    )


# PUBLIC_INTERFACE
def bad_request(message: str, details: dict | None = None) -> HTTPException:
    """400 helper."""
    return http_error(
        status_code=status.HTTP_400_BAD_REQUEST,
        error="BAD_REQUEST",
        message=message,
        details=details,
    )
