"""Scientist GRPO configuration and training helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel, ConfigDict, Field

from replicalab.agents.lab_manager_policy import check_feasibility
from replicalab.agents.scientist_policy import (
    ScientistOutputParseError,
    parse_scientist_output,
)
from replicalab.models import Protocol, ScientistActionType
from replicalab.scenarios import generate_scenario
from replicalab.scenarios.templates import Difficulty, TemplateName
from replicalab.scoring.rubric import build_reward_breakdown, compute_total_reward
from replicalab.training.artifacts import ArtifactLayout, build_run_name, write_json
from replicalab.training.corpus import evidence_pack_version, load_frozen_evidence_packs
from replicalab.training.datasets import (
    DEFAULT_DIFFICULTIES,
    DEFAULT_TEMPLATES,
    build_scientist_hf_rows,
)
from replicalab.training.runtime import build_hf_dataset, load_qwen_lora_model, require_module, save_adapter


class ScientistGRPOConfig(BaseModel):
    """Notebook- and Northflank-friendly Scientist training config."""

    model_config = ConfigDict(extra="forbid")

    model_name: str = "Qwen/Qwen3-8B"
    max_seq_length: int = 4096
    load_in_4bit: bool = False
    fast_inference: bool = True
    lora_rank: int = 32
    lora_alpha: int = 32
    seed: int = 3407
    templates: list[TemplateName] = Field(default_factory=lambda: list(DEFAULT_TEMPLATES))
    difficulties: list[Difficulty] = Field(default_factory=lambda: list(DEFAULT_DIFFICULTIES))
    train_seeds: list[int] = Field(default_factory=lambda: list(range(16)))
    learning_rate: float = 5e-6
    weight_decay: float = 0.1
    warmup_ratio: float = 0.1
    lr_scheduler_type: str = "cosine"
    optim: str = "adamw_8bit"
    logging_steps: int = 5
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 4
    num_generations: int = 4
    max_completion_length: int = 768
    save_steps: int = 50
    max_steps: int = 300


class ScientistTrainingPlan(BaseModel):
    """Preview payload saved before training starts."""

    model_config = ConfigDict(extra="forbid")

    run_name: str
    model_name: str
    dataset_size: int
    evidence_pack_version: str
    config: dict[str, object]
    output_dir: str


class ScientistRewardSuite:
    """Deterministic reward functions used by TRL GRPOTrainer."""

    def reward_json_contract(self, completions: list[Any], **_: Any) -> list[float]:
        scores: list[float] = []
        for text in _extract_completion_texts(completions):
            try:
                parse_scientist_output(text)
                scores.append(0.5)
            except ScientistOutputParseError as exc:
                if exc.code == "no_json":
                    scores.append(-1.5)
                else:
                    scores.append(-1.0)
        return scores

    def reward_protocol_quality(
        self,
        completions: list[Any],
        seed: list[int] | tuple[int, ...],
        scenario: list[str] | tuple[str, ...],
        difficulty: list[str] | tuple[str, ...],
        **_: Any,
    ) -> list[float]:
        scores: list[float] = []
        texts = _extract_completion_texts(completions)

        for text, row_seed, row_template, row_difficulty in zip(
            texts, seed, scenario, difficulty
        ):
            try:
                action = parse_scientist_output(text)
            except ScientistOutputParseError:
                scores.append(-2.0)
                continue

            if action.action_type is ScientistActionType.REQUEST_INFO:
                scores.append(_score_request_info(action.questions))
                continue

            if action.action_type is ScientistActionType.ACCEPT:
                scores.append(-0.5)
                continue

            scenario_pack = generate_scenario(
                seed=int(row_seed),
                template=row_template,  # type: ignore[arg-type]
                difficulty=row_difficulty,  # type: ignore[arg-type]
            )
            protocol = Protocol(
                sample_size=action.sample_size,
                controls=list(action.controls),
                technique=action.technique,
                duration_days=action.duration_days,
                required_equipment=list(action.required_equipment),
                required_reagents=list(action.required_reagents),
                rationale=action.rationale,
            )
            check = check_feasibility(protocol, scenario_pack)
            breakdown = build_reward_breakdown(
                protocol,
                scenario_pack,
                rounds_used=1,
                max_rounds=scenario_pack.scientist_observation.max_rounds,
                check=check,
            )
            reward = compute_total_reward(breakdown)
            if action.action_type is ScientistActionType.REVISE_PROTOCOL:
                reward += 0.25
            scores.append(round(reward, 6))

        return scores

    def reward_functions(self) -> list[Any]:
        return [self.reward_json_contract, self.reward_protocol_quality]


def preview_scientist_training(
    config: ScientistGRPOConfig,
    *,
    layout: ArtifactLayout | None = None,
) -> ScientistTrainingPlan:
    """Build and persist the training plan without touching GPU-only imports."""

    evidence_packs = load_frozen_evidence_packs()
    rows = build_scientist_hf_rows(
        seeds=config.train_seeds,
        templates=config.templates,
        difficulties=config.difficulties,
        evidence_packs=evidence_packs,
    )
    plan = ScientistTrainingPlan(
        run_name=(layout.run_name if layout is not None else build_run_name("scientist")),
        model_name=config.model_name,
        dataset_size=len(rows),
        evidence_pack_version=evidence_pack_version(evidence_packs),
        config=config.model_dump(mode="json"),
        output_dir=str((layout.run_dir if layout is not None else Path(".")).resolve()),
    )
    return plan


def train_scientist_grpo(
    config: ScientistGRPOConfig,
    *,
    layout: ArtifactLayout | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    """Run a Scientist GRPO training job or produce a dry-run preview."""

    artifact_layout = layout or ArtifactLayout.create(
        run_name=build_run_name("scientist")
    )
    evidence_packs = load_frozen_evidence_packs()
    rows = build_scientist_hf_rows(
        seeds=config.train_seeds,
        templates=config.templates,
        difficulties=config.difficulties,
        evidence_packs=evidence_packs,
    )

    plan = preview_scientist_training(config, layout=artifact_layout)
    write_json(artifact_layout.config_json, plan.model_dump(mode="json"))
    write_json(
        artifact_layout.evidence_manifest_json,
        [pack.model_dump(mode="json") for pack in evidence_packs],
    )

    if dry_run:
        return plan.model_dump(mode="json")

    trl_module = require_module("trl")
    model, tokenizer = load_qwen_lora_model(
        model_name=config.model_name,
        max_seq_length=config.max_seq_length,
        load_in_4bit=config.load_in_4bit,
        fast_inference=config.fast_inference,
        lora_rank=config.lora_rank,
        lora_alpha=config.lora_alpha,
        random_state=config.seed,
    )
    dataset = build_hf_dataset(rows)
    max_prompt_length = max(
        len(
            tokenizer.apply_chat_template(
                row["prompt"],
                tokenize=True,
                add_generation_prompt=True,
            )
        )
        for row in rows
    )
    reward_suite = ScientistRewardSuite()
    training_args = trl_module.GRPOConfig(
        output_dir=str(artifact_layout.checkpoints_dir),
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        lr_scheduler_type=config.lr_scheduler_type,
        optim=config.optim,
        logging_steps=config.logging_steps,
        per_device_train_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        num_generations=config.num_generations,
        max_prompt_length=max_prompt_length,
        max_completion_length=config.max_completion_length,
        save_steps=config.save_steps,
        max_steps=config.max_steps,
        bf16=True,
        report_to=[],
    )
    trainer = trl_module.GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=reward_suite.reward_functions(),
        args=training_args,
        train_dataset=dataset,
    )
    trainer.train()
    save_adapter(model, tokenizer, artifact_layout.scientist_adapter_dir)
    write_json(
        artifact_layout.reports_dir / "scientist_trainer_state.json",
        {"log_history": trainer.state.log_history},
    )
    return {
        "run_name": artifact_layout.run_name,
        "adapter_dir": str(artifact_layout.scientist_adapter_dir),
        "dataset_size": len(rows),
    }


def _extract_completion_texts(completions: list[Any]) -> list[str]:
    texts: list[str] = []
    for completion in completions:
        if isinstance(completion, str):
            texts.append(completion)
            continue
        if isinstance(completion, list) and completion:
            first = completion[0]
            if isinstance(first, dict) and "content" in first:
                texts.append(str(first["content"]))
                continue
        if isinstance(completion, dict) and "content" in completion:
            texts.append(str(completion["content"]))
            continue
        texts.append(json.dumps(completion, ensure_ascii=False))
    return texts


def _score_request_info(questions: list[str]) -> float:
    if not questions:
        return -0.5
    return round(min(0.75, 0.25 * len(questions)), 6)


__all__ = [
    "ScientistGRPOConfig",
    "ScientistRewardSuite",
    "ScientistTrainingPlan",
    "preview_scientist_training",
    "train_scientist_grpo",
]
