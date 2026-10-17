"""API routes for the ML classifier and provider registry."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.services.classifier import URLClassifier, get_classifier
from app.services.evaluation import full_evaluation
from app.services.providers import list_providers

router = APIRouter(tags=["classifier"])


class ClassifyRequest(BaseModel):
    """Body for ``POST /api/v1/classify``."""

    url: str = Field(..., min_length=1, max_length=4096)


class ClassifyResponse(BaseModel):
    """Response for a single-URL classification request."""

    provider: str
    confidence: float
    probabilities: dict[str, float]


class EvaluateResponse(BaseModel):
    """Response for full-dataset evaluation."""

    accuracy: float
    per_class: dict[str, dict[str, float]]
    n_samples: int
    n_classes: int
    train_size: int
    test_size: int
    confusion_matrix: list[list[int]]


@router.post("/classify", response_model=ClassifyResponse)
async def classify_url(
    request: ClassifyRequest,
    classifier: URLClassifier = Depends(get_classifier),
) -> ClassifyResponse:
    """Run the from-scratch TF-IDF + logistic-regression classifier on *url*."""
    provider, confidence = classifier.predict(request.url)
    probs = classifier.predict_proba(request.url)
    return ClassifyResponse(
        provider=provider,
        confidence=round(confidence, 4),
        probabilities={k: round(v, 4) for k, v in probs.items()},
    )


@router.get("/providers")
async def get_providers() -> list[dict]:
    """List all registered cloud-disk providers with their strategies."""
    return list_providers()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate() -> EvaluateResponse:
    """Train on the train split and evaluate on the held-out test split.

    Returns deterministic accuracy, per-class precision/recall/F1, and the
    confusion matrix.
    """
    report = full_evaluation()
    return EvaluateResponse(
        accuracy=report["accuracy"],
        per_class=report["per_class"],
        n_samples=report["n_samples"],
        n_classes=report["n_classes"],
        train_size=report["train_size"],
        test_size=report["test_size"],
        confusion_matrix=report["confusion_matrix"],
    )