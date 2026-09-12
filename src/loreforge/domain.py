from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ResearchBrief:
    prompt: str
    run_id: str

    @classmethod
    def from_prompt(cls, prompt: str) -> "ResearchBrief":
        cleaned = prompt.strip()
        if not cleaned:
            raise ValueError("prompt cannot be blank")
        return cls(prompt=cleaned, run_id=str(uuid4()))


@dataclass(frozen=True)
class ResearchQuestion:
    text: str


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    url: str
    summary: str
    text: str


@dataclass(frozen=True)
class Evidence:
    source_id: str
    quote: str


@dataclass(frozen=True)
class Claim:
    text: str
    kind: str = "fact"


@dataclass(frozen=True)
class CreativeBlueprint:
    title: str
    facts: list[Claim]
    proposals: list[Claim]
    sections: dict[str, str]


@dataclass(frozen=True)
class VerificationItem:
    claim: str
    status: str
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class VerificationReport:
    checked_claims: int
    supported_claims: int
    unverified_claims: int
    items: list[VerificationItem]


@dataclass(frozen=True)
class TraceEvent:
    stage: str
    status: str
    detail: str
    timestamp: str = field(default_factory=_now)


@dataclass
class ResearchState:
    brief: ResearchBrief
    questions: list[ResearchQuestion] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    blueprint: CreativeBlueprint | None = None
    verification: VerificationReport | None = None
    trace: list[TraceEvent] = field(default_factory=list)

    @classmethod
    def start(cls, brief: ResearchBrief) -> "ResearchState":
        return cls(brief=brief)


@dataclass(frozen=True)
class ResearchPackage:
    brief: ResearchBrief
    questions: list[ResearchQuestion]
    sources: list[Source]
    evidence: list[Evidence]
    blueprint: CreativeBlueprint
    verification: VerificationReport
    trace: list[TraceEvent]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

