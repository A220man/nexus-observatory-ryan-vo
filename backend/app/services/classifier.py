"""From-scratch character n-gram TF-IDF + multinomial logistic-regression
URL classifier.

No external ML dependencies (no numpy, no scikit-learn).  Every routine is
hand-written in pure Python.  Training and inference are fully deterministic:
gradient descent runs for a fixed number of epochs with a constant learning
rate and no stochastic shuffling, so repeated calls on the same data produce
identical weights and predictions.

The classifier is the AI/ML core of the observatory.  It is trained on the
labeled dataset in ``dataset.py`` and can run entirely offline — no LLM key
or network access required.

Training is accelerated with a sparse inner loop: dense TF-IDF vectors are
converted to ``{index: value}`` dicts so the gradient only touches non-zero
features (typically < 5% of the vocabulary).
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Optional

from app.services.dataset import DATASET


class CharNGramVectorizer:
    """Convert raw text to a TF-IDF vector using character n-grams.

    Each document is tokenised into overlapping substrings of length *n*
    (default 3–5).  Term frequency is the relative count of a gram; inverse
    document frequency uses the smoothed ``log((1+N)/(1+df))`` formula with
    an added 1.0 so zero-frequency grams never divide by zero.  The resulting
    vector is L2-normalised.

    *min_df* drops n-grams that appear in fewer than ``min_df`` documents,
    which shrinks the vocabulary and speeds up training without hurting
    classification quality (rare grams carry little discriminative signal).
    """

    def __init__(
        self, ngram_range: tuple[int, int] = (3, 5), min_df: int = 2
    ) -> None:
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.vocabulary_: dict[str, int] = {}
        self.idf_: list[float] = []
        self._n_docs: int = 0
        self._n_features: int = 0

    # ── tokenisation ───────────────────────────────────────────────

    def _tokenize(self, text: str) -> list[str]:
        """Return all character n-grams of *text* (lowercased)."""
        text = text.lower()
        n_min, n_max = self.ngram_range
        grams: list[str] = []
        for n in range(n_min, n_max + 1):
            if len(text) < n:
                continue
            for i in range(len(text) - n + 1):
                grams.append(text[i : i + n])
        return grams

    # ── fitting ────────────────────────────────────────────────────

    def fit(self, texts: list[str]) -> "CharNGramVectorizer":
        """Build the vocabulary and IDF weights from *texts*."""
        self._n_docs = len(texts)
        doc_freq: Counter[str] = Counter()
        for text in texts:
            seen = set(self._tokenize(text))
            for gram in seen:
                doc_freq[gram] += 1
        # Filter rare grams (min_df) and sort for deterministic ordering.
        if self.min_df > 1:
            kept = sorted(g for g, df in doc_freq.items() if df >= self.min_df)
        else:
            kept = sorted(doc_freq.keys())
        self.vocabulary_ = {gram: idx for idx, gram in enumerate(kept)}
        self._n_features = len(kept)
        self.idf_ = [
            math.log((1.0 + self._n_docs) / (1.0 + doc_freq[gram])) + 1.0
            for gram in kept
        ]
        return self

    @property
    def n_features(self) -> int:
        return self._n_features

    # ── transformation ─────────────────────────────────────────────

    def transform(self, text: str) -> list[float]:
        """Convert *text* to a dense TF-IDF vector."""
        grams = self._tokenize(text)
        vec = [0.0] * self._n_features
        if not grams or self._n_features == 0:
            return vec
        term_counts: Counter[str] = Counter(grams)
        n = len(grams)
        for gram, count in term_counts.items():
            idx = self.vocabulary_.get(gram)
            if idx is not None:
                vec[idx] = (count / n) * self.idf_[idx]
        # L2 normalisation
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0.0:
            vec = [v / norm for v in vec]
        return vec

    def transform_sparse(self, text: str) -> dict[int, float]:
        """Convert *text* to a sparse TF-IDF vector (``{index: value}``).

        Only non-zero entries are stored, which makes downstream dot
        products dramatically faster for high-dimensional sparse data.
        """
        grams = self._tokenize(text)
        vec: dict[int, float] = {}
        if not grams or self._n_features == 0:
            return vec
        term_counts: Counter[str] = Counter(grams)
        n = len(grams)
        for gram, count in term_counts.items():
            idx = self.vocabulary_.get(gram)
            if idx is not None:
                vec[idx] = (count / n) * self.idf_[idx]
        # L2 normalisation
        norm = math.sqrt(sum(v * v for v in vec.values()))
        if norm > 0.0:
            for k in vec:
                vec[k] /= norm
        return vec

    def fit_transform(self, texts: list[str]) -> list[list[float]]:
        self.fit(texts)
        return [self.transform(t) for t in texts]


class LogisticRegressionClassifier:
    """Multinomial logistic regression (one-vs-rest) with L2 regularisation.

    Each class gets its own weight vector and bias.  Training uses full-batch
    gradient descent: the gradient is computed over every sample in each epoch,
    then the weights are updated once.  This is fully deterministic.

    Sparse vectors (``{index: value}`` dicts) are used internally so the
    inner loop only touches non-zero features.
    """

    def __init__(
        self,
        learning_rate: float = 0.5,
        n_iterations: int = 100,
        l2: float = 0.01,
    ) -> None:
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.l2 = l2
        self.classes_: list[str] = []
        self.weights_: list[list[float]] = []
        self.bias_: list[float] = []

    @staticmethod
    def _sigmoid(z: float) -> float:
        """Numerically stable logistic sigmoid."""
        if z >= 0.0:
            return 1.0 / (1.0 + math.exp(-z))
        ez = math.exp(z)
        return ez / (1.0 + ez)

    def fit(self, X: list[list[float]], y: list[str]) -> "LogisticRegressionClassifier":
        """Train one sigmoid unit per class via gradient descent.

        *X* is expected to be dense vectors from :meth:`CharNGramVectorizer.transform`
        (the public contract); internally they are converted to sparse dicts
        for efficient computation.
        """
        self.classes_ = sorted(set(y))
        n_features = len(X[0]) if X else 0
        self.weights_ = [[0.0] * n_features for _ in self.classes_]
        self.bias_ = [0.0] * len(self.classes_)
        n = len(X)
        if n == 0:
            return self

        # Pre-compute sparse representations to avoid re-scanning dense vectors.
        X_sparse: list[dict[int, float]] = [
            {j: v for j, v in enumerate(vec) if v != 0.0} for vec in X
        ]

        for ci, _cls in enumerate(self.classes_):
            targets = [1.0 if yi == _cls else 0.0 for yi in y]
            decay = 1.0 - self.l2 * self.learning_rate
            for _epoch in range(self.n_iterations):
                grad_b = 0.0
                grad_w: dict[int, float] = {}
                for i in range(n):
                    z = self.bias_[ci]
                    wi = self.weights_[ci]
                    xi = X_sparse[i]
                    for j, xj in xi.items():
                        z += wi[j] * xj
                    p = self._sigmoid(z)
                    err = targets[i] - p
                    grad_b += err
                    if err != 0.0:
                        for j, xj in xi.items():
                            grad_w[j] = grad_w.get(j, 0.0) + err * xj
                # Apply weight decay to all features (cheap: just multiplication).
                for j in range(n_features):
                    self.weights_[ci][j] *= decay
                # Add gradient contribution for non-zero features only.
                lr_n = self.learning_rate / n
                for j, gj in grad_w.items():
                    self.weights_[ci][j] += lr_n * gj
                self.bias_[ci] += self.learning_rate * grad_b / n
        return self

    def predict_proba(self, X: list[list[float]]) -> list[list[float]]:
        """Return raw sigmoid probability for every class, per sample."""
        result: list[list[float]] = []
        for x in X:
            probs: list[float] = []
            for ci in range(len(self.classes_)):
                z = self.bias_[ci]
                wi = self.weights_[ci]
                for j in range(len(wi)):
                    z += wi[j] * x[j]
                probs.append(self._sigmoid(z))
            result.append(probs)
        return result

    def predict(self, X: list[list[float]]) -> list[str]:
        probas = self.predict_proba(X)
        return [
            self.classes_[max(range(len(p)), key=lambda i: p[i])] for p in probas
        ]


class URLClassifier:
    """End-to-end classifier bundling the vectorizer and logistic regression.

    The classifier is trained once on the labeled dataset and cached as a
    module-level singleton via :func:`get_classifier`.
    """

    def __init__(
        self,
        ngram_range: tuple[int, int] = (3, 5),
        learning_rate: float = 0.5,
        n_iterations: int = 100,
        l2: float = 0.01,
        min_df: int = 2,
    ) -> None:
        self.vectorizer = CharNGramVectorizer(ngram_range, min_df)
        self.model = LogisticRegressionClassifier(learning_rate, n_iterations, l2)
        self._fitted = False
        self.classes_: list[str] = []

    def fit(self, urls: list[str], labels: list[str]) -> "URLClassifier":
        """Train on parallel lists of *urls* and *labels*."""
        self.vectorizer.fit(urls)
        X = [self.vectorizer.transform(u) for u in urls]
        self.model.fit(X, labels)
        self.classes_ = sorted(set(labels))
        self._fitted = True
        return self

    # ── inference ──────────────────────────────────────────────────

    def predict(self, url: str) -> tuple[str, float]:
        """Return ``(provider_key, confidence)`` for *url*.

        Confidence is the raw sigmoid output of the winning class.
        Raises :class:`RuntimeError` if called before :meth:`fit`.
        """
        if not self._fitted:
            raise RuntimeError("classifier is not fitted")
        vec = self.vectorizer.transform(url)
        probas = self.model.predict_proba([vec])[0]
        best = max(range(len(probas)), key=lambda i: probas[i])
        return self.classes_[best], probas[best]

    def predict_proba(self, url: str) -> dict[str, float]:
        """Return a ``{provider: probability}`` mapping for *url*."""
        if not self._fitted:
            raise RuntimeError("classifier is not fitted")
        vec = self.vectorizer.transform(url)
        probas = self.model.predict_proba([vec])[0]
        return dict(zip(self.classes_, probas))


# ── module-level singleton ────────────────────────────────────────────

_classifier: Optional[URLClassifier] = None


def get_classifier() -> URLClassifier:
    """Return the shared, lazily-trained classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = URLClassifier()
        urls = [d.url for d in DATASET]
        labels = [d.label for d in DATASET]
        _classifier.fit(urls, labels)
    return _classifier


def fresh_classifier() -> URLClassifier:
    """Create and fit a new classifier (useful for tests / evaluation)."""
    clf = URLClassifier()
    urls = [d.url for d in DATASET]
    labels = [d.label for d in DATASET]
    clf.fit(urls, labels)
    return clf