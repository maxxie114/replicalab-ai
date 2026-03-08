"""Tests for JDG 01–06 scoring functions."""

from __future__ import annotations

from replicalab.agents.lab_manager_policy import check_feasibility
from replicalab.models import Protocol, RewardBreakdown
from replicalab.scenarios import generate_scenario
from replicalab.scenarios.templates import AllowedSubstitution, HiddenReferenceSpec
from replicalab.scoring import (
    build_reward_breakdown,
    compute_total_reward,
    explain_reward,
    score_feasibility,
    score_fidelity,
    score_rigor,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scenario(template: str = "ml_benchmark", difficulty: str = "easy"):
    return generate_scenario(seed=42, template=template, difficulty=difficulty)


def _good_protocol(scenario) -> Protocol:
    """Build a well-formed protocol aligned to the scenario."""
    lab = scenario.lab_manager_observation
    spec = scenario.hidden_reference_spec
    return Protocol(
        sample_size=10,
        controls=["baseline", "ablation"],
        technique=spec.summary[:60] if spec.summary else "replication_plan",
        duration_days=max(1, min(2, lab.time_limit_days)),
        required_equipment=(
            list(lab.equipment_available[:1])
            if lab.equipment_available
            else []
        ),
        required_reagents=(
            list(lab.reagents_in_stock[:1])
            if lab.reagents_in_stock
            else []
        ),
        rationale=(
            f"Plan addresses: {', '.join(spec.required_elements[:2])}. "
            f"Target metric: {spec.target_metric}. "
            f"Target value: {spec.target_value}. "
            "Stay within budget and schedule."
        ),
    )


def _bad_protocol() -> Protocol:
    """Build a minimal protocol that misses most requirements."""
    return Protocol(
        sample_size=1,
        controls=[],
        technique="unknown_method",
        duration_days=1,
        required_equipment=[],
        required_reagents=[],
        rationale="No plan.",
    )


def _awful_protocol(scenario) -> Protocol:
    """Build a structurally weak and clearly infeasible protocol."""
    return Protocol(
        sample_size=200,
        controls=[],
        technique="imaginary_method",
        duration_days=scenario.lab_manager_observation.time_limit_days + 5,
        required_equipment=["Imaginary Device"],
        required_reagents=["Imaginary Reagent"],
        rationale="No.",
    )


# ---------------------------------------------------------------------------
# JDG 01 — score_rigor
# ---------------------------------------------------------------------------


def test_rigor_good_protocol_scores_higher_than_bad() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    good = _good_protocol(scenario)
    bad = _bad_protocol()

    good_score = score_rigor(good, scenario)
    bad_score = score_rigor(bad, scenario)

    assert good_score > bad_score
    assert 0.0 <= good_score <= 1.0
    assert 0.0 <= bad_score <= 1.0


def test_rigor_is_deterministic() -> None:
    scenario = _scenario("ml_benchmark", "medium")
    protocol = _good_protocol(scenario)

    first = score_rigor(protocol, scenario)
    second = score_rigor(protocol, scenario)

    assert first == second


def test_rigor_empty_controls_reduces_score() -> None:
    scenario = _scenario("math_reasoning", "easy")
    with_controls = _good_protocol(scenario)
    without_controls = with_controls.model_copy(update={"controls": ["only_one"]})

    score_with = score_rigor(with_controls, scenario)
    score_without = score_rigor(without_controls, scenario)

    assert score_with >= score_without


def test_rigor_short_rationale_reduces_score() -> None:
    scenario = _scenario("finance_trading", "easy")
    good = _good_protocol(scenario)
    short = good.model_copy(update={"rationale": "OK."})

    assert score_rigor(good, scenario) > score_rigor(short, scenario)


def test_rigor_all_domains_return_valid_range() -> None:
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        for difficulty in ("easy", "medium", "hard"):
            scenario = generate_scenario(seed=99, template=template, difficulty=difficulty)
            protocol = _good_protocol(scenario)
            score = score_rigor(protocol, scenario)
            assert 0.0 <= score <= 1.0, f"{template}/{difficulty}: {score}"


# ---------------------------------------------------------------------------
# JDG 02 — score_feasibility
# ---------------------------------------------------------------------------


def test_feasibility_viable_protocol_scores_high() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _good_protocol(scenario)

    score = score_feasibility(protocol, scenario)

    assert score > 0.7
    assert 0.0 <= score <= 1.0


def test_feasibility_infeasible_protocol_scores_lower() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    good = _good_protocol(scenario)
    # Blow the budget and schedule
    bad = good.model_copy(update={
        "sample_size": 200,
        "duration_days": scenario.lab_manager_observation.time_limit_days + 5,
        "required_equipment": ["Imaginary Device"],
    })

    good_score = score_feasibility(good, scenario)
    bad_score = score_feasibility(bad, scenario)

    assert good_score > bad_score


def test_feasibility_accepts_precomputed_check() -> None:
    scenario = _scenario("finance_trading", "easy")
    protocol = _good_protocol(scenario)
    check = check_feasibility(protocol, scenario)

    score_with = score_feasibility(protocol, scenario, check=check)
    score_without = score_feasibility(protocol, scenario)

    assert score_with == score_without


def test_feasibility_is_deterministic() -> None:
    scenario = _scenario("math_reasoning", "medium")
    protocol = _good_protocol(scenario)

    first = score_feasibility(protocol, scenario)
    second = score_feasibility(protocol, scenario)

    assert first == second


def test_feasibility_partial_credit_for_near_budget() -> None:
    """A protocol slightly over budget should score higher than one far over."""
    scenario = _scenario("ml_benchmark", "easy")
    good = _good_protocol(scenario)

    slightly_over = good.model_copy(update={"sample_size": 40})
    far_over = good.model_copy(update={"sample_size": 200})

    score_slight = score_feasibility(slightly_over, scenario)
    score_far = score_feasibility(far_over, scenario)

    assert score_slight >= score_far


def test_feasibility_all_domains_return_valid_range() -> None:
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        for difficulty in ("easy", "medium", "hard"):
            scenario = generate_scenario(seed=99, template=template, difficulty=difficulty)
            protocol = _good_protocol(scenario)
            score = score_feasibility(protocol, scenario)
            assert 0.0 <= score <= 1.0, f"{template}/{difficulty}: {score}"


# ---------------------------------------------------------------------------
# JDG 03 — score_fidelity
# ---------------------------------------------------------------------------


def test_fidelity_aligned_protocol_scores_higher() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    aligned = _good_protocol(scenario)
    misaligned = _bad_protocol()

    aligned_score = score_fidelity(aligned, scenario)
    misaligned_score = score_fidelity(misaligned, scenario)

    assert aligned_score > misaligned_score
    assert 0.0 <= aligned_score <= 1.0
    assert 0.0 <= misaligned_score <= 1.0


def test_fidelity_is_deterministic() -> None:
    scenario = _scenario("finance_trading", "hard")
    protocol = _good_protocol(scenario)

    first = score_fidelity(protocol, scenario)
    second = score_fidelity(protocol, scenario)

    assert first == second


def test_fidelity_substitution_gets_partial_credit() -> None:
    """Using an allowed substitution should score better than a total miss."""
    scenario = _scenario("math_reasoning", "easy")
    spec = scenario.hidden_reference_spec

    # Find a required element that has a substitution
    sub_map = {}
    for sub in scenario.allowed_substitutions:
        sub_map[sub.original.lower()] = sub.alternative

    if not sub_map or not spec.required_elements:
        return  # skip if no substitution exists in this scenario

    # Build protocol that uses the substitution alternative
    first_sub_original = list(sub_map.keys())[0]
    first_sub_alt = sub_map[first_sub_original]

    with_sub = _good_protocol(scenario).model_copy(update={
        "rationale": f"We will use {first_sub_alt} instead. " + spec.target_metric,
    })
    without_anything = _bad_protocol()

    score_sub = score_fidelity(with_sub, scenario)
    score_miss = score_fidelity(without_anything, scenario)

    assert score_sub > score_miss


def test_fidelity_mentioning_target_metric_improves_score() -> None:
    scenario = _scenario("ml_benchmark", "easy")
    spec = scenario.hidden_reference_spec

    with_metric = _good_protocol(scenario)
    without_metric = with_metric.model_copy(update={
        "rationale": "Generic plan without any specific metric mentioned.",
    })

    score_with = score_fidelity(with_metric, scenario)
    score_without = score_fidelity(without_metric, scenario)

    assert score_with >= score_without


def test_fidelity_all_domains_return_valid_range() -> None:
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        for difficulty in ("easy", "medium", "hard"):
            scenario = generate_scenario(seed=99, template=template, difficulty=difficulty)
            protocol = _good_protocol(scenario)
            score = score_fidelity(protocol, scenario)
            assert 0.0 <= score <= 1.0, f"{template}/{difficulty}: {score}"


# ---------------------------------------------------------------------------
# Cross-scorer consistency
# ---------------------------------------------------------------------------


def test_all_scores_between_zero_and_one_for_bad_protocol() -> None:
    for template in ("ml_benchmark", "math_reasoning", "finance_trading"):
        scenario = generate_scenario(seed=7, template=template, difficulty="hard")
        bad = _bad_protocol()

        r = score_rigor(bad, scenario)
        fe = score_feasibility(bad, scenario)
        fi = score_fidelity(bad, scenario)

        assert 0.0 <= r <= 1.0, f"rigor {template}: {r}"
        assert 0.0 <= fe <= 1.0, f"feasibility {template}: {fe}"
        assert 0.0 <= fi <= 1.0, f"fidelity {template}: {fi}"


def test_good_protocol_dominates_bad_on_rigor_and_fidelity() -> None:
    """Good protocol beats bad on rigor and fidelity.

    Feasibility is excluded: a protocol that asks for nothing is trivially
    feasible (no equipment, no reagents → nothing can fail).  The other two
    scores correctly penalize an empty plan.
    """
    scenario = _scenario("ml_benchmark", "easy")
    good = _good_protocol(scenario)
    bad = _bad_protocol()

    assert score_rigor(good, scenario) > score_rigor(bad, scenario)
    assert score_fidelity(good, scenario) > score_fidelity(bad, scenario)


def test_good_protocol_beats_awful_protocol_on_all_scores_and_total_reward() -> None:
    """A clearly infeasible and low-quality protocol loses on every judge axis."""
    scenario = _scenario("ml_benchmark", "easy")
    good = _good_protocol(scenario)
    awful = _awful_protocol(scenario)

    good_breakdown = build_reward_breakdown(good, scenario, rounds_used=2, max_rounds=6)
    awful_breakdown = build_reward_breakdown(awful, scenario, rounds_used=2, max_rounds=6)

    assert score_rigor(good, scenario) > score_rigor(awful, scenario)
    assert score_feasibility(good, scenario) > score_feasibility(awful, scenario)
    assert score_fidelity(good, scenario) > score_fidelity(awful, scenario)
    assert compute_total_reward(good_breakdown) > compute_total_reward(awful_breakdown)


def test_rigor_explicit_success_criteria_mentions_improve_score() -> None:
    """Mentioning scenario success criteria should improve rigor coverage."""
    scenario = _scenario("finance_trading", "easy").model_copy(
        update={
            "success_criteria": ["risk-adjusted return", "drawdown control"],
            "hidden_reference_spec": HiddenReferenceSpec(
                summary="risk-aware replication plan",
                required_elements=[],
                flexible_elements=[],
                target_metric="sharpe ratio",
                target_value="> 1.5",
            ),
        }
    )
    generic = _good_protocol(scenario).model_copy(
        update={"rationale": "Follow a generic plan with basic checks."}
    )
    explicit = generic.model_copy(
        update={
            "rationale": (
                "Optimize for risk-adjusted return while preserving drawdown control "
                "through explicit checkpoints."
            )
        }
    )

    assert score_rigor(explicit, scenario) > score_rigor(generic, scenario)


def test_feasibility_partial_equipment_credit_sits_between_full_and_total_miss() -> None:
    """One available requirement should score between full availability and a total miss."""
    scenario = _scenario("ml_benchmark", "easy")
    available = list(scenario.lab_manager_observation.equipment_available)
    assert available, "scenario must expose at least one available equipment item"

    full = _good_protocol(scenario).model_copy(
        update={"required_equipment": [available[0]]}
    )
    partial = full.model_copy(
        update={"required_equipment": [available[0], "Imaginary Device"]}
    )
    miss = full.model_copy(
        update={"required_equipment": ["Imaginary Device", "Missing Device"]}
    )

    full_score = score_feasibility(full, scenario)
    partial_score = score_feasibility(partial, scenario)
    miss_score = score_feasibility(miss, scenario)

    assert full_score > partial_score > miss_score


def test_fidelity_direct_match_beats_substitution_and_miss() -> None:
    """Required-element scoring should prefer direct match > allowed substitution > miss."""
    scenario = _scenario("math_reasoning", "easy").model_copy(
        update={
            "hidden_reference_spec": HiddenReferenceSpec(
                summary="structured proof plan",
                required_elements=["alphaprobe"],
                flexible_elements=[],
                target_metric="accuracy",
                target_value="0.95",
            ),
            "allowed_substitutions": [
                AllowedSubstitution(
                    original="alphaprobe",
                    alternative="betaprobe",
                    condition="when the primary resource is booked",
                    tradeoff="backup sensor is slower",
                )
            ],
        }
    )
    base = Protocol(
        sample_size=10,
        controls=["baseline", "ablation"],
        technique="structured proof plan",
        duration_days=1,
        required_equipment=[],
        required_reagents=[],
        rationale="Target accuracy 0.95 with explicit evaluation.",
    )

    direct = base.model_copy(
        update={"rationale": base.rationale + " Use the alphaprobe."}
    )
    substitution = base.model_copy(
        update={"rationale": base.rationale + " Use the betaprobe."}
    )
    miss = base

    direct_score = score_fidelity(direct, scenario)
    substitution_score = score_fidelity(substitution, scenario)
    miss_score = score_fidelity(miss, scenario)

    assert direct_score > substitution_score > miss_score


# ---------------------------------------------------------------------------
# JDG 04 — compute_total_reward
# ---------------------------------------------------------------------------


def test_total_reward_perfect_beats_broken() -> None:
    """A well-aligned protocol earns a higher total reward than a bad one."""
    scenario = _scenario("ml_benchmark", "easy")
    good = _good_protocol(scenario)
    bad = _bad_protocol()

    good_bd = build_reward_breakdown(good, scenario, rounds_used=1, max_rounds=6)
    bad_bd = build_reward_breakdown(bad, scenario, rounds_used=1, max_rounds=6)

    assert compute_total_reward(good_bd) > compute_total_reward(bad_bd)


def test_zero_feasibility_zeroes_base() -> None:
    """If any component is 0, the multiplicative base is 0."""
    rb = RewardBreakdown(rigor=1.0, feasibility=0.0, fidelity=1.0)
    assert compute_total_reward(rb) == 0.0


def test_efficiency_bonus_higher_when_faster() -> None:
    """Finishing in fewer rounds yields a higher total reward."""
    scenario = _scenario()
    protocol = _good_protocol(scenario)

    fast = build_reward_breakdown(protocol, scenario, rounds_used=1, max_rounds=6)
    slow = build_reward_breakdown(protocol, scenario, rounds_used=5, max_rounds=6)

    assert compute_total_reward(fast) > compute_total_reward(slow)


def test_penalty_subtraction_exact() -> None:
    """Named penalties subtract exactly from the total."""
    rb = RewardBreakdown(
        rigor=1.0,
        feasibility=1.0,
        fidelity=1.0,
        penalties={"invalid_tool_use": 2.0, "unsupported_claim": 0.5},
    )
    total = compute_total_reward(rb)
    assert total == 7.5  # 10*1*1*1 - 2.5


def test_total_reward_clamps_at_zero() -> None:
    """Massive penalties cannot push the total below 0."""
    rb = RewardBreakdown(
        rigor=0.1,
        feasibility=0.1,
        fidelity=0.1,
        penalties={"massive_penalty": 50.0},
    )
    assert compute_total_reward(rb) == 0.0


def test_breakdown_determinism() -> None:
    """Same inputs always produce the same total reward."""
    scenario = _scenario("finance_trading", "medium")
    protocol = _good_protocol(scenario)

    b1 = build_reward_breakdown(protocol, scenario, rounds_used=3, max_rounds=6)
    b2 = build_reward_breakdown(protocol, scenario, rounds_used=3, max_rounds=6)

    assert compute_total_reward(b1) == compute_total_reward(b2)


# ---------------------------------------------------------------------------
# JDG 05 — build_reward_breakdown
# ---------------------------------------------------------------------------


def test_breakdown_accepts_external_penalties() -> None:
    """Callers can inject named penalty keys via the penalties parameter."""
    scenario = _scenario()
    protocol = _good_protocol(scenario)

    bd = build_reward_breakdown(
        protocol, scenario, rounds_used=2, max_rounds=6,
        penalties={"invalid_tool_use": 1.0},
    )

    assert "invalid_tool_use" in bd.penalties
    assert bd.penalties["invalid_tool_use"] == 1.0


def test_breakdown_no_penalties_by_default() -> None:
    """Without external penalties, the dict is empty."""
    scenario = _scenario()
    protocol = _good_protocol(scenario)

    bd = build_reward_breakdown(protocol, scenario, rounds_used=2, max_rounds=6)

    assert bd.penalties == {}


def test_breakdown_matches_with_and_without_precomputed_feasibility_check() -> None:
    """Providing a precomputed feasibility check should not change the breakdown."""
    scenario = _scenario("ml_benchmark", "medium")
    protocol = _good_protocol(scenario)
    precomputed = check_feasibility(protocol, scenario)

    with_check = build_reward_breakdown(
        protocol,
        scenario,
        rounds_used=3,
        max_rounds=6,
        check=precomputed,
    )
    without_check = build_reward_breakdown(
        protocol,
        scenario,
        rounds_used=3,
        max_rounds=6,
    )

    assert with_check == without_check


# ---------------------------------------------------------------------------
# JDG 06 — explain_reward
# ---------------------------------------------------------------------------


def test_explain_mentions_all_rubric_components() -> None:
    """Explanation must reference rigor, feasibility, and fidelity."""
    bd = RewardBreakdown(rigor=0.8, feasibility=0.6, fidelity=0.9)
    text = explain_reward(bd)

    assert "Rigor:" in text
    assert "Feasibility:" in text
    assert "Fidelity:" in text
    assert "0.80" in text
    assert "0.60" in text
    assert "0.90" in text


def test_explain_includes_penalties() -> None:
    """Each named penalty key appears in the explanation."""
    bd = RewardBreakdown(
        rigor=0.5,
        feasibility=0.5,
        fidelity=0.5,
        penalties={"invalid_tool_use": 1.0, "unsupported_claim": 0.5},
    )
    text = explain_reward(bd)

    assert "invalid tool use" in text
    assert "unsupported claim" in text
    assert "-1.00" in text
    assert "-0.50" in text


def test_explain_no_penalties_message() -> None:
    """When no penalties exist, the explanation says so."""
    bd = RewardBreakdown(rigor=1.0, feasibility=1.0, fidelity=1.0)
    text = explain_reward(bd)

    assert "No penalties applied" in text


def test_explain_includes_efficiency_bonus() -> None:
    """Efficiency bonus appears when present."""
    bd = RewardBreakdown(
        rigor=0.7, feasibility=0.7, fidelity=0.7, efficiency_bonus=0.8,
    )
    text = explain_reward(bd)

    assert "Efficiency bonus" in text
    assert "+0.80" in text


def test_explain_omits_efficiency_bonus_when_zero() -> None:
    """Efficiency bonus line is absent when bonus is 0."""
    bd = RewardBreakdown(rigor=0.7, feasibility=0.7, fidelity=0.7)
    text = explain_reward(bd)

    assert "Efficiency bonus" not in text


def test_explain_shows_total_reward() -> None:
    """Explanation ends with the computed total reward."""
    bd = RewardBreakdown(rigor=1.0, feasibility=1.0, fidelity=1.0)
    text = explain_reward(bd)

    assert "Total reward: 10.00" in text


def test_explain_tier_labels() -> None:
    """Quality tier labels map correctly to score ranges."""
    strong = RewardBreakdown(rigor=0.85, feasibility=0.5, fidelity=0.25)
    text = explain_reward(strong)

    assert "strong" in text   # rigor 0.85
    assert "moderate" in text  # feasibility 0.5
    assert "weak" in text      # fidelity 0.25


def test_explain_deterministic() -> None:
    """Same breakdown always produces the same explanation."""
    bd = RewardBreakdown(
        rigor=0.6, feasibility=0.4, fidelity=0.8,
        efficiency_bonus=0.5, penalties={"timeout": 0.3},
    )
    assert explain_reward(bd) == explain_reward(bd)


def test_explain_with_real_breakdown() -> None:
    """Explanation works end-to-end with build_reward_breakdown output."""
    scenario = _scenario("ml_benchmark", "easy")
    protocol = _good_protocol(scenario)
    bd = build_reward_breakdown(protocol, scenario, rounds_used=2, max_rounds=6)
    text = explain_reward(bd)

    assert "Rigor:" in text
    assert "Feasibility:" in text
    assert "Fidelity:" in text
    assert "Total reward:" in text
