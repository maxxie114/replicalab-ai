"""Prompt template assets and render helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Mapping

from replicalab.models import LabManagerActionType, ScientistActionType
from replicalab.scenarios import NormalizedScenarioPack

PromptRole = Literal["scientist", "lab_manager", "judge"]

_PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt_asset(name: str) -> str:
    """Load any prompt asset by filename stem."""

    path = _PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def load_prompt_template(role: PromptRole) -> str:
    """Load a role prompt template from disk."""

    return load_prompt_asset(role)


def render_prompt_template(
    role: PromptRole,
    scenario: NormalizedScenarioPack | Mapping[str, Any],
) -> str:
    """Render a role prompt from the normalized scenario pack."""

    pack = _coerce_scenario_pack(scenario)
    if role == "scientist":
        allowed_actions = ", ".join(action.value for action in ScientistActionType)
    elif role == "lab_manager":
        allowed_actions = ", ".join(action.value for action in LabManagerActionType)
    else:
        allowed_actions = "n/a"

    template = load_prompt_template(role)
    return template.format(
        domain_id=pack.domain_id,
        task_summary=pack.task_summary,
        success_criteria=_render_bullets(pack.success_criteria),
        constraints=_render_constraints(pack),
        resources=_render_resources(pack),
        substitutions=_render_substitutions(pack),
        allowed_actions=allowed_actions,
    )


def render_scientist_prompt(
    scenario: NormalizedScenarioPack | Mapping[str, Any],
) -> str:
    return render_prompt_template("scientist", scenario)


def render_lab_manager_prompt(
    scenario: NormalizedScenarioPack | Mapping[str, Any],
) -> str:
    return render_prompt_template("lab_manager", scenario)


def render_judge_prompt(
    scenario: NormalizedScenarioPack | Mapping[str, Any],
) -> str:
    return render_prompt_template("judge", scenario)


def _coerce_scenario_pack(
    scenario: NormalizedScenarioPack | Mapping[str, Any],
) -> NormalizedScenarioPack:
    if isinstance(scenario, NormalizedScenarioPack):
        return scenario
    return NormalizedScenarioPack.model_validate(scenario)


def _render_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _render_constraints(pack: NormalizedScenarioPack) -> str:
    lines: list[str] = []
    for constraint in pack.constraints:
        amount = ""
        if constraint.quantity is not None:
            unit = f" {constraint.unit}" if constraint.unit else ""
            amount = f" ({constraint.comparator} {constraint.quantity}{unit})"
        hardness = "hard" if constraint.hard else "soft"
        lines.append(f"- [{hardness}] {constraint.label}{amount}: {constraint.details}")
    return "\n".join(lines)


def _render_resources(pack: NormalizedScenarioPack) -> str:
    lines: list[str] = []
    for resource in pack.resources:
        availability = "available" if resource.available else "unavailable"
        amount = ""
        if resource.quantity is not None:
            unit = f" {resource.unit}" if resource.unit else ""
            amount = f" ({resource.quantity}{unit})"
        lines.append(
            f"- [{availability}] {resource.label}{amount}: {resource.details}"
        )
    return "\n".join(lines)


def _render_substitutions(pack: NormalizedScenarioPack) -> str:
    if not pack.allowed_substitutions:
        return "- No substitutions are pre-approved."

    lines: list[str] = []
    for substitution in pack.allowed_substitutions:
        lines.append(
            (
                f"- {substitution.original} -> {substitution.alternative}. "
                f"Condition: {substitution.condition} Tradeoff: {substitution.tradeoff}"
            )
        )
    return "\n".join(lines)


__all__ = [
    "PromptRole",
    "load_prompt_asset",
    "load_prompt_template",
    "render_prompt_template",
    "render_scientist_prompt",
    "render_lab_manager_prompt",
    "render_judge_prompt",
]
