# LoreForge

LoreForge is a small, reproducible, evidence-backed creative research Agent.

It turns a creative brief into research questions, searches a bounded corpus, preserves evidence, separates factual claims from creative proposals, and verifies whether factual claims have supporting evidence.

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

## Why It Is Useful

LoreForge is not just a chat wrapper. It exposes a typed research state, bounded workflow stages, provider interfaces, evidence records, verification output, and a trace that can be inspected or exported.

Workflow:

```text
plan -> gather -> extract -> draft -> verify
```

## Keywords

`AI Agent` `LLM` `RAG` `agent workflow` `creative writing` `worldbuilding`
`game development` `anime` `knowledge grounding` `citation` `evaluation`
`Python` `中文 Agent` `Chinese LLM` `智能体` `检索增强生成`

See the Chinese README and [`docs/architecture.md`](docs/architecture.md) for implementation details.
