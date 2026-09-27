import json

from loreforge.config import Settings
from loreforge.cli import main


def test_run_command_writes_markdown_and_json(tmp_path, capsys):
    assert main(
        [
            "run",
            "设计一个受海洋灾变影响的漂浮城市游戏世界观",
            "--out",
            str(tmp_path),
        ]
    ) == 0

    files = list(tmp_path.iterdir())
    assert any(file.suffix == ".md" for file in files)
    json_file = next(file for file in files if file.suffix == ".json")
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert data["verification"]["checked_claims"] >= 2
    assert data["tool_trace"]
    assert "研究完成" in capsys.readouterr().out


def test_run_command_accepts_custom_corpus(tmp_path):
    corpus_path = tmp_path / "corpus.json"
    corpus_path.write_text(
        json.dumps(
            [
                {
                    "source_id": "custom-1",
                    "title": "Custom source",
                    "url": "https://example.test/custom",
                    "summary": "custom",
                    "text": "custom evidence",
                }
            ]
        ),
        encoding="utf-8",
    )

    assert main(
        [
            "run",
            "custom brief",
            "--corpus",
            str(corpus_path),
            "--out",
            str(tmp_path / "reports"),
        ]
    ) == 0
    json_file = next(
        file for file in (tmp_path / "reports").iterdir() if file.suffix == ".json"
    )
    assert json.loads(json_file.read_text(encoding="utf-8"))["sources"][0]["source_id"] == "custom-1"


def test_run_command_persists_history_when_database_is_provided(tmp_path, capsys):
    database = tmp_path / "history.sqlite3"

    assert main(
        [
            "run",
            "设计一个资源冲突任务",
            "--out",
            str(tmp_path / "reports"),
            "--db",
            str(database),
        ]
    ) == 0

    output = capsys.readouterr().out
    assert database.exists()
    assert "数据库记录" in output


def test_history_and_show_commands_read_database(tmp_path, capsys):
    database = tmp_path / "history.sqlite3"
    main(
        [
            "run",
            "设计一个资源冲突任务",
            "--out",
            str(tmp_path / "reports"),
            "--db",
            str(database),
        ]
    )
    capsys.readouterr()

    assert main(["history", "--db", str(database)]) == 0
    history_output = capsys.readouterr().out
    assert "资源冲突" in history_output

    import sqlite3

    with sqlite3.connect(database) as connection:
        run_id = connection.execute("SELECT run_id FROM runs").fetchone()[0]

    assert main(["show", run_id, "--db", str(database)]) == 0
    assert run_id in capsys.readouterr().out


def test_run_command_passes_real_tool_provider_and_call_limit(tmp_path, monkeypatch):
    captured = {}

    def fake_run_research(prompt, **kwargs):
        captured.update(kwargs)
        from loreforge.demo import DemoModelProvider, DemoSearchProvider
        from loreforge.workflow import run_research

        return run_research(
            prompt,
            search=DemoSearchProvider(),
            model=DemoModelProvider(),
            max_tool_calls=1,
        )

    monkeypatch.setattr(
        "loreforge.cli.Settings.from_env",
        lambda: Settings("https://model.test", "secret", "model", 6),
    )
    monkeypatch.setattr("loreforge.cli.run_research", fake_run_research)

    assert main([
        "run",
        "设计一个世界观",
        "--out",
        str(tmp_path),
        "--max-tool-calls",
        "3",
    ]) == 0

    assert captured["tool_provider"].model == "model"
    assert captured["max_tool_calls"] == 3
