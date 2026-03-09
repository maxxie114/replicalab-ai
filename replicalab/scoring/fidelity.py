"""JDG 03 — Protocol fidelity score.

Measures how closely the final protocol matches the hidden reference spec.
The scientist never sees the hidden spec — this score is for the judge only.

Substitution-aware: allowed substitutions get partial credit instead of 0.

Pure deterministic function — no LLM calls, no side effects.
"""

from __future__ import annotations

from replicalab.models import Protocol
from replicalab.scenarios.templates import NormalizedScenarioPack
from replicalab.utils.text import bigram_overlap, element_tokens, normalize_label


def score_fidelity(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> float:
    """Score adherence to the hidden reference specification.

    Returns a float in [0.0, 1.0].

    Breakdown (weights):
      - Required element coverage:     0.50  (substitution-aware)
      - Flexible element alignment:    0.20  (bonus, no penalty for missing)
      - Target metric alignment:       0.20
      - Technique appropriateness:     0.10
    """
    spec = scenario.hidden_reference_spec
    protocol_text = _protocol_text_blob(protocol)
    sub_index = _build_substitution_index(scenario)

    required = _required_element_score(spec.required_elements, protocol_text, sub_index)
    flexible = _flexible_element_score(spec.flexible_elements, protocol_text)
    target = _target_metric_score(spec.target_metric, spec.target_value, protocol_text)
    technique = _technique_score(spec.summary, protocol_text)

    raw = (0.50 * required) + (0.20 * flexible) + (0.20 * target) + (0.10 * technique)
    return max(0.0, min(1.0, raw))


# ---------------------------------------------------------------------------
# Sub-scores
# ---------------------------------------------------------------------------


def _required_element_score(
    required_elements: list[str],
    protocol_text: str,
    sub_index: dict[str, list[str]],
) -> float:
    """Score coverage of required elements, with substitution partial credit.

    Direct match: 1.0 credit per element.
    Substitution match: 0.7 credit (allowed substitution present instead).
    Miss: 0.0 credit.
    """
    if not required_elements:
        return 1.0

    total = 0.0
    for element in required_elements:
        if _text_matches(element, protocol_text):
            total += 1.0
        elif _substitution_matches(element, protocol_text, sub_index):
            total += 0.7
        # else: 0.0

    return total / len(required_elements)


def _flexible_element_score(
    flexible_elements: list[str],
    protocol_text: str,
) -> float:
    """Bonus for addressing flexible elements. No penalty for missing."""
    if not flexible_elements:
        return 1.0

    matched = sum(1 for el in flexible_elements if _text_matches(el, protocol_text))
    return matched / len(flexible_elements)


def _target_metric_score(
    target_metric: str,
    target_value: str,
    protocol_text: str,
) -> float:
    """Score for mentioning the target metric and value."""
    score = 0.0
    if _text_matches(target_metric, protocol_text):
        score += 0.5
    if _text_matches(target_value, protocol_text):
        score += 0.5
    return score


def _technique_score(summary: str, protocol_text: str) -> float:
    """Score for technique alignment with the hidden spec summary."""
    return 1.0 if _text_matches(summary, protocol_text) else 0.0


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
    """Check if element appears in blob via token, substring, or bigram matching.

    Enhanced matching strategy:
      1. Token match (original): any significant word from element in blob
      2. Substring match: full normalized element as substring (>= 5 chars)
      3. Bigram overlap: >= 60% shared word bigrams (catches paraphrases)
    """
    tokens = element_tokens(element)
    if any(token in blob for token in tokens):
        return True

    # Substring match for multi-word elements
    normalized = normalize_label(element)
    if len(normalized) >= 5 and normalized in blob:
        return True

    # Bigram overlap for longer phrases
    if bigram_overlap(element, blob) >= 0.6:
        return True

    return False


def _substitution_matches(
    element: str,
    protocol_text: str,
    sub_index: dict[str, list[str]],
) -> bool:
    """Check if an allowed substitution for *element* appears in the protocol."""
    norm = normalize_label(element)
    alternatives = sub_index.get(norm, [])
    return any(_text_matches(alt, protocol_text) for alt in alternatives)


def _build_substitution_index(
    scenario: NormalizedScenarioPack,
) -> dict[str, list[str]]:
    """Map normalized originals to their alternative labels."""
    index: dict[str, list[str]] = {}
    for sub in scenario.allowed_substitutions:
        key = normalize_label(sub.original)
        index.setdefault(key, []).append(sub.alternative)
    return index
