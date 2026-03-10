"""Training and evaluation metrics helpers."""

from __future__ import annotations

from statistics import mean

from pydantic import BaseModel, ConfigDict

from replicalab.config import MAX_COMMUNICATION_BONUS
from replicalab.scoring import score_paper_understanding
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
    invalid_bounded_tool_count: int = 0
    invalid_bounded_tool_rate: float = 0.0
    rigor: float = 0.0
    feasibility: float = 0.0
    fidelity: float = 0.0
    parsimony: float = 1.0
    paper_understanding: float = 0.0
    communication_quality: float = 0.0


class EvaluationSummary(BaseModel):
    """Aggregate metrics for a batch of episodes."""

    model_config = ConfigDict(extra="forbid")

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


def episode_to_metrics(record: EpisodeRecord) -> EpisodeMetrics:
    """Flatten one trajectory into a stable metrics row."""

    invalid_actions = sum(1 for step in record.steps if step.error)
    rounds_used = max(1, record.rounds_used)
    invalid_bounded_tools = _count_invalid_bounded_tools(record.tool_traces)
    tool_trace_count = record.tool_trace_count
    breakdown = record.reward_breakdown
    paper_understanding = _episode_paper_understanding(record)
    communication_quality = _communication_quality(record)

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
        tool_trace_count=tool_trace_count,
        invalid_bounded_tool_count=invalid_bounded_tools,
        invalid_bounded_tool_rate=invalid_bounded_tools / max(1, tool_trace_count),
        rigor=(breakdown.rigor if breakdown is not None else 0.0),
        feasibility=(breakdown.feasibility if breakdown is not None else 0.0),
        fidelity=(breakdown.fidelity if breakdown is not None else 0.0),
        parsimony=(breakdown.parsimony if breakdown is not None else 1.0),
        paper_understanding=paper_understanding,
        communication_quality=communication_quality,
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
            average_invalid_bounded_tool_rate=0.0,
            average_rigor=0.0,
            average_feasibility=0.0,
            average_fidelity=0.0,
            average_parsimony=1.0,
            average_tool_trace_count=0.0,
            average_paper_understanding=0.0,
            average_communication_quality=0.0,
        )

    return EvaluationSummary(
        episode_count=len(metrics),
        average_reward=mean(item.total_reward for item in metrics),
        average_rounds=mean(item.rounds_used for item in metrics),
        agreement_rate=mean(1.0 if item.agreement_reached else 0.0 for item in metrics),
        invalid_action_rate=mean(item.invalid_action_rate for item in metrics),
        average_invalid_bounded_tool_rate=mean(
            item.invalid_bounded_tool_rate for item in metrics
        ),
        average_rigor=mean(item.rigor for item in metrics),
        average_feasibility=mean(item.feasibility for item in metrics),
        average_fidelity=mean(item.fidelity for item in metrics),
        average_parsimony=mean(item.parsimony for item in metrics),
        average_tool_trace_count=mean(item.tool_trace_count for item in metrics),
        average_paper_understanding=mean(item.paper_understanding for item in metrics),
        average_communication_quality=mean(
            item.communication_quality for item in metrics
        ),
    )


def _count_invalid_bounded_tools(traces: list[dict[str, object]]) -> int:
    invalid_count = 0
    for trace in traces:
        status = str(trace.get("status", "") or "").strip().lower()
        error = trace.get("error")
        valid = trace.get("valid")
        if error:
            invalid_count += 1
            continue
        if valid is False:
            invalid_count += 1
            continue
        if status and status not in {"ok", "success", "succeeded", "completed"}:
            invalid_count += 1
    return invalid_count


def _episode_paper_understanding(record: EpisodeRecord) -> float:
    scored_steps = [
        step
        for step in record.steps
        if getattr(step.action.action_type, "value", str(step.action.action_type)) != "accept"
    ]
    if not scored_steps:
        scored_steps = list(record.steps)
    if not scored_steps:
        return 0.0
    return round(
        mean(
            score_paper_understanding(step.observation, step.action)
            for step in scored_steps
        ),
        6,
    )


def _communication_quality(record: EpisodeRecord) -> float:
    breakdown = record.reward_breakdown
    if breakdown is None:
        return 0.0
    if MAX_COMMUNICATION_BONUS <= 0:
        return 0.0
    return round(
        max(0.0, min(1.0, breakdown.communication_bonus / MAX_COMMUNICATION_BONUS)),
        6,
    )


__all__ = [
    "EpisodeMetrics",
    "EvaluationSummary",
    "episode_to_metrics",
    "summarize_episodes",
]
