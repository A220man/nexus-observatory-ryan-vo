"""Lightweight audit log written to the same SQLite database."""
from __future__ import annotations

import contextlib
import enum
import time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditAction(str, enum.Enum):
    PARSE = "parse"
    CLASSIFY = "classify"
    EVALUATE = "evaluate"
    EXPORT = "export"
    LOGIN = "login"  # reserved for the future OIDC milestone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditEntry(Base):
    __tablename__ = "audit_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(32))
    actor: Mapped[str] = mapped_column(String(128), default="anonymous")
    target_id: Mapped[str | None] = mapped_column(String(64), default=None)
    detail: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    @classmethod
    def record(cls, action: AuditAction, actor: str = "anonymous",
               target_id: str | None = None, detail: dict[str, Any] | None = None) -> "AuditEntry":
        return cls(
            action=action.value,
            actor=actor,
            target_id=target_id,
            detail=None if detail is None else _to_text(detail),
            created_at=utcnow(),
        )


def _to_text(detail: dict[str, Any]) -> str:
    import json

    return json.dumps(detail, sort_keys=True, default=str)


@contextlib.asynccontextmanager
async def _measure(session: AsyncSession, action: AuditAction):
    start = time.perf_counter()
    entry: AuditEntry | None = None
    try:
        yield
        entry = AuditEntry.record(action, detail={"ok": True, "elapsed_ms": int((time.perf_counter() - start) * 1000)})
    except Exception as exc:
        entry = AuditEntry.record(action, detail={"ok": False, "error": type(exc).__name__,
                                                 "elapsed_ms": int((time.perf_counter() - start) * 1000)})
        raise
    finally:
        if entry is not None:
            session.add(entry)
            await session.flush()