"""Lab Manager supervised fine-tuning helpers."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from replicalab.scenarios.templates import Difficulty, TemplateName
from replicalab.training.artifacts import ArtifactLayout, build_run_name, write_json
from replicalab.training.corpus import evidence_pack_version, load_frozen_evidence_packs
from replicalab.training.datasets import (
    DEFAULT_DIFFICULTIES,
    DEFAULT_TEMPLATES,
    build_lab_manager_hf_rows,
)
from replicalab.training.runtime import build_hf_dataset, load_qwen_lora_model, require_module, save_adapter


class LabManagerSFTConfig(BaseModel):
    """Notebook- and Northflank-friendly Lab Manager training config."""

    model_config = ConfigDict(extra="forbid")

    model_name: str = "Qwen/Qwen3-8B"
    max_seq_length: int = 3072
    load_in_4bit: bool = False
    fast_inference: bool = False
    lora_rank: int = 32
    lora_alpha: int = 32
    seed: int = 3407
    templates: list[TemplateName] = Field(default_factory=lambda: list(DEFAULT_TEMPLATES))
    difficulties: list[Difficulty] = Field(default_factory=lambda: list(DEFAULT_DIFFICULTIES))
    train_seeds: list[int] = Field(default_factory=lambda: list(range(16)))
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.05
    lr_scheduler_type: str = "cosine"
    optim: str = "adamw_8bit"
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    logging_steps: int = 10
    save_steps: int = 100
    num_train_epochs: float = 1.0


class LabManagerTrainingPlan(BaseModel):
    """Preview payload saved before training starts."""

    model_config = ConfigDict(extra="forbid")

    run_name: str
    model_name: str
    dataset_size: int
    evidence_pack_version: str
    config: dict[str, object]
    output_dir: str


def preview_lab_manager_training(
    config: LabManagerSFTConfig,
    *,
    layout: ArtifactLayout | None = None,
) -> LabManagerTrainingPlan:
    evidence_packs = load_frozen_evidence_packs()
    rows = build_lab_manager_hf_rows(
        seeds=config.train_seeds,
        templates=config.templates,
        difficulties=config.difficulties,
        evidence_packs=evidence_packs,
    )
    return LabManagerTrainingPlan(
        run_name=(layout.run_name if layout is not None else build_run_name("lab-manager")),
        model_name=config.model_name,
        dataset_size=len(rows),
        evidence_pack_version=evidence_pack_version(evidence_packs),
        config=config.model_dump(mode="json"),
        output_dir=str((layout.run_dir if layout is not None else Path(".")).resolve()),
    )


def train_lab_manager_sft(
    config: LabManagerSFTConfig,
    *,
    layout: ArtifactLayout | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    """Run a Lab Manager SFT job or return a dry-run preview."""

    artifact_layout = layout or ArtifactLayout.create(
        run_name=build_run_name("lab-manager")
    )
    evidence_packs = load_frozen_evidence_packs()
    rows = build_lab_manager_hf_rows(
        seeds=config.train_seeds,
        templates=config.templates,
        difficulties=config.difficulties,
        evidence_packs=evidence_packs,
    )
    plan = preview_lab_manager_training(config, layout=artifact_layout)
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
    text_rows = [
        {
            **row,
            "text": tokenizer.apply_chat_template(
                row["messages"],
                tokenize=False,
                add_generation_prompt=False,
            ),
        }
        for row in rows
    ]
    dataset = build_hf_dataset(text_rows)
    training_args = trl_module.SFTConfig(
        output_dir=str(artifact_layout.checkpoints_dir),
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        lr_scheduler_type=config.lr_scheduler_type,
        optim=config.optim,
        per_device_train_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        num_train_epochs=config.num_train_epochs,
        dataset_text_field="text",
        max_seq_length=config.max_seq_length,
        report_to=[],
        bf16=True,
    )
    trainer = trl_module.SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=training_args,
    )
    trainer.train()
    save_adapter(model, tokenizer, artifact_layout.lab_manager_adapter_dir)
    write_json(
        artifact_layout.reports_dir / "lab_manager_trainer_state.json",
        {"log_history": trainer.state.log_history},
    )
    return {
        "run_name": artifact_layout.run_name,
        "adapter_dir": str(artifact_layout.lab_manager_adapter_dir),
        "dataset_size": len(rows),
    }


__all__ = [
    "LabManagerSFTConfig",
    "LabManagerTrainingPlan",
    "preview_lab_manager_training",
    "train_lab_manager_sft",
]
