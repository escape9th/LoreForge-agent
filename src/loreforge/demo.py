from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

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
    def plan(self, brief: ResearchBrief) -> list[ResearchQuestion]:
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
