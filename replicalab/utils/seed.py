"""Deterministic seeding helpers shared by scenarios and the environment."""

from __future__ import annotations

import hashlib
import random


def get_deterministic_seed(seed: int, namespace: str = "") -> int:
    """Derive a stable child seed from a base seed plus namespace."""

    payload = f"{seed}:{namespace}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def seed_rng(seed: int, namespace: str = "") -> random.Random:
    """Return a dedicated RNG instance seeded deterministically."""

    return random.Random(get_deterministic_seed(seed, namespace))
