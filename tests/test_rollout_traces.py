"""Additional rollout tests for TRN 04 metadata and collection behavior."""

from __future__ import annotations

from replicalab.models import Observation, RewardBreakdown, ScientistAction, StepInfo, StepResult
from replicalab.scenarios import generate_scenario
from replicalab.training.rollout import RolloutWorker


def _scientist_obs():
    return generate_scenario(
        seed=7, template="math_reasoning", difficulty="easy"
    ).scientist_observation


def _accept_action() -> ScientistAction:
    return ScientistAction(
        action_type="accept",
        sample_size=0,
        controls=[],
        technique="",
        duration_days=0,
        required_equipment=[],
        required_reagents=[],
        questions=[],
        rationale="",
    )


class _FakeClient:
    def __init__(self) -> None:
        self.episode_id = "episode-1"
        self._step_count = 0

    def reset(self, *, seed: int, scenario: str, difficulty: str) -> Observation:
        obs = _scientist_obs()
        return Observation(scientist=obs, lab_manager=None)

    def step(self, action: ScientistAction) -> StepResult:
        self._step_count += 1
        obs = _scientist_obs()
        if self._step_count == 1:
            return StepResult(
                observation=Observation(scientist=obs, lab_manager=None),
                reward=0.0,
                done=False,
                info=StepInfo(
                    agreement_reached=False,
                    error=None,
                    round=1,
                    tool_traces=[
                        {
                            "tool": "search_evidence",
                            "status": "ok",
                            "query": "baseline reference",
                        }
                    ],
                ),
            )
        return StepResult(
            observation=Observation(scientist=obs, lab_manager=None),
            reward=3.5,
            done=True,
            info=StepInfo(
                agreement_reached=True,
                error=None,
                reward_breakdown=RewardBreakdown(
                    rigor=0.8,
                    feasibility=0.7,
                    fidelity=0.75,
                ),
                judge_notes="Deterministic terminal note.",
                verdict="accept",
                round=2,
                tool_traces=[
                    {
                        "tool": "run_code_check",
                        "status": "ok",
                        "task_type": "metric_check",
                    }
                ],
            ),
        )


def test_rollout_captures_tool_traces_from_step_info_extras() -> None:
    worker = RolloutWorker(_FakeClient())
    record = worker.rollout(lambda _obs: _accept_action(), seed=11)

    assert record.tool_trace_count == 2
    assert record.steps[0].tool_traces[0]["tool"] == "search_evidence"
    assert record.steps[1].tool_traces[0]["tool"] == "run_code_check"
    assert record.terminal_info is not None


def test_collect_rollouts_returns_one_record_per_seed() -> None:
    worker = RolloutWorker(_FakeClient())
    records = worker.collect_rollouts(
        lambda _obs: _accept_action(),
        seeds=[1, 2, 3],
        scenario="math_reasoning",
        difficulty="easy",
    )

    assert [record.seed for record in records] == [1, 2, 3]
    assert all(record.verdict == "accept" for record in records)
