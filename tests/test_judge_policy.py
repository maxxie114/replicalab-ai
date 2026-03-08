"""Tests for JDG 11 — structured final audit payload (judge_policy)."""

from __future__ import annotations

from replicalab.agents.judge_policy import JudgeAudit, build_judge_audit
from replicalab.models import RewardBreakdown


def _good_breakdown() -> RewardBreakdown:
    return RewardBreakdown(
        rigor=0.85,
        feasibility=0.90,
        fidelity=0.80,
        efficiency_bonus=0.6,
        communication_bonus=0.0,
        penalties={},
    )


def _weak_breakdown() -> RewardBreakdown:
    return RewardBreakdown(
        rigor=0.30,
        feasibility=0.25,
        fidelity=0.40,
        efficiency_bonus=0.0,
        communication_bonus=0.0,
        penalties={},
    )


# ---------------------------------------------------------------------------
# Verdict derivation
# ---------------------------------------------------------------------------


def test_agreement_path_returns_accept() -> None:
    audit = build_judge_audit(
        _good_breakdown(),
        agreement_reached=True,
        rounds_used=2,
        max_rounds=6,
    )

    assert isinstance(audit, JudgeAudit)
    assert audit.verdict == "accept"
    assert isinstance(audit.judge_notes, str)
    assert len(audit.judge_notes) > 0


def test_timeout_path_returns_timeout() -> None:
    audit = build_judge_audit(
        _weak_breakdown(),
        agreement_reached=False,
        rounds_used=6,
        max_rounds=6,
    )

    assert audit.verdict == "timeout"
    assert any("round limit" in r for r in audit.top_failure_reasons)


def test_no_agreement_non_timeout_returns_no_agreement() -> None:
    audit = build_judge_audit(
        _weak_breakdown(),
        agreement_reached=False,
        rounds_used=3,
        max_rounds=6,
    )

    assert audit.verdict == "no_agreement"
    assert any("without reaching agreement" in r for r in audit.top_failure_reasons)


# ---------------------------------------------------------------------------
# Failure reason derivation
# ---------------------------------------------------------------------------


def test_low_feasibility_produces_feasibility_reason() -> None:
    bd = RewardBreakdown(
        rigor=0.85,
        feasibility=0.20,
        fidelity=0.80,
    )
    audit = build_judge_audit(
        bd,
        agreement_reached=True,
        rounds_used=3,
        max_rounds=6,
    )

    assert any("Feasibility" in r for r in audit.top_failure_reasons)


def test_low_rigor_and_fidelity_produce_multiple_reasons() -> None:
    bd = RewardBreakdown(
        rigor=0.30,
        feasibility=0.90,
        fidelity=0.40,
    )
    audit = build_judge_audit(
        bd,
        agreement_reached=True,
        rounds_used=3,
        max_rounds=6,
    )

    reasons_text = " ".join(audit.top_failure_reasons)
    assert "rigor" in reasons_text.lower() or "checks" in reasons_text.lower()
    assert "fidelity" in reasons_text.lower() or "reference" in reasons_text.lower()


def test_penalties_surface_in_failure_reasons() -> None:
    bd = RewardBreakdown(
        rigor=0.85,
        feasibility=0.85,
        fidelity=0.85,
        penalties={"invalid_tool_use": 0.5, "unsupported_claim": 0.3},
    )
    audit = build_judge_audit(
        bd,
        agreement_reached=True,
        rounds_used=2,
        max_rounds=6,
    )

    reasons_text = " ".join(audit.top_failure_reasons)
    assert "tool" in reasons_text.lower()
    assert "evidence" in reasons_text.lower() or "claim" in reasons_text.lower()


def test_good_protocol_has_no_failure_reasons() -> None:
    audit = build_judge_audit(
        _good_breakdown(),
        agreement_reached=True,
        rounds_used=2,
        max_rounds=6,
    )

    assert audit.verdict == "accept"
    assert len(audit.top_failure_reasons) == 0


def test_top_failure_reasons_capped_at_three() -> None:
    bd = RewardBreakdown(
        rigor=0.10,
        feasibility=0.10,
        fidelity=0.10,
        penalties={"invalid_tool_use": 0.5, "unsupported_claim": 0.3},
    )
    audit = build_judge_audit(
        bd,
        agreement_reached=False,
        rounds_used=6,
        max_rounds=6,
    )

    # 3 weak components + 2 penalties + 1 timeout = 6 candidate reasons,
    # but only top 3 should be returned.
    assert len(audit.top_failure_reasons) <= 3


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_same_input_returns_identical_audit() -> None:
    bd = _weak_breakdown()
    a1 = build_judge_audit(bd, agreement_reached=False, rounds_used=6, max_rounds=6)
    a2 = build_judge_audit(bd, agreement_reached=False, rounds_used=6, max_rounds=6)

    assert a1.judge_notes == a2.judge_notes
    assert a1.verdict == a2.verdict
    assert a1.top_failure_reasons == a2.top_failure_reasons


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------


def test_judge_audit_json_round_trip() -> None:
    audit = build_judge_audit(
        _weak_breakdown(),
        agreement_reached=False,
        rounds_used=4,
        max_rounds=6,
    )

    dumped = audit.model_dump_json()
    restored = JudgeAudit.model_validate_json(dumped)

    assert restored.verdict == audit.verdict
    assert restored.judge_notes == audit.judge_notes
    assert restored.top_failure_reasons == audit.top_failure_reasons
