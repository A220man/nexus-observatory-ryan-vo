"""Deterministic URL extraction service.

Takes a raw sharing URL and produces a normalised record dict using the
provider registry in ``providers.py``.  The extractor is the baseline parser:
it always works offline with no ML key, and the ML classifier only augments
it with a confidence score.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse, parse_qs

from app.services.providers import Provider, provider_for_url


def _error_record(url: str, status: str, error: str) -> dict[str, Any]:
    return {
        "input_url": url,
        "provider": "unknown",
        "resource_id": "",
        "password": "",
        "direct_link": "",
        "strategy": "",
        "status": status,
        "confidence": 0.0,
        "error": error,
    }


def _validate_url(url: str) -> str | None:
    """Return an error message if *url* is malformed, else ``None``."""
    if not url or not url.strip():
        return "URL is empty"
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return "Invalid URL: missing scheme or host"
    if parsed.scheme not in ("http", "https"):
        return f"Invalid URL scheme: {parsed.scheme}"
    return None


def extract(url: str) -> dict[str, Any]:
    """Parse a sharing URL into a normalised record dict.

    The returned dict has keys: ``input_url``, ``provider``, ``resource_id``,
    ``password``, ``direct_link``, ``strategy``, ``status``, ``confidence``,
    ``error``.

    *status* is one of ``parsed``, ``needs_password``, ``unsupported``,
    ``error``.
    """
    err = _validate_url(url)
    if err is not None:
        return _error_record(url, "error", err)

    provider: Provider | None = provider_for_url(url)
    if provider is None:
        return _error_record(url, "unsupported", "Unsupported provider or URL shape")

    parsed = urlparse(url)
    parsed_result = provider.parse(url)
    if parsed_result is None:
        return _error_record(url, "error", "Provider host matched but URL did not parse")

    resource_id, password = parsed_result
    password = password or ""

    # Fall back to query-string lookup if the pattern didn't capture a password.
    if not password and provider.password_param:
        qs = parse_qs(parsed.query)
        param_val = qs.get(provider.password_param, [None])[0]
        if param_val:
            password = param_val

    status = "needs_password" if password else "parsed"

    return {
        "input_url": url,
        "provider": provider.key,
        "resource_id": resource_id,
        "password": password,
        "direct_link": "",
        "strategy": provider.strategy,
        "status": status,
        "confidence": 0.0,  # filled in by the classifier layer
        "error": None,
    }