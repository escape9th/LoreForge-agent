import json

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
