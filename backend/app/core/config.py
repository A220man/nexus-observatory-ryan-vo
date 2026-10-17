"""Environment-driven configuration. No secrets are hardcoded."""
from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "nexus-observatory"
    environment: str = "development"
    # "development" binds 127.0.0.1. "production" refuses unsafe binds.
    host: str = "127.0.0.1"
    port: int = 8000

    database_url: str = "sqlite+aiosqlite:///./observatory.db"

    # OIDC / Keycloak (wired up in a future milestone). Present so compose and the
    # README can be authored now; auth stays planned until implemented.
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_issuer: str = ""
    oidc_redirect_uri: str = ""

    # LLM advisory (optional, opt-in). Only the API key is secret.
    llm_api_key: str = ""
    llm_provider: str = ""
    llm_model: str = ""
    llm_base_url: str = ""

    # Server-side request limits for the (future) direct-link fetcher.
    http_timeout_seconds: float = 10.0

    # Local-only demo mode: binds 127.0.0.1; startup refuses it in production.
    demo_mode: bool = False

    version: str = "1.0.0"


def is_production() -> bool:
    return os.environ.get("ENVIRONMENT", "development").lower() == "production"


settings = Settings()

# Repository root (backend lives at <root>/backend, so parents[3] is the root).
BASE_DIR = Path(__file__).resolve().parents[3]