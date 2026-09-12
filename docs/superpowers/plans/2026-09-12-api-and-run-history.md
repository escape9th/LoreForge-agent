# API and Run History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a reusable service layer, SQLite run history, FastAPI endpoints, and shared structured evaluation while preserving the dependency-free CLI Demo.

**Architecture:** Keep `run_research` as the domain workflow. Add `RunRepository` for SQLite snapshots and `RunService` for provider selection plus persistence. Let CLI and FastAPI call the service layer, while the API module remains an optional integration because FastAPI is not required for the core package.

**Tech Stack:** Python 3.11+, standard-library `sqlite3`, `dataclasses`, FastAPI, Starlette TestClient, pytest.

---

### Task 1: Add repository contract and SQLite implementation

**Files:**
- Create: `src/loreforge/repository.py`
- Test: `tests/test_repository.py`

- [ ] **Step 1: Write failing repository tests**

Cover database creation, save-and-get, newest-first listing, and missing run behavior. The test should construct a real `ResearchPackage` through `run_research`, then persist it.

- [ ] **Step 2: Run `python -m pytest tests/test_repository.py -q` and verify the expected import/behavior failure**

- [ ] **Step 3: Implement `RunSummary`, `RunRepository`, schema initialization, JSON serialization, and `get`/`list_recent` methods**

- [ ] **Step 4: Run the repository tests and the existing suite**

- [ ] **Step 5: Commit with `feat: persist research runs in sqlite`**

### Task 2: Add service layer and package deserialization

**Files:**
- Modify: `src/loreforge/domain.py`
- Create: `src/loreforge/service.py`
- Test: `tests/test_service.py`

- [ ] **Step 1: Write failing tests for `ResearchPackage.from_dict` and `RunService.create_run`**

- [ ] **Step 2: Run the focused tests and verify they fail because the deserializer and service do not exist**

- [ ] **Step 3: Implement explicit dataclass reconstruction and a service that selects Demo/custom corpus/model providers, runs research, and saves snapshots**

- [ ] **Step 4: Run focused tests, the full suite, and the evaluation script**

- [ ] **Step 5: Commit with `feat: add research run service`**

### Task 3: Add FastAPI application

**Files:**
- Create: `src/loreforge/api.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Write failing API tests for health, create, list, detail, validation, and 404**

- [ ] **Step 2: Run `python -m pytest tests/test_api.py -q` and verify the expected missing-module failure**

- [ ] **Step 3: Implement `create_app(repository=None)`, dependency-safe FastAPI import, and the five endpoints from the design**

- [ ] **Step 4: Run API tests and the full suite**

- [ ] **Step 5: Commit with `feat: expose research runs through fastapi`**

### Task 4: Wire CLI, evaluation, docs, and release metadata

**Files:**
- Modify: `src/loreforge/cli.py`
- Modify: `evaluation/run_evaluation.py`
- Modify: `pyproject.toml`
- Modify: `src/loreforge/__init__.py`
- Modify: `docs/CHANGELOG.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `docs/architecture.md`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests for `--db` persistence and `history` output**

- [ ] **Step 2: Run the focused CLI tests and verify the new flags are not recognized**

- [ ] **Step 3: Add `--db`, `history`, and `show` commands through `RunService`; centralize evaluation scoring**

- [ ] **Step 4: Update version, docs, changelog, keywords, and API run instructions**

- [ ] **Step 5: Run the full verification set**

```powershell
python -m pytest -q
python evaluation\run_evaluation.py
python -m compileall -q src tests evaluation scripts
git diff --check
```

- [ ] **Step 6: Commit with `release: LoreForge v0.3.0`**

### Task 5: Branch and remote verification

**Files:**
- No source changes.

- [ ] **Step 1: Verify the branch contains the expected commits and the worktree is clean**
- [ ] **Step 2: Attempt to push the feature branch using the configured remote**
- [ ] **Step 3: If the environment credential proxy still blocks GitHub, report the exact status without claiming a remote update**
