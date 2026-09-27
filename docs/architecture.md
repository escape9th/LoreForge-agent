# Architecture

## Boundary

LoreForge separates three kinds of concerns:

1. Domain objects describe what a research run contains.
2. Providers describe how planning, searching, and drafting happen.
3. Workflow code controls order, limits, and verification.
4. Service, repository, and API layers expose and persist completed runs.

This boundary matters because model calls are probabilistic, while the workflow contract should remain deterministic and testable.

## State

The workflow state contains the brief, research questions, sources, evidence, blueprint, verification report, and trace. Each stage adds one kind of information and leaves earlier information intact.

## Reliability

The Demo uses:

- bounded question and source counts;
- URL normalization and deduplication;
- explicit fact/proposal labels;
- a verification report with `supported` and `unverified`;
- no automatic promotion of unsupported text into facts;
- a trace event for each workflow stage.

## Extension Points

`SearchProvider` can later call a search API or MCP server. `ModelProvider` can later call an OpenAI-compatible API or local Ollama model. The domain and verification code should not need to know which provider is active.

## Run History and API

`RunService` calls the existing workflow and saves the resulting `ResearchPackage` as a JSON snapshot through `RunRepository`. SQLite stores a small searchable summary beside that snapshot, so the system can list recent runs without reconstructing the entire domain object.

`api.py` creates an optional FastAPI application around the service layer. The API does not duplicate workflow logic: `POST /runs` and the CLI `run --db` both use the same service. This keeps behavior consistent while making the project usable as a local Agent backend.

## Tool Calling Boundary

`tools.py` owns JSON-compatible tool schemas, validation, dispatch, and built-in tools. `toolcalling.py` owns the bounded loop between a model decision and the registry. The loop cannot execute arbitrary Python: a model can only name a registered tool and provide arguments that the tool validates.

The offline and OpenAI-compatible providers produce the same action shape. For real providers, assistant `tool_calls` and matching `tool_call_id` values are replayed on the next request. This follows the common OpenAI-compatible function-calling protocol and keeps provider-specific transport details outside the workflow.

Tool traces are part of the domain package, so JSON reports, SQLite snapshots, CLI output, and API responses all expose the same evidence about what the Agent did.
