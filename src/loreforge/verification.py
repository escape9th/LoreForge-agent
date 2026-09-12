from __future__ import annotations

import re

from .domain import Claim, Evidence, VerificationItem, VerificationReport


_STOP_WORDS = {"的", "是", "和", "与", "会", "为", "在", "可以", "将"}


def _terms(text: str) -> set[str]:
    normalized = text.lower()
    terms: set[str] = set()
    for chunk in re.findall(r"[一-龥]+", normalized):
        terms.update(
            chunk[index : index + 2]
            for index in range(len(chunk) - 1)
            if chunk[index : index + 2] not in _STOP_WORDS
        )
    terms.update(re.findall(r"[A-Za-z]{3,}|\d+", normalized))
    return terms


def verify_claims(claims: list[Claim], evidence: list[Evidence]) -> VerificationReport:
    items: list[VerificationItem] = []
    supported = 0
    evidence_terms = [(item, _terms(item.quote)) for item in evidence]
    for claim in claims:
        claim_terms = _terms(claim.text)
        matches = []
        for item, terms in evidence_terms:
            overlap = claim_terms & terms
            if claim_terms and len(overlap) >= 2 and len(overlap) / len(claim_terms) >= 0.25:
                matches.append(item.source_id)
        status = "supported" if matches else "unverified"
        supported += status == "supported"
        items.append(VerificationItem(claim=claim.text, status=status, evidence=matches))
    return VerificationReport(
        checked_claims=len(claims),
        supported_claims=supported,
        unverified_claims=len(claims) - supported,
        items=items,
    )
