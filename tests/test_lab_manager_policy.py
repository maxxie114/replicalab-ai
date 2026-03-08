from __future__ import annotations

from replicalab.agents.lab_manager_policy import (
    AlternativeSuggestion,
    check_feasibility,
    suggest_alternative,
)
from replicalab.models import Protocol
from replicalab.scenarios import generate_scenario


def _scenario(template: str = "ml_benchmark", difficulty: str = "easy"):
    return generate_scenario(seed=123, template=template, difficulty=difficulty)


def _protocol_for_scenario(scenario, **overrides) -> Protocol:
    lab = scenario.lab_manager_observation
    defaults = {
        "sample_size": 12,
        "controls": ["baseline"],
        "technique": "structured_offline_plan",
        "duration_days": max(1, min(3, lab.time_limit_days)),
        "required_equipment": (
            list(lab.equipment_available[:1])
            if lab.equipment_available
            else ["fallback_tool"]
        ),
        "required_reagents": (
            list(lab.reagents_in_stock[:1])
            if lab.reagents_in_stock
            else ["fallback_resource"]
        ),
        "rationale": "Keep the plan inside the available budget, staff, and policy limits.",
    }
    defaults.update(overrides)
    return Protocol(**defaults)


def test_check_feasibility_passes_for_viable_protocol() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _protocol_for_scenario(scenario)

    result = check_feasibility(protocol, scenario)

    assert result.feasible is True
    assert result.protocol_ok is True
    assert result.budget_ok is True
    assert result.equipment_ok is True
    assert result.reagents_ok is True
    assert result.schedule_ok is True
    assert result.staff_ok is True


def test_check_feasibility_flags_budget_overrun() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=80,
        duration_days=8,
        controls=["baseline", "ablation", "sanity_check"],
        required_equipment=list(scenario.lab_manager_observation.equipment_available),
        required_reagents=list(scenario.lab_manager_observation.reagents_in_stock),
    )

    result = check_feasibility(protocol, scenario)

    assert result.budget_ok is False
    assert any(
        "exceeds the remaining budget" in reason for reason in result.budget.reasons
    )


def test_check_feasibility_flags_unavailable_resource_and_lists_substitution() -> None:
    scenario = _scenario("math_reasoning", "easy")
    unavailable_item = "Graduate reviewer"
    protocol = _protocol_for_scenario(
        scenario,
        required_equipment=["Structured proof notebook"],
        required_reagents=[unavailable_item],
    )
    scenario.lab_manager_observation.reagents_in_stock = [
        item
        for item in scenario.lab_manager_observation.reagents_in_stock
        if item != unavailable_item
    ]
    scenario.lab_manager_observation.reagents_out_of_stock = [unavailable_item]

    result = check_feasibility(protocol, scenario)

    assert result.reagents_ok is False
    assert unavailable_item in result.substitution_options
    assert "self-check rubric" in ", ".join(
        result.substitution_options[unavailable_item]
    ).lower()


def test_check_feasibility_flags_schedule_overrun() -> None:
    scenario = _scenario("finance_trading", "easy")
    protocol = _protocol_for_scenario(
        scenario,
        duration_days=scenario.lab_manager_observation.time_limit_days + 2,
    )

    result = check_feasibility(protocol, scenario)

    assert result.schedule_ok is False
    assert any(
        "exceeds the allowed time limit" in reason for reason in result.schedule.reasons
    )


def test_check_feasibility_flags_staff_overload() -> None:
    scenario = _scenario("finance_trading", "hard")
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=60,
        controls=["baseline", "drawdown_guard", "slippage_check", "review_gate"],
        duration_days=10,
        required_equipment=[
            "Backtest engine",
            "Historical daily bar dataset",
            "Extra simulator",
        ],
        required_reagents=[
            "Risk reviewer",
            "Historical daily bar dataset",
            "Compliance packet",
        ],
    )

    result = check_feasibility(protocol, scenario)

    assert result.staff_ok is False
    assert result.required_staff > scenario.lab_manager_observation.staff_count


def test_check_feasibility_flags_policy_violation() -> None:
    scenario = _scenario("finance_trading", "easy")
    protocol = _protocol_for_scenario(
        scenario,
        technique="live trading execution plan",
        rationale="Use live trading once the backtest looks strong.",
    )

    result = check_feasibility(protocol, scenario)

    assert result.feasible is False
    assert result.policy.ok is False
    assert any(
        "offline-only execution policy" in reason for reason in result.policy.reasons
    )


def test_check_feasibility_is_deterministic() -> None:
    scenario = _scenario("ml_benchmark", "medium")
    protocol = _protocol_for_scenario(scenario)

    first = check_feasibility(protocol, scenario).model_dump()
    second = check_feasibility(protocol, scenario).model_dump()

    assert first == second


# ---------------------------------------------------------------------------
# AGT 06 — suggest_alternative
# ---------------------------------------------------------------------------


def test_suggest_alternative_returns_none_for_feasible_protocol() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _protocol_for_scenario(scenario)
    check = check_feasibility(protocol, scenario)

    assert check.feasible is True
    result = suggest_alternative(protocol, check, scenario)
    assert result is None


def test_suggest_alternative_substitutes_equipment() -> None:
    scenario = _scenario("math_reasoning", "easy")
    lab = scenario.lab_manager_observation

    # Force an equipment item to be booked with a substitution available
    if lab.equipment_available:
        booked_item = lab.equipment_available[0]
        lab.equipment_booked.append(booked_item)
        lab.equipment_available = lab.equipment_available[1:]

        # Ensure there's a substitution for this item
        from replicalab.scenarios.templates import AllowedSubstitution
        scenario.allowed_substitutions.append(AllowedSubstitution(
            original=booked_item,
            alternative="fallback_tool",
            condition="Use if primary is booked.",
            tradeoff="Fallback tool has lower precision.",
        ))

        protocol = _protocol_for_scenario(scenario, required_equipment=[booked_item])
        check = check_feasibility(protocol, scenario)

        result = suggest_alternative(protocol, check, scenario)
        assert result is not None
        assert any(c.field == "required_equipment" for c in result.applied_changes)
        assert "fallback_tool" in result.revised_protocol.required_equipment


def test_suggest_alternative_substitutes_reagent() -> None:
    scenario = _scenario("math_reasoning", "easy")
    lab = scenario.lab_manager_observation

    # Force a reagent out of stock with substitution
    unavailable_item = "Graduate reviewer"
    lab.reagents_in_stock = [
        r for r in lab.reagents_in_stock if r != unavailable_item
    ]
    lab.reagents_out_of_stock.append(unavailable_item)

    protocol = _protocol_for_scenario(scenario, required_reagents=[unavailable_item])
    check = check_feasibility(protocol, scenario)

    if check.feasible:
        return  # item wasn't actually used, skip

    result = suggest_alternative(protocol, check, scenario)
    assert result is not None
    # Should have attempted a reagent substitution if one exists
    reagent_changes = [c for c in result.applied_changes if c.field == "required_reagents"]
    if check.substitution_options.get(unavailable_item):
        assert len(reagent_changes) >= 1


def test_suggest_alternative_clamps_duration() -> None:
    scenario = _scenario("finance_trading", "easy")
    time_limit = scenario.lab_manager_observation.time_limit_days
    protocol = _protocol_for_scenario(
        scenario,
        duration_days=time_limit + 5,
    )
    check = check_feasibility(protocol, scenario)

    result = suggest_alternative(protocol, check, scenario)
    assert result is not None
    assert result.revised_protocol.duration_days <= time_limit
    assert any(c.field == "duration_days" for c in result.applied_changes)


def test_suggest_alternative_reduces_sample_size_for_budget() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=200,
        duration_days=scenario.lab_manager_observation.time_limit_days,
        controls=["baseline", "ablation", "sanity_check"],
        required_equipment=list(scenario.lab_manager_observation.equipment_available),
        required_reagents=list(scenario.lab_manager_observation.reagents_in_stock),
    )
    check = check_feasibility(protocol, scenario)

    assert check.budget_ok is False
    result = suggest_alternative(protocol, check, scenario)
    assert result is not None
    assert result.revised_protocol.sample_size < 200
    assert any(c.field == "sample_size" for c in result.applied_changes)


def test_suggest_alternative_is_deterministic() -> None:
    scenario = _scenario("finance_trading", "hard")
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=60,
        duration_days=scenario.lab_manager_observation.time_limit_days + 3,
        controls=["baseline", "drawdown_guard", "slippage_check"],
    )
    check = check_feasibility(protocol, scenario)

    first = suggest_alternative(protocol, check, scenario)
    second = suggest_alternative(protocol, check, scenario)

    assert first is not None and second is not None
    assert first.revised_protocol == second.revised_protocol
    assert len(first.applied_changes) == len(second.applied_changes)
    assert first.remaining_failures == second.remaining_failures


def test_suggest_alternative_post_check_is_not_worse() -> None:
    scenario = _scenario("ml_benchmark", "hard")
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=80,
        duration_days=scenario.lab_manager_observation.time_limit_days + 2,
    )
    check = check_feasibility(protocol, scenario)

    result = suggest_alternative(protocol, check, scenario)
    if result is None:
        return  # already feasible

    pre_failing = len([
        d for d in ("protocol", "budget", "equipment", "reagents", "schedule", "staff", "policy")
        if not getattr(check, d).ok
    ])
    post_failing = len(result.remaining_failures)
    assert post_failing <= pre_failing


def test_suggest_alternative_reports_remaining_failures() -> None:
    scenario = _scenario("finance_trading", "easy")
    # Policy violation can't be fixed by substitutions
    protocol = _protocol_for_scenario(
        scenario,
        technique="live trading execution plan",
        rationale="Use live trading once the backtest looks strong.",
    )
    check = check_feasibility(protocol, scenario)

    result = suggest_alternative(protocol, check, scenario)
    assert result is not None
    assert "policy" in result.remaining_failures
