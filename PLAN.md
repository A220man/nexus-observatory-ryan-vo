# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

lifespan-migration

## Roadmap

### lifespan-migration — Modernize FastAPI lifespan handlers

Status: done

Acceptance:
- Replace deprecated @app.on_event with @asynccontextmanager lifespan
- Eliminate deprecation warnings in test output
- All backend tests pass

Implementation: `backend/app/main.py`

Tests: `backend/tests/test_api.py`

### continue-implementation — Continue implementation and resolve known failures

Status: planned

Acceptance:
- Run checks, fix failures, and implement the next planned feature

