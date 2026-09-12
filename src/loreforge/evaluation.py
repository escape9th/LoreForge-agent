from __future__ import annotations

from .demo import DemoModelProvider, DemoSearchProvider
from .workflow import run_research


def score_prompt(prompt: str) -> tuple[int, list[str]]:
    package = run_research(
        prompt,
        search=DemoSearchProvider(),
        model=DemoModelProvider(),
    )
    checks = {
        "有研究问题": bool(package.questions),
        "有来源": bool(package.sources),
        "有证据": bool(package.evidence),
        "事实与提案分离": bool(
            package.blueprint.facts and package.blueprint.proposals
        ),
        "有核验结果": package.verification.checked_claims > 0,
    }
    passed = [name for name, ok in checks.items() if ok]
    return len(passed), passed
