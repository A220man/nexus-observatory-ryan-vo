"""Tests for the classifier evaluation utilities."""
from __future__ import annotations

import pytest

from app.services.classifier import fresh_classifier
from app.services.dataset import DATASET
from app.services.evaluation import (
    accuracy,
    full_evaluation,
    per_class_metrics,
    train_test_split,
)


def test_accuracy_perfect():
    assert accuracy(["a", "b", "a"], ["a", "b", "a"]) == 1.0


def test_accuracy_partial():
    assert accuracy(["a", "b", "a"], ["a", "a", "a"]) == pytest.approx(2 / 3)


def test_accuracy_empty_returns_zero():
    assert accuracy([], []) == 0.0


def test_per_class_metrics_returns_all_labels():
    y_true = ["a", "b", "a", "b"]
    y_pred = ["a", "a", "a", "b"]
    metrics = per_class_metrics(y_true, y_pred, ["a", "b"])
    assert set(metrics.keys()) == {"a", "b"}
    assert metrics["a"]["precision"] > 0
    assert metrics["a"]["recall"] == 1.0


def test_train_test_split_is_deterministic():
    train1, test1 = train_test_split(DATASET, 0.8)
    train2, test2 = train_test_split(DATASET, 0.8)
    assert train1 == train2
    assert test1 == test2


def test_train_test_split_covers_all_samples():
    train, test = train_test_split(DATASET, 0.8)
    assert len(train) + len(test) == len(DATASET)


def test_full_evaluation_returns_report():
    report = full_evaluation()
    assert "accuracy" in report
    assert 0.0 <= report["accuracy"] <= 1.0
    assert report["n_samples"] == report["test_size"]
    assert report["train_size"] > 0
    assert report["test_size"] > 0
    assert "per_class" in report
    assert "confusion_matrix" in report


def test_full_evaluation_confusion_matrix_shape():
    report = full_evaluation()
    n = report["n_classes"]  # should be 8
    matrix = report["confusion_matrix"]
    assert len(matrix) == n
    for row in matrix:
        assert len(row) == n
        assert sum(row) > 0  # at least some samples in each row