"""Evaluation utilities for the URL classifier.

Computes accuracy and per-class precision / recall / F1 on a labeled test
split.  All functions are pure and deterministic — no randomness, no external
service calls.
"""
from __future__ import annotations

from typing import Sequence

from app.services.classifier import URLClassifier
from app.services.dataset import DATASET, PROVIDER_KEYS


def accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    """Fraction of correct predictions."""
    if not y_true:
        return 0.0
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return correct / len(y_true)


def per_class_metrics(
    y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]
) -> dict[str, dict[str, float]]:
    """Precision, recall and F1 for each label (one-vs-rest)."""
    result: dict[str, dict[str, float]] = {}
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        result[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": tp + fn,
        }
    return result


def train_test_split(
    dataset: list, train_fraction: float = 0.8
) -> tuple[list, list]:
    """Deterministic 80/20 split that keeps each provider's examples together.

    For every provider, the first ``train_fraction`` of its examples go to
    training and the remainder to test.  Because the dataset is ordered by
    provider, this is a simple and reproducible per-class split.
    """
    by_provider: dict[str, list] = {}
    for item in dataset:
        by_provider.setdefault(item.label, []).append(item)

    train: list = []
    test: list = []
    for label in sorted(by_provider.keys()):
        examples = by_provider[label]
        n_train = int(round(len(examples) * train_fraction))
        # Ensure at least one example in each split when possible.
        if n_train == len(examples):
            n_train = max(1, len(examples) - 1) if len(examples) > 1 else 1
        n_train = max(1, n_train) if len(examples) > 1 else n_train
        train.extend(examples[:n_train])
        test.extend(examples[n_train:])
    return train, test


def evaluate_classifier(
    classifier: URLClassifier,
    test_set: list,
) -> dict:
    """Run *classifier* over *test_set* and return a metrics report."""
    y_true = [d.label for d in test_set]
    y_pred = [classifier.predict(d.url)[0] for d in test_set]
    return {
        "accuracy": accuracy(y_true, y_pred),
        "per_class": per_class_metrics(y_true, y_pred, PROVIDER_KEYS),
        "n_samples": len(y_true),
        "n_classes": len(PROVIDER_KEYS),
        "confusion_matrix": _confusion_matrix(y_true, y_pred, list(PROVIDER_KEYS)),
    }


def _confusion_matrix(
    y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]
) -> list[list[int]]:
    """Return confusion matrix rows = true, cols = predicted."""
    idx = {label: i for i, label in enumerate(labels)}
    matrix = [[0] * len(labels) for _ in labels]
    for t, p in zip(y_true, y_pred):
        matrix[idx[t]][idx[p]] += 1
    return matrix


def full_evaluation(train_fraction: float = 0.8) -> dict:
    """Train on the train split and evaluate on the test split.

    Returns a report with accuracy, per-class metrics, the confusion matrix,
    and the sizes of the train / test splits.
    """
    train, test = train_test_split(DATASET, train_fraction)
    classifier = URLClassifier()
    classifier.fit(
        [d.url for d in train],
        [d.label for d in train],
    )
    report = evaluate_classifier(classifier, test)
    report["train_size"] = len(train)
    report["test_size"] = len(test)
    return report