"""Tests for the deterministic URL extractor."""
from __future__ import annotations

import pytest

from app.services.extractor import extract


def test_extract_baidu_url_with_password():
    result = extract("https://pan.baidu.com/s/1aF2xYz9KpLmN?pwd=1234")
    assert result["provider"] == "baidu"
    assert result["resource_id"] == "1aF2xYz9KpLmN"
    assert result["password"] == "1234"
    assert result["status"] == "needs_password"
    assert result["error"] is None
    assert result["input_url"] == "https://pan.baidu.com/s/1aF2xYz9KpLmN?pwd=1234"


def test_extract_baidu_url_without_password():
    result = extract("https://pan.baidu.com/s/1aF2xYz9KpLmN")
    assert result["provider"] == "baidu"
    assert result["resource_id"] == "1aF2xYz9KpLmN"
    assert result["password"] == ""
    assert result["status"] == "parsed"


def test_extract_aliyun_share_url():
    result = extract("https://aliyuncloud.com/share/XyZw1234")
    assert result["provider"] == "aliyun"
    assert result["resource_id"] == "XyZw1234"
    assert result["status"] == "parsed"


def test_extract_unsupported_provider():
    result = extract("https://drive.google.com/file/123")
    assert result["provider"] == "unknown"
    assert result["status"] == "unsupported"


def test_extract_empty_url_returns_error():
    result = extract("")
    assert result["status"] == "error"
    assert result["error"] is not None


def test_extract_malformed_url_returns_error():
    result = extract("not-a-url")
    assert result["status"] == "error"
    assert result["error"] is not None


def test_extract_ftp_scheme_returns_error():
    result = extract("ftp://pan.baidu.com/s/1abc")
    assert result["status"] == "error"


def test_extract_all_eight_providers():
    urls = [
        "https://pan.baidu.com/s/1aBcD",
        "https://aliyuncloud.com/s/1aBcD",
        "https://yun.139.com/share/abcdefghij",
        "https://cloud.189.com/web/share/abc123def",
        "https://pan.xunlei.com/s/abc123def456",
        "https://qiniu.com/s/abc123def456",
        "https://pan.uc.com/s/abc123def456",
        "https://www.123pan.com/s/abc123def456",
    ]
    for url in urls:
        result = extract(url)
        assert result["status"] in ("parsed", "needs_password"), (
            f"URL {url} returned status {result['status']}"
        )
        assert result["provider"] != "unknown"


def test_extract_strips_whitespace_url():
    result = extract("  https://pan.baidu.com/s/1aBcD  ")
    assert result["provider"] == "baidu"
    assert result["resource_id"] == "1aBcD"