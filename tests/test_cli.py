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
    assert data["verification"]["checked_claims"] == 3
    assert "研究完成" in capsys.readouterr().out

