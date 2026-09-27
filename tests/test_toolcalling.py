from loreforge.demo import DemoSearchProvider, DemoToolCallingProvider
from loreforge.toolcalling import ToolCallingAgent
from loreforge.tools import build_default_registry


def test_offline_agent_calls_tools_and_returns_sources_and_trace():
    agent = ToolCallingAgent(
        DemoToolCallingProvider(),
        build_default_registry(DemoSearchProvider()),
    )

    result = agent.run("设计一个资源冲突的游戏任务线")

    assert result.sources
    assert result.evidence
    assert [event.tool_name for event in result.trace] == [
        "corpus_search",
        "source_lookup",
    ]
    assert all(event.status == "success" for event in result.trace)


def test_agent_records_unknown_tool_failure_and_stops_at_call_limit():
    class BrokenProvider:
        def next_action(self, prompt, context, tool_schemas):
            return {"type": "tool_call", "name": "missing", "arguments": {}}

    agent = ToolCallingAgent(
        BrokenProvider(),
        build_default_registry(DemoSearchProvider()),
        max_tool_calls=2,
    )

    result = agent.run("anything")

    assert len(result.trace) == 2
    assert all(event.status == "error" for event in result.trace)
    assert result.stopped_reason == "tool_call_limit"
