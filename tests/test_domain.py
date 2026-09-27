import pytest

from loreforge.domain import ResearchBrief, ResearchState


def test_blank_prompt_is_rejected():
    with pytest.raises(ValueError, match="prompt"):
        ResearchBrief.from_prompt("   ")


def test_state_starts_empty():
    state = ResearchState.start(ResearchBrief.from_prompt("漂浮城市游戏世界观"))
    assert state.sources == []
    assert state.evidence == []
    assert state.trace == []
    assert state.tool_trace == []
