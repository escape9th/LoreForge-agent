from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .domain import ResearchPackage


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    prompt: str
    title: str
    created_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "run_id": self.run_id,
            "prompt": self.prompt,
            "title": self.title,
            "created_at": self.created_at,
        }


class RunRepository:
    def __init__(self, database: str | Path):
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )

    def save(self, package: ResearchPackage) -> RunSummary:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO runs
                    (run_id, prompt, title, created_at, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    package.brief.run_id,
                    package.brief.prompt,
                    package.blueprint.title,
                    created_at,
                    json.dumps(package.to_dict(), ensure_ascii=False),
                ),
            )
        return RunSummary(
            run_id=package.brief.run_id,
            prompt=package.brief.prompt,
            title=package.blueprint.title,
            created_at=created_at,
        )

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT run_id, prompt, title, created_at, payload_json
                FROM runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        return dict(row) if row is not None else None

    def list_recent(self, limit: int = 20) -> list[RunSummary]:
        bounded_limit = max(1, min(limit, 100))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT run_id, prompt, title, created_at
                FROM runs
                ORDER BY created_at DESC, rowid DESC
                LIMIT ?
                """,
                (bounded_limit,),
            ).fetchall()
        return [
            RunSummary(
                run_id=row["run_id"],
                prompt=row["prompt"],
                title=row["title"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
