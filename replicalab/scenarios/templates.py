"""Normalized scenario generation and mapping helpers."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable, Literal

from pydantic import BaseModel, ConfigDict

from replicalab.config import MAX_BUDGET, MAX_ROUNDS
from replicalab.models import LabManagerObservation, ScientistObservation
from replicalab.scenarios.finance_trading import build_finance_trading_template
from replicalab.scenarios.math_reasoning import build_math_reasoning_template
from replicalab.scenarios.ml_benchmark import build_ml_benchmark_template
from replicalab.utils.seed import seed_rng

Difficulty = Literal["easy", "medium", "hard"]
TemplateName = Literal["math_reasoning", "ml_benchmark", "finance_trading"]

GOLDEN_SCENARIO_SPECS_PATH = (
    Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "golden_scenarios.json"
)


class ScenarioConstraint(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    key: str
    label: str
    quantity: float | int | None = None
    unit: str | None = None
    comparator: Literal["<=", ">=", "="] = "="
    hard: bool = True
    details: str


class ScenarioResource(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    key: str
    label: str
    quantity: float | int | None = None
    unit: str | None = None
    available: bool = True
    category: str
    details: str


class AllowedSubstitution(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    original: str
    alternative: str
    condition: str
    tradeoff: str


class HiddenReferenceSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    summary: str
    required_elements: list[str]
    flexible_elements: list[str]
    target_metric: str
    target_value: str


class NormalizedScenarioPack(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    scenario_id: str
    template: TemplateName
    domain_id: str
    difficulty: Difficulty
    seed: int
    task_summary: str
    success_criteria: list[str]
    constraints: list[ScenarioConstraint]
    resources: list[ScenarioResource]
    allowed_substitutions: list[AllowedSubstitution]
    hidden_reference_spec: HiddenReferenceSpec
    scientist_observation: ScientistObservation
    lab_manager_observation: LabManagerObservation


TemplateBuilder = Callable[[Any], dict[str, Any]]

_TEMPLATE_BUILDERS: dict[TemplateName, TemplateBuilder] = {
    "math_reasoning": build_math_reasoning_template,
    "ml_benchmark": build_ml_benchmark_template,
    "finance_trading": build_finance_trading_template,
}


def available_scenario_families() -> list[dict[str, Any]]:
    return [
        {"family": name, "difficulties": ["easy", "medium", "hard"]}
        for name in _TEMPLATE_BUILDERS
    ]


def load_template(template: TemplateName) -> TemplateBuilder:
    try:
        return _TEMPLATE_BUILDERS[template]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario template: {template}") from exc


def apply_difficulty(
    draft: dict[str, Any],
    difficulty: Difficulty,
    rng: Any,
) -> dict[str, Any]:
    scaled = copy.deepcopy(draft)
    scaled["difficulty"] = difficulty

    if difficulty == "easy":
        scaled["budget_total"] = round(float(draft["budget_total"]) * 1.15, 2)
        return scaled

    if difficulty == "medium":
        scaled["budget_total"] = round(float(draft["budget_total"]) * 0.95, 2)
        scaled["time_limit_days"] = max(1, int(draft["time_limit_days"]) - 1)
        _tighten_one_resource(scaled["resources"], rng)
        _append_conflict_constraint(
            scaled["constraints"],
            "One resource is partially constrained, so the plan must justify a fallback path.",
        )
        return scaled

    scaled["budget_total"] = round(float(draft["budget_total"]) * 0.8, 2)
    scaled["time_limit_days"] = max(1, int(draft["time_limit_days"]) - 1)
    scaled["staff_count"] = max(1, int(draft["staff_count"]) - 1)
    _tighten_one_resource(scaled["resources"], rng)
    _tighten_one_resource(scaled["resources"], rng)
    _append_conflict_constraint(
        scaled["constraints"],
        "At least one primary resource is unavailable, so the plan must use an allowed substitution or reduced scope.",
    )
    _append_conflict_constraint(
        scaled["constraints"],
        "The final plan must remain concise because review capacity is limited under hard mode.",
    )
    return scaled


def generate_scenario(
    seed: int,
    template: TemplateName,
    difficulty: Difficulty,
) -> NormalizedScenarioPack:
    rng = seed_rng(seed, namespace=f"scenario:{template}")
    base_draft = load_template(template)(rng)
    scaled = apply_difficulty(base_draft, difficulty, rng)
    return _build_pack(seed=seed, template=template, draft=scaled)


def _build_pack(seed: int, template: TemplateName, draft: dict[str, Any]) -> NormalizedScenarioPack:
    constraints = [ScenarioConstraint.model_validate(item) for item in draft["constraints"]]
    resources = [ScenarioResource.model_validate(item) for item in draft["resources"]]
    substitutions = [
        AllowedSubstitution.model_validate(item)
        for item in draft["allowed_substitutions"]
    ]

    time_limit_days = int(draft["time_limit_days"])
    budget_total = float(draft["budget_total"])
    staff_count = int(draft["staff_count"])
    max_rounds = int(draft["max_rounds"])

    if budget_total > MAX_BUDGET:
        raise ValueError(
            f"Scenario budget {budget_total} exceeds configured MAX_BUDGET={MAX_BUDGET}."
        )
    if max_rounds > MAX_ROUNDS:
        raise ValueError(
            f"Scenario max_rounds {max_rounds} exceeds configured MAX_ROUNDS={MAX_ROUNDS}."
        )

    equipment_available, equipment_booked = _split_resources(
        resources,
        include_categories={"tool", "compute"},
    )
    reagents_in_stock, reagents_out_of_stock = _split_resources(
        resources,
        include_categories={"reference", "data", "personnel"},
    )

    safety_restrictions = [
        constraint.details
        for constraint in constraints
        if not constraint.hard or constraint.key in {"live_execution", "evaluation_policy"}
    ]
    if not safety_restrictions:
        safety_restrictions = ["No policy exceptions are allowed."]

    scientist_observation = ScientistObservation(
        paper_title=draft["paper_title"],
        paper_hypothesis=draft["paper_hypothesis"],
        paper_method=draft["paper_method"],
        paper_key_finding=draft["paper_key_finding"],
        experiment_goal=draft["task_summary"],
        conversation_history=[],
        current_protocol=None,
        round_number=0,
        max_rounds=max_rounds,
    )

    lab_manager_observation = LabManagerObservation(
        budget_total=budget_total,
        budget_remaining=budget_total,
        equipment_available=equipment_available,
        equipment_booked=equipment_booked,
        reagents_in_stock=reagents_in_stock,
        reagents_out_of_stock=reagents_out_of_stock,
        staff_count=staff_count,
        time_limit_days=time_limit_days,
        safety_restrictions=safety_restrictions,
        conversation_history=[],
        current_protocol=None,
        round_number=0,
        max_rounds=max_rounds,
    )

    hidden_reference = HiddenReferenceSpec(
        summary=draft["reference_summary"],
        required_elements=list(draft["required_elements"]),
        flexible_elements=list(draft["flexible_elements"]),
        target_metric=draft["target_metric"],
        target_value=draft["target_value"],
    )

    return NormalizedScenarioPack(
        scenario_id=f"{template}-{draft['difficulty']}-{seed}",
        template=template,
        domain_id=draft["domain_id"],
        difficulty=draft["difficulty"],
        seed=seed,
        task_summary=draft["task_summary"],
        success_criteria=list(draft["success_criteria"]),
        constraints=constraints,
        resources=resources,
        allowed_substitutions=substitutions,
        hidden_reference_spec=hidden_reference,
        scientist_observation=scientist_observation,
        lab_manager_observation=lab_manager_observation,
    )


def _split_resources(
    resources: list[ScenarioResource],
    *,
    include_categories: set[str],
) -> tuple[list[str], list[str]]:
    available: list[str] = []
    unavailable: list[str] = []

    for resource in resources:
        if resource.category not in include_categories:
            continue
        target = available if resource.available else unavailable
        target.append(resource.label)

    return available, unavailable


def _tighten_one_resource(resources: list[dict[str, Any]], rng: Any) -> None:
    available_indices = [
        index
        for index, resource in enumerate(resources)
        if resource.get("available", True)
    ]
    if not available_indices:
        return

    chosen_index = rng.choice(available_indices)
    chosen = resources[chosen_index]
    chosen["available"] = False
    chosen["details"] = (
        f"{chosen['details']} Availability is constrained under the current difficulty."
    )


def _append_conflict_constraint(
    constraints: list[dict[str, Any]],
    details: str,
) -> None:
    constraints.append(
        {
            "key": f"conflict_{len(constraints) + 1}",
            "label": "Difficulty-induced conflict",
            "quantity": None,
            "unit": None,
            "comparator": "=",
            "hard": True,
            "details": details,
        }
    )
