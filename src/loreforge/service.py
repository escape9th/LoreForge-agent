from __future__ import annotations

import json
from pathlib import Path

from .adapters import CorpusSearchProvider, OpenAICompatibleModelProvider, OpenAICompatibleToolCallingProvider
from .config import Settings
from .domain import ResearchPackage
from .repository import RunRepository, RunSummary
from .workflow import run_research


class RunService:
    def __init__(
        self,
        repository: RunRepository,
        *,
        settings: Settings | None = None,
    ):
        self.repository = repository
        self.settings = settings or Settings.from_env()

    def create_run(
        self,
        prompt: str,
        *,
        corpus: str | Path | None = None,
        max_tool_calls: int | None = None,
    ) -> ResearchPackage:
        search = CorpusSearchProvider.from_json(corpus) if corpus else None
        model = (
            OpenAICompatibleModelProvider(
                endpoint=self.settings.model_endpoint,
                api_key=self.settings.model_api_key,
                model=self.settings.model_name,
            )
            if not self.settings.use_demo_model
            else None
        )
        tool_provider = (
            OpenAICompatibleToolCallingProvider(
                endpoint=self.settings.model_endpoint,
                api_key=self.settings.model_api_key,
                model=self.settings.model_name,
            )
            if not self.settings.use_demo_model
            else None
        )
        package = run_research(
            prompt,
            search=search,
            model=model,
            tool_provider=tool_provider,
            max_tool_calls=max_tool_calls or self.settings.max_tool_calls,
        )
        self.repository.save(package)
        return package

    def get_run(self, run_id: str) -> ResearchPackage | None:
        record = self.repository.get(run_id)
        if record is None:
            return None
        return ResearchPackage.from_dict(json.loads(record["payload_json"]))

    def list_runs(self, limit: int = 20) -> list[RunSummary]:
        return self.repository.list_recent(limit)
