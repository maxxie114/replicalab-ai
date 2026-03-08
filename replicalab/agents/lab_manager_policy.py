"""Deterministic Lab Manager grounding helpers.

AGT 05 introduces the first deterministic feasibility checker that reads the
normalized scenario pack and returns stable pass/fail status per dimension.
AGT 06 adds ``suggest_alternative`` which mechanically applies substitution
rules, clamps duration, and reduces sample size to produce a concrete
revised protocol with a post-fix feasibility recheck.
AGT 07 adds ``compose_lab_manager_response`` which converts those grounded
results into a typed ``LabManagerAction`` with stable flags plus a readable
explanation.  An optional explanation renderer can add richer language later
without taking over the verdict or constraint fields.
"""

from __future__ import annotations

from typing import Callable, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field

from replicalab.models import LabManagerAction, LabManagerActionType, Protocol
from replicalab.scenarios import NormalizedScenarioPack
from replicalab.utils.validation import ValidationResult, validate_protocol


class DimensionCheck(BaseModel):
    """Outcome for one feasibility dimension."""

    model_config = ConfigDict(extra="forbid")

    ok: bool = True
    reasons: list[str] = Field(default_factory=list)


class FeasibilityCheckResult(BaseModel):
    """Deterministic feasibility assessment for one protocol proposal."""

    model_config = ConfigDict(extra="forbid")

    protocol: DimensionCheck = Field(default_factory=DimensionCheck)
    budget: DimensionCheck = Field(default_factory=DimensionCheck)
    equipment: DimensionCheck = Field(default_factory=DimensionCheck)
    reagents: DimensionCheck = Field(default_factory=DimensionCheck)
    schedule: DimensionCheck = Field(default_factory=DimensionCheck)
    staff: DimensionCheck = Field(default_factory=DimensionCheck)
    policy: DimensionCheck = Field(default_factory=DimensionCheck)
    estimated_cost: float = 0.0
    required_staff: int = 1
    substitution_options: dict[str, list[str]] = Field(default_factory=dict)
    validation_result: ValidationResult

    @computed_field(return_type=bool)
    @property
    def protocol_ok(self) -> bool:
        return self.protocol.ok

    @computed_field(return_type=bool)
    @property
    def budget_ok(self) -> bool:
        return self.budget.ok

    @computed_field(return_type=bool)
    @property
    def equipment_ok(self) -> bool:
        return self.equipment.ok

    @computed_field(return_type=bool)
    @property
    def reagents_ok(self) -> bool:
        return self.reagents.ok

    @computed_field(return_type=bool)
    @property
    def schedule_ok(self) -> bool:
        return self.schedule.ok

    @computed_field(return_type=bool)
    @property
    def staff_ok(self) -> bool:
        return self.staff.ok

    @computed_field(return_type=bool)
    @property
    def feasible(self) -> bool:
        return all(
            (
                self.protocol.ok,
                self.budget.ok,
                self.equipment.ok,
                self.reagents.ok,
                self.schedule.ok,
                self.staff.ok,
                self.policy.ok,
            )
        )

    @computed_field(return_type=str)
    @property
    def summary(self) -> str:
        failing = [
            name
            for name, check in (
                ("protocol", self.protocol),
                ("budget", self.budget),
                ("equipment", self.equipment),
                ("reagents", self.reagents),
                ("schedule", self.schedule),
                ("staff", self.staff),
                ("policy", self.policy),
            )
            if not check.ok
        ]
        if not failing:
            return "Protocol is feasible across protocol, budget, equipment, reagents, schedule, staff, and policy checks."
        return f"Protocol is not feasible because these checks failed: {', '.join(failing)}."


def check_feasibility(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> FeasibilityCheckResult:
    """Return a deterministic feasibility assessment for *protocol*."""

    validation_result = validate_protocol(protocol, scenario)
    substitution_index = _build_substitution_index(scenario)

    protocol_check = _build_protocol_check(validation_result)
    budget_check, estimated_cost = _check_budget(protocol, scenario)
    equipment_check, equipment_substitutions = _check_equipment(
        protocol, scenario, substitution_index
    )
    reagent_check, reagent_substitutions = _check_reagents(
        protocol, scenario, substitution_index
    )
    schedule_check = _check_schedule(protocol, scenario)
    staff_check, required_staff = _check_staff(protocol, scenario)
    policy_check = _check_policy(protocol, scenario)

    substitution_options = {}
    substitution_options.update(equipment_substitutions)
    substitution_options.update(reagent_substitutions)

    return FeasibilityCheckResult(
        protocol=protocol_check,
        budget=budget_check,
        equipment=equipment_check,
        reagents=reagent_check,
        schedule=schedule_check,
        staff=staff_check,
        policy=policy_check,
        estimated_cost=estimated_cost,
        required_staff=required_staff,
        substitution_options=substitution_options,
        validation_result=validation_result,
    )


# ---------------------------------------------------------------------------
# AGT 06 — Alternative suggestion logic
# ---------------------------------------------------------------------------

_DIMENSION_NAMES = ("protocol", "budget", "equipment", "reagents", "schedule", "staff", "policy")


class SuggestionChange(BaseModel):
    """One deterministic modification applied to produce the revised protocol."""

    model_config = ConfigDict(extra="forbid")

    field: str
    original: str
    revised: str
    reason: str
    tradeoff: str


class AlternativeSuggestion(BaseModel):
    """Result of ``suggest_alternative``: a revised protocol with diagnostics."""

    model_config = ConfigDict(extra="forbid")

    revised_protocol: Protocol
    applied_changes: list[SuggestionChange]
    remaining_failures: list[str]
    improved: bool
    pre_check: FeasibilityCheckResult
    post_check: FeasibilityCheckResult


ExplanationRenderer = Callable[
    [LabManagerActionType, FeasibilityCheckResult, Optional[AlternativeSuggestion]],
    str,
]


def suggest_alternative(
    protocol: Protocol,
    check_result: FeasibilityCheckResult,
    scenario: NormalizedScenarioPack,
) -> Optional[AlternativeSuggestion]:
    """Build a concrete revised protocol by applying deterministic fixes.

    Returns ``None`` if the protocol is already feasible.  Otherwise applies
    fixes in a fixed order:

    1. Substitute unavailable equipment (first stable alternative)
    2. Substitute unavailable reagents/resources
    3. Clamp duration to the time limit
    4. Reduce sample size for budget and staff pressure
    5. Re-run ``check_feasibility`` on the revised protocol

    The result includes ``remaining_failures`` for dimensions that could not
    be fixed and ``improved`` indicating whether the revision is strictly
    better than the original.
    """

    if check_result.feasible:
        return None

    changes: list[SuggestionChange] = []
    tradeoff_index = _build_tradeoff_index(scenario)

    # Mutable copies of protocol fields
    equipment = list(protocol.required_equipment)
    reagents = list(protocol.required_reagents)
    duration = protocol.duration_days
    sample_size = protocol.sample_size

    # Step 1: Substitute unavailable equipment
    if not check_result.equipment.ok:
        equipment, equip_changes = _apply_substitutions(
            equipment,
            check_result.substitution_options,
            tradeoff_index,
            field_name="required_equipment",
        )
        changes.extend(equip_changes)

    # Step 2: Substitute unavailable reagents
    if not check_result.reagents.ok:
        reagents, reagent_changes = _apply_substitutions(
            reagents,
            check_result.substitution_options,
            tradeoff_index,
            field_name="required_reagents",
        )
        changes.extend(reagent_changes)

    # Step 3: Clamp duration to time limit
    time_limit = scenario.lab_manager_observation.time_limit_days
    if not check_result.schedule.ok and duration > time_limit:
        changes.append(SuggestionChange(
            field="duration_days",
            original=str(duration),
            revised=str(time_limit),
            reason=f"Duration ({duration} days) exceeds time limit ({time_limit} days).",
            tradeoff="Shorter duration may require reduced scope or parallel execution.",
        ))
        duration = time_limit

    # Step 4: Reduce sample size for budget / staff pressure
    if not check_result.budget.ok or not check_result.staff.ok:
        original_sample = sample_size
        sample_size = _reduce_sample_for_budget_and_staff(
            sample_size=sample_size,
            duration=duration,
            equipment=equipment,
            reagents=reagents,
            controls=list(protocol.controls),
            scenario=scenario,
        )
        if sample_size != original_sample:
            reasons = []
            if not check_result.budget.ok:
                reasons.append("budget overrun")
            if not check_result.staff.ok:
                reasons.append("staff overload")
            changes.append(SuggestionChange(
                field="sample_size",
                original=str(original_sample),
                revised=str(sample_size),
                reason=f"Reduced sample size to address {' and '.join(reasons)}.",
                tradeoff="Smaller sample may reduce statistical power or coverage.",
            ))

    # Build revised protocol
    revised = Protocol(
        sample_size=sample_size,
        controls=list(protocol.controls),
        technique=protocol.technique,
        duration_days=duration,
        required_equipment=equipment,
        required_reagents=reagents,
        rationale=protocol.rationale,
    )

    # Step 5: Re-run feasibility
    post_check = check_feasibility(revised, scenario)

    pre_failing = _failing_dimensions(check_result)
    post_failing = _failing_dimensions(post_check)
    improved = len(post_failing) < len(pre_failing)

    return AlternativeSuggestion(
        revised_protocol=revised,
        applied_changes=changes,
        remaining_failures=post_failing,
        improved=improved,
        pre_check=check_result,
        post_check=post_check,
    )


def compose_lab_manager_response(
    check_result: FeasibilityCheckResult,
    suggestion: Optional[AlternativeSuggestion] = None,
    *,
    explanation_renderer: Optional[ExplanationRenderer] = None,
) -> LabManagerAction:
    """Compose a grounded ``LabManagerAction`` from deterministic inputs.

    The verdict and all feasibility flags remain deterministic.  Callers may
    optionally inject an ``explanation_renderer`` for richer wording, but it
    never controls the action type or the pass/fail flags.
    """

    action_type = _select_lab_manager_action_type(check_result, suggestion)
    explanation = (
        explanation_renderer(action_type, check_result, suggestion)
        if explanation_renderer is not None
        else _build_default_explanation(action_type, check_result, suggestion)
    ).strip()
    if not explanation:
        raise ValueError("Lab Manager explanation must be non-empty")

    suggested_protocol = (
        suggestion.revised_protocol
        if action_type is LabManagerActionType.SUGGEST_ALTERNATIVE and suggestion is not None
        else None
    )

    return LabManagerAction(
        action_type=action_type,
        feasible=_lab_constraints_feasible(check_result),
        budget_ok=check_result.budget_ok,
        equipment_ok=check_result.equipment_ok,
        reagents_ok=check_result.reagents_ok,
        schedule_ok=check_result.schedule_ok,
        staff_ok=check_result.staff_ok,
        suggested_technique=(
            suggested_protocol.technique if suggested_protocol is not None else ""
        ),
        suggested_sample_size=(
            suggested_protocol.sample_size if suggested_protocol is not None else 0
        ),
        suggested_controls=(
            list(suggested_protocol.controls) if suggested_protocol is not None else []
        ),
        explanation=explanation,
    )


def _apply_substitutions(
    items: list[str],
    substitution_options: dict[str, list[str]],
    tradeoff_index: dict[str, str],
    *,
    field_name: str,
) -> tuple[list[str], list[SuggestionChange]]:
    """Replace items that have substitution options. Returns new list + changes."""
    result: list[str] = []
    changes: list[SuggestionChange] = []

    for item in items:
        alternatives = substitution_options.get(item, [])
        if alternatives:
            replacement = alternatives[0]  # first stable option
            result.append(replacement)
            changes.append(SuggestionChange(
                field=field_name,
                original=item,
                revised=replacement,
                reason=f"'{item}' is unavailable; substituting '{replacement}'.",
                tradeoff=tradeoff_index.get(_normalize(item), "No tradeoff documented."),
            ))
        else:
            result.append(item)

    return result, changes


def _reduce_sample_for_budget_and_staff(
    *,
    sample_size: int,
    duration: int,
    equipment: list[str],
    reagents: list[str],
    controls: list[str],
    scenario: NormalizedScenarioPack,
) -> int:
    """Iteratively halve sample_size until budget and staff constraints pass."""
    budget = scenario.lab_manager_observation.budget_remaining
    staff_available = scenario.lab_manager_observation.staff_count
    candidate = sample_size

    for _ in range(10):  # bounded iteration
        if candidate <= 1:
            break

        # Check cost
        test_protocol = Protocol(
            sample_size=candidate,
            controls=controls,
            technique="check",
            duration_days=duration,
            required_equipment=equipment,
            required_reagents=reagents,
            rationale="cost check",
        )
        cost = _estimate_protocol_cost(test_protocol, scenario)
        staff_needed = _estimate_staff_load(test_protocol)

        if cost <= budget and staff_needed <= staff_available:
            break

        candidate = max(1, candidate // 2)

    return candidate


def _failing_dimensions(check: FeasibilityCheckResult) -> list[str]:
    """Return dimension names that are still failing."""
    return [
        name
        for name in _DIMENSION_NAMES
        if not getattr(check, name).ok
    ]


def _build_tradeoff_index(scenario: NormalizedScenarioPack) -> dict[str, str]:
    """Map normalized original names to their tradeoff strings."""
    index: dict[str, str] = {}
    for sub in scenario.allowed_substitutions:
        index[_normalize(sub.original)] = sub.tradeoff
    return index


def _select_lab_manager_action_type(
    check_result: FeasibilityCheckResult,
    suggestion: Optional[AlternativeSuggestion],
) -> LabManagerActionType:
    """Choose the outward action mode from grounded feasibility results."""

    lab_constraints_ok = _lab_constraints_feasible(check_result)

    if lab_constraints_ok and check_result.protocol.ok and check_result.policy.ok:
        return LabManagerActionType.ACCEPT

    if suggestion is not None and suggestion.applied_changes:
        return LabManagerActionType.SUGGEST_ALTERNATIVE

    if lab_constraints_ok:
        return LabManagerActionType.REPORT_FEASIBILITY

    return LabManagerActionType.REJECT


def _build_default_explanation(
    action_type: LabManagerActionType,
    check_result: FeasibilityCheckResult,
    suggestion: Optional[AlternativeSuggestion],
) -> str:
    """Render a deterministic human-readable explanation."""

    if action_type is LabManagerActionType.ACCEPT:
        return f"Accepted. {check_result.summary}"

    if action_type is LabManagerActionType.SUGGEST_ALTERNATIVE and suggestion is not None:
        parts = [
            "Current proposal is not feasible under the present lab constraints.",
            _format_reason_block(check_result, include_protocol=False, include_policy=False),
            "Suggested revision: "
            + " ".join(_format_change_sentence(change) for change in suggestion.applied_changes),
        ]
        if suggestion.remaining_failures:
            parts.append(
                "Remaining issues after the suggested revision: "
                + ", ".join(suggestion.remaining_failures)
                + "."
            )
        return " ".join(part for part in parts if part)

    if action_type is LabManagerActionType.REPORT_FEASIBILITY:
        parts = [
            "Feasibility report: lab resources and schedule are workable, but the current proposal still needs revision.",
            _format_reason_block(check_result, include_protocol=True, include_policy=True),
        ]
        return " ".join(part for part in parts if part)

    parts = [
        "Rejected. No deterministic revision could satisfy the current lab constraints.",
        _format_reason_block(check_result, include_protocol=False, include_policy=False),
    ]
    return " ".join(part for part in parts if part)


def _lab_constraints_feasible(check_result: FeasibilityCheckResult) -> bool:
    return all(
        (
            check_result.budget_ok,
            check_result.equipment_ok,
            check_result.reagents_ok,
            check_result.schedule_ok,
            check_result.staff_ok,
        )
    )


def _format_reason_block(
    check_result: FeasibilityCheckResult,
    *,
    include_protocol: bool,
    include_policy: bool,
) -> str:
    blocks: list[str] = []
    for name, check in _iter_dimension_checks(
        check_result,
        include_protocol=include_protocol,
        include_policy=include_policy,
    ):
        if check.ok or not check.reasons:
            continue
        blocks.append(f"{name}: {' '.join(check.reasons)}")
    return " ".join(blocks)


def _format_change_sentence(change: SuggestionChange) -> str:
    return (
        f"{change.field} changed from {change.original} to {change.revised}. "
        f"{change.reason} Tradeoff: {change.tradeoff}"
    )


def _iter_dimension_checks(
    check_result: FeasibilityCheckResult,
    *,
    include_protocol: bool,
    include_policy: bool,
) -> list[tuple[str, DimensionCheck]]:
    checks: list[tuple[str, DimensionCheck]] = []
    if include_protocol:
        checks.append(("protocol", check_result.protocol))
    checks.extend(
        [
            ("budget", check_result.budget),
            ("equipment", check_result.equipment),
            ("reagents", check_result.reagents),
            ("schedule", check_result.schedule),
            ("staff", check_result.staff),
        ]
    )
    if include_policy:
        checks.append(("policy", check_result.policy))
    return checks


def _build_protocol_check(validation_result: ValidationResult) -> DimensionCheck:
    reasons = [issue.message for issue in validation_result.issues]
    return DimensionCheck(ok=validation_result.valid, reasons=reasons)


def _check_budget(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> tuple[DimensionCheck, float]:
    estimated_cost = _estimate_protocol_cost(protocol, scenario)
    remaining_budget = scenario.lab_manager_observation.budget_remaining

    if estimated_cost <= remaining_budget:
        return DimensionCheck(ok=True, reasons=[]), estimated_cost

    return (
        DimensionCheck(
            ok=False,
            reasons=[
                (
                    f"Estimated protocol cost ({estimated_cost:.2f}) exceeds the remaining "
                    f"budget ({remaining_budget:.2f})."
                )
            ],
        ),
        estimated_cost,
    )


def _check_equipment(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    substitution_index: dict[str, list[str]],
) -> tuple[DimensionCheck, dict[str, list[str]]]:
    available = {
        _normalize(label) for label in scenario.lab_manager_observation.equipment_available
    }
    booked = {
        _normalize(label) for label in scenario.lab_manager_observation.equipment_booked
    }

    reasons: list[str] = []
    substitutions: dict[str, list[str]] = {}

    for item in protocol.required_equipment:
        normalized = _normalize(item)
        if normalized in available:
            continue

        if normalized in booked:
            reasons.append(f"Equipment '{item}' is currently booked.")
        else:
            reasons.append(f"Equipment '{item}' is not available in the current scenario.")

        alternatives = substitution_index.get(normalized, [])
        if alternatives:
            substitutions[item] = alternatives
            reasons.append(
                f"Allowed substitutions for '{item}': {', '.join(alternatives)}."
            )

    return DimensionCheck(ok=not reasons, reasons=reasons), substitutions


def _check_reagents(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    substitution_index: dict[str, list[str]],
) -> tuple[DimensionCheck, dict[str, list[str]]]:
    in_stock = {
        _normalize(label) for label in scenario.lab_manager_observation.reagents_in_stock
    }
    out_of_stock = {
        _normalize(label)
        for label in scenario.lab_manager_observation.reagents_out_of_stock
    }

    reasons: list[str] = []
    substitutions: dict[str, list[str]] = {}

    for item in protocol.required_reagents:
        normalized = _normalize(item)
        if normalized in in_stock:
            continue

        if normalized in out_of_stock:
            reasons.append(f"Required resource '{item}' is currently unavailable.")
        else:
            reasons.append(f"Required resource '{item}' is not available in the current scenario.")

        alternatives = substitution_index.get(normalized, [])
        if alternatives:
            substitutions[item] = alternatives
            reasons.append(
                f"Allowed substitutions for '{item}': {', '.join(alternatives)}."
            )

    return DimensionCheck(ok=not reasons, reasons=reasons), substitutions


def _check_schedule(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> DimensionCheck:
    reasons: list[str] = []
    time_limit = scenario.lab_manager_observation.time_limit_days
    if protocol.duration_days > time_limit:
        reasons.append(
            f"Protocol duration ({protocol.duration_days} days) exceeds the allowed time limit ({time_limit} days)."
        )

    return DimensionCheck(ok=not reasons, reasons=reasons)


def _check_staff(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> tuple[DimensionCheck, int]:
    available_staff = scenario.lab_manager_observation.staff_count
    required_staff = _estimate_staff_load(protocol)

    if required_staff <= available_staff:
        return DimensionCheck(ok=True, reasons=[]), required_staff

    return (
        DimensionCheck(
            ok=False,
            reasons=[
                f"Protocol workload needs {required_staff} staff unit(s), but only {available_staff} are available."
            ],
        ),
        required_staff,
    )


def _check_policy(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> DimensionCheck:
    text = " ".join(
        [
            protocol.technique,
            protocol.rationale,
            *protocol.controls,
        ]
    ).lower()
    policy_text = " ".join(
        [constraint.details for constraint in scenario.constraints if constraint.hard]
        + scenario.lab_manager_observation.safety_restrictions
    ).lower()

    reasons: list[str] = []

    if ("offline" in policy_text or "no live trading" in policy_text) and any(
        token in text
        for token in ("live trading", "live execution", "real-money", "production trade")
    ):
        reasons.append("Protocol conflicts with the offline-only execution policy.")

    if ("held-out split" in policy_text or "test-set peeking" in policy_text) and any(
        token in text
        for token in (
            "peek at the test set",
            "tune on the test set",
            "optimize on the test set",
            "test-set peeking",
        )
    ):
        reasons.append("Protocol conflicts with the evaluation policy for held-out testing.")

    return DimensionCheck(ok=not reasons, reasons=reasons)


def _estimate_protocol_cost(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> float:
    """Return a transparent coarse cost estimate until explicit cost metadata exists."""

    base_effort = (
        (protocol.sample_size * 5)
        + (protocol.duration_days * 25)
        + (len(protocol.required_equipment) * 40)
        + (len(protocol.required_reagents) * 20)
        + (len(protocol.controls) * 10)
    )

    multiplier = {
        "mathematics": 1.0,
        "machine_learning": 4.0,
        "finance_trading": 2.0,
    }.get(scenario.domain_id, 1.5)

    return round(base_effort * multiplier, 2)


def _estimate_staff_load(protocol: Protocol) -> int:
    load = 1
    if protocol.sample_size > 24:
        load += 1
    if len(protocol.controls) > 2:
        load += 1
    if len(protocol.required_equipment) + len(protocol.required_reagents) > 5:
        load += 1
    if protocol.duration_days > 7:
        load += 1
    return load


def _build_substitution_index(
    scenario: NormalizedScenarioPack,
) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for substitution in scenario.allowed_substitutions:
        key = _normalize(substitution.original)
        index.setdefault(key, []).append(substitution.alternative)
    return index


def _normalize(value: str) -> str:
    return value.strip().lower()
