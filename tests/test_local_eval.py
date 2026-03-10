from __future__ import annotations

from replicalab.training.local_eval import build_trainable_paper_cases


def test_build_trainable_paper_cases_builds_exact_requested_count() -> None:
    cases = build_trainable_paper_cases(50)

    assert len(cases) == 50
    assert all(case.scenario in {"ml_benchmark", "finance_trading"} for case in cases)
    assert len({case.expected_evidence_id for case in cases[:34]}) == 34
    assert len({case.expected_evidence_id for case in cases}) >= 34


def test_build_trainable_paper_cases_rejects_non_positive_count() -> None:
    try:
        build_trainable_paper_cases(0)
    except ValueError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-positive case count")


def test_build_trainable_paper_cases_supports_offsets() -> None:
    cases = build_trainable_paper_cases(3, case_index_offset=34)

    assert [case.case_index for case in cases] == [34, 35, 36]
    assert len({case.expected_evidence_id for case in cases}) == 3
