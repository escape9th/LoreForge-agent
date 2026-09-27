import json

import pytest

from loreforge.adapters import (
    CorpusSearchProvider,
    OpenAICompatibleModelProvider,
    OpenAICompatibleToolCallingProvider,
)
from loreforge.domain import ResearchBrief


def test_corpus_provider_loads_and_deduplicates_json_sources(tmp_path):
    corpus = [
        {
            "source_id": "one",
            "title": "Tidal energy",
            "url": "https://example.test/tidal/",
            "summary": "Predictable tidal power for coastal infrastructure.",
            "text": "Tidal power is predictable and can support infrastructure.",
        },
        {
            "source_id": "duplicate",
            "title": "Tidal energy duplicate",
            "url": "https://example.test/tidal",
            "summary": "Same source with a normalized URL.",
            "text": "Tidal power remains predictable.",
        },
    ]
    path = tmp_path / "corpus.json"
    path.write_text(json.dumps(corpus), encoding="utf-8")

    provider = CorpusSearchProvider.from_json(path)
    results = provider.search("tidal power", limit=10)

    assert len(results) == 1
    assert results[0].url == "https://example.test/tidal/"


def test_openai_compatible_provider_parses_structured_plan():
    calls = []

    def transport(endpoint, headers, payload):
        calls.append((endpoint, headers, payload))
        return {
            "choices": [
                {
                    "message": {
                        "content": '{"questions": ["How does the city get power?"]}'
                    }
                }
            ]
        }

    provider = OpenAICompatibleModelProvider(
        endpoint="https://model.example.test/v1/chat/completions",
        api_key="test-key",
        model="demo-model",
        transport=transport,
    )
    questions = provider.plan(ResearchBrief.from_prompt("floating city"))

    assert [question.text for question in questions] == [
        "How does the city get power?"
    ]
    assert calls[0][0].endswith("/chat/completions")
    assert calls[0][1]["Authorization"] == "Bearer test-key"
    assert calls[0][2]["model"] == "demo-model"


def test_openai_compatible_provider_rejects_malformed_json():
    provider = OpenAICompatibleModelProvider(
        endpoint="https://model.example.test/v1/chat/completions",
        api_key="test-key",
        model="demo-model",
        transport=lambda endpoint, headers, payload: {
            "choices": [{"message": {"content": "not json"}}]
        },
    )

    with pytest.raises(ValueError, match="JSON"):
        provider.plan(ResearchBrief.from_prompt("floating city"))


def test_openai_compatible_provider_accepts_json_code_fence():
    provider = OpenAICompatibleModelProvider(
        endpoint="https://model.example.test/v1/chat/completions",
        api_key="test-key",
        model="demo-model",
        transport=lambda endpoint, headers, payload: {
            "choices": [
                {
                    "message": {
                        "content": '```json\n{"questions": ["What changes?"]}\n```'
                    }
                }
            ]
        },
    )

    assert provider.plan(ResearchBrief.from_prompt("floating city"))[0].text == "What changes?"


def test_openai_compatible_tool_provider_sends_schemas_and_parses_tool_call():
    calls = []

    def transport(endpoint, headers, payload):
        calls.append(payload)
        return {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "function": {
                            "name": "corpus_search",
                            "arguments": '{"query": "floating city", "limit": 2}',
                        }
                    }]
                }
            }]
        }

    provider = OpenAICompatibleToolCallingProvider(
        endpoint="https://model.example.test/v1/chat/completions",
        api_key="test-key",
        model="demo-model",
        transport=transport,
    )

    action = provider.next_action("floating city", [], [{"type": "function"}])

    assert action == {
        "type": "tool_call",
        "id": "",
        "name": "corpus_search",
        "arguments": {"query": "floating city", "limit": 2},
    }
    assert calls[0]["tools"] == [{"type": "function"}]


def test_openai_compatible_tool_provider_parses_final_action():
    provider = OpenAICompatibleToolCallingProvider(
        endpoint="https://model.example.test/v1/chat/completions",
        api_key="test-key",
        model="demo-model",
        transport=lambda endpoint, headers, payload: {
            "choices": [{"message": {"content": '{"type": "final"}'}}]
        },
    )

    assert provider.next_action("done", [], []) == {"type": "final"}


def test_openai_compatible_tool_provider_replays_tool_call_protocol():
    payloads = []

    def transport(endpoint, headers, payload):
        payloads.append(payload)
        return {"choices": [{"message": {"content": '{"type": "final"}'}}]}

    provider = OpenAICompatibleToolCallingProvider(
        endpoint="https://model.example.test/v1/chat/completions",
        api_key="test-key",
        model="demo-model",
        transport=transport,
    )
    context = [{
        "action": {
            "type": "tool_call",
            "id": "call-123",
            "name": "corpus_search",
            "arguments": {"query": "city"},
        },
        "result": {"tool_name": "corpus_search", "ok": True, "data": {"sources": []}, "error": ""},
    }]

    provider.next_action("city", context, [])

    assistant, tool = payloads[0]["messages"][-2:]
    assert assistant["role"] == "assistant"
    assert assistant["tool_calls"][0]["id"] == "call-123"
    assert tool["role"] == "tool"
    assert tool["tool_call_id"] == "call-123"
