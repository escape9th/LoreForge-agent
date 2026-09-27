# v0.4.0 Tool Calling and RAG Trace

## Goal

Add inspectable Tool Calling, registered RAG tools, a real-model adapter, trace evaluation, and a complete interview guide without breaking the offline Demo.

## Phases

- [x] Phase 1: Design and implementation plan
- [x] Phase 2: Tool contracts and registry
- [x] Phase 3: Offline and OpenAI-compatible Tool Calling
- [x] Phase 4: Workflow trace, reports, and evaluation
- [x] Phase 5: Documentation and interview guide
- [x] Phase 6: Release verification, commit, tag, and push attempt

## Errors Encountered

| Error | Attempt | Resolution |
|---|---:|---|
| GitHub push failed with `SEC_E_NO_CREDENTIALS` | 1 | Continue local work; retry only after implementation is verified |
| Escalated GitHub push was rejected by the environment risk gate | 2 | Do not bypass the gate; keep the verified local branch and tag |

## Decisions

- Keep the default path deterministic and offline.
- Use a tool whitelist and bounded loop rather than arbitrary code execution.
- Preserve provider, service, SQLite, CLI, and API boundaries.
- Keep lightweight retrieval replaceable through `SearchProvider`.
