from __future__ import annotations

from replicalab.config import (
    DEFAULT_DIFFICULTY,
    DEFAULT_SCENARIO_TEMPLATE,
    MAX_BUDGET,
    MAX_ROUNDS,
    SESSION_TTL_SECONDS,
    WS_IDLE_TIMEOUT_SECONDS,
)
from replicalab.scenarios import generate_scenario
from server.app import ResetRequest


def test_reset_request_defaults_match_shared_config() -> None:
    request = ResetRequest()

    assert request.scenario == DEFAULT_SCENARIO_TEMPLATE
    assert request.difficulty == DEFAULT_DIFFICULTY


def test_generated_scenarios_respect_shared_round_and_budget_caps() -> None:
    for template in ("math_reasoning", "ml_benchmark", "finance_trading"):
        for difficulty in ("easy", "medium", "hard"):
            pack = generate_scenario(seed=123, template=template, difficulty=difficulty)
            assert pack.scientist_observation.max_rounds == MAX_ROUNDS
            assert pack.lab_manager_observation.max_rounds == MAX_ROUNDS
            assert pack.lab_manager_observation.budget_total <= MAX_BUDGET


def test_timeout_exports_share_the_same_default_value() -> None:
    assert SESSION_TTL_SECONDS == WS_IDLE_TIMEOUT_SECONDS
