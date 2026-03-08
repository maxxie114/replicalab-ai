"""Dataset builders for Scientist GRPO and Lab Manager SFT."""

from __future__ import annotations

import json
from typing import Iterable, Sequence

from pydantic import BaseModel, ConfigDict, Field

from replicalab.agents.lab_manager_policy import (
    check_feasibility,
    compose_lab_manager_response,
    suggest_alternative,
)
from replicalab.agents.scientist_policy import (
    build_baseline_scientist_action,
    build_scientist_system_prompt,
    format_scientist_observation,
)
from replicalab.models import LabManagerAction, Protocol, ScientistAction, ScientistActionType
from replicalab.prompts import render_lab_manager_prompt
from replicalab.scenarios import NormalizedScenarioPack, generate_scenario
from replicalab.scenarios.templates import Difficulty, TemplateName
from replicalab.training.corpus import (
    FrozenEvidencePack,
    load_frozen_evidence_packs,
    select_evidence_pack,
)

DEFAULT_DIFFICULTIES: tuple[Difficulty, ...] = ("easy", "medium", "hard")
DEFAULT_TEMPLATES: tuple[TemplateName, ...] = (
    "math_reasoning",
    "ml_benchmark",
    "finance_trading",
)


class ScientistPromptExample(BaseModel):
    """One GRPO prompt row for the Scientist model."""

    model_config = ConfigDict(extra="forbid")

    prompt: list[dict[str, str]]
    seed: int
    scenario: TemplateName
    difficulty: Difficulty
    scenario_id: str
    paper_title: str
    evidence_id: str | None = None
    evidence_summary: str | None = None


class LabManagerSFTExample(BaseModel):
    """One supervised Lab Manager chat row with a deterministic target."""

    model_config = ConfigDict(extra="forbid")

    messages: list[dict[str, str]]
    seed: int
    scenario: TemplateName
    difficulty: Difficulty
    scenario_id: str
    candidate_kind: str
    evidence_id: str | None = None
    target_json: str


def build_scientist_prompt_examples(
    *,
    seeds: Iterable[int],
    templates: Sequence[TemplateName] = DEFAULT_TEMPLATES,
    difficulties: Sequence[Difficulty] = DEFAULT_DIFFICULTIES,
    evidence_packs: Sequence[FrozenEvidencePack] | None = None,
) -> list[ScientistPromptExample]:
    """Build GRPO prompt rows backed by normalized scenarios and frozen evidence."""

    packs = list(evidence_packs or load_frozen_evidence_packs())
    rows: list[ScientistPromptExample] = []

    for template in templates:
        for difficulty in difficulties:
            for seed in seeds:
                scenario_pack = generate_scenario(seed=seed, template=template, difficulty=difficulty)
                evidence_pack = select_evidence_pack(packs, template=template, seed=seed)
                user_message = format_scientist_observation(scenario_pack.scientist_observation)
                if evidence_pack is not None:
                    user_message += "\n\nFrozen evidence pack:\n" + evidence_pack.prompt_block()
                rows.append(
                    ScientistPromptExample(
                        prompt=[
                            {
                                "role": "system",
                                "content": build_scientist_system_prompt(scenario_pack),
                            },
                            {"role": "user", "content": user_message},
                        ],
                        seed=seed,
                        scenario=template,
                        difficulty=difficulty,
                        scenario_id=scenario_pack.scenario_id,
                        paper_title=scenario_pack.scientist_observation.paper_title,
                        evidence_id=evidence_pack.evidence_id if evidence_pack else None,
                        evidence_summary=evidence_pack.prompt_block() if evidence_pack else None,
                    )
                )

    return rows


def build_lab_manager_sft_examples(
    *,
    seeds: Iterable[int],
    templates: Sequence[TemplateName] = DEFAULT_TEMPLATES,
    difficulties: Sequence[Difficulty] = DEFAULT_DIFFICULTIES,
    evidence_packs: Sequence[FrozenEvidencePack] | None = None,
) -> list[LabManagerSFTExample]:
    """Build deterministic Lab Manager supervision rows."""

    packs = list(evidence_packs or load_frozen_evidence_packs())
    rows: list[LabManagerSFTExample] = []

    for template in templates:
        for difficulty in difficulties:
            for seed in seeds:
                scenario_pack = generate_scenario(seed=seed, template=template, difficulty=difficulty)
                evidence_pack = select_evidence_pack(packs, template=template, seed=seed)
                for candidate_kind, protocol, scientist_action in _build_protocol_candidates(scenario_pack):
                    check_result = check_feasibility(protocol, scenario_pack)
                    suggestion = suggest_alternative(protocol, check_result, scenario_pack)
                    target = compose_lab_manager_response(check_result, suggestion)
                    rows.append(
                        LabManagerSFTExample(
                            messages=[
                                {
                                    "role": "system",
                                    "content": render_lab_manager_prompt(scenario_pack),
                                },
                                {
                                    "role": "user",
                                    "content": _format_lab_manager_input(
                                        scenario_pack,
                                        protocol,
                                        scientist_action,
                                        evidence_pack,
                                    ),
                                },
                                {
                                    "role": "assistant",
                                    "content": target.model_dump_json(indent=2),
                                },
                            ],
                            seed=seed,
                            scenario=template,
                            difficulty=difficulty,
                            scenario_id=scenario_pack.scenario_id,
                            candidate_kind=candidate_kind,
                            evidence_id=evidence_pack.evidence_id if evidence_pack else None,
                            target_json=target.model_dump_json(indent=2),
                        )
                    )

    return rows


def build_scientist_hf_rows(
    *,
    seeds: Iterable[int],
    templates: Sequence[TemplateName] = DEFAULT_TEMPLATES,
    difficulties: Sequence[Difficulty] = DEFAULT_DIFFICULTIES,
    evidence_packs: Sequence[FrozenEvidencePack] | None = None,
) -> list[dict[str, object]]:
    """Return Hugging Face dataset rows for Scientist GRPO."""

    return [row.model_dump(mode="python") for row in build_scientist_prompt_examples(
        seeds=seeds,
        templates=templates,
        difficulties=difficulties,
        evidence_packs=evidence_packs,
    )]


def build_lab_manager_hf_rows(
    *,
    seeds: Iterable[int],
    templates: Sequence[TemplateName] = DEFAULT_TEMPLATES,
    difficulties: Sequence[Difficulty] = DEFAULT_DIFFICULTIES,
    evidence_packs: Sequence[FrozenEvidencePack] | None = None,
) -> list[dict[str, object]]:
    """Return Hugging Face dataset rows for Lab Manager SFT."""

    return [row.model_dump(mode="python") for row in build_lab_manager_sft_examples(
        seeds=seeds,
        templates=templates,
        difficulties=difficulties,
        evidence_packs=evidence_packs,
    )]


def _build_protocol_candidates(
    scenario_pack: NormalizedScenarioPack,
) -> list[tuple[str, Protocol, ScientistAction]]:
    """Create deterministic protocol candidates for Lab Manager supervision."""

    baseline_action = build_baseline_scientist_action(scenario_pack.scientist_observation)
    if baseline_action.action_type not in ScientistAction.PROTOCOL_ACTION_TYPES:
        return []

    baseline_protocol = _protocol_from_action(baseline_action)
    stressed_protocol = _stress_protocol(baseline_protocol, scenario_pack)
    stressed_action = _action_with_protocol(
        baseline_action,
        stressed_protocol,
        action_type=ScientistActionType.PROPOSE_PROTOCOL,
    )

    candidates: list[tuple[str, Protocol, ScientistAction]] = [
        ("baseline", baseline_protocol, baseline_action),
        ("constraint_stress", stressed_protocol, stressed_action),
    ]

    stressed_check = check_feasibility(stressed_protocol, scenario_pack)
    stressed_suggestion = suggest_alternative(stressed_protocol, stressed_check, scenario_pack)
    if stressed_suggestion.applied_changes:
        revised_action = _action_with_protocol(
            baseline_action,
            stressed_suggestion.revised_protocol,
            action_type=ScientistActionType.REVISE_PROTOCOL,
        )
        candidates.append(
            ("deterministic_revision", stressed_suggestion.revised_protocol, revised_action)
        )

    return candidates


def _protocol_from_action(action: ScientistAction) -> Protocol:
    return Protocol(
        sample_size=action.sample_size,
        controls=list(action.controls),
        technique=action.technique,
        duration_days=action.duration_days,
        required_equipment=list(action.required_equipment),
        required_reagents=list(action.required_reagents),
        rationale=action.rationale,
    )


def _action_with_protocol(
    base_action: ScientistAction,
    protocol: Protocol,
    *,
    action_type: ScientistActionType,
) -> ScientistAction:
    return ScientistAction(
        action_type=action_type,
        sample_size=protocol.sample_size,
        controls=list(protocol.controls),
        technique=protocol.technique,
        duration_days=protocol.duration_days,
        required_equipment=list(protocol.required_equipment),
        required_reagents=list(protocol.required_reagents),
        questions=[],
        rationale=protocol.rationale,
    )


def _stress_protocol(
    protocol: Protocol,
    scenario_pack: NormalizedScenarioPack,
) -> Protocol:
    """Create a deterministic harder-to-approve protocol candidate."""

    observation = scenario_pack.lab_manager_observation
    required_equipment = list(protocol.required_equipment)
    required_reagents = list(protocol.required_reagents)

    if observation.equipment_booked:
        required_equipment.append(observation.equipment_booked[0])
    if observation.reagents_out_of_stock:
        required_reagents.append(observation.reagents_out_of_stock[0])

    required_equipment = _dedupe(required_equipment)
    required_reagents = _dedupe(required_reagents)

    time_limit = max(1, observation.time_limit_days)
    return Protocol(
        sample_size=max(protocol.sample_size + 3, protocol.sample_size * 2),
        controls=list(protocol.controls),
        technique=protocol.technique,
        duration_days=max(protocol.duration_days, time_limit + 1),
        required_equipment=required_equipment,
        required_reagents=required_reagents,
        rationale=(
            f"{protocol.rationale} Stress candidate for deterministic Lab Manager "
            "supervision under tighter budget, schedule, and inventory pressure."
        ),
    )


def _format_lab_manager_input(
    scenario_pack: NormalizedScenarioPack,
    protocol: Protocol,
    scientist_action: ScientistAction,
    evidence_pack: FrozenEvidencePack | None,
) -> str:
    observation = scenario_pack.lab_manager_observation
    sections = [
        f"Round {observation.round_number} of {observation.max_rounds}.",
        (
            f"Budget remaining: {observation.budget_remaining:.2f} / "
            f"{observation.budget_total:.2f}"
        ),
        (
            "Equipment available: "
            + (", ".join(observation.equipment_available) or "(none listed)")
        ),
        (
            "Equipment booked: "
            + (", ".join(observation.equipment_booked) or "(none booked)")
        ),
        (
            "Reagents in stock: "
            + (", ".join(observation.reagents_in_stock) or "(none listed)")
        ),
        (
            "Reagents out of stock: "
            + (", ".join(observation.reagents_out_of_stock) or "(none listed)")
        ),
        f"Staff count: {observation.staff_count}",
        f"Time limit: {observation.time_limit_days} day(s)",
        "Safety restrictions:\n- " + "\n- ".join(observation.safety_restrictions),
        "Current protocol:\n" + protocol.model_dump_json(indent=2),
        "Scientist action:\n" + scientist_action.model_dump_json(indent=2),
    ]

    if evidence_pack is not None:
        sections.append("Frozen evidence pack:\n" + evidence_pack.prompt_block())

    sections.append(
        "Respond with exactly one JSON object matching LabManagerAction. "
        "Do not add markdown or commentary."
    )
    return "\n\n".join(sections)


def _dedupe(items: Iterable[str]) -> list[str]:
    seen: dict[str, None] = {}
    for item in items:
        seen[item] = None
    return list(seen)


__all__ = [
    "DEFAULT_DIFFICULTIES",
    "DEFAULT_TEMPLATES",
    "LabManagerSFTExample",
    "ScientistPromptExample",
    "build_lab_manager_hf_rows",
    "build_lab_manager_sft_examples",
    "build_scientist_hf_rows",
    "build_scientist_prompt_examples",
]
