"""Shared pytest fixtures for backend tests."""
from __future__ import annotations

import asyncio
import os
import tempfile

# Set a temp-file database *before* any app module is imported, so the
# module-level ``settings`` / ``engine`` singletons pick it up.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_db_path}"
os.environ["ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _session_cleanup():
    """Remove the temp database file when the session ends."""
    yield
    try:
        os.close(_db_fd)
    except OSError:
        pass
    try:
        os.unlink(_db_path)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def clean_db():
    """Drop and recreate all tables before each test for isolation."""
    from app.core.database import Base, engine

    async def _reset():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_reset())
    finally:
        loop.close()
    yield


@pytest.fixture
def client() -> TestClient:
    """A TestClient backed by the temp-file test database."""
    from app.main import create_app

    app = create_app()
    with TestClient(app) as c:
        yield c