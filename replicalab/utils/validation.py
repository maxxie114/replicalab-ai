"""Deterministic semantic validation for proposed protocols.

MOD 05 provides a pure-function validator that checks a Protocol against
the scenario's resource vocabulary, substitution rules, time limits, and
required-element coverage.  Every check is deterministic — no LLM calls,
no budget heuristics.  The result is a structured ValidationResult that
downstream code (judge, environment, UI) can consume without crashing.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from replicalab.models import Protocol
from replicalab.scenarios.templates import NormalizedScenarioPack
from replicalab.utils.text import element_tokens as _element_tokens
from replicalab.utils.text import normalize_label as _normalize


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class ValidationIssue(BaseModel):
    """One problem detected during protocol validation."""

    model_config = ConfigDict(extra="forbid")

    severity: IssueSeverity
    category: str
    message: str


class ValidationResult(BaseModel):
    """Aggregate result of validating a protocol against a scenario."""

    model_config = ConfigDict(extra="forbid")

    valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity is IssueSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity is IssueSeverity.WARNING]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_protocol(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
) -> ValidationResult:
    """Validate *protocol* against *scenario* constraints.

    Returns a ``ValidationResult`` — never raises.  ``valid`` is True only
    when there are zero error-level issues.
    """
    issues: list[ValidationIssue] = []

    _check_obvious_impossibilities(protocol, issues)
    _check_duration_vs_time_limit(protocol, scenario, issues)
    _check_equipment_vocabulary(protocol, scenario, issues)
    _check_reagent_vocabulary(protocol, scenario, issues)
    _check_required_element_coverage(protocol, scenario, issues)

    has_errors = any(i.severity is IssueSeverity.ERROR for i in issues)
    return ValidationResult(valid=not has_errors, issues=issues)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_obvious_impossibilities(
    protocol: Protocol,
    issues: list[ValidationIssue],
) -> None:
    if protocol.sample_size < 1:
        issues.append(
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category="sample_size",
                message="Sample size must be at least 1.",
            )
        )
    if not protocol.controls:
        issues.append(
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category="controls",
                message="Protocol has no controls listed.",
            )
        )
    if protocol.duration_days < 1:
        issues.append(
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category="duration",
                message="Duration must be at least 1 day.",
            )
        )


def _check_duration_vs_time_limit(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    issues: list[ValidationIssue],
) -> None:
    time_limit = scenario.lab_manager_observation.time_limit_days
    if protocol.duration_days > time_limit:
        issues.append(
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category="duration",
                message=(
                    f"Protocol duration ({protocol.duration_days} days) "
                    f"exceeds the lab time limit ({time_limit} days)."
                ),
            )
        )


def _check_equipment_vocabulary(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    issues: list[ValidationIssue],
) -> None:
    lab = scenario.lab_manager_observation
    available = set(_normalize(label) for label in lab.equipment_available)
    booked = set(_normalize(label) for label in lab.equipment_booked)
    known = available | booked
    substitution_targets = _substitution_alternatives(scenario)

    for item in protocol.required_equipment:
        norm = _normalize(item)
        if norm in available:
            continue
        if norm in booked:
            if norm in substitution_targets:
                issues.append(
                    ValidationIssue(
                        severity=IssueSeverity.WARNING,
                        category="equipment",
                        message=(
                            f"Equipment '{item}' is booked but has an allowed substitution."
                        ),
                    )
                )
            else:
                issues.append(
                    ValidationIssue(
                        severity=IssueSeverity.ERROR,
                        category="equipment",
                        message=f"Equipment '{item}' is booked and has no substitution.",
                    )
                )
        elif norm not in known:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category="equipment",
                    message=f"Equipment '{item}' is not in the lab's known inventory.",
                )
            )


def _check_reagent_vocabulary(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    issues: list[ValidationIssue],
) -> None:
    lab = scenario.lab_manager_observation
    in_stock = set(_normalize(label) for label in lab.reagents_in_stock)
    out_of_stock = set(_normalize(label) for label in lab.reagents_out_of_stock)
    known = in_stock | out_of_stock
    substitution_targets = _substitution_alternatives(scenario)

    for item in protocol.required_reagents:
        norm = _normalize(item)
        if norm in in_stock:
            continue
        if norm in out_of_stock:
            if norm in substitution_targets:
                issues.append(
                    ValidationIssue(
                        severity=IssueSeverity.WARNING,
                        category="reagent",
                        message=(
                            f"Reagent '{item}' is out of stock but has an allowed substitution."
                        ),
                    )
                )
            else:
                issues.append(
                    ValidationIssue(
                        severity=IssueSeverity.ERROR,
                        category="reagent",
                        message=f"Reagent '{item}' is out of stock with no substitution.",
                    )
                )
        elif norm not in known:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category="reagent",
                    message=f"Reagent '{item}' is not in the lab's known inventory.",
                )
            )


def _check_required_element_coverage(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    issues: list[ValidationIssue],
) -> None:
    """Check whether the protocol plausibly addresses each required element.

    Uses simple substring matching against the protocol's technique,
    rationale, controls, equipment, and reagents.  This is intentionally
    conservative — an element is "covered" if any protocol field mentions
    a token from the required element string.
    """
    required = scenario.hidden_reference_spec.required_elements
    if not required:
        return

    protocol_text = " ".join([
        protocol.technique,
        protocol.rationale,
        " ".join(protocol.controls),
        " ".join(protocol.required_equipment),
        " ".join(protocol.required_reagents),
    ]).lower()

    for element in required:
        tokens = _element_tokens(element)
        if not any(token in protocol_text for token in tokens):
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category="required_element",
                    message=f"Required element '{element}' may not be addressed by the protocol.",
                )
            )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _substitution_alternatives(scenario: NormalizedScenarioPack) -> set[str]:
    """Return the normalized 'original' values from allowed substitutions."""
    return {
        _normalize(sub.original)
        for sub in scenario.allowed_substitutions
    }
