"""Tests for the deterministic provider registry."""
from __future__ import annotations

import pytest

from app.services.providers import (
    BY_KEY,
    PROVIDERS,
    list_providers,
    provider_for_url,
)

# (url, expected_key) pairs covering all 8 providers.
SAMPLE_URLS: list[tuple[str, str]] = [
    ("https://pan.baidu.com/s/1aF2xYz9KpLmN?pwd=1234", "baidu"),
    ("https://yun.baidu.com/s/1XxYyZzAaBb", "baidu"),
    ("https://aliyuncloud.com/s/AbCdEfGh?pwd=abcd", "aliyun"),
    ("https://aliyuncloud.com/share/XyZw1234", "aliyun"),
    ("https://yun.139.com/share/a1b2c3d4e5f6g7h8i9j0", "cmcc"),
    ("https://cloud.189.com/web/share/abc123def456ghi", "tianyi"),
    ("https://cloud.189.com/share/xyz789abc456def", "tianyi"),
    ("https://pan.xunlei.com/s/a1b2c3d4e5f6g7h8", "xunlei"),
    ("https://yunpan.xunlei.com/s/xyzxyzxyzxyzxyzx", "xunlei"),
    ("https://qiniu.com/s/abc123def456ghi789", "qiniu"),
    ("https://pan.uc.com/s/abc123def456ghi789?code=1234", "uc"),
    ("https://www.123pan.com/s/abc123def456ghi789?pwd=1234", "wy123"),
]


def test_providers_count_is_eight():
    """The product brief requires eight major cloud-disk providers."""
    assert len(PROVIDERS) == 8


def test_provider_keys_match_expected_set():
    expected = {"baidu", "aliyun", "cmcc", "tianyi", "xunlei", "qiniu", "uc", "wy123"}
    assert set(BY_KEY.keys()) == expected


@pytest.mark.parametrize("url,expected_key", SAMPLE_URLS)
def test_provider_for_url_identifies_each_provider(url: str, expected_key: str):
    provider = provider_for_url(url)
    assert provider is not None
    assert provider.key == expected_key


def test_provider_parse_extracts_resource_id_and_password():
    url = "https://pan.baidu.com/s/1aF2xYz9KpLmN?pwd=1234"
    provider = provider_for_url(url)
    assert provider is not None
    resource_id, password = provider.parse(url)
    assert resource_id == "1aF2xYz9KpLmN"
    assert password == "1234"


def test_provider_parse_without_password():
    url = "https://pan.baidu.com/s/1aF2xYz9KpLmN"
    provider = provider_for_url(url)
    assert provider is not None
    resource_id, password = provider.parse(url)
    assert resource_id == "1aF2xYz9KpLmN"
    assert password is None


def test_provider_for_url_returns_none_for_unknown():
    assert provider_for_url("https://example.com/file/123") is None


def test_provider_for_url_returns_none_for_malformed():
    assert provider_for_url("not-a-url") is None


def test_list_providers_returns_serializable_dicts():
    providers = list_providers()
    assert len(providers) == 8
    for p in providers:
        assert "key" in p
        assert "name" in p
        assert "domains" in p
        assert "strategy" in p
    keys = {p["key"] for p in providers}
    assert "baidu" in keys
    assert "wy123" in keys