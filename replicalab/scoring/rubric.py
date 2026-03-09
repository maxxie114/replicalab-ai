"""JDG 04-05 - Total reward computation and reward breakdown builder.

Combines rigor (JDG 01), feasibility (JDG 02), fidelity (JDG 03), and a
lightweight parsimony term into a single scalar reward with bonuses and
named penalties.

Formula:
    total = 10 * rigor * feasibility * fidelity * parsimony
            + bonuses - penalties

Pure deterministic functions - no model calls, no side effects.
"""

from __future__ import annotations

from replicalab.agents.lab_manager_policy import (
    FeasibilityCheckResult,
    check_feasibility,
)
from replicalab.config import (
    DEFAULT_DOMAIN_WEIGHTS,
    DOMAIN_WEIGHTS,
    MAX_COMMUNICATION_BONUS,
)
from replicalab.models import ConversationEntry, Protocol, RewardBreakdown
from replicalab.scenarios.templates import NormalizedScenarioPack
from replicalab.scoring.communication import score_communication
from replicalab.scoring.feasibility import score_feasibility
from replicalab.scoring.fidelity import score_fidelity
from replicalab.scoring.rigor import score_rigor


_REWARD_SCALE = 10.0
_MAX_EFFICIENCY_BONUS = 1.0


def compute_total_reward(breakdown: RewardBreakdown) -> float:
    """Compute the scalar reward from a RewardBreakdown."""
    base = (
        _REWARD_SCALE
        * breakdown.rigor
        * breakdown.feasibility
        * breakdown.fidelity
        * breakdown.parsimony
    )
    bonus = (
        breakdown.efficiency_bonus
        + breakdown.communication_bonus
        + breakdown.domain_emphasis_bonus
    )
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
    conversation_history: list[ConversationEntry] | None = None,
) -> RewardBreakdown:
    """Build a full RewardBreakdown from the sub-scores plus bonuses."""
    if check is None:
        check = check_feasibility(protocol, scenario)

    rigor = score_rigor(protocol, scenario)
    feasibility = score_feasibility(protocol, scenario, check=check)
    fidelity = score_fidelity(protocol, scenario)
    parsimony = _score_parsimony(protocol, scenario)

    efficiency_bonus = _efficiency_bonus(rounds_used, max_rounds)
    merged_penalties = dict(penalties) if penalties else {}

    communication_bonus = 0.0
    if conversation_history is not None:
        communication_bonus = score_communication(
            conversation_history, max_bonus=MAX_COMMUNICATION_BONUS,
        )

    domain_bonus = _domain_emphasis_bonus(
        rigor, feasibility, fidelity, scenario.domain_id,
    )

    return RewardBreakdown(
        rigor=rigor,
        feasibility=feasibility,
        fidelity=fidelity,
        parsimony=parsimony,
        efficiency_bonus=efficiency_bonus,
        communication_bonus=communication_bonus,
        domain_emphasis_bonus=domain_bonus,
        penalties=merged_penalties,
    )


def _efficiency_bonus(rounds_used: int, max_rounds: int) -> float:
    """Reward finishing in fewer rounds."""
    if max_rounds <= 1 or rounds_used <= 0:
        return 0.0
    saved = max(0, max_rounds - rounds_used)
    return round(_MAX_EFFICIENCY_BONUS * saved / (max_rounds - 1), 6)


def _score_parsimony(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> float:
    """Score how lean the protocol is relative to scenario complexity."""
    required_element_count = len(scenario.hidden_reference_spec.required_elements)
    complexity_budget = max(2, required_element_count + 2)
    requested_count = (
        len(set(protocol.controls))
        + len(set(protocol.required_equipment))
        + len(set(protocol.required_reagents))
    )
    if requested_count <= 0:
        return 1.0

    ratio = complexity_budget / max(complexity_budget, requested_count)
    return round(max(0.25, min(1.0, ratio)), 6)


def _domain_emphasis_bonus(
    rigor: float, feasibility: float, fidelity: float, domain_id: str,
) -> float:
    """Bonus for excelling in the domain's priority dimensions.

    Returns up to 0.5 when the weighted average of sub-scores exceeds 0.7.
    """
    weights = DOMAIN_WEIGHTS.get(domain_id, DEFAULT_DOMAIN_WEIGHTS)
    weighted = (
        weights.get("rigor", 0.33) * rigor
        + weights.get("feasibility", 0.34) * feasibility
        + weights.get("fidelity", 0.33) * fidelity
    )
    if weighted >= 0.7:
        return round(min(0.5, (weighted - 0.7) / 0.3 * 0.5), 6)
    return 0.0
