"""Tests for MOD 05 — deterministic semantic validation."""

from __future__ import annotations

from replicalab.models import Protocol
from replicalab.scenarios.templates import generate_scenario
from replicalab.utils.validation import (
    IssueSeverity,
    ValidationResult,
    validate_protocol,
)


def _easy_math_scenario():
    return generate_scenario(seed=42, template="math_reasoning", difficulty="easy")


def _hard_finance_scenario():
    return generate_scenario(seed=42, template="finance_trading", difficulty="hard")


def _protocol_for_scenario(scenario, **overrides) -> Protocol:
    """Build a plausible protocol from the scenario's lab inventory."""
    lab = scenario.lab_manager_observation
    defaults = {
        "sample_size": 10,
        "controls": ["baseline"],
        "technique": "grid_search",
        "duration_days": lab.time_limit_days,
        "required_equipment": list(lab.equipment_available[:1]) if lab.equipment_available else ["compute"],
        "required_reagents": list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else ["data"],
        "rationale": "Uses available resources within time and budget.",
    }
    defaults.update(overrides)
    return Protocol(**defaults)


# ---------------------------------------------------------------------------
# Basic valid / invalid
# ---------------------------------------------------------------------------


def test_valid_protocol_passes() -> None:
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(scenario)
    result = validate_protocol(protocol, scenario)

    assert result.valid is True
    assert len(result.errors) == 0


def test_zero_sample_size_is_error() -> None:
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(scenario, sample_size=0)
    result = validate_protocol(protocol, scenario)

    assert result.valid is False
    assert any(i.category == "sample_size" for i in result.errors)


def test_zero_duration_is_error() -> None:
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(scenario, duration_days=0)
    result = validate_protocol(protocol, scenario)

    assert result.valid is False
    assert any(
        i.category == "duration" and i.severity is IssueSeverity.ERROR
        for i in result.issues
    )


# ---------------------------------------------------------------------------
# Duration vs time limit
# ---------------------------------------------------------------------------


def test_duration_exceeding_time_limit_is_error() -> None:
    scenario = _easy_math_scenario()
    time_limit = scenario.lab_manager_observation.time_limit_days
    protocol = _protocol_for_scenario(scenario, duration_days=time_limit + 5)
    result = validate_protocol(protocol, scenario)

    assert result.valid is False
    duration_errors = [
        i for i in result.errors
        if i.category == "duration" and "exceeds" in i.message
    ]
    assert len(duration_errors) == 1


def test_duration_within_limit_passes() -> None:
    scenario = _easy_math_scenario()
    time_limit = scenario.lab_manager_observation.time_limit_days
    protocol = _protocol_for_scenario(scenario, duration_days=time_limit)
    result = validate_protocol(protocol, scenario)

    duration_errors = [
        i for i in result.errors if i.category == "duration" and "exceeds" in i.message
    ]
    assert len(duration_errors) == 0


# ---------------------------------------------------------------------------
# Equipment vocabulary
# ---------------------------------------------------------------------------


def test_unknown_equipment_is_warning() -> None:
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(
        scenario,
        required_equipment=["quantum_flux_capacitor"],
    )
    result = validate_protocol(protocol, scenario)

    equip_warnings = [
        i for i in result.warnings if i.category == "equipment"
    ]
    assert len(equip_warnings) >= 1
    assert "not in the lab" in equip_warnings[0].message


def test_booked_equipment_without_substitution_is_error() -> None:
    scenario = _easy_math_scenario()
    lab = scenario.lab_manager_observation
    if not lab.equipment_booked:
        # Force a booked item for the test
        lab.equipment_booked.append("special_scope")
        lab.equipment_available = [
            e for e in lab.equipment_available if e != "special_scope"
        ]
    booked_item = lab.equipment_booked[0]
    protocol = _protocol_for_scenario(
        scenario,
        required_equipment=[booked_item],
    )
    result = validate_protocol(protocol, scenario)

    equip_errors = [i for i in result.errors if i.category == "equipment"]
    assert len(equip_errors) >= 1


# ---------------------------------------------------------------------------
# Reagent vocabulary
# ---------------------------------------------------------------------------


def test_out_of_stock_reagent_without_substitution_is_error() -> None:
    scenario = _easy_math_scenario()
    lab = scenario.lab_manager_observation
    if not lab.reagents_out_of_stock:
        lab.reagents_out_of_stock.append("unobtainium")
    oos_item = lab.reagents_out_of_stock[0]
    protocol = _protocol_for_scenario(
        scenario,
        required_reagents=[oos_item],
    )
    result = validate_protocol(protocol, scenario)

    reagent_errors = [i for i in result.errors if i.category == "reagent"]
    assert len(reagent_errors) >= 1


def test_unknown_reagent_is_warning() -> None:
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(
        scenario,
        required_reagents=["exotic_compound_99"],
    )
    result = validate_protocol(protocol, scenario)

    reagent_warnings = [i for i in result.warnings if i.category == "reagent"]
    assert len(reagent_warnings) >= 1


# ---------------------------------------------------------------------------
# Required-element coverage
# ---------------------------------------------------------------------------


def test_required_element_warning_when_not_addressed() -> None:
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(
        scenario,
        technique="unrelated_method",
        rationale="No relation to any required element.",
        controls=[],
        required_equipment=["laptop"],
        required_reagents=["water"],
    )
    result = validate_protocol(protocol, scenario)

    element_warnings = [
        i for i in result.warnings if i.category == "required_element"
    ]
    assert len(element_warnings) >= 1


# ---------------------------------------------------------------------------
# MOD 06 — Semantic impossibility checks
# ---------------------------------------------------------------------------


def test_zero_sample_with_controls_is_error() -> None:
    """Zero sample_size + non-empty controls is self-contradictory."""
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=0,
        controls=["baseline", "positive"],
    )
    result = validate_protocol(protocol, scenario)

    assert result.valid is False
    sc_errors = [i for i in result.errors if i.category == "sample_controls"]
    assert len(sc_errors) >= 1
    assert "controls require samples" in sc_errors[0].message


def test_controls_count_gte_sample_size_is_error() -> None:
    """More controls than samples means no experimental samples remain."""
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=2,
        controls=["baseline", "positive", "negative"],
    )
    result = validate_protocol(protocol, scenario)

    assert result.valid is False
    sc_errors = [i for i in result.errors if i.category == "sample_controls"]
    assert len(sc_errors) >= 1
    assert "no experimental samples remain" in sc_errors[0].message


def test_controls_equal_sample_size_is_error() -> None:
    """Exactly as many controls as samples — still no experimental arm."""
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=2,
        controls=["baseline", "positive"],
    )
    result = validate_protocol(protocol, scenario)

    assert result.valid is False
    sc_errors = [i for i in result.errors if i.category == "sample_controls"]
    assert len(sc_errors) >= 1


def test_duplicate_controls_is_warning() -> None:
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=20,
        controls=["baseline", "baseline", "positive"],
    )
    result = validate_protocol(protocol, scenario)

    dup_warnings = [i for i in result.warnings if i.category == "duplicate_controls"]
    assert len(dup_warnings) == 1
    assert "baseline" in dup_warnings[0].message


def test_duplicate_equipment_is_warning() -> None:
    scenario = _easy_math_scenario()
    lab = scenario.lab_manager_observation
    equip = lab.equipment_available[0] if lab.equipment_available else "compute"
    protocol = _protocol_for_scenario(
        scenario,
        required_equipment=[equip, equip],
    )
    result = validate_protocol(protocol, scenario)

    dup_warnings = [i for i in result.warnings if i.category == "duplicate_equipment"]
    assert len(dup_warnings) == 1


def test_duplicate_reagents_is_warning() -> None:
    scenario = _easy_math_scenario()
    lab = scenario.lab_manager_observation
    reagent = lab.reagents_in_stock[0] if lab.reagents_in_stock else "data"
    protocol = _protocol_for_scenario(
        scenario,
        required_reagents=[reagent, reagent],
    )
    result = validate_protocol(protocol, scenario)

    dup_warnings = [i for i in result.warnings if i.category == "duplicate_reagents"]
    assert len(dup_warnings) == 1


def test_valid_protocol_still_passes_after_mod06() -> None:
    """Ensure MOD 06 checks don't break valid protocols."""
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(scenario, sample_size=10, controls=["baseline"])
    result = validate_protocol(protocol, scenario)

    assert result.valid is True
    assert len(result.errors) == 0
    # No MOD 06 categories should appear as errors
    mod06_errors = [
        i for i in result.errors
        if i.category in ("sample_controls", "duplicate_controls", "duplicate_equipment", "duplicate_reagents")
    ]
    assert len(mod06_errors) == 0


def test_no_controls_is_warning() -> None:
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(scenario, controls=[])
    result = validate_protocol(protocol, scenario)

    control_warnings = [
        i for i in result.warnings if i.category == "controls"
    ]
    assert len(control_warnings) == 1


# ---------------------------------------------------------------------------
# Result structure
# ---------------------------------------------------------------------------


def test_validation_result_never_raises() -> None:
    """validate_protocol should always return a result, never crash."""
    scenario = _easy_math_scenario()
    protocol = Protocol(
        sample_size=0,
        controls=[],
        technique="nothing",
        duration_days=0,
        required_equipment=["nonexistent"],
        required_reagents=["nonexistent"],
        rationale="Completely invalid.",
    )
    result = validate_protocol(protocol, scenario)

    assert isinstance(result, ValidationResult)
    assert result.valid is False
    assert len(result.issues) > 0


def test_validation_result_json_round_trip() -> None:
    scenario = _easy_math_scenario()
    protocol = _protocol_for_scenario(scenario, sample_size=0)
    result = validate_protocol(protocol, scenario)

    dumped = result.model_dump_json()
    restored = ValidationResult.model_validate_json(dumped)

    assert restored.valid == result.valid
    assert len(restored.issues) == len(result.issues)
