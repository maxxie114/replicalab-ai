"""JDG 11 — Structured final audit payload builder.

Produces a deterministic ``JudgeAudit`` from an existing
``RewardBreakdown`` without introducing any new scoring logic.
Downstream consumers (env, API, logs, UI) should use this as the
single canonical judge output once wired (ENV 11+).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from replicalab.models import RewardBreakdown
from replicalab.scoring.explain import explain_reward
from replicalab.scoring.rubric import compute_total_reward


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

Verdict = Literal["accept", "timeout", "no_agreement"]


class JudgeAudit(BaseModel):
    """Canonical structured audit payload from the judge."""

    model_config = ConfigDict(extra="forbid")

    judge_notes: str
    verdict: Verdict
    top_failure_reasons: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

_MAX_FAILURE_REASONS = 3

# Thresholds for flagging weak components.
_WEAK_THRESHOLD = 0.5


def build_judge_audit(
    breakdown: RewardBreakdown,
    *,
    agreement_reached: bool,
    rounds_used: int,
    max_rounds: int,
) -> JudgeAudit:
    """Build a ``JudgeAudit`` from rubric outputs.

    Parameters
    ----------
    breakdown : RewardBreakdown
        The reward breakdown produced by ``build_reward_breakdown()``.
    agreement_reached : bool
        Whether the Scientist accepted a protocol before the episode ended.
    rounds_used : int
        How many negotiation rounds were consumed.
    max_rounds : int
        The episode's round cap.

    Returns
    -------
    JudgeAudit
        Deterministic audit with notes, verdict, and top failure reasons.
    """
    verdict = _derive_verdict(agreement_reached, rounds_used, max_rounds)
    notes = explain_reward(breakdown)
    reasons = _derive_failure_reasons(breakdown, verdict)

    return JudgeAudit(
        judge_notes=notes,
        verdict=verdict,
        top_failure_reasons=reasons,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _derive_verdict(
    agreement_reached: bool,
    rounds_used: int,
    max_rounds: int,
) -> Verdict:
    if agreement_reached:
        return "accept"
    if rounds_used >= max_rounds:
        return "timeout"
    return "no_agreement"


def _derive_failure_reasons(
    breakdown: RewardBreakdown,
    verdict: Verdict,
) -> list[str]:
    """Build a sorted, trimmed list of top failure reasons."""
    reasons: list[tuple[float, str]] = []

    # --- weak rubric components (sorted by score ascending = worst first) ---
    components: list[tuple[float, str, str]] = [
        (breakdown.feasibility, "feasibility", "Feasibility remained too low under the scenario constraints."),
        (breakdown.fidelity, "fidelity", "The final plan diverged too far from the hidden reference requirements."),
        (breakdown.rigor, "rigor", "The plan missed required checks or justification quality targets."),
        (breakdown.parsimony, "parsimony", "The final plan requested more resources or controls than the scenario complexity justified."),
    ]
    for score, _name, message in components:
        if score < _WEAK_THRESHOLD:
            # Use (score) as sort key so lowest score comes first.
            reasons.append((score, message))

    # --- named penalties ---
    _PENALTY_LABELS: dict[str, str] = {
        "invalid_tool_use": "A bounded-tool usage violation was detected.",
        "unsupported_claim": "An unsupported evidence claim was penalized.",
        "timeout": "A timeout penalty was applied at the round limit.",
        "no_agreement": "A no-agreement penalty was applied.",
        "invalid_action": "An invalid action penalty was applied after a failed protocol proposal.",
        "hallucination": "A hallucination penalty was applied for unsupported inventory references.",
        "contradiction": "A contradiction penalty was applied for repeating blocked requirements.",
        "stalling": "A stalling penalty was applied for repeating an unproductive move.",
        "regression": "A regression penalty was applied because the revision worsened the protocol.",
    }
    for key, amount in sorted(breakdown.penalties.items()):
        if amount > 0:
            label = _PENALTY_LABELS.get(
                key,
                f"Penalty '{key.replace('_', ' ')}' was applied.",
            )
            # Penalties sort after component weaknesses (use a negative
            # priority so they appear after score-based reasons).
            reasons.append((-amount, label))

    # --- episode-level state ---
    if verdict == "timeout":
        reasons.append((-0.01, "The episode ended at the round limit without agreement."))
    elif verdict == "no_agreement":
        reasons.append((-0.01, "The episode ended without reaching agreement."))

    # Sort: lowest score first (worst component), then most severe penalty.
    reasons.sort(key=lambda t: t[0])

    return [msg for _, msg in reasons[:_MAX_FAILURE_REASONS]]
