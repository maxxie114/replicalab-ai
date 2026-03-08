"""Prompt asset tests for AGT 10."""

from __future__ import annotations

from replicalab.prompts import (
    load_prompt_asset,
    load_prompt_template,
    render_judge_prompt,
    render_lab_manager_prompt,
    render_scientist_prompt,
)
from replicalab.scenarios import generate_scenario


def _scenario(template: str = "ml_benchmark"):
    return generate_scenario(seed=42, template=template, difficulty="medium")


def test_load_prompt_template_reads_all_role_files() -> None:
    for role in ("scientist", "lab_manager", "judge"):
        template = load_prompt_template(role)
        assert len(template) > 100
        assert "ReplicaLab" in template


def test_load_oracle_prompt_assets_reads_all_oracle_files() -> None:
    for name in (
        "oracle_world_architect",
        "oracle_adjudicator",
        "oracle_event_injector",
        "oracle_post_mortem",
        "oracle_lab_manager",
    ):
        template = load_prompt_asset(name)
        assert len(template) > 100


def test_render_scientist_prompt_injects_task_and_bounded_tools() -> None:
    prompt = render_scientist_prompt(_scenario("ml_benchmark"))

    assert "You are the Scientist agent" in prompt
    assert "search_evidence" in prompt
    assert "run_code_check" in prompt
    assert "inspect_image" in prompt
    assert "Allowed action_type values:" in prompt
    assert "Task:" in prompt
    assert "Domain:" in prompt


def test_render_lab_manager_prompt_injects_grounding_rules() -> None:
    prompt = render_lab_manager_prompt(_scenario("finance_trading"))

    assert "You are the Lab Manager agent" in prompt
    assert "deterministic checker outputs" in prompt
    assert "suggest_alternative" in prompt
    assert "No unrestricted browsing" in prompt
    assert "Available resources:" in prompt


def test_render_judge_prompt_injects_rubric_rules() -> None:
    prompt = render_judge_prompt(_scenario("math_reasoning"))

    assert "You are the Judge agent" in prompt
    assert "Explain rigor, feasibility, and fidelity" in prompt
    assert "Never rescore" in prompt
    assert "top failure reasons" in prompt


def test_rendered_prompts_leave_no_unformatted_placeholders() -> None:
    scenario = _scenario("ml_benchmark")
    prompts = (
        render_scientist_prompt(scenario),
        render_lab_manager_prompt(scenario),
        render_judge_prompt(scenario),
    )

    for prompt in prompts:
        assert "{domain_id}" not in prompt
        assert "{task_summary}" not in prompt
        assert "{constraints}" not in prompt


def test_rendered_prompts_are_domain_neutral_but_scenario_specific() -> None:
    ml_scenario = _scenario("ml_benchmark")
    finance_scenario = _scenario("finance_trading")
    ml_prompt = render_scientist_prompt(ml_scenario)
    finance_prompt = render_scientist_prompt(finance_scenario)

    assert ml_prompt != finance_prompt
    assert ml_scenario.task_summary in ml_prompt
    assert finance_scenario.task_summary in finance_prompt
