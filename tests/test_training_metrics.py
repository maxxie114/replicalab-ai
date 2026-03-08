"""Tests for training metric summarization helpers."""

from __future__ import annotations

from replicalab.models import RewardBreakdown, ScientistAction, ScientistObservation, StepInfo
from replicalab.training.metrics import episode_to_metrics, summarize_episodes
from replicalab.training.rollout import EpisodeRecord, StepRecord


def _build_step_record(
    error: str | None = None,
    *,
    tool_traces: list[dict[str, object]] | None = None,
) -> StepRecord:
    return StepRecord(
        round_number=0,
        observation=ScientistObservation(
            paper_title="Paper",
            paper_hypothesis="Hypothesis",
            paper_method="Method",
            paper_key_finding="Finding",
            experiment_goal="Goal",
            conversation_history=[],
            current_protocol=None,
            round_number=0,
            max_rounds=6,
        ),
        action=ScientistAction(
            action_type="request_info",
            sample_size=0,
            controls=[],
            technique="",
            duration_days=0,
            required_equipment=[],
            required_reagents=[],
            questions=["What is missing?"],
            rationale="",
        ),
        reward=0.0,
        done=False,
        error=error,
        info=StepInfo(error=error),
        tool_traces=tool_traces or [],
    )


def test_episode_to_metrics_counts_invalid_actions() -> None:
    record = EpisodeRecord(
        seed=11,
        scenario="math_reasoning",
        difficulty="easy",
        episode_id="ep-1",
        steps=[_build_step_record("invalid"), _build_step_record(None)],
        total_reward=1.25,
        reward_breakdown=RewardBreakdown(
            rigor=0.8,
            feasibility=0.9,
            fidelity=0.7,
            parsimony=0.95,
        ),
        verdict="accept",
        agreement_reached=True,
        tool_traces=[
            {"tool": "search_evidence", "status": "ok"},
            {"tool": "run_code_check", "status": "error", "error": "timeout"},
        ],
    )

    metrics = episode_to_metrics(record)

    assert metrics.invalid_action_count == 1
    assert metrics.invalid_action_rate == 0.5
    assert metrics.invalid_bounded_tool_count == 1
    assert metrics.invalid_bounded_tool_rate == 0.5
    assert metrics.agreement_reached is True


def test_summarize_episodes_aggregates_rewards() -> None:
    first = EpisodeRecord(
        seed=1,
        scenario="math_reasoning",
        difficulty="easy",
        episode_id="ep-1",
        steps=[_build_step_record(None)],
        total_reward=2.0,
        reward_breakdown=RewardBreakdown(rigor=0.6, feasibility=0.7, fidelity=0.8),
        verdict="accept",
        agreement_reached=True,
        tool_traces=[{"tool": "search_evidence", "status": "ok"}],
    )
    second = EpisodeRecord(
        seed=2,
        scenario="ml_benchmark",
        difficulty="medium",
        episode_id="ep-2",
        steps=[_build_step_record("invalid")],
        total_reward=0.5,
        reward_breakdown=RewardBreakdown(rigor=0.2, feasibility=0.4, fidelity=0.5),
        verdict="timeout",
        agreement_reached=False,
        tool_traces=[{"tool": "run_code_check", "status": "error"}],
    )

    summary = summarize_episodes([first, second])

    assert summary.episode_count == 2
    assert summary.average_reward == 1.25
    assert 0.0 < summary.invalid_action_rate < 1.0
    assert summary.average_invalid_bounded_tool_rate == 0.5
