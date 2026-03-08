from __future__ import annotations

from replicalab.agents.lab_manager_policy import (
    AlternativeSuggestion,
    check_feasibility,
    compose_lab_manager_response,
    suggest_alternative,
)
from replicalab.models import LabManagerActionType, Protocol
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


# ---------------------------------------------------------------------------
# AGT 07 - compose_lab_manager_response
# ---------------------------------------------------------------------------


def test_compose_lab_manager_response_accepts_feasible_protocol() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _protocol_for_scenario(scenario)
    check = check_feasibility(protocol, scenario)

    action = compose_lab_manager_response(check)

    assert action.action_type is LabManagerActionType.ACCEPT
    assert action.feasible is True
    assert action.suggested_technique == ""
    assert "Accepted." in action.explanation


def test_compose_lab_manager_response_suggests_alternative_when_revision_exists() -> None:
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
    suggestion = suggest_alternative(protocol, check, scenario)

    assert suggestion is not None
    action = compose_lab_manager_response(check, suggestion)

    assert action.action_type is LabManagerActionType.SUGGEST_ALTERNATIVE
    assert action.feasible is False
    assert action.suggested_sample_size == suggestion.revised_protocol.sample_size
    assert action.suggested_controls == suggestion.revised_protocol.controls
    assert "Suggested revision:" in action.explanation


def test_compose_lab_manager_response_rejects_when_no_revision_exists() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _protocol_for_scenario(
        scenario,
        required_equipment=["Imaginary GPU Rack"],
    )
    check = check_feasibility(protocol, scenario)
    suggestion = suggest_alternative(protocol, check, scenario)

    action = compose_lab_manager_response(check, suggestion)

    assert action.action_type is LabManagerActionType.REJECT
    assert action.feasible is False
    assert "No deterministic revision could satisfy" in action.explanation


def test_compose_lab_manager_response_reports_non_lab_issues() -> None:
    scenario = _scenario("finance_trading", "easy")
    protocol = _protocol_for_scenario(
        scenario,
        technique="live trading execution plan",
        rationale="Use live trading once the backtest looks strong.",
    )
    check = check_feasibility(protocol, scenario)
    suggestion = suggest_alternative(protocol, check, scenario)

    action = compose_lab_manager_response(check, suggestion)

    assert action.action_type is LabManagerActionType.REPORT_FEASIBILITY
    assert action.feasible is True
    assert "policy" in action.explanation.lower()


def test_compose_lab_manager_response_uses_custom_renderer_without_changing_verdict() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _protocol_for_scenario(scenario)
    check = check_feasibility(protocol, scenario)

    action = compose_lab_manager_response(
        check,
        explanation_renderer=lambda action_type, result, suggestion: (
            f"Renderer saw {action_type.value} with feasible={result.feasible}."
        ),
    )

    assert action.action_type is LabManagerActionType.ACCEPT
    assert action.feasible is True
    assert action.explanation == "Renderer saw accept with feasible=True."


# ---------------------------------------------------------------------------
# AGT 09 — Deterministic regression suite for the Lab Manager grounding stack
# ---------------------------------------------------------------------------


# --- check_feasibility: determinism and stability ---


def test_check_feasibility_deterministic_across_all_domains() -> None:
    """Same protocol + same scenario -> identical result in every domain."""
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        for difficulty in ("easy", "medium", "hard"):
            scenario = generate_scenario(seed=42, template=template, difficulty=difficulty)
            protocol = _protocol_for_scenario(scenario)

            first = check_feasibility(protocol, scenario).model_dump()
            second = check_feasibility(protocol, scenario).model_dump()

            assert first == second, f"Non-deterministic for {template}/{difficulty}"


def test_check_feasibility_good_protocol_passes_expected_dimensions() -> None:
    """A well-formed protocol passes all lab constraint dimensions."""
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        scenario = generate_scenario(seed=7, template=template, difficulty="easy")
        protocol = _protocol_for_scenario(scenario)
        result = check_feasibility(protocol, scenario)

        assert result.budget_ok is True, f"budget failed for {template}"
        assert result.equipment_ok is True, f"equipment failed for {template}"
        assert result.reagents_ok is True, f"reagents failed for {template}"
        assert result.schedule_ok is True, f"schedule failed for {template}"
        assert result.staff_ok is True, f"staff failed for {template}"


def test_check_feasibility_bad_protocol_fails_expected_dimensions() -> None:
    """An over-budget, over-schedule protocol fails budget and schedule."""
    scenario = _scenario("ml_benchmark", "easy")
    time_limit = scenario.lab_manager_observation.time_limit_days
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=200,
        duration_days=time_limit + 10,
        controls=["baseline", "ablation", "sanity", "extra"],
        required_equipment=list(scenario.lab_manager_observation.equipment_available)
        + ["Imaginary Device"],
    )
    result = check_feasibility(protocol, scenario)

    assert result.budget_ok is False
    assert result.schedule_ok is False
    assert result.equipment_ok is False
    assert result.feasible is False


def test_check_feasibility_substitution_options_stable_and_ordered() -> None:
    """Substitution options for the same unavailable item are identical across runs."""
    scenario = _scenario("math_reasoning", "easy")
    lab = scenario.lab_manager_observation

    # Force an equipment item to be booked
    if lab.equipment_available:
        booked = lab.equipment_available[0]
        lab.equipment_booked.append(booked)
        lab.equipment_available = lab.equipment_available[1:]

        protocol = _protocol_for_scenario(scenario, required_equipment=[booked])

        r1 = check_feasibility(protocol, scenario)
        r2 = check_feasibility(protocol, scenario)

        assert r1.substitution_options == r2.substitution_options
        if booked in r1.substitution_options:
            assert r1.substitution_options[booked] == r2.substitution_options[booked]


def test_check_feasibility_estimated_cost_deterministic() -> None:
    """Estimated cost is stable across repeated calls."""
    scenario = _scenario("finance_trading", "medium")
    protocol = _protocol_for_scenario(scenario, sample_size=30)

    c1 = check_feasibility(protocol, scenario).estimated_cost
    c2 = check_feasibility(protocol, scenario).estimated_cost

    assert c1 == c2


def test_check_feasibility_summary_stable() -> None:
    """Summary string is identical across repeated calls."""
    scenario = _scenario("ml_benchmark", "hard")
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=200,
        duration_days=scenario.lab_manager_observation.time_limit_days + 5,
    )
    s1 = check_feasibility(protocol, scenario).summary
    s2 = check_feasibility(protocol, scenario).summary

    assert s1 == s2
    assert isinstance(s1, str)
    assert len(s1) > 0


# --- suggest_alternative: determinism and stability ---


def test_suggest_alternative_first_alternative_chosen_consistently() -> None:
    """The same booked-equipment scenario always picks the same first substitution."""
    from replicalab.scenarios.templates import AllowedSubstitution

    scenario = _scenario("math_reasoning", "easy")
    lab = scenario.lab_manager_observation

    if not lab.equipment_available:
        return

    booked = lab.equipment_available[0]
    lab.equipment_booked.append(booked)
    lab.equipment_available = lab.equipment_available[1:]

    scenario.allowed_substitutions.append(AllowedSubstitution(
        original=booked,
        alternative="alt_tool_A",
        condition="when booked",
        tradeoff="slower",
    ))
    scenario.allowed_substitutions.append(AllowedSubstitution(
        original=booked,
        alternative="alt_tool_B",
        condition="when booked",
        tradeoff="less precise",
    ))

    protocol = _protocol_for_scenario(scenario, required_equipment=[booked])
    check = check_feasibility(protocol, scenario)

    r1 = suggest_alternative(protocol, check, scenario)
    r2 = suggest_alternative(protocol, check, scenario)

    assert r1 is not None and r2 is not None
    # First stable alternative is always chosen
    equip_changes_1 = [c for c in r1.applied_changes if c.field == "required_equipment"]
    equip_changes_2 = [c for c in r2.applied_changes if c.field == "required_equipment"]
    assert len(equip_changes_1) == len(equip_changes_2)
    for c1, c2 in zip(equip_changes_1, equip_changes_2):
        assert c1.revised == c2.revised


def test_suggest_alternative_duration_clamp_deterministic() -> None:
    """Duration clamp produces identical revised duration across runs."""
    scenario = _scenario("finance_trading", "easy")
    time_limit = scenario.lab_manager_observation.time_limit_days
    protocol = _protocol_for_scenario(scenario, duration_days=time_limit + 7)
    check = check_feasibility(protocol, scenario)

    r1 = suggest_alternative(protocol, check, scenario)
    r2 = suggest_alternative(protocol, check, scenario)

    assert r1 is not None and r2 is not None
    assert r1.revised_protocol.duration_days == r2.revised_protocol.duration_days
    assert r1.revised_protocol.duration_days <= time_limit


def test_suggest_alternative_sample_reduction_deterministic() -> None:
    """Sample-size reduction produces identical values across runs."""
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

    r1 = suggest_alternative(protocol, check, scenario)
    r2 = suggest_alternative(protocol, check, scenario)

    assert r1 is not None and r2 is not None
    assert r1.revised_protocol.sample_size == r2.revised_protocol.sample_size
    assert r1.revised_protocol.sample_size < 200


def test_suggest_alternative_cross_domain_deterministic() -> None:
    """suggest_alternative output is stable across all domains."""
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        scenario = generate_scenario(seed=42, template=template, difficulty="hard")
        time_limit = scenario.lab_manager_observation.time_limit_days
        protocol = _protocol_for_scenario(
            scenario,
            sample_size=100,
            duration_days=time_limit + 3,
        )
        check = check_feasibility(protocol, scenario)
        if check.feasible:
            continue

        r1 = suggest_alternative(protocol, check, scenario)
        r2 = suggest_alternative(protocol, check, scenario)

        assert r1 is not None and r2 is not None
        assert r1.revised_protocol == r2.revised_protocol, f"Non-deterministic for {template}"
        assert r1.remaining_failures == r2.remaining_failures
        assert r1.improved == r2.improved


def test_suggest_alternative_never_worsens_failing_count() -> None:
    """Post-check failing dimension count <= pre-check failing count, all domains."""
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        for difficulty in ("easy", "medium", "hard"):
            scenario = generate_scenario(seed=99, template=template, difficulty=difficulty)
            time_limit = scenario.lab_manager_observation.time_limit_days
            protocol = _protocol_for_scenario(
                scenario,
                sample_size=150,
                duration_days=time_limit + 5,
            )
            check = check_feasibility(protocol, scenario)
            if check.feasible:
                continue

            result = suggest_alternative(protocol, check, scenario)
            if result is None:
                continue

            pre_count = sum(
                1 for d in ("protocol", "budget", "equipment", "reagents", "schedule", "staff", "policy")
                if not getattr(check, d).ok
            )
            assert len(result.remaining_failures) <= pre_count, (
                f"Worsened for {template}/{difficulty}: "
                f"{len(result.remaining_failures)} > {pre_count}"
            )


# --- compose_lab_manager_response: determinism and stability ---


def test_compose_response_deterministic() -> None:
    """Same check + suggestion -> identical LabManagerAction."""
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
    suggestion = suggest_alternative(protocol, check, scenario)

    a1 = compose_lab_manager_response(check, suggestion)
    a2 = compose_lab_manager_response(check, suggestion)

    assert a1.action_type == a2.action_type
    assert a1.feasible == a2.feasible
    assert a1.explanation == a2.explanation
    assert a1.suggested_sample_size == a2.suggested_sample_size
    assert a1.suggested_technique == a2.suggested_technique
    assert a1.suggested_controls == a2.suggested_controls


def test_compose_response_flags_mirror_check_result() -> None:
    """LabManagerAction flag fields exactly mirror FeasibilityCheckResult."""
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        scenario = generate_scenario(seed=42, template=template, difficulty="easy")
        protocol = _protocol_for_scenario(scenario)
        check = check_feasibility(protocol, scenario)

        action = compose_lab_manager_response(check)

        assert action.budget_ok == check.budget_ok, f"budget mismatch for {template}"
        assert action.equipment_ok == check.equipment_ok, f"equipment mismatch for {template}"
        assert action.reagents_ok == check.reagents_ok, f"reagents mismatch for {template}"
        assert action.schedule_ok == check.schedule_ok, f"schedule mismatch for {template}"
        assert action.staff_ok == check.staff_ok, f"staff mismatch for {template}"


def test_compose_response_flags_mirror_infeasible_check() -> None:
    """Flags mirror the check result even when dimensions fail."""
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=200,
        duration_days=scenario.lab_manager_observation.time_limit_days + 10,
        required_equipment=["Imaginary Device"],
    )
    check = check_feasibility(protocol, scenario)
    suggestion = suggest_alternative(protocol, check, scenario)
    action = compose_lab_manager_response(check, suggestion)

    assert action.budget_ok == check.budget_ok
    assert action.equipment_ok == check.equipment_ok
    assert action.schedule_ok == check.schedule_ok
    assert action.staff_ok == check.staff_ok


def test_compose_response_explanation_stable() -> None:
    """Explanation text is identical across repeated calls with the same inputs."""
    scenario = _scenario("finance_trading", "hard")
    time_limit = scenario.lab_manager_observation.time_limit_days
    protocol = _protocol_for_scenario(
        scenario,
        sample_size=60,
        duration_days=time_limit + 3,
    )
    check = check_feasibility(protocol, scenario)
    suggestion = suggest_alternative(protocol, check, scenario)

    e1 = compose_lab_manager_response(check, suggestion).explanation
    e2 = compose_lab_manager_response(check, suggestion).explanation

    assert e1 == e2
    assert len(e1) > 0


def test_compose_response_action_type_branching_stable() -> None:
    """Action-type selection is stable across all domain/difficulty combos."""
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        for difficulty in ("easy", "medium", "hard"):
            scenario = generate_scenario(seed=42, template=template, difficulty=difficulty)
            protocol = _protocol_for_scenario(scenario)
            check = check_feasibility(protocol, scenario)
            suggestion = suggest_alternative(protocol, check, scenario)

            a1 = compose_lab_manager_response(check, suggestion)
            a2 = compose_lab_manager_response(check, suggestion)

            assert a1.action_type == a2.action_type, (
                f"Action type unstable for {template}/{difficulty}"
            )


def test_compose_response_accept_for_feasible_all_domains() -> None:
    """A feasible protocol in any domain produces an ACCEPT action."""
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        scenario = generate_scenario(seed=7, template=template, difficulty="easy")
        protocol = _protocol_for_scenario(scenario)
        check = check_feasibility(protocol, scenario)

        if not check.feasible:
            continue

        action = compose_lab_manager_response(check)
        assert action.action_type is LabManagerActionType.ACCEPT, (
            f"Expected ACCEPT for feasible {template}, got {action.action_type}"
        )
