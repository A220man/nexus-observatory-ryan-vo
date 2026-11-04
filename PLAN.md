# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

add-frontend-component-tests

## Roadmap

### lifespan-migration — Modernize FastAPI lifespan handlers

Status: done

Acceptance:
- Replace deprecated @app.on_event with @asynccontextmanager lifespan
- Eliminate deprecation warnings in test output
- All backend tests pass

Implementation: `backend/app/main.py`

Tests: `backend/tests/test_api.py`

### add-frontend-component-tests — Add test coverage for untested frontend components

Status: done

Acceptance:
- Add tests for LinkResult component
- Add tests for ProviderCard component
- Add tests for LinkList component
- All frontend tests pass

Implementation: `frontend/src/components/LinkResult.test.tsx`, `frontend/src/components/ProviderCard.test.tsx`, `frontend/src/components/LinkList.test.tsx`

Tests: `frontend/src/components/LinkResult.test.tsx`, `frontend/src/components/ProviderCard.test.tsx`, `frontend/src/components/LinkList.test.tsx`

### continue-implementation — Continue implementation and resolve known failures

Status: planned

Acceptance:
- Run checks, fix failures, and implement the next planned feature

