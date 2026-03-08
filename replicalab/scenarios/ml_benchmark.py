"""Machine learning benchmark scenario templates."""

from __future__ import annotations

import random
from typing import Any

from replicalab.config import MAX_ROUNDS


def build_ml_benchmark_template(rng: random.Random) -> dict[str, Any]:
    cases = [
        {
            "domain_id": "machine_learning",
            "paper_title": "Reproducing an AG News TinyBERT baseline",
            "paper_hypothesis": "A distilled model can match the published accuracy within the stated compute budget.",
            "paper_method": "Fine-tune TinyBERT on AG News with the published split, tokenizer, and evaluation script.",
            "paper_key_finding": "The baseline is accepted only if the held-out accuracy is within one point of the target.",
            "task_summary": "Plan an ML benchmark replication for AG News classification with strict GPU and deadline limits.",
            "success_criteria": [
                "Use the published train-validation-test split.",
                "Report held-out accuracy with the same metric definition as the paper.",
                "Fit the full plan within the available GPU budget and time window.",
            ],
            "reference_summary": "A valid plan keeps the published split and evaluation metric while staying inside the compute budget.",
            "required_elements": [
                "published data split",
                "matching tokenizer family",
                "held-out accuracy evaluation",
                "run logging",
            ],
            "flexible_elements": [
                "batch size",
                "learning-rate schedule",
                "checkpoint cadence",
            ],
            "target_metric": "held_out_accuracy",
            "target_value": "within one point of the reported AG News baseline",
            "constraints": [
                {
                    "key": "gpu_hours",
                    "label": "Maximum GPU budget",
                    "quantity": 8,
                    "unit": "gpu_hours",
                    "comparator": "<=",
                    "hard": True,
                    "details": "The full run must fit within eight GPU-hours.",
                },
                {
                    "key": "deadline_days",
                    "label": "Replication deadline",
                    "quantity": 4,
                    "unit": "days",
                    "comparator": "<=",
                    "hard": True,
                    "details": "The benchmark must be reproduced within four days.",
                },
                {
                    "key": "evaluation_policy",
                    "label": "Evaluation policy",
                    "quantity": None,
                    "unit": None,
                    "comparator": "=",
                    "hard": True,
                    "details": "Use only the held-out split; no test-set peeking.",
                },
            ],
            "resources": [
                {
                    "key": "gpu_node",
                    "label": "A100 GPU node",
                    "quantity": 1,
                    "unit": "node",
                    "available": True,
                    "category": "compute",
                    "details": "Reserved for one benchmark run at a time.",
                },
                {
                    "key": "dataset_mirror",
                    "label": "AG News dataset mirror",
                    "quantity": 1,
                    "unit": "mirror",
                    "available": True,
                    "category": "data",
                    "details": "Local mirror with the published split manifest.",
                },
                {
                    "key": "tracking_tool",
                    "label": "Experiment tracking workspace",
                    "quantity": 1,
                    "unit": "workspace",
                    "available": True,
                    "category": "tool",
                    "details": "Captures configs, metrics, and artifacts.",
                },
            ],
            "allowed_substitutions": [
                {
                    "original": "full training schedule",
                    "alternative": "shorter schedule with early stopping",
                    "condition": "Use when the GPU budget is tight.",
                    "tradeoff": "The plan must justify why the metric remains trustworthy.",
                },
                {
                    "original": "large batch size",
                    "alternative": "smaller batch size with accumulation",
                    "condition": "Use when the node has limited memory.",
                    "tradeoff": "Training takes longer and must still fit the deadline.",
                },
            ],
            "budget_total": 1800.0,
            "staff_count": 2,
            "time_limit_days": 4,
            "max_rounds": MAX_ROUNDS,
        },
        {
            "domain_id": "machine_learning",
            "paper_title": "Reproducing a CIFAR-10 ResNet-18 baseline",
            "paper_hypothesis": "The reported top-1 accuracy is reachable with the stated data pipeline and a smaller tuning budget.",
            "paper_method": "Train ResNet-18 on CIFAR-10 with the published augmentation recipe and evaluation checkpoint.",
            "paper_key_finding": "The baseline is accepted only if the final accuracy and training recipe are reproducible.",
            "task_summary": "Plan a CIFAR-10 benchmark replication with limited compute, strict evaluation rules, and one reviewer pass.",
            "success_criteria": [
                "Use the published augmentation recipe or justify a compatible substitution.",
                "Keep evaluation isolated from any tuning loop.",
                "Log all seeds, configs, and final metrics for reproducibility.",
            ],
            "reference_summary": "A valid plan preserves the published augmentation and evaluation rules while logging every run.",
            "required_elements": [
                "published augmentation recipe",
                "fixed evaluation checkpoint",
                "seed logging",
                "final metric report",
            ],
            "flexible_elements": [
                "optimizer implementation",
                "checkpoint interval",
                "data-loader worker count",
            ],
            "target_metric": "top1_accuracy",
            "target_value": "within one point of the CIFAR-10 baseline",
            "constraints": [
                {
                    "key": "gpu_hours",
                    "label": "Maximum GPU budget",
                    "quantity": 10,
                    "unit": "gpu_hours",
                    "comparator": "<=",
                    "hard": True,
                    "details": "The benchmark must fit within ten GPU-hours.",
                },
                {
                    "key": "deadline_days",
                    "label": "Replication deadline",
                    "quantity": 5,
                    "unit": "days",
                    "comparator": "<=",
                    "hard": True,
                    "details": "The plan must finish inside the review window.",
                },
                {
                    "key": "review_passes",
                    "label": "Required review passes",
                    "quantity": 1,
                    "unit": "pass",
                    "comparator": ">=",
                    "hard": False,
                    "details": "A teammate should review the config before launch.",
                },
            ],
            "resources": [
                {
                    "key": "gpu_node",
                    "label": "L40S GPU node",
                    "quantity": 1,
                    "unit": "node",
                    "available": True,
                    "category": "compute",
                    "details": "Shared node with moderate queue pressure.",
                },
                {
                    "key": "dataset_archive",
                    "label": "CIFAR-10 dataset archive",
                    "quantity": 1,
                    "unit": "archive",
                    "available": True,
                    "category": "data",
                    "details": "Local archive with checksum verification.",
                },
                {
                    "key": "reviewer",
                    "label": "Benchmark reviewer",
                    "quantity": 1,
                    "unit": "reviewer",
                    "available": True,
                    "category": "personnel",
                    "details": "Can review the config once before training.",
                },
            ],
            "allowed_substitutions": [
                {
                    "original": "full epoch schedule",
                    "alternative": "reduced epoch schedule with checkpoint comparison",
                    "condition": "Use if queue time or GPU budget becomes tight.",
                    "tradeoff": "Needs a clear explanation for any metric gap.",
                }
            ],
            "budget_total": 2100.0,
            "staff_count": 2,
            "time_limit_days": 5,
            "max_rounds": MAX_ROUNDS,
        },
    ]
    return rng.choice(cases)
