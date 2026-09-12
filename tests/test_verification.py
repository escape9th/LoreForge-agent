from loreforge.domain import Claim, Evidence
from loreforge.verification import verify_claims


def test_claim_is_supported_when_evidence_contains_its_terms():
    claims = [Claim(text="城市依靠潮汐发电", kind="fact")]
    evidence = [
        Evidence(
            source_id="source-1",
            quote="漂浮城市使用潮汐发电维持基础设施。",
        )
    ]
    report = verify_claims(claims, evidence)
    assert report.supported_claims == 1
    assert report.unverified_claims == 0


def test_claim_is_unverified_without_matching_evidence():
    claims = [Claim(text="城市拥有月面电梯", kind="fact")]
    evidence = [
        Evidence(source_id="source-1", quote="城市依靠潮汐发电。")
    ]
    report = verify_claims(claims, evidence)
    assert report.supported_claims == 0
    assert report.unverified_claims == 1


def test_punctuation_does_not_change_support_decision():
    claims = [Claim(text="潮汐能具有周期性和可预测性。", kind="fact")]
    evidence = [
        Evidence(source_id="source-1", quote="潮汐能具有周期性和可预测性，适合提供稳定电力。")
    ]
    report = verify_claims(claims, evidence)
    assert report.items[0].status == "supported"
