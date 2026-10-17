"""Persistent model for a parsed cloud-disk sharing link."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.audit import utcnow


class ParseStatus(str, enum.Enum):
    """Status of a parsed share link.

    - parsed: a known provider and resource id were extracted.
    - needs_password: link is parsed but the share is password-protected.
    - unsupported: provider or URL shape not recognized.
    - error: parsing failed unexpectedly.
    """
    PARSED = "parsed"
    NEEDS_PASSWORD = "needs_password"
    UNSUPPORTED = "unsupported"
    ERROR = "error"


class LinkRecord(Base):
    __tablename__ = "link_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    input_url: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(48), default="unknown")
    resource_id: Mapped[str] = mapped_column(String(256), default="")
    password: Mapped[str] = mapped_column(String(64), default="")
    direct_link: Mapped[str] = mapped_column(Text, default="")
    strategy: Mapped[str] = mapped_column(String(128), default="")
    status: Mapped[str] = mapped_column(String(24), default=ParseStatus.UNSUPPORTED.value)
    confidence: Mapped[float] = mapped_column(default=0.0)
    error: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<LinkRecord provider={self.provider!r} id={self.id}>"