"""Communication bonus scorer.

Rewards action diversity, responsiveness to lab-manager feedback, and
substantive rationales during the negotiation.  Pure deterministic —
no LLM calls.
"""

from __future__ import annotations

from replicalab.models import ConversationEntry


def score_communication(
    conversation_history: list[ConversationEntry],
    max_bonus: float = 0.5,
) -> float:
    """Score communication quality across the negotiation.

    Returns a float in [0, max_bonus].

    Sub-scores (weights):
      - diversity:        0.40  (fraction of distinct scientist action types used)
      - responsiveness:   0.35  (fraction of critiques followed by a revision)
      - substantiveness:  0.25  (average message length relative to 120 chars)
    """
    if not conversation_history:
        return 0.0

    diversity = _diversity_score(conversation_history)
    responsiveness = _responsiveness_score(conversation_history)
    substantiveness = _substantiveness_score(conversation_history)

    raw = 0.40 * diversity + 0.35 * responsiveness + 0.25 * substantiveness
    return round(min(max_bonus, max(0.0, max_bonus * raw)), 6)


_SCIENTIST_ACTION_TYPES = {"propose_protocol", "revise_protocol", "request_info"}


def _diversity_score(history: list[ConversationEntry]) -> float:
    """Fraction of distinct scientist action types used (out of 3)."""
    types_used = {
        entry.action_type
        for entry in history
        if entry.role == "scientist" and entry.action_type in _SCIENTIST_ACTION_TYPES
    }
    return len(types_used) / len(_SCIENTIST_ACTION_TYPES)


def _responsiveness_score(history: list[ConversationEntry]) -> float:
    """Fraction of lab-manager critiques followed by a scientist revision."""
    critiques = 0
    revisions_after_critique = 0

    for i, entry in enumerate(history):
        if entry.role != "lab_manager":
            continue
        is_critique = entry.action_type in {
            "report_feasibility",
            "suggest_alternative",
            "reject",
        }
        if not is_critique:
            continue
        critiques += 1
        # Check if the next scientist action is a revision
        for j in range(i + 1, len(history)):
            if history[j].role == "scientist":
                if history[j].action_type == "revise_protocol":
                    revisions_after_critique += 1
                break

    if critiques == 0:
        return 1.0  # no critiques means nothing to respond to
    return revisions_after_critique / critiques


def _substantiveness_score(history: list[ConversationEntry]) -> float:
    """Average scientist message length relative to a 120-char baseline."""
    scientist_messages = [
        entry.message
        for entry in history
        if entry.role == "scientist" and entry.message
    ]
    if not scientist_messages:
        return 0.0
    avg_len = sum(len(m) for m in scientist_messages) / len(scientist_messages)
    return min(1.0, avg_len / 120.0)
