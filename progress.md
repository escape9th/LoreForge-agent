# Progress

## 2026-09-12

- Confirmed v0.2.0 tests: 18 passed.
- Committed v0.2.0 as `476cc81`.
- Created branch `feature/api-and-run-history`.
- Added and approved the v0.3.0 design and implementation plan.
- Push to GitHub is currently blocked by the local credential proxy; no remote state was changed.
- Added SQLite `RunRepository` with snapshot persistence and recent-run summaries.
- Repository tests and the full suite pass: 3 focused, 21 total.
- Added `ResearchPackage.from_dict` and `RunService` for persisted workflow runs.
- Service tests and the full suite pass: 3 focused, 24 total.
- Added optional FastAPI app with health, create, list, and detail run endpoints.
- API tests and the full suite pass: 3 focused, 27 total; Starlette emits one existing deprecation warning.
