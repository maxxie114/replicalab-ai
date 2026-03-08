"""Scenario caching for Oracle-generated environments."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from replicalab.config import ORACLE_SCENARIO_CACHE_DIR
from replicalab.oracle import Oracle
from replicalab.oracle_models import Scenario


class ScenarioCache:
    """Cache Oracle-generated scenarios by seed, difficulty, and domain."""

    def __init__(self, cache_dir: str | Path = ORACLE_SCENARIO_CACHE_DIR) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, seed: int, difficulty: str, domain: str) -> str:
        raw = f"{seed}:{difficulty}:{domain}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def _path(self, seed: int, difficulty: str, domain: str) -> Path:
        return self.cache_dir / f"{self._key(seed, difficulty, domain)}.json"

    def get(self, seed: int, difficulty: str, domain: str) -> Optional[Scenario]:
        path = self._path(seed, difficulty, domain)
        if not path.exists():
            return None
        return Scenario.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def put(self, seed: int, difficulty: str, domain: str, scenario: Scenario) -> Path:
        path = self._path(seed, difficulty, domain)
        path.write_text(scenario.model_dump_json(indent=2), encoding="utf-8")
        return path


class CachedOracle(Oracle):
    """Oracle wrapper that caches scenario generation by seed."""

    def __init__(
        self,
        client: object,
        model: str = "frontier-oracle",
        *,
        cache: ScenarioCache | None = None,
    ) -> None:
        super().__init__(client=client, model=model)
        self.cache = cache or ScenarioCache()

    def generate_scenario(self, seed: int, difficulty: str, domain: str) -> Scenario:
        cached = self.cache.get(seed, difficulty, domain)
        if cached is not None:
            return cached
        scenario = super().generate_scenario(seed=seed, difficulty=difficulty, domain=domain)
        self.cache.put(seed, difficulty, domain, scenario)
        return scenario


__all__ = [
    "CachedOracle",
    "ScenarioCache",
]
