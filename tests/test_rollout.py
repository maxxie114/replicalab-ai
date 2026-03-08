"""Tests for replicalab.training.rollout — TRN 03.

Verifies that RolloutWorker can run full episodes through the client,
collect trajectories, and surface judge output for RL training.
"""

from __future__ import annotations

import threading
import time

import pytest
import uvicorn

from replicalab.agents import build_baseline_scientist_action
from replicalab.client import ReplicaLabClient
from replicalab.models import RewardBreakdown, ScientistAction, ScientistObservation
from replicalab.training.rollout import EpisodeRecord, RolloutWorker, StepRecord


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TEST_PORT = 18766


@pytest.fixture(scope="module")
def live_server():
    """Start a live uvicorn server for rollout tests."""
    from server.app import app

    config = uvicorn.Config(app, host="127.0.0.1", port=_TEST_PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    import httpx

    for _ in range(50):
        try:
            resp = httpx.get(f"http://127.0.0.1:{_TEST_PORT}/health", timeout=1.0)
            if resp.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(0.1)
    else:
        pytest.fail("Live server did not start in time")

    yield f"http://127.0.0.1:{_TEST_PORT}"

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture()
def client(live_server: str):
    """Provide a connected REST client."""
    c = ReplicaLabClient(live_server, transport="rest")
    c.connect()
    yield c
    c.close()


# ---------------------------------------------------------------------------
# Full episode via baseline policy
# ---------------------------------------------------------------------------


class TestBaselineRollout:
    """Run real episodes with the deterministic baseline policy."""

    def test_rollout_completes(self, client: ReplicaLabClient) -> None:
        """Baseline policy finishes an episode start-to-finish."""
        worker = RolloutWorker(client)
        record = worker.rollout(build_baseline_scientist_action, seed=42)

        assert isinstance(record, EpisodeRecord)
        assert record.rounds_used > 0
        assert record.verdict is not None

    def test_rollout_returns_reward(self, client: ReplicaLabClient) -> None:
        """Terminal episode has a real total reward."""
        worker = RolloutWorker(client)
        record = worker.rollout(build_baseline_scientist_action, seed=42)

        assert record.total_reward > 0.0
        assert record.agreement_reached is True
        assert record.succeeded is True

    def test_rollout_returns_reward_breakdown(
        self, client: ReplicaLabClient
    ) -> None:
        """Reward breakdown has rigor, feasibility, fidelity in [0,1]."""
        worker = RolloutWorker(client)
        record = worker.rollout(build_baseline_scientist_action, seed=42)

        rb = record.reward_breakdown
        assert rb is not None
        assert isinstance(rb, RewardBreakdown)
        assert 0.0 <= rb.rigor <= 1.0
        assert 0.0 <= rb.feasibility <= 1.0
        assert 0.0 <= rb.fidelity <= 1.0

    def test_rollout_returns_judge_notes(
        self, client: ReplicaLabClient
    ) -> None:
        """Judge notes and verdict are populated."""
        worker = RolloutWorker(client)
        record = worker.rollout(build_baseline_scientist_action, seed=42)

        assert record.judge_notes is not None
        assert len(record.judge_notes) > 0
        assert record.verdict in ("accept", "timeout", "no_agreement")

    def test_rollout_steps_have_observations(
        self, client: ReplicaLabClient
    ) -> None:
        """Each step record contains the scientist observation and action."""
        worker = RolloutWorker(client)
        record = worker.rollout(build_baseline_scientist_action, seed=42)

        for step in record.steps:
            assert isinstance(step, StepRecord)
            assert isinstance(step.observation, ScientistObservation)
            assert isinstance(step.action, ScientistAction)

    def test_rollout_episode_id_set(self, client: ReplicaLabClient) -> None:
        """Episode ID is captured from the client."""
        worker = RolloutWorker(client)
        record = worker.rollout(build_baseline_scientist_action, seed=42)

        assert record.episode_id is not None
        assert len(record.episode_id) > 0


# ---------------------------------------------------------------------------
# Determinism and configuration
# ---------------------------------------------------------------------------


class TestRolloutConfig:
    """Configuration, determinism, and edge cases."""

    def test_rollout_is_deterministic(self, client: ReplicaLabClient) -> None:
        """Same seed → same reward and verdict."""
        worker = RolloutWorker(client)

        r1 = worker.rollout(build_baseline_scientist_action, seed=99)
        r2 = worker.rollout(build_baseline_scientist_action, seed=99)

        assert r1.total_reward == r2.total_reward
        assert r1.verdict == r2.verdict
        assert r1.rounds_used == r2.rounds_used

    def test_different_seeds_produce_different_episodes(
        self, client: ReplicaLabClient
    ) -> None:
        """Different seeds may produce different episode IDs."""
        worker = RolloutWorker(client)

        r1 = worker.rollout(build_baseline_scientist_action, seed=1)
        r2 = worker.rollout(build_baseline_scientist_action, seed=2)

        assert r1.episode_id != r2.episode_id

    def test_rollout_across_scenarios(self, client: ReplicaLabClient) -> None:
        """Rollout works for all 3 scenario families."""
        worker = RolloutWorker(client)

        for template in ("math_reasoning", "ml_benchmark", "finance_trading"):
            record = worker.rollout(
                build_baseline_scientist_action,
                seed=42,
                scenario=template,
                difficulty="easy",
            )
            assert record.rounds_used > 0
            assert record.verdict is not None

    def test_rollout_metadata_matches_input(
        self, client: ReplicaLabClient
    ) -> None:
        """EpisodeRecord captures the seed, scenario, and difficulty."""
        worker = RolloutWorker(client)
        record = worker.rollout(
            build_baseline_scientist_action,
            seed=77,
            scenario="finance_trading",
            difficulty="medium",
        )

        assert record.seed == 77
        assert record.scenario == "finance_trading"
        assert record.difficulty == "medium"

    def test_max_steps_cap(self, client: ReplicaLabClient) -> None:
        """max_steps prevents infinite loops even with a bad policy."""
        def _always_propose(obs: ScientistObservation) -> ScientistAction:
            return ScientistAction(
                action_type="propose_protocol",
                sample_size=5,
                controls=["baseline"],
                technique="method",
                duration_days=1,
                required_equipment=[],
                required_reagents=[],
                questions=[],
                rationale="Repeating proposal every round.",
            )

        worker = RolloutWorker(client, max_steps=3)
        record = worker.rollout(_always_propose, seed=42)

        assert record.rounds_used <= 3


# ---------------------------------------------------------------------------
# Error path
# ---------------------------------------------------------------------------


class TestRolloutErrors:
    """Error surfacing from env through the rollout."""

    def test_validation_error_captured_in_step(
        self, client: ReplicaLabClient
    ) -> None:
        """If the policy produces a semantically invalid action,
        info.error is captured in the step record."""
        call_count = 0

        def _bad_then_accept(obs: ScientistObservation) -> ScientistAction:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call: invalid duration
                return ScientistAction(
                    action_type="propose_protocol",
                    sample_size=5,
                    controls=["baseline"],
                    technique="method",
                    duration_days=999,
                    required_equipment=[],
                    required_reagents=[],
                    questions=[],
                    rationale="Duration is impossibly long.",
                )
            # After that: use baseline to finish
            return build_baseline_scientist_action(obs)

        worker = RolloutWorker(client)
        record = worker.rollout(_bad_then_accept, seed=42)

        # First step should have captured the validation error
        assert record.steps[0].error is not None
        assert "Validation" in record.steps[0].error
