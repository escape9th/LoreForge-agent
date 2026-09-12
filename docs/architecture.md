# Architecture

## Boundary

LoreForge separates three kinds of concerns:

1. Domain objects describe what a research run contains.
2. Providers describe how planning, searching, and drafting happen.
3. Workflow code controls order, limits, and verification.

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

