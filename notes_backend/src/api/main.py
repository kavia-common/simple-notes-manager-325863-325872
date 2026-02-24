import logging
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.core.errors import ApiError
from src.api.routes.notes import router as notes_router

logger = logging.getLogger(__name__)

openapi_tags = [
    {"name": "system", "description": "Health and system endpoints."},
    {"name": "notes", "description": "CRUD operations for notes."},
]

app = FastAPI(
    title="Simple Notes Manager API",
    description="Backend API for a simple notes app (SQLite persistence).",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS configuration:
# Prefer explicit env vars if present (set by platform/orchestrator).
# Otherwise, default to allowing the local dev origin + the preview host pattern.
#
# IMPORTANT: When allow_credentials=True, allow_origins cannot be ["*"] in browsers.
# We therefore keep defaults explicit and configurable.
allowed_origins = os.getenv("ALLOWED_ORIGINS")
if allowed_origins:
    allow_origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]
else:
    # Default preview + dev origins
    allow_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Kavia preview frontend origin (current workspace)
        "https://vscode-internal-28946-beta.beta01.cloud.kavia.ai:3000",
    ]

allowed_headers = os.getenv("ALLOWED_HEADERS", "*")
allow_headers = [h.strip() for h in allowed_headers.split(",")] if allowed_headers != "*" else ["*"]

allowed_methods = os.getenv("ALLOWED_METHODS", "*")
allow_methods = [m.strip() for m in allowed_methods.split(",")] if allowed_methods != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)

# Routes
app.include_router(notes_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return consistent validation errors.

    FastAPI's default 422 response is fine, but its shape differs from our ApiError.
    We keep the 422 semantics while returning an ApiError payload for consistency.
    """
    payload = ApiError(
        error="VALIDATION_ERROR",
        message="Request validation failed.",
        details={"errors": exc.errors()},
    ).model_dump()
    return JSONResponse(status_code=422, content={"detail": payload})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all to ensure a consistent error envelope for unexpected failures."""
    logger.exception("Unhandled error path=%s", request.url.path)
    payload = ApiError(
        error="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred.",
        details=None,
    ).model_dump()
    return JSONResponse(status_code=500, content={"detail": payload})


@app.get(
    "/",
    tags=["system"],
    summary="Health check",
    description="Basic health endpoint to verify the API process is running.",
    operation_id="health_check",
)
# PUBLIC_INTERFACE
def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {"message": "Healthy"}
