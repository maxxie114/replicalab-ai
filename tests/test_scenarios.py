from __future__ import annotations

import json

from replicalab.scenarios import (
    GOLDEN_SCENARIO_SPECS_PATH,
    available_scenario_families,
    generate_scenario,
)


def test_generate_scenario_is_deterministic_for_same_seed() -> None:
    first = generate_scenario(seed=101, template="math_reasoning", difficulty="easy")
    second = generate_scenario(seed=101, template="math_reasoning", difficulty="easy")

    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_generate_scenario_varies_across_seeded_cases() -> None:
    first = generate_scenario(seed=101, template="math_reasoning", difficulty="easy")
    second = generate_scenario(seed=102, template="math_reasoning", difficulty="easy")

    assert first.scientist_observation.paper_title != second.scientist_observation.paper_title


def test_available_scenario_families_exposes_three_domain_families() -> None:
    assert available_scenario_families() == [
        {"family": "math_reasoning", "difficulties": ["easy", "medium", "hard"]},
        {"family": "ml_benchmark", "difficulties": ["easy", "medium", "hard"]},
        {"family": "finance_trading", "difficulties": ["easy", "medium", "hard"]},
    ]


def test_hard_finance_scenario_exposes_unavailable_resource_and_safety_rules() -> None:
    pack = generate_scenario(seed=303, template="finance_trading", difficulty="hard")

    assert any(not resource.available for resource in pack.resources)
    assert pack.lab_manager_observation.reagents_out_of_stock
    assert pack.lab_manager_observation.safety_restrictions


def test_difficulty_levels_mechanically_change_budget_and_constraints() -> None:
    easy = generate_scenario(seed=202, template="ml_benchmark", difficulty="easy")
    medium = generate_scenario(seed=202, template="ml_benchmark", difficulty="medium")
    hard = generate_scenario(seed=202, template="ml_benchmark", difficulty="hard")

    assert easy.lab_manager_observation.budget_total > medium.lab_manager_observation.budget_total
    assert medium.lab_manager_observation.budget_total > hard.lab_manager_observation.budget_total
    assert len(easy.constraints) < len(medium.constraints) < len(hard.constraints)


def test_generated_scenarios_keep_unique_constraint_and_resource_keys() -> None:
    for template in ("math_reasoning", "ml_benchmark", "finance_trading"):
        pack = generate_scenario(seed=303, template=template, difficulty="hard")
        constraint_keys = [constraint.key for constraint in pack.constraints]
        resource_keys = [resource.key for resource in pack.resources]
        assert len(constraint_keys) == len(set(constraint_keys))
        assert len(resource_keys) == len(set(resource_keys))
        assert pack.hidden_reference_spec.required_elements
        assert pack.allowed_substitutions


def test_golden_scenario_specs_exist_for_manual_prompt_checks() -> None:
    specs = json.loads(GOLDEN_SCENARIO_SPECS_PATH.read_text(encoding="utf-8"))

    assert len(specs) == 3
    assert [spec["id"] for spec in specs] == [
        "golden_math_easy",
        "golden_ml_medium",
        "golden_finance_hard",
    ]


def test_golden_scenarios_match_expected_title_and_domain() -> None:
    specs = json.loads(GOLDEN_SCENARIO_SPECS_PATH.read_text(encoding="utf-8"))

    for spec in specs:
        pack = generate_scenario(
            seed=spec["seed"],
            template=spec["template"],
            difficulty=spec["difficulty"],
        )
        assert pack.domain_id == spec["expected_domain_id"]
        assert spec["expected_title_contains"] in pack.scientist_observation.paper_title
