# v0.3.0 API and Run History

## Goal

Add SQLite run history, a service layer, a FastAPI API, and shared evaluation without breaking the dependency-free Demo.

## Phases

- [x] Phase 1: Design and implementation plan
- [x] Phase 2: SQLite repository
- [x] Phase 3: Service layer and deserialization
- [x] Phase 4: FastAPI API
- [x] Phase 5: CLI, evaluation, docs, and release verification
- [x] Phase 6: Local release commit, tag, and remote push attempt

## Errors Encountered

| Error | Attempt | Resolution |
|---|---:|---|
| GitHub push failed with `SEC_E_NO_CREDENTIALS` | 1 | Continue local work; retry only after implementation is verified |
| Escalated GitHub push was rejected by the environment risk gate | 2 | Do not bypass the gate; keep the verified local branch and tag |

## Decisions

- Use SQLite snapshot storage instead of multiple normalized tables.
- Keep FastAPI optional for the core CLI.
- Preserve the existing workflow and Provider protocols.
