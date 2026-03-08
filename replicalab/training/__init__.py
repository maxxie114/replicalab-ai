"""Training utilities for ReplicaLab."""

from replicalab.training.artifacts import ArtifactLayout
from replicalab.training.corpus import FrozenEvidencePack, load_frozen_evidence_packs
from replicalab.training.datasets import (
    LabManagerSFTExample,
    ScientistPromptExample,
    build_lab_manager_sft_examples,
    build_scientist_prompt_examples,
)
from replicalab.training.evaluation import (
    EvaluationCase,
    build_default_evaluation_cases,
    evaluate_policy,
)
from replicalab.training.lab_manager_sft import (
    LabManagerSFTConfig,
    preview_lab_manager_training,
    train_lab_manager_sft,
)
from replicalab.training.metrics import EvaluationSummary, summarize_episodes
from replicalab.training.rollout import EpisodeRecord, RolloutWorker, StepRecord
from replicalab.training.scientist_grpo import (
    ScientistGRPOConfig,
    ScientistRewardSuite,
    preview_scientist_training,
    train_scientist_grpo,
)

__all__ = [
    "ArtifactLayout",
    "EpisodeRecord",
    "EvaluationCase",
    "EvaluationSummary",
    "FrozenEvidencePack",
    "LabManagerSFTConfig",
    "LabManagerSFTExample",
    "RolloutWorker",
    "ScientistGRPOConfig",
    "ScientistPromptExample",
    "ScientistRewardSuite",
    "StepRecord",
    "build_default_evaluation_cases",
    "build_lab_manager_sft_examples",
    "build_scientist_prompt_examples",
    "evaluate_policy",
    "load_frozen_evidence_packs",
    "preview_lab_manager_training",
    "preview_scientist_training",
    "summarize_episodes",
    "train_lab_manager_sft",
    "train_scientist_grpo",
]
