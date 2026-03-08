"""JDG 04-05 — Total reward computation and reward breakdown builder.

Combines rigor (JDG 01), feasibility (JDG 02), and fidelity (JDG 03)
into a single scalar reward with efficiency bonus and penalties.

Formula:  total = 10 × rigor × feasibility × fidelity + bonuses − penalties

Pure deterministic functions — no model calls, no side effects.
"""

from __future__ import annotations

from replicalab.agents.lab_manager_policy import (
    FeasibilityCheckResult,
    check_feasibility,
)
from replicalab.models import Protocol, RewardBreakdown
from replicalab.scenarios.templates import NormalizedScenarioPack
from replicalab.scoring.feasibility import score_feasibility
from replicalab.scoring.fidelity import score_fidelity
from replicalab.scoring.rigor import score_rigor


_REWARD_SCALE = 10.0
_MAX_EFFICIENCY_BONUS = 1.0
_MAX_COMMUNICATION_BONUS = 0.0  # reserved for future use


def compute_total_reward(breakdown: RewardBreakdown) -> float:
    """Compute the scalar reward from a RewardBreakdown.

    Formula: 10 × rigor × feasibility × fidelity + efficiency_bonus
             + communication_bonus − sum(penalties)
    """
    base = _REWARD_SCALE * breakdown.rigor * breakdown.feasibility * breakdown.fidelity
    bonus = breakdown.efficiency_bonus + breakdown.communication_bonus
    penalty = sum(breakdown.penalties.values())
    return max(0.0, round(base + bonus - penalty, 6))


def build_reward_breakdown(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    rounds_used: int,
    max_rounds: int,
    *,
    check: FeasibilityCheckResult | None = None,
    penalties: dict[str, float] | None = None,
) -> RewardBreakdown:
    """Build a full RewardBreakdown from the three sub-scores plus bonuses.

    Parameters
    ----------
    protocol : Protocol
        The final agreed protocol.
    scenario : NormalizedScenarioPack
        The scenario pack for this episode.
    rounds_used : int
        How many rounds were consumed.
    max_rounds : int
        The episode's round cap.
    check : FeasibilityCheckResult, optional
        Pre-computed feasibility check to avoid redundant work.
    penalties : dict[str, float], optional
        Named penalty keys for bounded-tool diagnostics, unsupported
        evidence claims, or other deterministic deductions.  Use named
        keys (e.g. ``"invalid_tool_use"``, ``"unsupported_claim"``)
        instead of adding new fields to RewardBreakdown.
    """
    if check is None:
        check = check_feasibility(protocol, scenario)

    rigor = score_rigor(protocol, scenario)
    feasibility = score_feasibility(protocol, scenario, check=check)
    fidelity = score_fidelity(protocol, scenario)

    efficiency_bonus = _efficiency_bonus(rounds_used, max_rounds)
    merged_penalties = dict(penalties) if penalties else {}

    return RewardBreakdown(
        rigor=rigor,
        feasibility=feasibility,
        fidelity=fidelity,
        efficiency_bonus=efficiency_bonus,
        communication_bonus=0.0,
        penalties=merged_penalties,
    )


def _efficiency_bonus(rounds_used: int, max_rounds: int) -> float:
    """Reward finishing in fewer rounds.

    If the scientist reaches agreement in round 1 of 6, that's the maximum
    bonus.  If they use all rounds, the bonus is 0.
    """
    if max_rounds <= 1 or rounds_used <= 0:
        return 0.0
    saved = max(0, max_rounds - rounds_used)
    return round(_MAX_EFFICIENCY_BONUS * saved / (max_rounds - 1), 6)
