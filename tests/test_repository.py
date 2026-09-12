import json

from loreforge.demo import DemoModelProvider, DemoSearchProvider
from loreforge.repository import RunRepository
from loreforge.workflow import run_research


def make_package(prompt: str):
    return run_research(
        prompt,
        search=DemoSearchProvider(),
        model=DemoModelProvider(),
    )


def test_repository_creates_database_and_round_trips_run(tmp_path):
    database = tmp_path / "history.sqlite3"
    repository = RunRepository(database)
    package = make_package("设计一个漂浮城市世界观")

    summary = repository.save(package)

    assert database.exists()
    assert summary.run_id == package.brief.run_id
    payload = repository.get(package.brief.run_id)
    assert payload is not None
    assert json.loads(payload["payload_json"])["brief"]["prompt"] == "设计一个漂浮城市世界观"


def test_repository_lists_newest_runs_first(tmp_path):
    repository = RunRepository(tmp_path / "history.sqlite3")
    older = make_package("设计一个失忆角色")
    newer = make_package("设计一个资源冲突任务")

    repository.save(older)
    repository.save(newer)

    summaries = repository.list_recent()

    assert [item.run_id for item in summaries] == [
        newer.brief.run_id,
        older.brief.run_id,
    ]


def test_repository_returns_none_for_unknown_run(tmp_path):
    repository = RunRepository(tmp_path / "history.sqlite3")

    assert repository.get("missing-run") is None
