"""Evaluation helpers for baseline and trained Scientist policies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from replicalab.client import ReplicaLabClient
from replicalab.models import ScientistAction, ScientistObservation
from replicalab.training.metrics import EvaluationSummary, summarize_episodes
from replicalab.training.rollout import EpisodeRecord, RolloutWorker


PolicyFn = Callable[[ScientistObservation], ScientistAction]


@dataclass(frozen=True)
class EvaluationCase:
    seed: int
    scenario: str
    difficulty: str


def build_default_evaluation_cases(
    *,
    seeds: Iterable[int],
    scenarios: Sequence[str] = ("math_reasoning", "ml_benchmark", "finance_trading"),
    difficulties: Sequence[str] = ("easy", "medium", "hard"),
) -> list[EvaluationCase]:
    return [
        EvaluationCase(seed=seed, scenario=scenario, difficulty=difficulty)
        for scenario in scenarios
        for difficulty in difficulties
        for seed in seeds
    ]


def evaluate_policy(
    *,
    base_url: str,
    policy_fn: PolicyFn,
    cases: Sequence[EvaluationCase],
    transport: str = "rest",
) -> tuple[list[EpisodeRecord], EvaluationSummary]:
    """Run a policy through live rollouts and return records plus summary."""

    client = ReplicaLabClient(base_url, transport=transport)
    client.connect()
    try:
        worker = RolloutWorker(client)
        records = [
            worker.rollout(
                policy_fn,
                seed=case.seed,
                scenario=case.scenario,
                difficulty=case.difficulty,
            )
            for case in cases
        ]
    finally:
        client.close()
    return records, summarize_episodes(records)


__all__ = [
    "EvaluationCase",
    "build_default_evaluation_cases",
    "evaluate_policy",
]
