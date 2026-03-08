"""Training and evaluation metrics helpers."""

from __future__ import annotations

from statistics import mean

from pydantic import BaseModel, ConfigDict

from replicalab.training.rollout import EpisodeRecord


class EpisodeMetrics(BaseModel):
    """Flat metrics row derived from one episode record."""

    model_config = ConfigDict(extra="forbid")

    seed: int
    scenario: str
    difficulty: str
    total_reward: float
    rounds_used: int
    agreement_reached: bool
    verdict: str | None = None
    invalid_action_count: int = 0
    invalid_action_rate: float = 0.0
    tool_trace_count: int = 0
    rigor: float = 0.0
    feasibility: float = 0.0
    fidelity: float = 0.0
    parsimony: float = 1.0


class EvaluationSummary(BaseModel):
    """Aggregate metrics for a batch of episodes."""

    model_config = ConfigDict(extra="forbid")

    episode_count: int
    average_reward: float
    average_rounds: float
    agreement_rate: float
    invalid_action_rate: float
    average_rigor: float
    average_feasibility: float
    average_fidelity: float
    average_parsimony: float
    average_tool_trace_count: float


def episode_to_metrics(record: EpisodeRecord) -> EpisodeMetrics:
    """Flatten one trajectory into a stable metrics row."""

    invalid_actions = sum(1 for step in record.steps if step.error)
    rounds_used = max(1, record.rounds_used)
    breakdown = record.reward_breakdown

    return EpisodeMetrics(
        seed=record.seed,
        scenario=record.scenario,
        difficulty=record.difficulty,
        total_reward=record.total_reward,
        rounds_used=record.rounds_used,
        agreement_reached=record.agreement_reached,
        verdict=record.verdict,
        invalid_action_count=invalid_actions,
        invalid_action_rate=invalid_actions / rounds_used,
        tool_trace_count=record.tool_trace_count,
        rigor=(breakdown.rigor if breakdown is not None else 0.0),
        feasibility=(breakdown.feasibility if breakdown is not None else 0.0),
        fidelity=(breakdown.fidelity if breakdown is not None else 0.0),
        parsimony=(breakdown.parsimony if breakdown is not None else 1.0),
    )


def summarize_episodes(records: list[EpisodeRecord]) -> EvaluationSummary:
    """Aggregate a batch of episode records into summary metrics."""

    metrics = [episode_to_metrics(record) for record in records]
    if not metrics:
        return EvaluationSummary(
            episode_count=0,
            average_reward=0.0,
            average_rounds=0.0,
            agreement_rate=0.0,
            invalid_action_rate=0.0,
            average_rigor=0.0,
            average_feasibility=0.0,
            average_fidelity=0.0,
            average_parsimony=1.0,
            average_tool_trace_count=0.0,
        )

    return EvaluationSummary(
        episode_count=len(metrics),
        average_reward=mean(item.total_reward for item in metrics),
        average_rounds=mean(item.rounds_used for item in metrics),
        agreement_rate=mean(1.0 if item.agreement_reached else 0.0 for item in metrics),
        invalid_action_rate=mean(item.invalid_action_rate for item in metrics),
        average_rigor=mean(item.rigor for item in metrics),
        average_feasibility=mean(item.feasibility for item in metrics),
        average_fidelity=mean(item.fidelity for item in metrics),
        average_parsimony=mean(item.parsimony for item in metrics),
        average_tool_trace_count=mean(item.tool_trace_count for item in metrics),
    )


__all__ = [
    "EpisodeMetrics",
    "EvaluationSummary",
    "episode_to_metrics",
    "summarize_episodes",
]
