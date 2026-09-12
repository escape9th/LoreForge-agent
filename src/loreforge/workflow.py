from __future__ import annotations

from .demo import DemoModelProvider, DemoSearchProvider, ModelProvider, SearchProvider
from .domain import Evidence, ResearchBrief, ResearchPackage, ResearchState, TraceEvent
from .verification import verify_claims


def _mark(state: ResearchState, stage: str, detail: str) -> None:
    state.trace.append(TraceEvent(stage=stage, status="complete", detail=detail))


def run_research(
    prompt: str,
    *,
    search: SearchProvider | None = None,
    model: ModelProvider | None = None,
    max_questions: int = 3,
    max_sources: int = 6,
) -> ResearchPackage:
    brief = ResearchBrief.from_prompt(prompt)
    search = search or DemoSearchProvider()
    model = model or DemoModelProvider()
    state = ResearchState.start(brief)

    state.questions = model.plan(brief)[:max_questions]
    _mark(state, "plan", f"拆解出 {len(state.questions)} 个研究问题")

    gathered: list = []
    for question in state.questions:
        gathered.extend(search.search(question.text, limit=2))
    unique: dict[str, object] = {}
    for source in gathered:
        unique.setdefault(source.url.rstrip("/").lower(), source)
    state.sources = list(unique.values())[:max_sources]
    _mark(state, "gather", f"收集并去重 {len(state.sources)} 个来源")

    state.evidence = [
        Evidence(source_id=source.source_id, quote=source.text)
        for source in state.sources
    ]
    _mark(state, "extract", f"提取 {len(state.evidence)} 条证据")

    state.blueprint = model.draft(brief, state.questions, state.sources)
    _mark(state, "draft", "生成事实与创作提案分离的蓝图")

    state.verification = verify_claims(state.blueprint.facts, state.evidence)
    _mark(
        state,
        "verify",
        f"核验 {state.verification.checked_claims} 条事实声明",
    )

    return ResearchPackage(
        brief=brief,
        questions=state.questions,
        sources=state.sources,
        evidence=state.evidence,
        blueprint=state.blueprint,
        verification=state.verification,
        trace=state.trace,
    )

