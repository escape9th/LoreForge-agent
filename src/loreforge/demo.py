from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from typing import Any

from .domain import (
    Claim,
    CreativeBlueprint,
    ResearchBrief,
    ResearchQuestion,
    Source,
)
from .verification import _terms


class SearchProvider(Protocol):
    def search(self, query: str, limit: int = 3) -> list[Source]: ...


class ModelProvider(Protocol):
    def plan(self, brief: ResearchBrief) -> list[ResearchQuestion]: ...

    def draft(
        self,
        brief: ResearchBrief,
        questions: list[ResearchQuestion],
        sources: list[Source],
    ) -> CreativeBlueprint: ...


@dataclass
class DemoToolCallingProvider:
    """Deterministic stand-in for an LLM that supports function calling."""

    def next_action(
        self,
        prompt: str,
        context: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
    ) -> dict[str, Any]:
        names = [item["function"]["name"] for item in tool_schemas]
        if not context and "corpus_search" in names:
            return {
                "type": "tool_call",
                "name": "corpus_search",
                "arguments": {"query": prompt, "limit": 3},
            }
        if len(context) == 1 and "source_lookup" in names:
            sources = context[0]["result"].get("data", {}).get("sources", [])
            if sources:
                return {
                    "type": "tool_call",
                    "name": "source_lookup",
                    "arguments": {"source_id": sources[0]["source_id"]},
                }
        return {"type": "final", "context": context}


@dataclass
class DemoSearchProvider:
    catalog: tuple[Source, ...] = ()

    def __post_init__(self) -> None:
        if self.catalog:
            return
        self.catalog = (
            Source(
                source_id="ocean-city-01",
                title="潮汐能与海上基础设施",
                url="https://example.org/loreforge/ocean-energy",
                summary="潮汐能可以为沿海和海上基础设施提供可预测的周期性能源。",
                text="潮汐能具有周期性和可预测性，适合为漂浮城市的基础设施提供稳定电力。",
            ),
            Source(
                source_id="ocean-city-02",
                title="漂浮城市的模块化结构",
                url="https://example.org/loreforge/floating-modules",
                summary="模块化平台便于维护、扩建和在恶劣海况下进行隔离。",
                text="漂浮城市可以采用模块化平台，将居住区、能源区和农业区连接为可替换的单元。",
            ),
            Source(
                source_id="ocean-city-03",
                title="海洋灾害下的社区治理",
                url="https://example.org/loreforge/ocean-governance",
                summary="资源分配、避险权限和维修劳动会成为海上社区的治理核心。",
                text="在长期海洋灾害环境中，淡水、能源和避险空间的分配会推动新的社区治理规则。",
            ),
            Source(
                source_id="character-01",
                title="角色弧光与身份冲突",
                url="https://example.org/loreforge/character-arcs",
                summary="角色弧光通常通过目标、阻力和选择体现身份变化。",
                text="角色弧光可以通过目标、阻力和关键选择表现身份变化，失去记忆会放大自我认同冲突。",
            ),
            Source(
                source_id="character-02",
                title="动漫角色的关系动力",
                url="https://example.org/loreforge/character-dynamics",
                summary="关系中的承诺、误解和背叛可以推动角色改变。",
                text="承诺、误解和背叛会改变角色关系，并推动角色在关键时刻重新选择立场。",
            ),
            Source(
                source_id="quest-01",
                title="游戏任务的目标与代价",
                url="https://example.org/loreforge/quest-design",
                summary="任务需要清晰目标、可见代价和玩家选择。",
                text="游戏任务需要清晰目标、可见代价和玩家选择，资源冲突可以把系统压力转化为叙事决策。",
            ),
            Source(
                source_id="quest-02",
                title="分支任务与后果反馈",
                url="https://example.org/loreforge/quest-consequences",
                summary="分支结果应该反馈到角色关系、资源状态或后续任务。",
                text="分支任务的结果应该反馈到角色关系、资源状态或后续任务，让玩家选择产生可观察的后果。",
            ),
        )

    def search(self, query: str, limit: int = 3) -> list[Source]:
        keywords = _terms(query)
        ranked = sorted(
            self.catalog,
            key=lambda source: sum(
                keyword in (source.title + source.summary + source.text).lower()
                for keyword in keywords
            ),
            reverse=True,
        )
        return ranked[:limit]


@dataclass
class DemoModelProvider:
    @staticmethod
    def profile(prompt: str) -> str:
        lowered = prompt.lower()
        if any(word in lowered for word in ("角色", "人物", "记忆", "弧光")):
            return "character"
        if any(word in lowered for word in ("任务", "关卡", "玩法", "游戏")):
            return "quest"
        if any(word in lowered for word in ("世界观", "城市", "阵营", "设定")):
            return "world"
        return "general"

    def plan(self, brief: ResearchBrief) -> list[ResearchQuestion]:
        if self.profile(brief.prompt) == "character":
            return [
                ResearchQuestion("角色的核心目标和内在阻力是什么？"),
                ResearchQuestion("哪些关系会推动角色改变？"),
                ResearchQuestion("哪个关键选择能体现人物弧光？"),
            ]
        if self.profile(brief.prompt) == "quest":
            return [
                ResearchQuestion("任务的目标、代价和玩家选择是什么？"),
                ResearchQuestion("分支结果会怎样反馈到系统和角色？"),
                ResearchQuestion("资源冲突如何转化为可玩的决策？"),
            ]
        return [
            ResearchQuestion("能源系统如何维持城市运行？"),
            ResearchQuestion("城市结构如何适应海洋环境？"),
            ResearchQuestion("资源稀缺会怎样改变社区治理？"),
        ]

    def draft(
        self,
        brief: ResearchBrief,
        questions: list[ResearchQuestion],
        sources: list[Source],
    ) -> CreativeBlueprint:
        profile = self.profile(brief.prompt)
        if profile == "character":
            return CreativeBlueprint(
                title="失忆者的回声：角色弧光蓝图",
                facts=[
                    Claim("角色弧光可以通过目标、阻力和关键选择表现身份变化。"),
                    Claim("承诺、误解和背叛会改变角色关系。"),
                ],
                proposals=[
                    Claim("让角色发现自己曾经伤害过最信任的同伴，并必须重新赢得对方的选择。", kind="proposal"),
                    Claim("把记忆恢复设计成有代价的主动选择，而不是一次性揭露真相。", kind="proposal"),
                ],
                sections={
                    "核心概念": "一个失去记忆的角色通过关系和关键选择重新定义自己。",
                    "玩法钩子": "玩家决定角色相信哪一段互相矛盾的过去。",
                    "叙事冲突": "恢复真实记忆，可能意味着失去现在建立的身份。",
                },
            )
        if profile == "quest":
            return CreativeBlueprint(
                title="最后一桶淡水：资源冲突任务蓝图",
                facts=[
                    Claim("游戏任务需要清晰目标、可见代价和玩家选择。"),
                    Claim("分支任务的结果应该反馈到角色关系、资源状态或后续任务。"),
                ],
                proposals=[
                    Claim("让玩家在救援外环居民和保护中央淡水库之间做出不可逆选择。", kind="proposal"),
                    Claim("把任务结果反馈到商店价格、阵营关系和下一章可用路线。", kind="proposal"),
                ],
                sections={
                    "核心概念": "一项看似简单的补给任务，逐步暴露社区资源分配的不平等。",
                    "玩法钩子": "玩家必须在有限时间内决定资源送给谁。",
                    "叙事冲突": "完成任务不代表所有人都能被拯救。",
                },
            )
        facts = [
            Claim("潮汐能具有周期性和可预测性，适合提供稳定电力。"),
            Claim("模块化平台便于扩建、维护和隔离风险。"),
            Claim("淡水、能源和避险空间会成为社区治理的核心资源。"),
        ]
        proposals = [
            Claim(
                "将城市设计为三个可脱离的环形平台：居住环、能源环和藻类农业环。",
                kind="proposal",
            ),
            Claim(
                "把玩家的核心冲突设为“是否牺牲外环居民来保护中央淡水库”。",
                kind="proposal",
            ),
            Claim(
                "让维修工会、潮汐观测者和淡水配给委员会形成互相制衡的阵营。",
                kind="proposal",
            ),
        ]
        return CreativeBlueprint(
            title="潮汐之环：漂浮城市创作蓝图",
            facts=facts,
            proposals=proposals,
            sections={
                "核心概念": "一座由多个可替换平台组成的漂浮城市，在海洋灾变后依靠潮汐能源和严格配给维持生存。",
                "玩法钩子": "玩家管理能源、淡水和平台连接，在短期生存与长期迁徙之间做出选择。",
                "叙事冲突": "城市中央的安全秩序与外环居民的生存权发生冲突。",
            },
        )
