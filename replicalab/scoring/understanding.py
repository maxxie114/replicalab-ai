"""Deterministic paper-understanding scorer.

Measures whether the Scientist action is grounded in the visible paper/task
brief rather than hidden reference data. This is an evaluation metric first,
not part of the scalar reward loop.
"""

from __future__ import annotations

from replicalab.models import ScientistAction, ScientistObservation
from replicalab.utils.text import bigram_overlap, element_tokens, normalize_label

_SECTION_WEIGHTS = (
    ("experiment_goal", 0.35),
    ("paper_method", 0.25),
    ("paper_hypothesis", 0.20),
    ("paper_key_finding", 0.20),
)

_GENERIC_TOKENS = {
    "about",
    "after",
    "before",
    "data",
    "does",
    "experiment",
    "finding",
    "goal",
    "into",
    "method",
    "paper",
    "result",
    "study",
    "system",
    "under",
    "using",
    "with",
}


def score_paper_understanding(
    observation: ScientistObservation,
    action: ScientistAction,
) -> float:
    """Score how well an action reflects the visible paper brief.

    Returns a float in [0.0, 1.0]. The score rewards plans and questions that
    stay anchored to the paper hypothesis, method, finding, and explicit goal.
    """

    action_blob = _action_text_blob(action)
    if not action_blob:
        return 0.0

    score = 0.0
    for field_name, weight in _SECTION_WEIGHTS:
        score += weight * _coverage_score(getattr(observation, field_name), action_blob)
    return round(max(0.0, min(1.0, score)), 6)


def _coverage_score(section_text: str, blob: str) -> float:
    normalized = normalize_label(section_text)
    if not normalized:
        return 0.0

    tokens = [
        token
        for token in element_tokens(section_text)
        if token not in _GENERIC_TOKENS
    ]
    if tokens:
        token_hits = sum(1 for token in tokens if token in blob)
        token_score = token_hits / len(tokens)
    else:
        token_score = 0.0

    phrase_score = 1.0 if len(normalized) >= 8 and normalized in blob else 0.0
    bigram_score = bigram_overlap(section_text, blob)
    return round(max(token_score, phrase_score, bigram_score), 6)


def _action_text_blob(action: ScientistAction) -> str:
    return normalize_label(
        " ".join(
            [
                action.technique,
                action.rationale,
                " ".join(action.controls),
                " ".join(action.required_equipment),
                " ".join(action.required_reagents),
                " ".join(action.questions),
            ]
        )
    )


__all__ = ["score_paper_understanding"]
