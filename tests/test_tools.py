import pytest

from loreforge.demo import DemoSearchProvider
from loreforge.tools import ToolRegistry, build_default_registry


def test_registry_lists_json_tool_schemas_and_dispatches_search():
    registry = build_default_registry(DemoSearchProvider())

    schemas = registry.schemas()
    result = registry.invoke("corpus_search", {"query": "漂浮城市", "limit": 2})

    assert {schema["function"]["name"] for schema in schemas} == {
        "corpus_search",
        "source_lookup",
        "citation_check",
        "consistency_check",
    }
    assert result.ok is True
    assert len(result.data["sources"]) == 2


def test_registry_returns_structured_failures_for_unknown_and_invalid_calls():
    registry = build_default_registry(DemoSearchProvider())

    unknown = registry.invoke("missing_tool", {})
    invalid = registry.invoke("corpus_search", {"limit": 2})

    assert unknown.ok is False
    assert "unknown tool" in unknown.error
    assert invalid.ok is False
    assert "query" in invalid.error


def test_source_lookup_requires_a_known_source():
    registry = build_default_registry(DemoSearchProvider())

    result = registry.invoke("source_lookup", {"source_id": "missing"})

    assert result.ok is False
    assert "missing" in result.error
