from fastapi.testclient import TestClient

from loreforge.api import create_app
from loreforge.repository import RunRepository


def client_for(tmp_path):
    repository = RunRepository(tmp_path / "history.sqlite3")
    return TestClient(create_app(repository=repository))


def test_health_endpoint_reports_service_version(tmp_path):
    response = client_for(tmp_path).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.4.0"


def test_create_list_and_get_run(tmp_path):
    client = client_for(tmp_path)

    created = client.post("/runs", json={"prompt": "设计一个资源冲突任务"})
    run_id = created.json()["run_id"]

    assert created.status_code == 200
    assert created.json()["package"]["brief"]["run_id"] == run_id
    listed = client.get("/runs")
    assert listed.status_code == 200
    assert listed.json()["runs"][0]["run_id"] == run_id

    detail = client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["brief"]["run_id"] == run_id


def test_api_rejects_blank_prompt_and_unknown_run(tmp_path):
    client = client_for(tmp_path)

    blank = client.post("/runs", json={"prompt": "   "})
    missing = client.get("/runs/missing-run")

    assert blank.status_code == 422
    assert missing.status_code == 404


def test_api_accepts_a_tool_call_limit(tmp_path):
    response = client_for(tmp_path).post(
        "/runs",
        json={"prompt": "设计一个游戏任务", "max_tool_calls": 1},
    )

    assert response.status_code == 200
    assert len(response.json()["package"]["tool_trace"]) == 1
