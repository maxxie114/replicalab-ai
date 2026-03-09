"""JDG 06 - Plain-English explanation builder from RewardBreakdown.

Pure deterministic function - reads existing breakdown fields only,
introduces no new scoring logic.
"""

from __future__ import annotations

from replicalab.models import RewardBreakdown
from replicalab.scoring.rubric import compute_total_reward


def _tier(score: float) -> str:
    """Map a [0, 1] sub-score to a human-readable quality tier."""
    if score >= 0.8:
        return "strong"
    if score >= 0.5:
        return "moderate"
    if score >= 0.2:
        return "weak"
    return "very weak"


def explain_reward(breakdown: RewardBreakdown) -> str:
    """Build a plain-English explanation from a RewardBreakdown."""
    total = compute_total_reward(breakdown)
    lines: list[str] = []

    lines.append(
        f"Rigor: {breakdown.rigor:.2f} ({_tier(breakdown.rigor)}) - "
        "measures structural completeness, success-criteria coverage, "
        "and required-element coverage."
    )
    lines.append(
        f"Feasibility: {breakdown.feasibility:.2f} ({_tier(breakdown.feasibility)}) - "
        "measures whether the protocol respects budget, equipment, reagent, "
        "schedule, and staffing constraints."
    )
    lines.append(
        f"Fidelity: {breakdown.fidelity:.2f} ({_tier(breakdown.fidelity)}) - "
        "measures alignment with the hidden reference spec, including "
        "required elements, substitutions, and target metrics."
    )
    lines.append(
        f"Parsimony: {breakdown.parsimony:.2f} ({_tier(breakdown.parsimony)}) - "
        "measures whether the plan stays lean instead of requesting more "
        "controls, equipment, or reagents than the scenario complexity calls for."
    )

    if breakdown.efficiency_bonus > 0:
        lines.append(
            f"Efficiency bonus: +{breakdown.efficiency_bonus:.2f} "
            "(awarded for reaching agreement in fewer rounds)."
        )
    if breakdown.communication_bonus > 0:
        lines.append(
            f"Communication bonus: +{breakdown.communication_bonus:.2f} "
            "(awarded for action diversity, responsiveness to feedback, "
            "and substantive rationales)."
        )
    if breakdown.domain_emphasis_bonus > 0:
        lines.append(
            f"Domain emphasis bonus: +{breakdown.domain_emphasis_bonus:.2f} "
            "(awarded for strong performance in this domain's priority dimensions)."
        )

    if breakdown.penalties:
        for key, amount in sorted(breakdown.penalties.items()):
            label = key.replace("_", " ")
            lines.append(f"Penalty - {label}: -{amount:.2f}.")
    else:
        lines.append("No penalties applied.")

    lines.append(
        "Total reward: "
        f"{total:.2f} "
        "(formula: 10 x rigor x feasibility x fidelity x parsimony + bonuses - penalties)."
    )

    return "\n".join(lines)
