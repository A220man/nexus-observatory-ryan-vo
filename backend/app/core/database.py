"""Async SQLAlchemy engine + session factory over SQLite."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

_pool_kwargs: dict = {}
if settings.environment == "test":
    # Avoid pool carrying connections across event loops (TestClient runs
    # in a worker thread with its own loop).
    from sqlalchemy.pool import NullPool
    _pool_kwargs["poolclass"] = NullPool

engine = create_async_engine(settings.database_url, echo=False, future=True, **_pool_kwargs)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Create tables from the declarative models registered on Base."""
    from app.models import link  # noqa: F401  -- registers models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:  # type: ignore[arg-type]
    async with AsyncSessionFactory() as session:
        yield session