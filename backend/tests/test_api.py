"""Integration tests crossing the real HTTP boundary via TestClient."""
from __future__ import annotations

import pytest
from fastapi import status


# ── health ────────────────────────────────────────────────────────────


def test_get_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


# ── providers ─────────────────────────────────────────────────────────


def test_get_providers(client):
    resp = client.get("/api/v1/providers")
    assert resp.status_code == 200
    providers = resp.json()
    assert len(providers) == 8
    keys = {p["key"] for p in providers}
    assert "baidu" in keys
    assert "wy123" in keys


# ── parse (create) ────────────────────────────────────────────────────


def test_parse_baidu_url_creates_record(client):
    resp = client.post(
        "/api/v1/links",
        json={"url": "https://pan.baidu.com/s/1aF2xYz9KpLmN?pwd=1234"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["provider"] == "baidu"
    assert data["resource_id"] == "1aF2xYz9KpLmN"
    assert data["password"] == "1234"
    assert data["status"] == "needs_password"
    assert data["confidence"] > 0.0
    assert data["id"] is not None


def test_parse_unsupported_url_returns_unsupported(client):
    resp = client.post(
        "/api/v1/links",
        json={"url": "https://example.com/file/123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["provider"] == "unknown"
    assert data["status"] == "unsupported"


def test_parse_empty_url_returns_422(client):
    resp = client.post("/api/v1/links", json={"url": ""})
    assert resp.status_code == 422


def test_parse_missing_url_field_returns_422(client):
    resp = client.post("/api/v1/links", json={})
    assert resp.status_code == 422


# ── list / pagination ─────────────────────────────────────────────────


def test_list_links_after_parsing(client):
    client.post(
        "/api/v1/links",
        json={"url": "https://pan.baidu.com/s/1aF2xYz9KpLmN?pwd=1234"},
    )
    client.post(
        "/api/v1/links",
        json={"url": "https://aliyuncloud.com/s/AbCdEfGh?pwd=abcd"},
    )
    resp = client.get("/api/v1/links")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2
    assert data["page"] == 1
    assert data["limit"] == 20


def test_list_links_filter_by_provider(client):
    client.post("/api/v1/links", json={"url": "https://pan.baidu.com/s/1aBc"})
    client.post("/api/v1/links", json={"url": "https://aliyuncloud.com/s/1aBc"})
    resp = client.get("/api/v1/links?provider=baidu")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["provider"] == "baidu"


def test_list_links_filter_by_status(client):
    client.post("/api/v1/links", json={"url": "https://pan.baidu.com/s/1aBc"})
    resp = client.get("/api/v1/links?status=parsed")
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["status"] == "parsed"


def test_list_links_empty_returns_zero(client):
    resp = client.get("/api/v1/links")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


# ── detail ────────────────────────────────────────────────────────────


def test_get_link_detail(client):
    resp = client.post(
        "/api/v1/links",
        json={"url": "https://pan.baidu.com/s/1aF2xYz9KpLmN?pwd=1234"},
    )
    link_id = resp.json()["id"]
    resp = client.get(f"/api/v1/links/{link_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == link_id
    assert data["provider"] == "baidu"


def test_get_link_detail_not_found(client):
    resp = client.get("/api/v1/links/99999")
    assert resp.status_code == 404


# ── export ────────────────────────────────────────────────────────────


def test_export_json(client):
    client.post(
        "/api/v1/links",
        json={"url": "https://pan.baidu.com/s/1aBc"},
    )
    resp = client.get("/api/v1/links/export?format=json")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "provider" in data[0]


def test_export_csv(client):
    client.post(
        "/api/v1/links",
        json={"url": "https://pan.baidu.com/s/1aBc"},
    )
    resp = client.get("/api/v1/links/export?format=csv")
    assert resp.status_code == 200
    content = resp.text
    assert "provider" in content
    assert "baidu" in content


# ── classify ──────────────────────────────────────────────────────────


def test_classify_endpoint_returns_prediction(client):
    resp = client.post(
        "/api/v1/classify",
        json={"url": "https://pan.baidu.com/s/1aF2xYz9KpLmN"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "baidu"
    assert 0.0 < data["confidence"] <= 1.0
    assert len(data["probabilities"]) == 8


def test_evaluate_endpoint_returns_metrics(client):
    resp = client.post("/api/v1/evaluate")
    assert resp.status_code == 200
    data = resp.json()
    assert "accuracy" in data
    assert "per_class" in data
    assert "confusion_matrix" in data
    assert data["n_classes"] == 8


# ── statuses ──────────────────────────────────────────────────────────


def test_get_statuses(client):
    resp = client.get("/api/v1/statuses")
    assert resp.status_code == 200
    statuses = resp.json()
    assert "parsed" in statuses
    assert "needs_password" in statuses
    assert "unsupported" in statuses