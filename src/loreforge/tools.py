from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

from .demo import SearchProvider
from .domain import Claim, Evidence, Source
from .verification import verify_claims


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]

    def to_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    ok: bool
    data: dict[str, Any]
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "ok": self.ok,
            "data": self.data,
            "error": self.error,
        }


@dataclass(frozen=True)
class Tool:
    spec: ToolSpec
    handler: Callable[..., dict[str, Any]]
    required: tuple[str, ...] = ()

    def invoke(self, arguments: dict[str, Any]) -> ToolResult:
        if not isinstance(arguments, dict):
            return ToolResult(self.spec.name, False, {}, "arguments must be an object")
        missing = [name for name in self.required if name not in arguments]
        if missing:
            return ToolResult(
                self.spec.name,
                False,
                {},
                f"missing required arguments: {', '.join(missing)}",
            )
        properties = self.spec.parameters.get("properties", {})
        python_types = {
            "string": str,
            "integer": int,
            "array": list,
            "object": dict,
            "boolean": bool,
        }
        for name, value in arguments.items():
            schema = properties.get(name)
            if schema is None:
                return ToolResult(self.spec.name, False, {}, f"unknown argument: {name}")
            expected_name = schema.get("type")
            expected_type = python_types.get(expected_name)
            if expected_type is not None and (
                not isinstance(value, expected_type)
                or expected_name == "integer" and isinstance(value, bool)
            ):
                return ToolResult(
                    self.spec.name,
                    False,
                    {},
                    f"argument {name} must be {expected_name}",
                )
            if "minimum" in schema and value < schema["minimum"]:
                return ToolResult(self.spec.name, False, {}, f"argument {name} is below minimum")
            if "maximum" in schema and value > schema["maximum"]:
                return ToolResult(self.spec.name, False, {}, f"argument {name} exceeds maximum")
        try:
            return ToolResult(self.spec.name, True, self.handler(**arguments))
        except Exception as exc:  # tool failures become inspectable Agent results
            return ToolResult(self.spec.name, False, {}, str(exc))


class ToolRegistry:
    def __init__(self, tools: list[Tool]):
        self._tools = {tool.spec.name: tool for tool in tools}

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.spec.to_schema() for tool in self._tools.values()]

    def invoke(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(name, False, {}, f"unknown tool: {name}")
        return tool.invoke(arguments)


def _source_dict(source: Source) -> dict[str, str]:
    return asdict(source)


def _all_sources(provider: SearchProvider) -> list[Source]:
    catalog = getattr(provider, "catalog", None)
    sources = getattr(provider, "sources", None)
    values = catalog or sources or ()
    return list(values)


def build_default_registry(search: SearchProvider) -> ToolRegistry:
    source_cache = {source.source_id: source for source in _all_sources(search)}

    def corpus_search(query: str, limit: int = 3) -> dict[str, Any]:
        bounded_limit = max(1, min(int(limit), 10))
        sources = search.search(query, limit=bounded_limit)
        source_cache.update({source.source_id: source for source in sources})
        return {
            "query": query,
            "sources": [_source_dict(source) for source in sources],
        }

    def source_lookup(source_id: str) -> dict[str, Any]:
        source = source_cache.get(source_id)
        if source is None:
            raise ValueError(f"source not found: {source_id}")
        return {"source": _source_dict(source)}

    def citation_check(claims: list[str], evidence: list[dict[str, str]]) -> dict[str, Any]:
        report = verify_claims(
            [Claim(text=str(claim)) for claim in claims],
            [Evidence(source_id=str(item["source_id"]), quote=str(item["quote"])) for item in evidence],
        )
        return {"report": asdict(report)}

    def consistency_check(text: str, constraints: list[str] | None = None) -> dict[str, Any]:
        constraints = constraints or []
        normalized = text.lower()
        conflicts = [constraint for constraint in constraints if constraint.lower() not in normalized]
        return {
            "consistent": not conflicts,
            "checked_constraints": len(constraints),
            "conflicts": conflicts,
        }

    return ToolRegistry(
        [
            Tool(
                ToolSpec(
                    "corpus_search",
                    "Search the configured creative research corpus.",
                    {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                        },
                        "required": ["query"],
                    },
                ),
                corpus_search,
                ("query",),
            ),
            Tool(
                ToolSpec(
                    "source_lookup",
                    "Load the full text of one corpus source by source_id.",
                    {
                        "type": "object",
                        "properties": {"source_id": {"type": "string"}},
                        "required": ["source_id"],
                    },
                ),
                source_lookup,
                ("source_id",),
            ),
            Tool(
                ToolSpec(
                    "citation_check",
                    "Check whether claims have overlapping evidence.",
                    {
                        "type": "object",
                        "properties": {
                            "claims": {"type": "array", "items": {"type": "string"}},
                            "evidence": {"type": "array", "items": {"type": "object"}},
                        },
                        "required": ["claims", "evidence"],
                    },
                ),
                citation_check,
                ("claims", "evidence"),
            ),
            Tool(
                ToolSpec(
                    "consistency_check",
                    "Check whether text contains each requested worldbuilding constraint.",
                    {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "constraints": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["text"],
                    },
                ),
                consistency_check,
                ("text",),
            ),
        ]
    )
