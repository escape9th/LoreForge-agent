from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .domain import Evidence, Source, ToolTraceEvent
from .tools import ToolRegistry


class ToolCallingProvider(Protocol):
    def next_action(
        self,
        prompt: str,
        context: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class ToolAgentResult:
    sources: list[Source]
    evidence: list[Evidence]
    trace: list[ToolTraceEvent]
    context: list[dict[str, Any]] = field(default_factory=list)
    stopped_reason: str = "final"


class ToolCallingAgent:
    def __init__(
        self,
        provider: ToolCallingProvider,
        registry: ToolRegistry,
        *,
        max_tool_calls: int = 6,
    ):
        self.provider = provider
        self.registry = registry
        self.max_tool_calls = max(1, max_tool_calls)

    def run(self, prompt: str) -> ToolAgentResult:
        context: list[dict[str, Any]] = []
        trace: list[ToolTraceEvent] = []
        sources: dict[str, Source] = {}
        evidence: dict[str, Evidence] = {}
        stopped_reason = "final"

        for _ in range(self.max_tool_calls):
            action = self.provider.next_action(prompt, context, self.registry.schemas())
            if action.get("type") == "final":
                stopped_reason = "final"
                break
            if action.get("type") != "tool_call":
                raise ValueError("tool provider action must be a tool_call or final object")
            name = str(action.get("name", ""))
            arguments = action.get("arguments", {})
            result = self.registry.invoke(name, arguments)
            trace.append(
                ToolTraceEvent(
                    tool_name=name,
                    arguments=arguments if isinstance(arguments, dict) else {},
                    result=result.to_dict(),
                    status="success" if result.ok else "error",
                )
            )
            context.append({"action": action, "result": result.to_dict()})
            if result.ok:
                for item in result.data.get("sources", []):
                    source = Source(**item)
                    sources[source.source_id] = source
                    evidence[source.source_id] = Evidence(
                        source_id=source.source_id,
                        quote=source.text,
                    )
                source_data = result.data.get("source")
                if source_data:
                    source = Source(**source_data)
                    sources[source.source_id] = source
                    evidence[source.source_id] = Evidence(
                        source_id=source.source_id,
                        quote=source.text,
                    )
        else:
            stopped_reason = "tool_call_limit"

        return ToolAgentResult(
            sources=list(sources.values()),
            evidence=list(evidence.values()),
            trace=trace,
            context=context,
            stopped_reason=stopped_reason,
        )
