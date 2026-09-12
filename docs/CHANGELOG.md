# Changelog

## 0.3.0 - 2026-09-12

### Added

- SQLite-backed run history with complete JSON snapshots.
- Shared `RunService` for CLI and API workflows.
- Optional FastAPI service with health, create, list, and detail endpoints.
- CLI `--db`, `history`, and `show` commands.
- Shared structured evaluation module used by the evaluation script.
- Optional `api` dependency group for FastAPI and Uvicorn.
- English and Chinese discovery keywords for API, SQLite, observability, and Agent platform use cases.

## 0.2.0 - 2026-09-12

### Added

- Custom JSON corpus adapter with URL normalization and deduplication.
- OpenAI-compatible model adapter using only the Python standard library.
- Environment-based model configuration.
- CLI support for `--corpus`.
- JSON response parsing that tolerates common Markdown code fences.
- Provider and configuration regression tests.
- Public CI workflow and contribution templates.
- Chinese and English discovery keywords for Agent, RAG, LLM, worldbuilding, game development, and creative writing use cases.

## 0.1.0 - 2026-09-12

### Added

- First runnable LoreForge Demo.
- Deterministic research workflow: plan, gather, extract, draft, verify.
- Built-in sources for a floating-city creative research scenario.
- Separate factual claims and creative proposals.
- Evidence-backed claim verification.
- Markdown and JSON report output.
- CLI commands for running and inspecting a report.
- Unit, integration, and evaluation tests.
- Beginner-friendly architecture and learning documentation.

### Design Note

This is a real first release from an initially empty repository. The Demo intentionally favors reproducibility and inspectability over provider count or UI breadth.
