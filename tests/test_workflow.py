from loreforge.demo import DemoSearchProvider, DemoModelProvider
from loreforge.workflow import run_research


def test_demo_workflow_builds_evidence_backed_package():
    package = run_research(
        "设计一个受海洋灾变影响的漂浮城市游戏世界观",
        search=DemoSearchProvider(),
        model=DemoModelProvider(),
    )

    assert package.brief.prompt.startswith("设计一个")
    assert package.sources
    assert package.evidence
    assert package.blueprint.facts
    assert package.blueprint.proposals
    assert package.verification.checked_claims >= 1
    assert package.verification.unverified_claims == 0
    assert [event.stage for event in package.trace] == [
        "plan",
        "gather",
        "extract",
        "draft",
        "verify",
    ]


def test_duplicate_sources_are_removed():
    package = run_research(
        "漂浮城市",
        search=DemoSearchProvider(),
        model=DemoModelProvider(),
    )
    urls = [source.url for source in package.sources]
    assert len(urls) == len(set(urls))
