"""Tests for Scientist and Lab Manager dataset builders."""

from __future__ import annotations

import json

from replicalab.models import LabManagerAction
from replicalab.training.datasets import (
    build_lab_manager_sft_examples,
    build_scientist_prompt_examples,
)


def test_scientist_prompt_examples_include_frozen_evidence_when_available() -> None:
    rows = build_scientist_prompt_examples(
        seeds=[3],
        templates=["math_reasoning", "ml_benchmark"],
        difficulties=["easy"],
    )

    assert len(rows) == 2
    math_row = next(row for row in rows if row.scenario == "math_reasoning")
    ml_row = next(row for row in rows if row.scenario == "ml_benchmark")

    assert math_row.evidence_id is None
    assert ml_row.evidence_id is not None
    assert "Frozen evidence pack" in ml_row.prompt[-1]["content"]


def test_lab_manager_sft_examples_emit_valid_lab_manager_action_json() -> None:
    rows = build_lab_manager_sft_examples(
        seeds=[2],
        templates=["ml_benchmark"],
        difficulties=["easy"],
    )

    assert len(rows) >= 2
    assert {row.candidate_kind for row in rows} >= {"baseline", "constraint_stress"}

    payload = json.loads(rows[0].target_json)
    action = LabManagerAction.model_validate(payload)

    assert action.explanation
    assert rows[0].messages[-1]["role"] == "assistant"
