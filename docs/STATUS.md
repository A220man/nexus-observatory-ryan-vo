# Status — Known Defects and Limitations

## v1.0.0 (skeleton)

### In scope (done)

- Parse share URLs from 8 providers into normalized records (provider, resource
  ID, password param, direct-link strategy).
- From-scratch TF-IDF + logistic-regression classifier (no numpy/sklearn).
- SQLite persistence with list, detail, and export (JSON/CSV) workflows.
- React 18 dashboard: submit URL → parse → persist → list → detail → export.
- Dockerized backend + frontend with compose.yaml.
- CI pipeline (backend pytest + preflight, frontend type-check + test + build).

### Out of scope (future milestones)

- **Auth/SSO (Round 2):** No authentication or authorization. All endpoints are
  public. OIDC config fields exist in `core/config.py` but are unused.
- **Direct-link resolution:** The engine extracts identifiers and passwords
  but does **not** produce working download URLs. Each provider's `strategy`
  field documents the steps a full client would need (e.g., login tokens,
  signed URL APIs). See `docs/STRATEGIES.md` for details.
- **LLM advisory explanations (Round 3):** LLM config fields exist but are
  unused. The classifier confidence is purely from logistic regression.
- **Catalog search/filter/pagination polish (Round 4):** Basic filtering by
  provider and status is implemented; advanced search and sorting are future
  enhancements.

### Known issues

- The classifier confidence is based on raw sigmoid output, which tends to
  be high (>0.9) for well-represented providers and lower for rare ones. This
  is expected behavior for the skeleton but may be calibrated in a future round.
- The `exportLinks` frontend method only handles JSON; CSV download is via a
  direct browser link in a future round.
- CORS is set to `allow_origins=["*"]` in development mode. Production deploys
  should use the nginx reverse proxy to restrict origins.