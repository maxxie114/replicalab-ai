from __future__ import annotations

import json

from replicalab.scenarios import (
    GOLDEN_SCENARIO_SPECS_PATH,
    NormalizedScenarioPack,
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


# ---------------------------------------------------------------------------
# SCN 13 — Booking and scheduling data model
# ---------------------------------------------------------------------------


def test_booking_data_is_deterministic_for_same_seed() -> None:
    """Same seed produces identical bookings and scheduling windows."""
    a = generate_scenario(seed=42, template="ml_benchmark", difficulty="medium")
    b = generate_scenario(seed=42, template="ml_benchmark", difficulty="medium")

    a_dump = a.model_dump(mode="json")
    b_dump = b.model_dump(mode="json")
    assert a_dump["resource_bookings"] == b_dump["resource_bookings"]
    assert a_dump["scheduling_windows"] == b_dump["scheduling_windows"]


def test_easy_bookings_have_no_conflicts() -> None:
    """All booking slots are 'available' at easy difficulty."""
    for template in ("math_reasoning", "ml_benchmark", "finance_trading"):
        pack = generate_scenario(seed=42, template=template, difficulty="easy")
        for b in pack.resource_bookings:
            assert b.status == "available", (
                f"{template}: {b.slot_label} is {b.status}"
            )


def test_bookings_serialize_round_trip() -> None:
    """Bookings and windows survive JSON serialization."""
    pack = generate_scenario(seed=42, template="finance_trading", difficulty="hard")
    dumped = pack.model_dump(mode="json")
    restored = NormalizedScenarioPack.model_validate(dumped)

    assert len(restored.resource_bookings) == len(pack.resource_bookings)
    assert len(restored.scheduling_windows) == len(pack.scheduling_windows)
    assert dumped["resource_bookings"] == restored.model_dump(mode="json")["resource_bookings"]


def test_scheduling_windows_are_valid() -> None:
    """All scheduling windows have end > start and non-negative offsets."""
    for template in ("math_reasoning", "ml_benchmark", "finance_trading"):
        for diff in ("easy", "medium", "hard"):
            pack = generate_scenario(seed=42, template=template, difficulty=diff)
            for w in pack.scheduling_windows:
                assert w.end_offset_hours > w.start_offset_hours, (
                    f"{template}/{diff}: window {w.key} has end <= start"
                )
                assert w.start_offset_hours >= 0.0


def test_all_domains_produce_bookings_and_windows() -> None:
    """Each domain template generates at least one booking and one window."""
    for template in ("math_reasoning", "ml_benchmark", "finance_trading"):
        pack = generate_scenario(seed=42, template=template, difficulty="medium")
        assert len(pack.resource_bookings) > 0, f"{template} has no bookings"
        assert len(pack.scheduling_windows) > 0, f"{template} has no windows"
