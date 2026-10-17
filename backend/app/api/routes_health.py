"""Health-check endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Basic liveness probe for the reverse proxy and compose healthcheck."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
    }