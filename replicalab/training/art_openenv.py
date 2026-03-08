"""ART + ReplicaLab OpenEnv training helpers."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

from pydantic import BaseModel, ConfigDict, Field

from replicalab.agents.scientist_policy import (
    ScientistOutputParseError,
    format_scientist_observation,
    parse_scientist_output,
)
from replicalab.client import ReplicaLabClient
from replicalab.models import ScientistObservation
from replicalab.training.artifacts import ArtifactLayout, append_jsonl, build_run_name, write_json
from replicalab.training.corpus import (
    FrozenEvidencePack,
    evidence_pack_version,
    load_frozen_evidence_packs,
    select_evidence_pack,
)


class ArtScenarioSpec(BaseModel):
    """One deterministic scenario spec for ART/OpenEnv rollouts."""

    model_config = ConfigDict(extra="forbid")

    seed: int
    scenario: str
    difficulty: str


class ArtOpenEnvConfig(BaseModel):
    """Config for serverless ART training against ReplicaLab."""

    model_config = ConfigDict(extra="forbid")

    project: str = "replicalab-art-openenv"
    model_name: str = "replicalab-scientist-art"
    base_model: str = "OpenPipe/Qwen3-14B-Instruct"
    base_url: str = "https://ayushozha-replicalab.hf.space"
    transport: str = "rest"
    train_steps: int = 1
    rollouts_per_group: int = 2
    max_turns: int = 6
    max_completion_tokens: int = 700
    max_parse_retries: int = 2
    learning_rate: float = 5e-6
    beta: float = 0.0
    scenarios: list[ArtScenarioSpec] = Field(
        default_factory=lambda: [
            ArtScenarioSpec(seed=11, scenario="math_reasoning", difficulty="easy"),
            ArtScenarioSpec(seed=12, scenario="ml_benchmark", difficulty="easy"),
        ]
    )


class ArtRolloutSummary(BaseModel):
    """Flat rollout record for demo/docs and post-run analysis."""

    model_config = ConfigDict(extra="forbid")

    run_name: str
    training_step: int
    group_index: int
    rollout_index: int
    seed: int
    scenario: str
    difficulty: str
    paper_title: str
    evidence_id: str | None = None
    evidence_match_type: str | None = None
    reward: float
    verdict: str | None = None
    agreement_reached: bool = False
    rounds_used: int = 0
    invalid_action_count: int = 0
    parse_error_count: int = 0
    rigor: float = 0.0
    feasibility: float = 0.0
    fidelity: float = 0.0
    parsimony: float = 1.0
    artifact_step: int | None = None
    artifact_name: str | None = None


class ArtTrainingSummary(BaseModel):
    """Top-level training summary written after the run."""

    model_config = ConfigDict(extra="forbid")

    run_name: str
    project: str
    model_name: str
    base_model: str
    train_steps: int
    rollouts_per_group: int
    scenario_count: int
    base_url: str
    evidence_version: str
    started_at: str
    finished_at: str
    final_artifact_step: int | None = None
    final_artifact_name: str | None = None
    average_reward: float = 0.0
    agreement_rate: float = 0.0
    average_rounds: float = 0.0


@dataclass
class _TurnRecord:
    messages_and_choices: list[Any]
    parse_error: str | None
    raw_text: str


@dataclass
class _EpisodeTrace:
    trajectory: Any
    summary: ArtRolloutSummary


def run_art_openenv_training(
    config: ArtOpenEnvConfig,
    *,
    layout: ArtifactLayout | None = None,
) -> dict[str, object]:
    """Sync wrapper used by CLI entrypoints."""

    artifact_layout = layout or ArtifactLayout.create(run_name=build_run_name("art-scientist"))
    return asyncio.run(_run_art_openenv_training_async(config, artifact_layout))


async def _run_art_openenv_training_async(
    config: ArtOpenEnvConfig,
    layout: ArtifactLayout,
) -> dict[str, object]:
    art_module = __import__("art")
    from art import Trajectory, TrajectoryGroup, TrainableModel
    from art.gather import gather_trajectory_groups
    from art.serverless import ServerlessBackend
    from art.trajectories import History

    started_at = _utc_now()
    evidence_packs = [pack for pack in load_frozen_evidence_packs() if pack.trainable_in_env]
    evidence_version = evidence_pack_version(evidence_packs)
    backend = ServerlessBackend()
    model = TrainableModel(
        name=config.model_name,
        project=config.project,
        base_model=config.base_model,
        base_path=str(layout.run_dir),
        report_metrics=[
            "average_reward",
            "agreement_rate",
            "average_rounds",
            "average_rigor",
            "average_feasibility",
            "average_fidelity",
            "average_parsimony",
            "invalid_action_rate",
        ],
    )
    await model.register(backend)

    write_json(layout.config_json, config.model_dump(mode="json"))
    write_json(
        layout.evidence_manifest_json,
        {
            "evidence_version": evidence_version,
            "packs": [pack.model_dump(mode="json") for pack in evidence_packs],
        },
    )
    process_log_path = layout.reports_dir / "art_training_process.md"
    process_log_path.parent.mkdir(parents=True, exist_ok=True)
    process_log_path.write_text(
        "# ReplicaLab ART Training Run\n\n",
        encoding="utf-8",
    )
    _append_process_log(
        process_log_path,
        f"Started at `{started_at}` against `{config.base_url}` using `{config.base_model}`.",
    )
    _append_process_log(
        process_log_path,
        (
            f"Loaded `{len(evidence_packs)}` trainable frozen evidence packs "
            f"(version `{evidence_version}`)."
        ),
    )

    all_rollouts: list[ArtRolloutSummary] = []
    final_artifact_step: int | None = None
    final_artifact_name: str | None = None

    for training_step in range(1, config.train_steps + 1):
        _append_process_log(
            process_log_path,
            (
                f"Training step {training_step}: collecting "
                f"{len(config.scenarios)} trajectory groups with "
                f"{config.rollouts_per_group} rollouts each."
            ),
        )

        groups = await gather_trajectory_groups(
            [
                _collect_trajectory_group(
                    model=model,
                    config=config,
                    spec=spec,
                    evidence_pack=select_evidence_pack(
                        evidence_packs,
                        template=spec.scenario,
                        seed=spec.seed,
                    ),
                    group_index=group_index,
                    training_step=training_step,
                    run_name=layout.run_name,
                )
                for group_index, spec in enumerate(config.scenarios)
            ],
            pbar_desc=f"replicalab-step-{training_step}",
        )

        batch_summaries: list[ArtRolloutSummary] = []
        for group in groups:
            for trajectory in group.trajectories:
                summary = ArtRolloutSummary.model_validate(trajectory.metadata)
                batch_summaries.append(summary)
                append_jsonl(layout.metrics_jsonl, summary.model_dump(mode="json"))

        await model.log(groups, split="train")
        train_result = await backend.train(
            model,
            groups,
            learning_rate=config.learning_rate,
            beta=config.beta,
        )
        await model.log(
            split="train",
            metrics=train_result.metrics,
            step=train_result.step,
        )

        final_artifact_step = train_result.step
        final_artifact_name = train_result.artifact_name
        _append_process_log(
            process_log_path,
            (
                f"Completed training step {training_step}: artifact="
                f"`{train_result.artifact_name}` step={train_result.step} "
                f"metrics={json.dumps(train_result.metrics, sort_keys=True)}"
            ),
        )

        for summary in batch_summaries:
            summary.artifact_step = train_result.step
            summary.artifact_name = train_result.artifact_name

        all_rollouts.extend(batch_summaries)

    finished_at = _utc_now()
    summary = _summarize_art_training(
        config=config,
        layout=layout,
        started_at=started_at,
        finished_at=finished_at,
        rollouts=all_rollouts,
        evidence_version=evidence_version,
        final_artifact_step=final_artifact_step,
        final_artifact_name=final_artifact_name,
    )
    write_json(layout.summary_json, summary.model_dump(mode="json"))
    _append_process_log(
        process_log_path,
        (
            f"Finished at `{finished_at}`. Average reward={summary.average_reward:.4f}, "
            f"agreement_rate={summary.agreement_rate:.4f}, "
            f"average_rounds={summary.average_rounds:.4f}."
        ),
    )
    return summary.model_dump(mode="json")


async def _collect_trajectory_group(
    *,
    model: Any,
    config: ArtOpenEnvConfig,
    spec: ArtScenarioSpec,
    evidence_pack: FrozenEvidencePack | None,
    group_index: int,
    training_step: int,
    run_name: str,
) -> Any:
    from art import TrajectoryGroup

    traces = await asyncio.gather(
        *[
            _run_art_episode(
                model=model,
                config=config,
                spec=spec,
                evidence_pack=evidence_pack,
                group_index=group_index,
                rollout_index=rollout_index,
                training_step=training_step,
                run_name=run_name,
            )
            for rollout_index in range(config.rollouts_per_group)
        ]
    )
    return TrajectoryGroup(
        trajectories=[trace.trajectory for trace in traces],
        metadata={
            "scenario": spec.scenario,
            "difficulty": spec.difficulty,
            "seed": spec.seed,
            "training_step": training_step,
        },
        metrics={
            "average_reward": _mean(summary.reward for summary in [trace.summary for trace in traces]),
            "agreement_rate": _mean(
                1.0 if trace.summary.agreement_reached else 0.0 for trace in traces
            ),
        },
        logs=[
            (
                f"group={group_index} seed={spec.seed} scenario={spec.scenario} "
                f"difficulty={spec.difficulty}"
            )
        ],
    )


async def _run_art_episode(
    *,
    model: Any,
    config: ArtOpenEnvConfig,
    spec: ArtScenarioSpec,
    evidence_pack: FrozenEvidencePack | None,
    group_index: int,
    rollout_index: int,
    training_step: int,
    run_name: str,
) -> _EpisodeTrace:
    from art import Trajectory
    from art.trajectories import History

    client = ReplicaLabClient(config.base_url, transport=config.transport)
    await asyncio.to_thread(client.connect)
    invalid_action_count = 0
    parse_error_count = 0
    turns: list[_TurnRecord] = []

    try:
        observation = await asyncio.to_thread(
            client.reset,
            spec.seed,
            spec.scenario,
            spec.difficulty,
        )
        scientist_obs = observation.scientist
        if scientist_obs is None:
            raise RuntimeError("Reset returned no scientist observation.")

        terminal_reward = -1.0
        terminal_info = None

        for _ in range(config.max_turns):
            system_prompt = _build_art_scientist_system_prompt(
                spec=spec,
                observation=scientist_obs,
                evidence_pack=evidence_pack,
            )
            user_prompt = format_scientist_observation(scientist_obs)
            if evidence_pack is not None:
                user_prompt += "\n\nFrozen evidence pack:\n" + evidence_pack.prompt_block()
            turn = await _generate_turn(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_completion_tokens=config.max_completion_tokens,
                max_parse_retries=config.max_parse_retries,
            )
            turns.append(turn)

            if turn.parse_error is not None:
                parse_error_count += 1
                terminal_reward = -1.0
                break

            action = parse_scientist_output(turn.raw_text)
            result = await asyncio.to_thread(client.step, action)
            terminal_reward = result.reward
            terminal_info = result.info
            if result.info.error:
                invalid_action_count += 1

            if result.done:
                break

            if result.observation is None or result.observation.scientist is None:
                raise RuntimeError("Non-terminal step returned no scientist observation.")
            scientist_obs = result.observation.scientist

        histories = [
            History(messages_and_choices=turn.messages_and_choices)
            for turn in turns[1:]
        ]
        trajectory = Trajectory(
            messages_and_choices=(turns[0].messages_and_choices if turns else []),
            additional_histories=histories,
            reward=terminal_reward,
            metrics=_extract_terminal_metrics(
                terminal_info=terminal_info,
                invalid_action_count=invalid_action_count,
                parse_error_count=parse_error_count,
                rounds_used=len(turns),
            ),
            metadata={},
            logs=[
                (
                    f"training_step={training_step} group={group_index} rollout={rollout_index} "
                    f"seed={spec.seed} scenario={spec.scenario} difficulty={spec.difficulty}"
                )
            ],
        )
        summary = ArtRolloutSummary(
            run_name=run_name,
            training_step=training_step,
            group_index=group_index,
            rollout_index=rollout_index,
            seed=spec.seed,
            scenario=spec.scenario,
            difficulty=spec.difficulty,
            paper_title=scientist_obs.paper_title,
            evidence_id=(evidence_pack.evidence_id if evidence_pack is not None else None),
            evidence_match_type=(
                evidence_pack.match_type if evidence_pack is not None else None
            ),
            reward=terminal_reward,
            verdict=(terminal_info.verdict if terminal_info is not None else None),
            agreement_reached=(
                terminal_info.agreement_reached if terminal_info is not None else False
            ),
            rounds_used=len(turns),
            invalid_action_count=invalid_action_count,
            parse_error_count=parse_error_count,
            rigor=(
                terminal_info.reward_breakdown.rigor
                if terminal_info and terminal_info.reward_breakdown
                else 0.0
            ),
            feasibility=(
                terminal_info.reward_breakdown.feasibility
                if terminal_info and terminal_info.reward_breakdown
                else 0.0
            ),
            fidelity=(
                terminal_info.reward_breakdown.fidelity
                if terminal_info and terminal_info.reward_breakdown
                else 0.0
            ),
            parsimony=(
                terminal_info.reward_breakdown.parsimony
                if terminal_info and terminal_info.reward_breakdown
                else 1.0
            ),
        )
        trajectory.metadata.update(summary.model_dump(mode="json"))
        return _EpisodeTrace(trajectory=trajectory, summary=summary)
    finally:
        await asyncio.to_thread(client.close)


async def _generate_turn(
    *,
    model: Any,
    system_prompt: str,
    user_prompt: str,
    max_completion_tokens: int,
    max_parse_retries: int,
) -> _TurnRecord:
    client = model.openai_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    for attempt in range(max_parse_retries + 1):
        completion = await client.chat.completions.create(
            model=model.get_inference_name(),
            messages=messages,
            max_completion_tokens=max_completion_tokens,
            temperature=0.0,
        )
        choice = completion.choices[0]
        raw_text = _extract_choice_text(choice)
        try:
            parse_scientist_output(raw_text)
            return _TurnRecord(
                messages_and_choices=[
                    *messages,
                    {"role": "assistant", "content": raw_text},
                ],
                parse_error=None,
                raw_text=raw_text,
            )
        except ScientistOutputParseError as exc:
            if attempt >= max_parse_retries:
                return _TurnRecord(
                    messages_and_choices=[
                        *messages,
                        {"role": "assistant", "content": raw_text},
                    ],
                    parse_error=exc.message,
                    raw_text=raw_text,
                )
            messages.extend(
                [
                    {"role": "assistant", "content": raw_text},
                    {"role": "user", "content": _build_art_correction_prompt(exc)},
                ]
            )
    raise RuntimeError("unreachable")


def _build_art_scientist_system_prompt(
    *,
    spec: ArtScenarioSpec,
    observation: ScientistObservation,
    evidence_pack: FrozenEvidencePack | None,
) -> str:
    sections = [
        "You are the Scientist agent in ReplicaLab.",
        "Negotiate toward the strongest feasible technical plan under hard real-world constraints.",
        "Return exactly one valid ScientistAction JSON object with no markdown and no extra prose.",
        "Use request_info only when a concrete blocking question remains.",
        "Use accept only when the current protocol is genuinely ready.",
        "Bounded tool policy: search_evidence, run_code_check, and inspect_image are support tools only; they never override constraints or reveal hidden ground truth.",
        f"Scenario family: {spec.scenario}",
        f"Difficulty: {spec.difficulty}",
        f"Paper title: {observation.paper_title}",
        f"Goal: {observation.experiment_goal}",
        (
            "The user observation already contains the full conversation "
            "history and current protocol. Use that as your source of truth "
            "for each turn."
        ),
    ]
    if evidence_pack is not None:
        sections.extend(
            [
                f"Frozen evidence id: {evidence_pack.evidence_id}",
                f"Grounding paper: {evidence_pack.downloaded_paper_title}",
                f"Claim: {evidence_pack.claim}",
                f"Technique: {evidence_pack.key_technique}",
                f"Constraint tension: {evidence_pack.primary_constraint_tension}",
            ]
        )
    sections.extend(
        [
            "Always emit all ScientistAction fields, even for request_info or accept.",
            (
                "Shape example: "
                '{"action_type":"propose_protocol","sample_size":8,"controls":["baseline"],'
                '"technique":"LoRA fine-tuning on the public subset","duration_days":2,'
                '"required_equipment":["gpu_h100"],"required_reagents":[],'
                '"questions":[],"rationale":"Uses the available hardware and stays within the reduced dataset budget."}'
            ),
        ]
    )
    return "\n".join(sections)


def _extract_choice_text(choice: Any) -> str:
    message = getattr(choice, "message", None)
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                parts.append(str(text))
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
        return "\n".join(parts)
    return ""


def _build_art_correction_prompt(error: ScientistOutputParseError) -> str:
    suffix = (
        "Return exactly one JSON object with all ScientistAction fields. "
        "No markdown fences, no prose, no commentary."
    )
    if error.code == "no_json":
        return "Your previous response did not contain a JSON object. " + suffix
    if error.code == "invalid_json":
        return (
            f"Your previous response contained malformed JSON: {error.message}. " + suffix
        )
    return (
        "Your previous response contained valid JSON but failed ScientistAction "
        f"validation: {error.message}. Fix the validation error and return a corrected "
        "ScientistAction JSON object. " + suffix
    )


def _extract_terminal_metrics(
    *,
    terminal_info: Any,
    invalid_action_count: int,
    parse_error_count: int,
    rounds_used: int,
) -> dict[str, float | int | bool]:
    breakdown = terminal_info.reward_breakdown if terminal_info is not None else None
    return {
        "agreement_reached": terminal_info.agreement_reached if terminal_info else False,
        "invalid_action_count": invalid_action_count,
        "invalid_action_rate": (invalid_action_count / max(1, rounds_used)),
        "parse_error_count": parse_error_count,
        "parse_error_rate": (parse_error_count / max(1, rounds_used)),
        "rounds_used": rounds_used,
        "rigor": (breakdown.rigor if breakdown is not None else 0.0),
        "feasibility": (breakdown.feasibility if breakdown is not None else 0.0),
        "fidelity": (breakdown.fidelity if breakdown is not None else 0.0),
        "parsimony": (breakdown.parsimony if breakdown is not None else 1.0),
    }


def _summarize_art_training(
    *,
    config: ArtOpenEnvConfig,
    layout: ArtifactLayout,
    started_at: str,
    finished_at: str,
    rollouts: Sequence[ArtRolloutSummary],
    evidence_version: str,
    final_artifact_step: int | None,
    final_artifact_name: str | None,
) -> ArtTrainingSummary:
    return ArtTrainingSummary(
        run_name=layout.run_name,
        project=config.project,
        model_name=config.model_name,
        base_model=config.base_model,
        train_steps=config.train_steps,
        rollouts_per_group=config.rollouts_per_group,
        scenario_count=len(config.scenarios),
        base_url=config.base_url,
        evidence_version=evidence_version,
        started_at=started_at,
        finished_at=finished_at,
        final_artifact_step=final_artifact_step,
        final_artifact_name=final_artifact_name,
        average_reward=_mean(item.reward for item in rollouts),
        agreement_rate=_mean(1.0 if item.agreement_reached else 0.0 for item in rollouts),
        average_rounds=_mean(item.rounds_used for item in rollouts),
    )


def _append_process_log(path: Path, line: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {line}\n")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _mean(values: Any) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(float(value) for value in values) / len(values), 6)


__all__ = [
    "ArtOpenEnvConfig",
    "ArtRolloutSummary",
    "ArtScenarioSpec",
    "ArtTrainingSummary",
    "run_art_openenv_training",
]
