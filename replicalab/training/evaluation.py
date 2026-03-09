"""Evaluation helpers for baseline and trained Scientist policies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from pydantic import BaseModel, ConfigDict

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


class PolicyComparisonRow(BaseModel):
    """One flattened before/after comparison row."""

    model_config = ConfigDict(extra="forbid")

    label: str
    episode_count: int
    average_reward: float
    average_rounds: float
    agreement_rate: float
    invalid_action_rate: float
    average_invalid_bounded_tool_rate: float
    average_rigor: float
    average_feasibility: float
    average_fidelity: float
    average_parsimony: float
    average_tool_trace_count: float
    average_paper_understanding: float
    average_communication_quality: float


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


def compare_policies(
    *,
    base_url: str,
    policies: Sequence[tuple[str, PolicyFn]],
    cases: Sequence[EvaluationCase],
    transport: str = "rest",
) -> tuple[dict[str, list[EpisodeRecord]], list[PolicyComparisonRow]]:
    """Evaluate multiple policies on the exact same case set."""

    records_by_label: dict[str, list[EpisodeRecord]] = {}
    rows: list[PolicyComparisonRow] = []
    for label, policy_fn in policies:
        records, summary = evaluate_policy(
            base_url=base_url,
            policy_fn=policy_fn,
            cases=cases,
            transport=transport,
        )
        records_by_label[label] = records
        rows.append(
            PolicyComparisonRow(
                label=label,
                **summary.model_dump(mode="json"),
            )
        )
    return records_by_label, rows


__all__ = [
    "EvaluationCase",
    "PolicyComparisonRow",
    "build_default_evaluation_cases",
    "compare_policies",
    "evaluate_policy",
]
