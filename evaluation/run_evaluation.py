from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from loreforge.demo import DemoModelProvider, DemoSearchProvider
from loreforge.workflow import run_research


CASES = [
    "设计一个受海洋灾变影响的漂浮城市游戏世界观",
    "为一个资源稀缺的海上社区设计游戏冲突",
    "为一名失去记忆的动漫角色设计人物弧光",
    "设计一个能体现资源冲突的游戏任务线",
]


def score(prompt: str) -> tuple[int, list[str]]:
    package = run_research(
        prompt,
        search=DemoSearchProvider(),
        model=DemoModelProvider(),
    )
    checks = {
        "有研究问题": bool(package.questions),
        "有来源": bool(package.sources),
        "有证据": bool(package.evidence),
        "事实与提案分离": bool(package.blueprint.facts and package.blueprint.proposals),
        "有核验结果": package.verification.checked_claims > 0,
    }
    passed = [name for name, ok in checks.items() if ok]
    return len(passed), passed


if __name__ == "__main__":
    for case in CASES:
        total, passed = score(case)
        print(f"[{total}/5] {case}")
        print("  " + "、".join(passed))
    print(f"通过 {len(CASES)} 个 Demo 评测案例")
