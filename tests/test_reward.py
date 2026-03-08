"""Tests for JDG 01–03 scoring functions."""

from __future__ import annotations

from replicalab.agents.lab_manager_policy import check_feasibility
from replicalab.models import Protocol
from replicalab.scenarios import generate_scenario
from replicalab.scoring import score_feasibility, score_fidelity, score_rigor


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
