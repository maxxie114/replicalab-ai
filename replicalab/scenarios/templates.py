"""Normalized scenario generation and mapping helpers."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable, Literal

from pydantic import BaseModel, ConfigDict

from replicalab.config import MAX_BUDGET, MAX_ROUNDS
from replicalab.models import LabManagerObservation, ScientistObservation
from replicalab.oracle_models import Scenario as OracleScenario
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


class ResourceBooking(BaseModel):
    """A time-slot booking for a schedulable resource."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    resource_key: str
    resource_label: str
    slot_label: str
    start_offset_hours: float
    duration_hours: float
    status: Literal["available", "booked", "maintenance"]
    details: str


class SchedulingWindow(BaseModel):
    """A time window constraining when a resource or activity is accessible."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    key: str
    label: str
    start_offset_hours: float
    end_offset_hours: float
    hard: bool = True
    details: str


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
    resource_bookings: list[ResourceBooking] = []
    scheduling_windows: list[SchedulingWindow] = []


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
    pack = _build_pack(seed=seed, template=template, draft=scaled, rng=rng)
    validate_scenario_consistency(pack)
    return pack


def validate_scenario_consistency(pack: NormalizedScenarioPack) -> None:
    """Verify internal consistency of a generated scenario pack.

    Checks budget, equipment/reagent list consistency, time limits,
    and hidden reference element validity.
    """
    lab = pack.lab_manager_observation

    if lab.budget_remaining < 0:
        raise ValueError(
            f"Scenario {pack.scenario_id}: negative budget_remaining ({lab.budget_remaining})"
        )
    if lab.budget_remaining > lab.budget_total:
        raise ValueError(
            f"Scenario {pack.scenario_id}: budget_remaining ({lab.budget_remaining}) "
            f"exceeds budget_total ({lab.budget_total})"
        )
    if lab.time_limit_days < 1:
        raise ValueError(
            f"Scenario {pack.scenario_id}: time_limit_days must be >= 1"
        )

    equip_overlap = set(lab.equipment_available) & set(lab.equipment_booked)
    if equip_overlap:
        raise ValueError(
            f"Scenario {pack.scenario_id}: equipment in both available and booked: {equip_overlap}"
        )

    reagent_overlap = set(lab.reagents_in_stock) & set(lab.reagents_out_of_stock)
    if reagent_overlap:
        raise ValueError(
            f"Scenario {pack.scenario_id}: reagents in both in_stock and out_of_stock: {reagent_overlap}"
        )

    for elem in pack.hidden_reference_spec.required_elements:
        if not elem.strip():
            raise ValueError(
                f"Scenario {pack.scenario_id}: empty required_element in hidden_reference_spec"
            )


def oracle_scenario_to_normalized_pack(
    *,
    seed: int,
    template: TemplateName,
    oracle_scenario: OracleScenario,
    max_rounds: int = MAX_ROUNDS,
) -> NormalizedScenarioPack:
    """Adapt an Oracle-generated Scenario into the canonical normalized pack."""

    difficulty = oracle_scenario.difficulty.value
    budget_total = oracle_scenario.lab_constraints.budget_total
    budget_remaining = oracle_scenario.lab_constraints.budget_remaining
    time_limit_days = oracle_scenario.lab_constraints.max_duration_days
    staff_count = len(oracle_scenario.lab_constraints.staff)

    constraints: list[ScenarioConstraint] = [
        ScenarioConstraint(
            key="budget_total",
            label="Budget total",
            quantity=budget_total,
            unit="USD",
            comparator="<=",
            hard=True,
            details=f"Total available budget is {budget_total:.2f} USD.",
        ),
        ScenarioConstraint(
            key="budget_remaining",
            label="Budget remaining",
            quantity=budget_remaining,
            unit="USD",
            comparator="<=",
            hard=True,
            details=f"Remaining budget at episode start is {budget_remaining:.2f} USD.",
        ),
        ScenarioConstraint(
            key="max_duration_days",
            label="Maximum duration",
            quantity=time_limit_days,
            unit="days",
            comparator="<=",
            hard=True,
            details=f"The plan must finish within {time_limit_days} days.",
        ),
        ScenarioConstraint(
            key="staff_count",
            label="Available staff",
            quantity=staff_count,
            unit="people",
            comparator=">=",
            hard=True,
            details=f"{staff_count} staff member(s) are available for this scenario.",
        ),
    ]
    constraints.extend(
        ScenarioConstraint(
            key=f"safety_rule_{index + 1}",
            label=f"Safety rule {index + 1}",
            comparator="=",
            hard=True,
            details=rule,
        )
        for index, rule in enumerate(oracle_scenario.lab_constraints.safety_rules)
    )

    resources: list[ScenarioResource] = []
    for equipment in oracle_scenario.lab_constraints.equipment:
        category = (
            "compute"
            if any(token in equipment.name.lower() for token in ("gpu", "cluster", "accelerator"))
            else "tool"
        )
        resources.append(
            ScenarioResource(
                key=_slug(equipment.name),
                label=equipment.name,
                quantity=1,
                unit="unit",
                available=equipment.available and equipment.condition != "shared_booking",
                category=category,
                details=(
                    f"Condition: {equipment.condition}. "
                    f"Booking conflicts: {', '.join(equipment.booking_conflicts) or 'none'}."
                ),
            )
        )

    for reagent in oracle_scenario.lab_constraints.reagents:
        resources.append(
            ScenarioResource(
                key=_slug(reagent.name),
                label=reagent.name,
                quantity=reagent.quantity_available,
                unit=reagent.unit,
                available=reagent.in_stock,
                category="reference",
                details=(
                    f"Lead time: {reagent.lead_time_days} day(s). "
                    f"Unit cost: {reagent.cost:.2f}."
                ),
            )
        )

    for member in oracle_scenario.lab_constraints.staff:
        resources.append(
            ScenarioResource(
                key=_slug(member.name),
                label=member.name,
                quantity=len(member.available_days),
                unit="days",
                available=bool(member.available_days),
                category="personnel",
                details=f"Role: {member.role}. Skills: {', '.join(member.skills) or 'generalist'}.",
            )
        )

    substitutions = [
        AllowedSubstitution(
            original=item.original,
            alternative=item.substitute,
            condition=item.validity,
            tradeoff=item.caveats or item.validity,
        )
        for item in oracle_scenario.lab_constraints.valid_substitutions
    ]

    required_elements = (
        list(oracle_scenario.minimum_viable_spec.must_keep_controls)
        + list(oracle_scenario.minimum_viable_spec.critical_equipment)
        + list(oracle_scenario.minimum_viable_spec.critical_reagents)
    )
    flexible_elements = (
        list(oracle_scenario.minimum_viable_spec.acceptable_techniques)
        + list(oracle_scenario.minimum_viable_spec.flexible_equipment)
        + list(oracle_scenario.minimum_viable_spec.flexible_reagents)
    )

    hidden_reference = HiddenReferenceSpec(
        summary=oracle_scenario.paper.method_summary,
        required_elements=required_elements,
        flexible_elements=flexible_elements,
        target_metric=oracle_scenario.paper.statistical_test,
        target_value=f"power>={oracle_scenario.minimum_viable_spec.power_threshold:.2f}",
    )

    success_criteria = [
        oracle_scenario.paper.claim,
        f"Preserve controls: {', '.join(oracle_scenario.paper.required_controls) or 'none listed'}",
        f"Use an acceptable technique from the viable spec where possible.",
        f"Stay within {budget_total:.2f} USD and {time_limit_days} days.",
    ]

    equipment_available = [
        equipment.name
        for equipment in oracle_scenario.lab_constraints.equipment
        if equipment.available and equipment.condition != "shared_booking"
    ]
    equipment_booked = [
        equipment.name
        for equipment in oracle_scenario.lab_constraints.equipment
        if not equipment.available or equipment.condition == "shared_booking"
    ]
    reagents_in_stock = [
        reagent.name for reagent in oracle_scenario.lab_constraints.reagents if reagent.in_stock
    ]
    reagents_out_of_stock = [
        reagent.name for reagent in oracle_scenario.lab_constraints.reagents if not reagent.in_stock
    ]

    scientist_observation = ScientistObservation(
        paper_title=oracle_scenario.paper.title,
        paper_hypothesis=oracle_scenario.paper.claim,
        paper_method=oracle_scenario.paper.method_summary,
        paper_key_finding=oracle_scenario.narrative_hook,
        experiment_goal=oracle_scenario.paper.claim,
        conversation_history=[],
        current_protocol=None,
        round_number=0,
        max_rounds=max_rounds,
    )

    lab_manager_observation = LabManagerObservation(
        budget_total=budget_total,
        budget_remaining=budget_remaining,
        equipment_available=equipment_available,
        equipment_booked=equipment_booked,
        reagents_in_stock=reagents_in_stock,
        reagents_out_of_stock=reagents_out_of_stock,
        staff_count=staff_count,
        time_limit_days=time_limit_days,
        safety_restrictions=list(oracle_scenario.lab_constraints.safety_rules),
        conversation_history=[],
        current_protocol=None,
        round_number=0,
        max_rounds=max_rounds,
    )

    bookings = _oracle_bookings(oracle_scenario)
    windows = _oracle_windows(oracle_scenario)

    return NormalizedScenarioPack(
        scenario_id=f"{template}-{difficulty}-{seed}-oracle",
        template=template,
        domain_id=oracle_scenario.paper.domain,
        difficulty=difficulty,
        seed=seed,
        task_summary=oracle_scenario.paper.claim,
        success_criteria=success_criteria,
        constraints=constraints,
        resources=resources,
        allowed_substitutions=substitutions,
        hidden_reference_spec=hidden_reference,
        scientist_observation=scientist_observation,
        lab_manager_observation=lab_manager_observation,
        resource_bookings=bookings,
        scheduling_windows=windows,
    )


def _build_pack(seed: int, template: TemplateName, draft: dict[str, Any], rng: Any) -> NormalizedScenarioPack:
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

    bookings = _generate_bookings(resources, template, draft["difficulty"], rng)
    windows = _generate_scheduling_windows(
        template, draft["difficulty"], time_limit_days, rng,
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
        resource_bookings=bookings,
        scheduling_windows=windows,
    )


def _slug(value: str) -> str:
    return "_".join(value.lower().replace("/", " ").replace("-", " ").split())


def _day_to_offset(day: str) -> int:
    mapping = {
        "monday": 0,
        "tuesday": 24,
        "wednesday": 48,
        "thursday": 72,
        "friday": 96,
        "saturday": 120,
        "sunday": 144,
    }
    return mapping.get(day.strip().lower(), 0)


def _oracle_bookings(oracle_scenario: OracleScenario) -> list[ResourceBooking]:
    bookings: list[ResourceBooking] = []
    for equipment in oracle_scenario.lab_constraints.equipment:
        if equipment.booking_conflicts:
            for day in equipment.booking_conflicts:
                bookings.append(
                    ResourceBooking(
                        resource_key=_slug(equipment.name),
                        resource_label=equipment.name,
                        slot_label=day,
                        start_offset_hours=_day_to_offset(day),
                        duration_hours=8.0,
                        status="booked" if equipment.available else "maintenance",
                        details=f"{equipment.name} is constrained on {day}.",
                    )
                )
        else:
            bookings.append(
                ResourceBooking(
                    resource_key=_slug(equipment.name),
                    resource_label=equipment.name,
                    slot_label="default",
                    start_offset_hours=0.0,
                    duration_hours=8.0,
                    status="available" if equipment.available else "maintenance",
                    details=f"{equipment.name} is available under normal scheduling.",
                )
            )
    return bookings


def _oracle_windows(oracle_scenario: OracleScenario) -> list[SchedulingWindow]:
    windows: list[SchedulingWindow] = [
        SchedulingWindow(
            key="max_duration_window",
            label="Maximum project duration",
            start_offset_hours=0.0,
            end_offset_hours=float(oracle_scenario.lab_constraints.max_duration_days * 24),
            hard=True,
            details=(
                f"All work must complete within "
                f"{oracle_scenario.lab_constraints.max_duration_days} days."
            ),
        )
    ]

    seen_days: set[str] = set()
    for member in oracle_scenario.lab_constraints.staff:
        for day in member.available_days:
            normalized = day.strip().lower()
            if normalized in seen_days:
                continue
            seen_days.add(normalized)
            start = float(_day_to_offset(day))
            windows.append(
                SchedulingWindow(
                    key=f"staff_{normalized}",
                    label=f"Staff availability {day}",
                    start_offset_hours=start,
                    end_offset_hours=start + 8.0,
                    hard=False,
                    details=f"At least one staff member is available on {day}.",
                )
            )
    return windows


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


# ---------------------------------------------------------------------------
# Booking / scheduling generation (SCN 13)
# ---------------------------------------------------------------------------

_BOOKABLE_CATEGORIES: dict[TemplateName, set[str]] = {
    "ml_benchmark": {"compute", "tool"},
    "math_reasoning": {"tool", "personnel"},
    "finance_trading": {"data", "personnel"},
}

_WINDOW_CONFIGS: dict[TemplateName, list[dict[str, str]]] = {
    "ml_benchmark": [
        {"key": "gpu_cluster_hours", "label": "GPU cluster availability window"},
        {"key": "maintenance_window", "label": "Scheduled maintenance window"},
    ],
    "math_reasoning": [
        {"key": "reviewer_hours", "label": "Reviewer availability window"},
        {"key": "room_access", "label": "Workspace access hours"},
    ],
    "finance_trading": [
        {"key": "data_feed_window", "label": "Market data feed window"},
        {"key": "analyst_hours", "label": "Analyst availability window"},
    ],
}


def _generate_bookings(
    resources: list[ScenarioResource],
    template: TemplateName,
    difficulty: Difficulty,
    rng: Any,
) -> list[ResourceBooking]:
    """Create deterministic time-slot bookings from existing resources."""
    bookable_cats = _BOOKABLE_CATEGORIES[template]
    bookable = [r for r in resources if r.category in bookable_cats]

    bookings: list[ResourceBooking] = []
    for resource in bookable:
        num_slots = rng.randint(2, 4)
        offset = 0.0
        for slot_idx in range(num_slots):
            duration = rng.choice([2.0, 4.0, 8.0])

            if difficulty == "easy":
                status: Literal["available", "booked", "maintenance"] = "available"
            elif difficulty == "medium":
                status = rng.choice(["available", "available", "booked"])
            else:
                status = rng.choice(["available", "booked", "booked", "maintenance"])

            if status == "available":
                detail = f"Open for use from offset {offset}h for {duration}h."
            elif status == "booked":
                detail = f"Reserved by another team from offset {offset}h for {duration}h."
            else:
                detail = f"Under maintenance from offset {offset}h for {duration}h."

            bookings.append(ResourceBooking(
                resource_key=resource.key,
                resource_label=resource.label,
                slot_label=f"{resource.label} — slot {slot_idx + 1}",
                start_offset_hours=offset,
                duration_hours=duration,
                status=status,
                details=detail,
            ))

            gap = round(rng.uniform(1.0, 4.0), 1)
            offset = round(offset + duration + gap, 1)

    return bookings


def _generate_scheduling_windows(
    template: TemplateName,
    difficulty: Difficulty,
    time_limit_days: int,
    rng: Any,
) -> list[SchedulingWindow]:
    """Create deterministic scheduling windows scaled by difficulty."""
    configs = _WINDOW_CONFIGS[template]
    total_hours = float(time_limit_days * 24)

    windows: list[SchedulingWindow] = []
    for cfg in configs:
        if difficulty == "easy":
            start = 0.0
            end = total_hours
            hard = False
        elif difficulty == "medium":
            start = round(rng.uniform(0, total_hours * 0.1), 1)
            end = round(total_hours - rng.uniform(0, total_hours * 0.2), 1)
            hard = rng.choice([True, False])
        else:
            start = round(rng.uniform(total_hours * 0.1, total_hours * 0.25), 1)
            end = round(total_hours - rng.uniform(total_hours * 0.15, total_hours * 0.3), 1)
            hard = True

        end = max(start + 1.0, end)

        constraint_label = "hard" if hard else "soft"
        windows.append(SchedulingWindow(
            key=cfg["key"],
            label=cfg["label"],
            start_offset_hours=start,
            end_offset_hours=end,
            hard=hard,
            details=f"{cfg['label']}: offset {start}h to {end}h ({constraint_label} constraint).",
        ))

    return windows
