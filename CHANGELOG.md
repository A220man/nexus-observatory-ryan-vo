# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this
project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-10-17

### Added — Skeleton feature

**Backend (FastAPI + Python 3.12)**

- Provider registry (`providers.py`): deterministic URL patterns and
  direct-link strategies for 8 cloud-disk providers (Baidu, Aliyun, China
  Mobile, Tianyi, Xunlei, Qiniu, UC, 123 Cloud).
- URL extractor (`extractor.py`): rule-based parser that extracts provider,
  resource ID, password parameter, and direct-link strategy from a sharing URL.
- ML classifier (`classifier.py`): from-scratch character n-gram TF-IDF vectorizer
  and one-vs-rest logistic regression with L2 regularization. Trains in ~1s
  using a sparse gradient inner loop. No external ML dependencies (no numpy,
  no scikit-learn).
- Labeled dataset (`dataset.py`): 51 synthetic-but-pattern-faithful URLs across
  8 providers.
- Evaluation (`evaluation.py`): accuracy, per-class precision/recall/F1,
  confusion matrix, deterministic 80/20 train/test split.
- SQLite persistence (`models/link.py`, `core/database.py`): async SQLAlchemy
  with aiosqlite; models for `LinkRecord` and `AuditEntry`.
- REST API (`api/routes_links.py`, `api/routes_classifier.py`,
  `api/routes_health.py`): POST/GET/{id}/export/statuses endpoints,
  classify endpoint, provider listing, and evaluation endpoint.
- Configuration (`core/config.py`): pydantic-settings driven by environment
  variables; production safety checks.
- 64 backend tests: providers, classifier, extractor, evaluation, API
  integration.

**Frontend (React 18 + TypeScript + Vite)**

- Dashboard (`ObservatoryDashboard.tsx`): tab-based UI for Parse, Catalog,
  and Providers views.
- LinkForm component: URL input with submission, loading state, and error
  handling.
- LinkResult component: displays parsed record with provider, resource ID,
  password, status, confidence, and strategy.
- LinkList component: paginated catalog with provider/status filtering.
- ProviderCard component: displays provider metadata.
- Typed API client (`api/client.ts`): zero-dependency `fetch`-based client
  with full TypeScript types matching the backend.
- 7 frontend tests: API client (7 tests) and LinkForm (5 tests).

**Packaging & CI**

- Backend Dockerfile (Python 3.12 slim, nonroot user).
- Frontend Dockerfile (multi-stage: Node 24 build → nginx runtime, nonroot).
- `compose.yaml`: backend + frontend with health checks.
- GitHub Actions CI: backend pytest + preflight, frontend type-check +
  vitest + build.
- `.env.example`, `.gitignore`, `portfolio.json`.

### Documentation

- README with quick-start, API table, architecture diagram, and roadmap.
- LICENSE (MIT).
- CHANGELOG.

### Notes

- Auth/SSO (OIDC/Keycloak): future milestone. OIDC config fields are present
  in settings but unused.
- LLM advisory explanations: future milestone. LLM config fields are present
  but unused.
- Direct-link verification: out of scope (see PLAN.md). The engine extracts
  identifiers and passwords but does not reverse-engineer working download URLs.