from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .demo import ModelProvider, SearchProvider
from .toolcalling import ToolCallingProvider
from .domain import (
    Claim,
    CreativeBlueprint,
    ResearchBrief,
    ResearchQuestion,
    Source,
)
from .verification import _terms


def _normalize_url(url: str) -> str:
    return url.rstrip("/").lower()


@dataclass
class CorpusSearchProvider(SearchProvider):
    sources: list[Source]

    @classmethod
    def from_json(cls, path: str | Path) -> "CorpusSearchProvider":
        raw_sources = json.loads(Path(path).read_text(encoding="utf-8"))
        sources: list[Source] = []
        seen: set[str] = set()
        for item in raw_sources:
            source = Source(
                source_id=str(item["source_id"]),
                title=str(item["title"]),
                url=str(item["url"]),
                summary=str(item.get("summary", "")),
                text=str(item["text"]),
            )
            key = _normalize_url(source.url)
            if key not in seen:
                seen.add(key)
                sources.append(source)
        return cls(sources=sources)

    def search(self, query: str, limit: int = 3) -> list[Source]:
        keywords = _terms(query)
        ranked = sorted(
            self.sources,
            key=lambda source: sum(
                keyword in _terms(source.title + " " + source.summary + " " + source.text)
                for keyword in keywords
            ),
            reverse=True,
        )
        return ranked[:limit]


Transport = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]


def _urllib_transport(
    endpoint: str,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _parse_json_content(content: Any) -> dict[str, Any]:
    if not isinstance(content, str):
        raise ValueError("model response content must be a JSON string")
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("model response must contain valid JSON content") from exc
    if not isinstance(parsed, dict):
        raise ValueError("model response JSON must be an object")
    return parsed


@dataclass
class OpenAICompatibleModelProvider(ModelProvider):
    endpoint: str
    api_key: str
    model: str
    transport: Transport = _urllib_transport

    def _complete(self, system: str, user: str) -> dict[str, Any]:
        response = self.transport(
            self.endpoint,
            {"Authorization": f"Bearer {self.api_key}"},
            {
                "model": self.model,
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("model response must contain choices.message.content") from exc
        return _parse_json_content(content)

    def plan(self, brief: ResearchBrief) -> list[ResearchQuestion]:
        payload = self._complete(
            "Return JSON only with a 'questions' array of short research questions.",
            brief.prompt,
        )
        questions = payload.get("questions")
        if not isinstance(questions, list) or not all(
            isinstance(item, str) and item.strip() for item in questions
        ):
            raise ValueError("model JSON must contain a non-empty string questions array")
        return [ResearchQuestion(text=item.strip()) for item in questions[:5]]

    def draft(
        self,
        brief: ResearchBrief,
        questions: list[ResearchQuestion],
        sources: list[Source],
    ) -> CreativeBlueprint:
        source_text = "\n".join(f"- {source.title}: {source.text}" for source in sources)
        payload = self._complete(
            "Return JSON only with title, facts, proposals, and sections. "
            "facts and proposals must be arrays of strings; sections must be an object.",
            f"Brief: {brief.prompt}\nQuestions: {[q.text for q in questions]}\n"
            f"Sources:\n{source_text}",
        )
        try:
            title = str(payload["title"])
            facts = [Claim(text=str(item), kind="fact") for item in payload["facts"]]
            proposals = [
                Claim(text=str(item), kind="proposal") for item in payload["proposals"]
            ]
            sections = {str(key): str(value) for key, value in payload["sections"].items()}
        except (KeyError, TypeError, AttributeError) as exc:
            raise ValueError(
                "model JSON must contain title, facts, proposals, and sections"
            ) from exc
        return CreativeBlueprint(
            title=title,
            facts=facts,
            proposals=proposals,
            sections=sections,
        )


@dataclass
class OpenAICompatibleToolCallingProvider(ToolCallingProvider):
    endpoint: str
    api_key: str
    model: str
    transport: Transport = _urllib_transport

    def next_action(
        self,
        prompt: str,
        context: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
    ) -> dict[str, Any]:
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are a research agent. Use tools when evidence is needed. "
                    "Return a final object with type=final when done."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        for item in context:
            action = item["action"]
            call_id = str(action.get("id") or f"loreforge-{len(messages)}")
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {
                                "name": action["name"],
                                "arguments": json.dumps(
                                    action.get("arguments", {}),
                                    ensure_ascii=False,
                                ),
                            },
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": json.dumps(item["result"], ensure_ascii=False),
                }
            )
        response = self.transport(
            self.endpoint,
            {"Authorization": f"Bearer {self.api_key}"},
            {
                "model": self.model,
                "temperature": 0.2,
                "messages": messages,
                "tools": tool_schemas,
                "tool_choice": "auto",
            },
        )
        try:
            message = response["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("tool-calling response must contain choices.message") from exc
        tool_calls = message.get("tool_calls")
        if tool_calls:
            call = tool_calls[0]
            try:
                function = call["function"]
                arguments = _parse_json_content(function.get("arguments", "{}"))
                return {
                    "type": "tool_call",
                    "id": str(call.get("id", "")),
                    "name": str(function["name"]),
                    "arguments": arguments,
                }
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("tool call must contain a function name and JSON arguments") from exc
        content = message.get("content")
        payload = _parse_json_content(content)
        if payload.get("type") != "final":
            raise ValueError("final tool-calling response must have type=final")
        return payload
