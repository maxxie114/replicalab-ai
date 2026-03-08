from __future__ import annotations

import json

from replicalab.cache import CachedOracle, ScenarioCache
from replicalab.oracle_models import Scenario


def _scenario_payload() -> dict:
    return {
        "paper": {
            "title": "Cached benchmark",
            "domain": "ml_benchmark",
            "claim": "A small run remains useful under a tighter budget.",
            "method_summary": "Train a compact model and verify against a held-out split.",
            "original_sample_size": 1000,
            "original_duration_days": 2,
            "original_technique": "compact_model",
            "required_controls": ["baseline"],
            "required_equipment": ["GPU cluster"],
            "required_reagents": ["dataset snapshot"],
            "statistical_test": "accuracy_gap",
        },
        "lab_constraints": {
            "budget_total": 1200.0,
            "budget_remaining": 1200.0,
            "equipment": [
                {
                    "name": "GPU cluster",
                    "available": True,
                    "condition": "operational",
                    "booking_conflicts": [],
                    "cost_per_use": 100.0,
                }
            ],
            "reagents": [
                {
                    "name": "dataset snapshot",
                    "in_stock": True,
                    "quantity_available": 1.0,
                    "unit": "copy",
                    "lead_time_days": 0,
                    "cost": 0.0,
                }
            ],
            "staff": [],
            "max_duration_days": 3,
            "safety_rules": ["No external internet."],
            "valid_substitutions": [],
        },
        "minimum_viable_spec": {
            "min_sample_size": 800,
            "must_keep_controls": ["baseline"],
            "acceptable_techniques": ["compact_model"],
            "min_duration_days": 1,
            "critical_equipment": ["GPU cluster"],
            "flexible_equipment": [],
            "critical_reagents": ["dataset snapshot"],
            "flexible_reagents": [],
            "power_threshold": 0.75,
        },
        "difficulty": "easy",
        "narrative_hook": "The benchmark owners tightened the reporting budget.",
    }


def test_scenario_cache_round_trips(tmp_path) -> None:
    cache = ScenarioCache(tmp_path)
    scenario = Scenario.model_validate(_scenario_payload())

    path = cache.put(13, "easy", "ml_benchmark", scenario)
    restored = cache.get(13, "easy", "ml_benchmark")

    assert path.exists()
    assert restored is not None
    assert restored.model_dump(mode="json") == scenario.model_dump(mode="json")


def test_cached_oracle_uses_cache_after_first_generation(tmp_path) -> None:
    calls = {"count": 0}

    def fake_client(system: str, user: str, model: str) -> str:
        calls["count"] += 1
        return json.dumps(_scenario_payload())

    oracle = CachedOracle(fake_client, cache=ScenarioCache(tmp_path))

    first = oracle.generate_scenario(9, "easy", "ml_benchmark")
    second = oracle.generate_scenario(9, "easy", "ml_benchmark")

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert calls["count"] == 1
