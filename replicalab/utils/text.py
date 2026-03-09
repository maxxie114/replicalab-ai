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


def bigram_overlap(element: str, blob: str) -> float:
    """Compute bigram overlap ratio between element words and blob words.

    Returns fraction of element bigrams found in blob.  Useful for
    catching multi-word paraphrases that token matching misses.
    """
    elem_bigrams = _bigrams(normalize_label(element))
    if not elem_bigrams:
        return 0.0
    blob_bigrams = _bigrams(blob)
    if not blob_bigrams:
        return 0.0
    return len(elem_bigrams & blob_bigrams) / len(elem_bigrams)


def _bigrams(text: str) -> set[str]:
    """Extract word bigrams from text."""
    words = text.split()
    if len(words) < 2:
        return set()
    return {f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)}
