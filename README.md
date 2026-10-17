# Nexus Observatory

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


**Cloud-disk share URL parser • classifier • catalog**

Nexus Observatory parses cloud-disk sharing URLs (8 providers) into normalized
resource records, classifies the provider using a from-scratch TF-IDF +
logistic-regression ML engine, persists results to SQLite, and provides
catalog/export workflows.

**Version 1.0.0 (skeleton)** — built from the empty repo as a new, original
implementation.

## Authors

- **Ryan Vo** &lt;ryandtvo@gmail.com&gt; — GitHub: `A220man`

## Providers

Baidu Cloud · Aliyun Disk · China Mobile Cloud · Tianyi Cloud · Xunlei Cloud ·
Qiniu Cloud Disk · UC Cloud · 123 Cloud

## Quick start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=backend .venv/bin/uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
npm test             # vitest
npm run build        # production build to dist/
```

### Tests

```bash
# Backend
PYTHONPATH=backend .venv/bin/python -m pytest backend/tests -v

# Frontend
npm --prefix frontend test
```

## API

All endpoints are under `/api/v1/` (plus `/health`).

| Method   | Endpoint               | Description                          |
|----------|------------------------|--------------------------------------|
| GET      | `/health`              | Liveness probe                       |
| POST     | `/api/v1/links`        | Parse a share URL → persist          |
| GET      | `/api/v1/links`        | List records (pagination + filters)  |
| GET      | `/api/v1/links/{id}`   | Get a single record                  |
| GET      | `/api/v1/links/export` | Export all records as JSON or CSV    |
| GET      | `/api/v1/statuses`     | List parse status values             |
| POST     | `/api/v1/classify`     | ML classification of a URL           |
| GET      | `/api/v1/providers`    | List all provider metadata           |
| POST     | `/api/v1/evaluate`     | Full evaluation metrics              |

## Architecture

```
┌─────────────┐   typed REST API   ┌──────────┐
│   Browser   │ ─────────────────→ │  FastAPI │
│  (React)    │                    │  backend │
└──────┬──────┘                    └──┬───────┘
       │  submit URL                  │ SQLite
       │  (POST /api/v1/links)        │
       └─────→  extractor.py         │
              ↓  providers.py          │
             ↓  classifier.py          │
              ↓  dataset.py            │
             ↓  evaluation.py          │
```

### ML engine

The classifier is implemented **from scratch in pure Python** (no numpy, no
scikit-learn). It combines:

- A character n-gram vectorizer (TF-IDF with L2 normalization)
- A one-vs-rest logistic regression with L2 regularization, trained via
  full-batch gradient descent

Sparse training optimization: dense vectors are converted to `{index: value}`
dicts so the gradient only touches non-zero features.

## Docker

```bash
docker compose up --build
# Backend:  http://localhost:8000
# Frontend: http://localhost:80
```

## Roadmap

- **Round 1 (done):** Runnable skeleton with end-to-end workflow, ML engine,
  Docker, CI.
- **Round 2 (future):** OIDC Keycloak login + role authorization.
- **Round 3 (future):** LLM advisory explanations (OpenAI/Anthropic/Gemini).
- **Round 4 (future):** Catalog search/filter/pagination/export polish.

## License

MIT — see [LICENSE](LICENSE).