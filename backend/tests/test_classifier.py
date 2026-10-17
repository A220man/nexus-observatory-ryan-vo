"""Tests for the from-scratch TF-IDF + logistic-regression classifier."""
from __future__ import annotations

import pytest

from app.services.classifier import (
    CharNGramVectorizer,
    LogisticRegressionClassifier,
    URLClassifier,
    fresh_classifier,
    get_classifier,
)
from app.services.dataset import DATASET, PROVIDER_KEYS


# ── vectorizer tests ──────────────────────────────────────────────────


def test_vectorizer_tokenizes_character_ngrams():
    vec = CharNGramVectorizer(ngram_range=(3, 3))
    grams = vec._tokenize("abc")
    assert grams == ["abc"]


def test_vectorizer_produces_fixed_length_vector():
    vec = CharNGramVectorizer(ngram_range=(3, 5))
    vec.fit(["https://example.com/a", "https://example.com/b"])
    result = vec.transform("https://example.com/a")
    assert len(result) == vec.n_features
    assert all(isinstance(v, float) for v in result)


def test_vectorizer_l2_normalizes_output():
    vec = CharNGramVectorizer(ngram_range=(3, 3), min_df=1)
    vec.fit(["aaa", "bbb", "ccc"])
    result = vec.transform("aaa")
    norm = sum(v * v for v in result) ** 0.5
    assert abs(norm - 1.0) < 1e-6


def test_vectorizer_unsupported_text_returns_zero_vector():
    vec = CharNGramVectorizer(ngram_range=(3, 5))
    vec.fit(["https://example.com/path"])
    result = vec.transform("ab")  # shorter than ngram_range[0]
    assert all(v == 0.0 for v in result)


# ── logistic regression tests ─────────────────────────────────────────


def test_logreg_trains_and_predicts():
    X = [[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]]
    y = ["a", "b", "a", "b"]
    model = LogisticRegressionClassifier(n_iterations=100, learning_rate=0.5)
    model.fit(X, y)
    assert model.classes_ == ["a", "b"]
    preds = model.predict(X)
    assert preds == ["a", "b", "a", "b"]


def test_logreg_sigmoid_is_bounded():
    assert LogisticRegressionClassifier._sigmoid(0.0) == pytest.approx(0.5)
    assert 0.0 < LogisticRegressionClassifier._sigmoid(-100) < 1e-40
    assert 0.999 < LogisticRegressionClassifier._sigmoid(10) < 1.0


# ── end-to-end classifier tests ───────────────────────────────────────


def test_classifier_predicts_correct_provider_for_known_urls():
    clf = fresh_classifier()
    # Use a few URLs from the dataset and check the classifier recovers the label.
    correct = 0
    for entry in DATASET[:20]:
        pred, confidence = clf.predict(entry.url)
        if pred == entry.label:
            correct += 1
    # At least 15 of the first 20 training URLs should be classified correctly.
    assert correct >= 15


def test_classifier_confidence_is_between_zero_and_one():
    clf = fresh_classifier()
    for entry in DATASET[:10]:
        _, confidence = clf.predict(entry.url)
        assert 0.0 < confidence <= 1.0


def test_classifier_predict_all_returns_all_classes():
    clf = fresh_classifier()
    probs = clf.predict_proba(DATASET[0].url)
    assert set(probs.keys()) == set(PROVIDER_KEYS)


def test_classifier_singleton_is_consistent():
    """The module-level singleton must produce identical predictions."""
    clf1 = get_classifier()
    clf2 = get_classifier()
    assert clf1 is clf2
    pred1, conf1 = clf1.predict(DATASET[0].url)
    pred2, conf2 = clf2.predict(DATASET[0].url)
    assert pred1 == pred2
    assert conf1 == conf2


def test_classifier_not_fitted_raises():
    clf = URLClassifier()
    with pytest.raises(RuntimeError, match="not fitted"):
        clf.predict("https://pan.baidu.com/s/1abc")