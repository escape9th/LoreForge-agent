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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchPackage":
        brief_data = data["brief"]
        brief = ResearchBrief(
            prompt=str(brief_data["prompt"]),
            run_id=str(brief_data["run_id"]),
        )
        questions = [
            ResearchQuestion(text=str(item["text"]))
            for item in data["questions"]
        ]
        sources = [
            Source(
                source_id=str(item["source_id"]),
                title=str(item["title"]),
                url=str(item["url"]),
                summary=str(item["summary"]),
                text=str(item["text"]),
            )
            for item in data["sources"]
        ]
        evidence = [
            Evidence(
                source_id=str(item["source_id"]),
                quote=str(item["quote"]),
            )
            for item in data["evidence"]
        ]
        blueprint_data = data["blueprint"]
        blueprint = CreativeBlueprint(
            title=str(blueprint_data["title"]),
            facts=[
                Claim(text=str(item["text"]), kind=str(item["kind"]))
                for item in blueprint_data["facts"]
            ],
            proposals=[
                Claim(text=str(item["text"]), kind=str(item["kind"]))
                for item in blueprint_data["proposals"]
            ],
            sections={
                str(key): str(value)
                for key, value in blueprint_data["sections"].items()
            },
        )
        verification_data = data["verification"]
        verification = VerificationReport(
            checked_claims=int(verification_data["checked_claims"]),
            supported_claims=int(verification_data["supported_claims"]),
            unverified_claims=int(verification_data["unverified_claims"]),
            items=[
                VerificationItem(
                    claim=str(item["claim"]),
                    status=str(item["status"]),
                    evidence=[str(value) for value in item["evidence"]],
                )
                for item in verification_data["items"]
            ],
        )
        trace = [
            TraceEvent(
                stage=str(item["stage"]),
                status=str(item["status"]),
                detail=str(item["detail"]),
                timestamp=str(item["timestamp"]),
            )
            for item in data["trace"]
        ]
        return cls(
            brief=brief,
            questions=questions,
            sources=sources,
            evidence=evidence,
            blueprint=blueprint,
            verification=verification,
            trace=trace,
        )
