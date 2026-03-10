"""Training utilities for ReplicaLab."""

from replicalab.training.artifacts import ArtifactLayout
from replicalab.training.art_openenv import (
    ArtOpenEnvConfig,
    ArtRolloutSummary,
    ArtScenarioSpec,
    ArtTrainingSummary,
    run_art_openenv_training,
)
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
from replicalab.training.local_eval import (
    PaperBalancedEvaluationCase,
    build_local_scientist_policy,
    build_trainable_paper_cases,
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
    "ArtOpenEnvConfig",
    "ArtRolloutSummary",
    "ArtScenarioSpec",
    "ArtTrainingSummary",
    "EpisodeRecord",
    "EvaluationCase",
    "EvaluationSummary",
    "FrozenEvidencePack",
    "LabManagerSFTConfig",
    "LabManagerSFTExample",
    "PaperBalancedEvaluationCase",
    "RolloutWorker",
    "ScientistGRPOConfig",
    "ScientistPromptExample",
    "ScientistRewardSuite",
    "StepRecord",
    "build_default_evaluation_cases",
    "build_lab_manager_sft_examples",
    "build_scientist_prompt_examples",
    "evaluate_policy",
    "build_local_scientist_policy",
    "load_frozen_evidence_packs",
    "preview_lab_manager_training",
    "preview_scientist_training",
    "run_art_openenv_training",
    "summarize_episodes",
    "train_lab_manager_sft",
    "train_scientist_grpo",
    "build_trainable_paper_cases",
]
