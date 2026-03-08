"""Shared text-matching helpers used by validation and scoring modules."""

from __future__ import annotations


def normalize_label(label: str) -> str:
    """Lowercase, strip, collapse whitespace for fuzzy matching."""
    return " ".join(label.lower().split())


def element_tokens(element: str) -> list[str]:
    """Split a required-element description into searchable tokens.

    Returns individual significant words (>= 3 chars) so that
    "transaction cost assumption" matches a rationale containing
    "transaction" or "cost".
    """
    return [word for word in element.lower().split() if len(word) >= 3]
