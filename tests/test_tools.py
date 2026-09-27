from loreforge.demo import DemoSearchProvider
from loreforge.domain import Source
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


def test_registry_validates_argument_types_and_numeric_bounds():
    registry = build_default_registry(DemoSearchProvider())

    wrong_type = registry.invoke("corpus_search", {"query": "city", "limit": "2"})
    out_of_range = registry.invoke("corpus_search", {"query": "city", "limit": 99})

    assert wrong_type.ok is False
    assert "limit" in wrong_type.error
    assert "integer" in wrong_type.error
    assert out_of_range.ok is False
    assert "maximum" in out_of_range.error


def test_source_lookup_requires_a_known_source():
    registry = build_default_registry(DemoSearchProvider())

    result = registry.invoke("source_lookup", {"source_id": "missing"})

    assert result.ok is False
    assert "missing" in result.error


def test_source_lookup_uses_sources_returned_by_an_opaque_search_provider():
    source = Source(
        source_id="remote-1",
        title="Remote source",
        url="https://example.test/remote",
        summary="Remote result",
        text="Full remote evidence",
    )

    class OpaqueSearchProvider:
        def search(self, query, limit=3):
            return [source][:limit]

    registry = build_default_registry(OpaqueSearchProvider())

    registry.invoke("corpus_search", {"query": "remote"})
    result = registry.invoke("source_lookup", {"source_id": "remote-1"})

    assert result.ok is True
    assert result.data["source"]["text"] == "Full remote evidence"


def test_citation_and_consistency_tools_return_structured_checks():
    registry = build_default_registry(DemoSearchProvider())

    citation = registry.invoke(
        "citation_check",
        {
            "claims": ["潮汐能具有周期性和可预测性。"],
            "evidence": [
                {
                    "source_id": "ocean-city-01",
                    "quote": "潮汐能具有周期性和可预测性，适合提供稳定电力。",
                }
            ],
        },
    )
    consistency = registry.invoke(
        "consistency_check",
        {"text": "城市依靠潮汐能运行。", "constraints": ["潮汐能", "淡水配给"]},
    )

    assert citation.data["report"]["supported_claims"] == 1
    assert consistency.data["consistent"] is False
    assert consistency.data["conflicts"] == ["淡水配给"]
