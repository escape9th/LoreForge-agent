from __future__ import annotations

import os
from typing import Any

from . import __version__
from .domain import ResearchPackage
from .repository import RunRepository
from .service import RunService

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:  # pragma: no cover - exercised in minimal installs
    FastAPI = None
    HTTPException = None
    BaseModel = None


if BaseModel is not None:

    class RunRequest(BaseModel):
        prompt: str
        corpus: str | None = None
        max_tool_calls: int | None = None

else:

    class RunRequest:  # type: ignore[no-redef]
        pass


def _default_database() -> str:
    return os.getenv("LOREFORGE_HISTORY_DB", "loreforge.db")


def create_app(
    *,
    repository: RunRepository | None = None,
    service: RunService | None = None,
) -> Any:
    if FastAPI is None:
        raise RuntimeError(
            "FastAPI is required for the API; install loreforge[api] first"
        )

    if service is None:
        service = RunService(repository or RunRepository(_default_database()))

    app = FastAPI(
        title="LoreForge API",
        description="Evidence-backed creative research Agent service.",
        version=__version__,
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.post("/runs")
    def create_run(request: RunRequest) -> dict[str, Any]:
        try:
            package = service.create_run(
                request.prompt,
                corpus=request.corpus,
                max_tool_calls=request.max_tool_calls,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {
            "run_id": package.brief.run_id,
            "title": package.blueprint.title,
            "package": package.to_dict(),
        }

    @app.get("/runs")
    def list_runs(limit: int = 20) -> dict[str, Any]:
        summaries = service.list_runs(limit)
        return {
            "runs": [summary.to_dict() for summary in summaries],
            "count": len(summaries),
        }

    @app.get("/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, Any]:
        package: ResearchPackage | None = service.get_run(run_id)
        if package is None:
            raise HTTPException(status_code=404, detail="run not found")
        return package.to_dict()

    return app
