"""Training rollout worker for ReplicaLab (TRN 04).

Builds on the completed client wrapper to collect full episode
trajectories (observations, actions, rewards, judge output, and
bounded-tool traces when present) for RL training.

Notebooks and training scripts use ``RolloutWorker`` instead of
writing their own reset→step loops::

    from replicalab.client import ReplicaLabClient
    from replicalab.training.rollout import RolloutWorker

    client = ReplicaLabClient("http://localhost:7860", transport="rest")
    client.connect()
    worker = RolloutWorker(client)

    record = worker.rollout(policy_fn, seed=42)
    print(record.total_reward, record.verdict, record.rounds_used)
    client.close()

The ``policy_fn`` callable receives a ``ScientistObservation`` and
returns a ``ScientistAction``.  The baseline from
``replicalab.agents`` can be used directly::

    from replicalab.agents import build_baseline_scientist_action
    record = worker.rollout(build_baseline_scientist_action, seed=1)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional

from replicalab.client import ReplicaLabClient
from replicalab.config import DEFAULT_DIFFICULTY, DEFAULT_SCENARIO_TEMPLATE
from replicalab.models import (
    Observation,
    RewardBreakdown,
    ScientistAction,
    ScientistObservation,
    StepInfo,
    StepResult,
)


@dataclass
class StepRecord:
    """One step in an episode trajectory."""

    round_number: int
    observation: ScientistObservation
    action: ScientistAction
    reward: float
    done: bool
    error: Optional[str] = None
    info: Optional[StepInfo] = None
    tool_traces: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class EpisodeRecord:
    """Complete episode trajectory with judge output."""

    seed: int
    scenario: str
    difficulty: str
    episode_id: Optional[str]
    steps: list[StepRecord] = field(default_factory=list)
    total_reward: float = 0.0
    reward_breakdown: Optional[RewardBreakdown] = None
    judge_notes: Optional[str] = None
    verdict: Optional[str] = None
    agreement_reached: bool = False
    tool_traces: list[dict[str, Any]] = field(default_factory=list)
    terminal_info: Optional[StepInfo] = None

    @property
    def rounds_used(self) -> int:
        return len(self.steps)

    @property
    def succeeded(self) -> bool:
        return self.agreement_reached and self.total_reward > 0.0

    @property
    def tool_trace_count(self) -> int:
        return len(self.tool_traces)


# Type alias for the policy callable
PolicyFn = Callable[[ScientistObservation], ScientistAction]


class RolloutWorker:
    """Runs single episodes through the client and collects trajectories.

    Parameters
    ----------
    client:
        A connected ``ReplicaLabClient`` instance.
    max_steps:
        Safety cap to prevent infinite loops. Defaults to 20
        (well above MAX_ROUNDS=6).
    """

    def __init__(
        self,
        client: ReplicaLabClient,
        *,
        max_steps: int = 20,
    ) -> None:
        self._client = client
        self._max_steps = max_steps

    def rollout(
        self,
        policy_fn: PolicyFn,
        seed: int = 0,
        scenario: str = DEFAULT_SCENARIO_TEMPLATE,
        difficulty: str = DEFAULT_DIFFICULTY,
    ) -> EpisodeRecord:
        """Run one full episode and return the trajectory.

        Parameters
        ----------
        policy_fn:
            Callable that maps ``ScientistObservation`` to ``ScientistAction``.
        seed, scenario, difficulty:
            Passed to ``client.reset()``.

        Returns
        -------
        EpisodeRecord with all steps, reward, and judge output.
        """
        obs = self._client.reset(seed=seed, scenario=scenario, difficulty=difficulty)
        episode_id = self._client.episode_id

        record = EpisodeRecord(
            seed=seed,
            scenario=scenario,
            difficulty=difficulty,
            episode_id=episode_id,
        )

        scientist_obs = obs.scientist
        if scientist_obs is None:
            raise RuntimeError("Reset returned no scientist observation")

        for step_idx in range(self._max_steps):
            action = policy_fn(scientist_obs)

            result: StepResult = self._client.step(action)
            tool_traces = _extract_tool_traces(result.info)

            step = StepRecord(
                round_number=step_idx,
                observation=scientist_obs,
                action=action,
                reward=result.reward,
                done=result.done,
                error=result.info.error,
                info=result.info.model_copy(deep=True),
                tool_traces=tool_traces,
            )
            record.steps.append(step)
            record.tool_traces.extend(tool_traces)
            record.total_reward = round(record.total_reward + result.reward, 6)

            if result.done:
                record.reward_breakdown = result.info.reward_breakdown
                record.judge_notes = result.info.judge_notes
                record.verdict = result.info.verdict
                record.agreement_reached = result.info.agreement_reached
                record.terminal_info = result.info.model_copy(deep=True)
                break

            # Advance to next observation
            if result.observation and result.observation.scientist:
                scientist_obs = result.observation.scientist
            else:
                raise RuntimeError(
                    f"Step {step_idx} returned no scientist observation "
                    f"but done=False"
                )

        return record

    def collect_rollouts(
        self,
        policy_fn: PolicyFn,
        seeds: Iterable[int],
        *,
        scenario: str = DEFAULT_SCENARIO_TEMPLATE,
        difficulty: str = DEFAULT_DIFFICULTY,
    ) -> list[EpisodeRecord]:
        """Collect a deterministic batch of episode trajectories.

        This is the notebook-facing rollout collection loop used by TRN 04.
        """

        return [
            self.rollout(
                policy_fn,
                seed=seed,
                scenario=scenario,
                difficulty=difficulty,
            )
            for seed in seeds
        ]


def _extract_tool_traces(info: StepInfo) -> list[dict[str, Any]]:
    """Read bounded tool traces from StepInfo extras when present."""

    extras = getattr(info, "model_extra", None) or {}
    raw = extras.get("tool_traces") or extras.get("bounded_tool_traces") or []
    if not isinstance(raw, list):
        return []
    traces: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            traces.append(dict(item))
    return traces
