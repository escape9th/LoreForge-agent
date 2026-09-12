from loreforge.repository import RunRepository
from loreforge.service import RunService


def test_service_creates_and_reads_a_persisted_run(tmp_path):
    repository = RunRepository(tmp_path / "history.sqlite3")
    service = RunService(repository)

    package = service.create_run("设计一个漂浮城市世界观")
    loaded = service.get_run(package.brief.run_id)

    assert loaded is not None
    assert loaded.brief.run_id == package.brief.run_id
    assert loaded.blueprint.title == package.blueprint.title
    assert loaded.verification.checked_claims == package.verification.checked_claims


def test_service_lists_saved_run_summaries(tmp_path):
    repository = RunRepository(tmp_path / "history.sqlite3")
    service = RunService(repository)

    package = service.create_run("设计一个资源冲突任务")

    summaries = service.list_runs()

    assert summaries[0].run_id == package.brief.run_id
    assert summaries[0].title == package.blueprint.title
