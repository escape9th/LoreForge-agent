from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model_endpoint: str | None = None
    model_api_key: str | None = None
    model_name: str = "default-model"

    @property
    def use_demo_model(self) -> bool:
        return not (self.model_endpoint and self.model_api_key)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            model_endpoint=os.getenv("LOREFORGE_MODEL_ENDPOINT"),
            model_api_key=os.getenv("LOREFORGE_MODEL_API_KEY"),
            model_name=os.getenv("LOREFORGE_MODEL_NAME", "default-model"),
        )

