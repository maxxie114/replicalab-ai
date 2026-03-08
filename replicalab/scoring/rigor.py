"""JDG 01 — Protocol rigor score.

Measures structural completeness and alignment to scenario requirements.
Pure deterministic function — no LLM calls, no side effects.
"""

from __future__ import annotations

from replicalab.models import Protocol
from replicalab.scenarios.templates import NormalizedScenarioPack
from replicalab.utils.text import element_tokens


def score_rigor(protocol: Protocol, scenario: NormalizedScenarioPack) -> float:
    """Score protocol structural quality and requirement coverage.

    Returns a float in [0.0, 1.0].

    Breakdown (weights):
      - Structural completeness:       0.30
      - Success criteria coverage:     0.40
      - Required element coverage:     0.30
    """
    completeness = _structural_completeness(protocol)
    criteria = _success_criteria_coverage(protocol, scenario)
    elements = _required_element_coverage(protocol, scenario)

    raw = (0.30 * completeness) + (0.40 * criteria) + (0.30 * elements)
    return max(0.0, min(1.0, raw))


# ---------------------------------------------------------------------------
# Sub-scores
# ---------------------------------------------------------------------------


def _structural_completeness(protocol: Protocol) -> float:
    """Score based on whether protocol fields are meaningfully populated."""
    score = 0.0
    total = 0.35

    # sample_size present
    if protocol.sample_size >= 1:
        score += 0.05
    # sample_size statistically meaningful
    if protocol.sample_size >= 4:
        score += 0.05
    # at least one control
    if len(protocol.controls) >= 1:
        score += 0.05
    # second control (stronger design)
    if len(protocol.controls) >= 2:
        score += 0.05
    # technique specified
    if protocol.technique:
        score += 0.05
    # duration allocated
    if protocol.duration_days >= 1:
        score += 0.05
    # rationale is substantive (not a placeholder)
    if len(protocol.rationale) > 20:
        score += 0.05

    return score / total


def _success_criteria_coverage(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> float:
    """Fraction of scenario success criteria addressed by protocol text."""
    criteria = scenario.success_criteria
    if not criteria:
        return 1.0

    protocol_text = _protocol_text_blob(protocol)
    matched = sum(1 for c in criteria if _text_matches(c, protocol_text))
    return matched / len(criteria)


def _required_element_coverage(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> float:
    """Fraction of hidden reference required elements addressed."""
    required = scenario.hidden_reference_spec.required_elements
    if not required:
        return 1.0

    protocol_text = _protocol_text_blob(protocol)
    matched = sum(1 for el in required if _text_matches(el, protocol_text))
    return matched / len(required)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _protocol_text_blob(protocol: Protocol) -> str:
    """Join all protocol text fields into one lowercase blob for matching."""
    return " ".join([
        protocol.technique,
        protocol.rationale,
        " ".join(protocol.controls),
        " ".join(protocol.required_equipment),
        " ".join(protocol.required_reagents),
    ]).lower()


def _text_matches(element: str, blob: str) -> bool:
    """Check if any token from *element* appears in *blob*."""
    tokens = element_tokens(element)
    return any(token in blob for token in tokens) if tokens else False
