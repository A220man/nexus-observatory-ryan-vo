"""API routes for the link-parsing workflow.

Covers submit (parse) → persist → list → detail → export.
"""
from __future__ import annotations

import csv
import io

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditAction, AuditEntry
from app.core.database import get_session
from app.models.link import LinkRecord, ParseStatus
from app.services.classifier import get_classifier
from app.services.extractor import extract

router = APIRouter(tags=["links"])


# ── request / response models ────────────────────────────────────────

class ParseRequest(BaseModel):
    """Body for ``POST /api/v1/links``."""

    url: str = Field(..., min_length=1, max_length=4096)

    @field_validator("url")
    @classmethod
    def _check_url(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("URL must not be empty")
        return stripped


class LinkResponse(BaseModel):
    """Public representation of a persisted :class:`LinkRecord`."""

    id: int
    input_url: str
    provider: str
    resource_id: str
    password: str
    direct_link: str
    strategy: str
    status: str
    confidence: float
    error: str | None
    created_at: str


class LinkListResponse(BaseModel):
    """Paginated list envelope."""

    items: list[LinkResponse]
    total: int
    page: int
    limit: int


def _row_to_response(record: LinkRecord) -> LinkResponse:
    return LinkResponse(
        id=record.id,
        input_url=record.input_url,
        provider=record.provider,
        resource_id=record.resource_id,
        password=record.password,
        direct_link=record.direct_link,
        strategy=record.strategy,
        status=record.status,
        confidence=record.confidence,
        error=record.error,
        created_at=record.created_at.isoformat(),
    )


# ── routes ────────────────────────────────────────────────────────────

@router.post("/links", response_model=LinkResponse, status_code=201)
async def parse_link(
    request: ParseRequest,
    session: AsyncSession = Depends(get_session),
) -> LinkResponse:
    """Parse a sharing URL, augment with the ML classifier, and persist."""
    # Deterministic rule-based extraction.
    result = extract(request.url)

    # Augment with the from-scratch classifier's confidence.
    classifier = get_classifier()
    provider_pred, confidence = classifier.predict(request.url)
    result["confidence"] = round(confidence, 4)

    # If the rule-based extractor found a provider, keep its prediction
    # (it is more reliable for known URL patterns) but record the ML confidence.
    record = LinkRecord(**result)
    session.add(record)
    try:
        await session.commit()
        await session.refresh(record)
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Audit log entry.
    session.add(
        AuditEntry.record(
            AuditAction.PARSE,
            actor="anonymous",
            target_id=str(record.id),
            detail={"provider": record.provider, "status": record.status},
        )
    )
    await session.commit()

    return _row_to_response(record)


@router.get("/links", response_model=LinkListResponse)
async def list_links(
    session: AsyncSession = Depends(get_session),
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    provider: Annotated[str | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
) -> LinkListResponse:
    """List persisted link records with optional filtering and pagination."""
    query = select(LinkRecord)
    if provider:
        query = query.where(LinkRecord.provider == provider)
    if status:
        query = query.where(LinkRecord.status == status)

    total_result = await session.execute(
        select(func.count()).select_from(LinkRecord)
    )
    total = total_result.scalar_one()

    offset = (page - 1) * limit
    result = await session.execute(
        query.order_by(LinkRecord.id.desc()).offset(offset).limit(limit)
    )
    records = result.scalars().all()
    return LinkListResponse(
        items=[_row_to_response(r) for r in records],
        total=total,
        page=page,
        limit=limit,
    )

@router.get("/links/export")
async def export_links(
    session: AsyncSession = Depends(get_session),
    fmt: Annotated[str, Query(pattern="^(json|csv)$", alias="format")] = "json",
):
    """Export all link records as JSON or CSV."""
    result = await session.execute(select(LinkRecord).order_by(LinkRecord.id))
    records = result.scalars().all()

    if fmt == "json":
        payload = [_row_to_response(r).model_dump() for r in records]
        return JSONResponse(content=payload)

    # CSV
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "id", "input_url", "provider", "resource_id", "password",
        "direct_link", "strategy", "status", "confidence", "error",
        "created_at",
    ])
    for r in records:
        writer.writerow([
            r.id, r.input_url, r.provider, r.resource_id, r.password,
            r.direct_link, r.strategy, r.status, r.confidence, r.error,
            r.created_at.isoformat(),
        ])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=links.csv"},
    )

@router.get("/links/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: int,
    session: AsyncSession = Depends(get_session),
) -> LinkResponse:
    """Retrieve a single link record by ID."""
    result = await session.execute(
        select(LinkRecord).where(LinkRecord.id == link_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return _row_to_response(record)


# ── status enum endpoint ──────────────────────────────────────────────

@router.get("/statuses")
async def list_statuses() -> list[str]:
    """List the possible parse statuses."""
    return [e.value for e in ParseStatus]