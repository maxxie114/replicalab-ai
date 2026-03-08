"""JDG 02 — Protocol feasibility score.

Derives a continuous [0, 1] signal from the existing FeasibilityCheckResult
produced by AGT 05. Does NOT rescore from scratch — this prevents drift
between Lab Manager grounding and Judge scoring.

Pure deterministic function — no LLM calls, no side effects.
"""

from __future__ import annotations

from replicalab.agents.lab_manager_policy import (
    FeasibilityCheckResult,
    check_feasibility,
)
from replicalab.models import Protocol
from replicalab.scenarios.templates import NormalizedScenarioPack


def score_feasibility(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    check: FeasibilityCheckResult | None = None,
) -> float:
    """Score resource feasibility as a continuous signal.

    Returns a float in [0.0, 1.0].

    If *check* is not provided, calls ``check_feasibility(protocol, scenario)``
    to compute it.  Passing a pre-computed check avoids redundant work.

    Each of the 7 dimensions contributes equally (1/7).  Binary dimensions
    score 0 or 1.  Continuous dimensions (budget, equipment, reagents, staff)
    give partial credit based on how close the protocol is to passing.
    """
    if check is None:
        check = check_feasibility(protocol, scenario)

    weight = 1.0 / 7.0
    lab = scenario.lab_manager_observation

    scores = [
        # Protocol — binary
        1.0 if check.protocol.ok else 0.0,
        # Budget — partial credit
        _budget_score(check, lab.budget_remaining),
        # Equipment — partial credit
        _fraction_score(
            protocol.required_equipment,
            set(lab.equipment_available),
        ) if not check.equipment.ok else 1.0,
        # Reagents — partial credit
        _fraction_score(
            protocol.required_reagents,
            set(lab.reagents_in_stock),
        ) if not check.reagents.ok else 1.0,
        # Schedule — binary
        1.0 if check.schedule.ok else 0.0,
        # Staff — partial credit
        _staff_score(check, lab.staff_count),
        # Policy — binary (hard constraint)
        1.0 if check.policy.ok else 0.0,
    ]

    raw = sum(s * weight for s in scores)
    return max(0.0, min(1.0, raw))


# ---------------------------------------------------------------------------
# Partial credit helpers
# ---------------------------------------------------------------------------


def _budget_score(check: FeasibilityCheckResult, budget_remaining: float) -> float:
    """Continuous budget score: ratio of budget to estimated cost."""
    if check.budget.ok:
        return 1.0
    if check.estimated_cost <= 0:
        return 0.0
    return max(0.0, min(1.0, budget_remaining / check.estimated_cost))


def _staff_score(check: FeasibilityCheckResult, staff_count: int) -> float:
    """Continuous staff score: ratio of available staff to required."""
    if check.staff.ok:
        return 1.0
    if check.required_staff <= 0:
        return 0.0
    return max(0.0, min(1.0, staff_count / check.required_staff))


def _fraction_score(required: list[str], available: set[str]) -> float:
    """Fraction of required items that are in the available set."""
    if not required:
        return 1.0
    available_lower = {item.lower().strip() for item in available}
    matched = sum(1 for item in required if item.lower().strip() in available_lower)
    return matched / len(required)
