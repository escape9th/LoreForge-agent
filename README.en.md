# LoreForge

LoreForge is a reproducible, evidence-backed creative research Agent with offline and OpenAI-compatible Tool Calling.

It turns a creative brief into research questions, chooses registered tools, searches a bounded corpus, preserves evidence, separates factual claims from creative proposals, and verifies whether factual claims have supporting evidence. Every tool call is recorded as structured trace data.

## Quick Start

No API key or third-party runtime dependency is required for the Demo:

```powershell
python scripts\run_demo.py run "Design a floating city game world after an ocean disaster" --out demo-output
```

Run checks:

```powershell
python -m pytest -q
python evaluation\run_evaluation.py
```

## Run History

Pass a SQLite path to persist the complete research package:

```powershell
python scripts\run_demo.py run "Design a resource-conflict quest" `
  --out demo-output --db data\loreforge.sqlite3
python scripts\run_demo.py history --db data\loreforge.sqlite3
python scripts\run_demo.py show <run-id> --db data\loreforge.sqlite3
```

## FastAPI Service

The API is optional and does not change the dependency-free Demo:

```powershell
.\.venv\Scripts\python -m pip install -e ".[api]"
uvicorn loreforge.api:create_app --factory --reload
```

Endpoints:

```text
GET  /health
POST /runs       {"prompt": "Design an original game world", "max_tool_calls": 6}
GET  /runs
GET  /runs/{run_id}
```

The service stores history in `loreforge.db` by default. Set
`LOREFORGE_HISTORY_DB` to choose another path.

## Why It Is Useful

LoreForge is not just a chat wrapper. It exposes a typed research state, bounded workflow stages, provider interfaces, evidence records, verification output, and a trace that can be inspected or exported.

Workflow:

```text
plan -> choose tool -> execute tool -> gather -> extract -> draft -> verify
```

## Keywords

`AI Agent` `LLM` `RAG` `agent workflow` `creative writing` `worldbuilding`
`game development` `anime` `knowledge grounding` `citation` `evaluation`
`Python` `FastAPI` `SQLite` `REST API` `run history` `observability`
`Tool Calling` `Function Calling` `Agent tools` `Agent trace`
`中文 Agent` `Chinese LLM` `智能体` `智能体平台` `检索增强生成`

See the Chinese README and [`docs/architecture.md`](docs/architecture.md) for implementation details.
