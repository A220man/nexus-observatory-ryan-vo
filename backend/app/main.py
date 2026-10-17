"""FastAPI application factory for the Nexus Observatory.

The factory pattern (``create_app``) is used so that both the UVicorn CLI and
Docker can bootstrap the app from the same entry point.  Database tables are
created and the ML classifier singleton is initialised during startup.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_classifier import router as classifier_router
from app.api.routes_health import router as health_router
from app.api.routes_links import router as links_router
from app.core.audit import AuditAction, AuditEntry
from app.core.config import settings
from app.core.database import AsyncSessionFactory, init_db
from app.services.classifier import get_classifier

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=(
            "Nexus Observatory — cloud-disk share URL parsing, classification, "
            "cataloging and export."
        ),
    )

    # CORS: dev mode allows localhost; production should use the reverse proxy.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.environment == "development" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _register_routers(app)
    _register_lifecycle(app)
    return app


def _register_routers(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(links_router, prefix="/api/v1")
    app.include_router(classifier_router, prefix="/api/v1")


def _register_lifecycle(app: FastAPI) -> None:
    @app.on_event("startup")
    async def _startup() -> None:
        await init_db()
        # Eagerly build the classifier so the first request is fast.
        get_classifier()
        logger.info("Observatory started (version %s)", settings.version)

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        logger.info("Observatory shutting down")


# A module-level app instance for ``uvicorn app.main:app``.
app = create_app()


# Re-export for convenience.
__all__ = ["create_app", "app", "AuditAction", "AuditEntry", "AsyncSessionFactory"]