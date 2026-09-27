# Tool Calling and RAG Trace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add bounded, inspectable Tool Calling and RAG tool traces to LoreForge while preserving offline reproducibility and OpenAI-compatible model integration.

**Architecture:** Keep `workflow.py` as the outer orchestrator. Add focused `tools.py` for tool contracts and built-ins, `toolcalling.py` for the bounded model/tool loop, and extend domain/provider/reporting code only where the trace crosses an existing boundary. The Demo provider is deterministic; the real adapter translates the same protocol to OpenAI-compatible JSON.

**Tech Stack:** Python 3.11+, standard library JSON/SQLite/urllib, pytest, optional FastAPI/Uvicorn.

---

### Task 1: Domain trace contracts

**Files:**
- Modify: `src/loreforge/domain.py`
- Test: `tests/test_domain.py`

- [ ] Add frozen `ToolTraceEvent` with tool name, arguments, result, status, and timestamp.
- [ ] Add `tool_trace` to `ResearchState`, `ResearchPackage`, serialization, and deserialization.
- [ ] Preserve equality and old snapshots by defaulting missing serialized `tool_trace` to an empty list.
- [ ] Run focused domain tests, then the existing suite.

### Task 2: Tool protocol and built-in tools

**Files:**
- Create: `src/loreforge/tools.py`
- Test: `tests/test_tools.py`

- [ ] Define `ToolSpec`, `ToolCall`, `ToolResult`, `Tool`, and `ToolRegistry`.
- [ ] Validate required object arguments and reject unknown tool names with structured failures.
- [ ] Implement `corpus_search`, `source_lookup`, `citation_check`, and `consistency_check` using existing providers and verification helpers.
- [ ] Ensure tool outputs are JSON-serializable and bounded.
- [ ] Run tests and confirm registry behavior before adding the agent loop.

### Task 3: Offline Tool Calling agent

**Files:**
- Create: `src/loreforge/toolcalling.py`
- Modify: `src/loreforge/demo.py`
- Test: `tests/test_toolcalling.py`

- [ ] Define a model protocol for tool decisions and a deterministic `DemoToolCallingProvider`.
- [ ] Implement `ToolCallingAgent.run` with a maximum call count, structured failure results, and one trace event per call.
- [ ] Make the demo provider choose corpus search and source lookup based on the prompt profile, then return collected sources/evidence.
- [ ] Cover success, unknown tool, malformed arguments, provider errors, and call-limit behavior with tests.

### Task 4: Integrate the agent into the workflow

**Files:**
- Modify: `src/loreforge/workflow.py`
- Modify: `src/loreforge/service.py`
- Test: `tests/test_workflow.py`, `tests/test_service.py`

- [ ] Add optional `tool_agent` injection while preserving existing `search` and `model` callers.
- [ ] Use the agent to collect sources/evidence and append tool traces before draft/verify stages.
- [ ] Keep the existing Demo path deterministic and keep custom corpus support working.
- [ ] Verify persisted packages round-trip with tool traces.

### Task 5: Real OpenAI-compatible tool calling

**Files:**
- Modify: `src/loreforge/adapters.py`
- Modify: `src/loreforge/config.py`
- Test: `tests/test_adapters.py`, `tests/test_config.py`

- [ ] Add an OpenAI-compatible tool-calling adapter that sends `tools` schemas and parses assistant `tool_calls`.
- [ ] Parse final JSON content into a bounded decision object and reject malformed responses clearly.
- [ ] Reuse the existing transport injection so tests do not access the network.
- [ ] Add a setting for the maximum tool calls without exposing secrets in traces.

### Task 6: Reports, API, CLI, and evaluation

**Files:**
- Modify: `src/loreforge/reporting.py`
- Modify: `src/loreforge/cli.py`
- Modify: `src/loreforge/api.py`
- Modify: `src/loreforge/evaluation.py`
- Modify: `evaluation/run_evaluation.py`
- Modify: `evaluation/cases.json`
- Test: `tests/test_api.py`, `tests/test_cli.py`, `tests/test_evaluation.py`

- [ ] Render a readable tool trace section in Markdown and expose it through existing JSON/API responses.
- [ ] Add CLI options for the tool-call limit and an inspectable trace summary.
- [ ] Score whether a run made tool calls and recorded successful tool results.
- [ ] Add evaluation cases for character, quest, and worldbuilding retrieval.

### Task 7: Documentation and release

**Files:**
- Modify: `README.md`, `README.en.md`, `docs/architecture.md`, `docs/CHANGELOG.md`, `docs/keywords.md`, `pyproject.toml`, `src/loreforge/__init__.py`
- Create: `docs/项目完全解读与面试手册.md`
- Modify: `.gitignore`, `progress.md`, `task_plan.md`

- [ ] Document the full request path, RAG boundaries, Tool Calling protocol, failure handling, interview questions, and reproduction commands in Chinese.
- [ ] Update examples, keywords, version, and release notes to `0.4.0`.
- [ ] Ignore local diagnostic output without touching the existing untracked file.
- [ ] Run pytest, evaluation, compileall, diff check, and a manual CLI run.
- [ ] Commit the verified release, create tag `v0.4.0`, and push the branch and tag to `origin` using the repository's configured remote.
