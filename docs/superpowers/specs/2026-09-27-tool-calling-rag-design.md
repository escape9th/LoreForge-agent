# LoreForge v0.4 Tool Calling and RAG Trace Design

## Goal

Upgrade LoreForge from a fixed research workflow into an inspectable Agent workflow that can select and execute registered tools, while keeping the default demo offline and deterministic and supporting OpenAI-compatible tool calling when configured.

## Scope

This release adds:

- A small tool protocol and registry.
- Built-in corpus search, source lookup, citation checking, and consistency checking tools.
- A deterministic offline Tool Calling provider.
- OpenAI-compatible Tool Calling support using the standard `tools` and `tool_calls` message shape.
- Tool invocation trace events and limits for malformed or excessive calls.
- Evaluation cases that measure tool use and trace quality.
- A Chinese project and interview guide that explains the architecture and replay path.

This release does not add a web frontend, a vector database, authentication, background jobs, or a multi-agent supervisor. The existing provider, service, SQLite, CLI, API, and report contracts remain usable.

## Architecture

The existing workflow remains the outer orchestration boundary:

```text
brief -> plan -> tool-calling research -> draft -> verify -> package
```

`Tool` describes one capability. `ToolRegistry` validates names and dispatches calls. `ToolCallingAgent` owns the bounded loop: ask the model for a tool call, validate and execute it, append a trace, then ask for the next action. The agent returns structured tool results to the workflow; it never mutates the domain model directly.

The built-in tools use the existing `SearchProvider`, `Source`, `Evidence`, and verification logic. This keeps RAG inspectable: corpus retrieval is still replaceable through the provider boundary, while every retrieval and lookup is visible in the trace.

The offline provider chooses calls deterministically from the prompt profile and then returns a final structured research context. The real provider sends tool schemas to an OpenAI-compatible endpoint and parses either a tool call or a final JSON response. Both providers satisfy the same protocol so tests can exercise the workflow without network access.

## Data Flow

1. `run_research` creates a brief and asks the model for research questions.
2. `ToolCallingAgent` receives the brief and questions.
3. The model requests `corpus_search` calls. The registry executes them against the configured corpus provider.
4. The model may request `source_lookup`, `citation_check`, or `consistency_check`.
5. Each request and result becomes a `ToolTraceEvent` with name, input, output summary, status, and timestamp.
6. The agent stops at a bounded call count and returns the collected sources/evidence.
7. The existing draft and verification stages produce the final package.
8. SQLite, JSON, Markdown, API, and CLI outputs include the tool trace.

## Error Handling

- Unknown tools produce a failed result and a trace event; the loop can continue until the call limit.
- Invalid JSON arguments produce a failed result rather than crashing the process.
- Tool exceptions are captured as failed results with a safe error message.
- A provider that returns neither a tool call nor a valid final response raises a clear `ValueError`.
- `max_tool_calls` prevents infinite loops.
- Empty retrieval results remain valid and are visible as an empty result, not silently converted into facts.

## Testing and Evaluation

Tests cover registry dispatch, argument validation, offline tool calling, unknown tools, call limits, real-provider payload parsing, workflow trace integration, API/report serialization, and evaluation scores. The full suite must remain dependency-light; FastAPI tests continue to be optional through the existing environment.

The release gate is:

- Full pytest suite passes.
- Evaluation cases include at least one tool call and a complete trace.
- `compileall` passes.
- `git diff --check` passes.
- CLI offline demo produces Markdown and JSON containing tool events.

## Compatibility

The public `run_research`, `RunService`, repository, API routes, and existing Demo Provider behavior remain compatible. The version advances to `0.4.0` only after the new trace and tool-calling behavior is verified.
