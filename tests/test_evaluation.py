from loreforge.demo import DemoModelProvider, DemoSearchProvider
from loreforge.evaluation import score_prompt
from loreforge.workflow import run_research


def test_demo_case_meets_minimum_quality_bar():
    package = run_research(
        "设计一个受海洋灾变影响的漂浮城市游戏世界观",
        search=DemoSearchProvider(),
        model=DemoModelProvider(),
    )
    assert len(package.sources) >= 2
    assert len(package.evidence) >= 2
    assert package.blueprint.proposals
    assert package.verification.checked_claims == len(package.blueprint.facts)
    assert package.verification.supported_claims >= 2


def test_shared_evaluation_scores_a_prompt():
    score, passed = score_prompt("设计一个能体现资源冲突的游戏任务线")

    assert score == 7
    assert "事实与提案分离" in passed
    assert "有工具调用轨迹" in passed
