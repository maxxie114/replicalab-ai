"""Client module tests — TRN 13.

Tests cover ReplicaLabClient with both REST and WebSocket transports
against the real FastAPI test server.
"""

from __future__ import annotations

import contextlib
import json
import threading
import time

import pytest
import uvicorn

from replicalab.client import ReplicaLabClient
from replicalab.models import (
    Observation,
    ScientistAction,
    StepResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _propose_action(obs: Observation) -> ScientistAction:
    """Build a valid propose_protocol action from the observation."""
    from replicalab.scenarios import generate_scenario

    pack = generate_scenario(seed=42, template="math_reasoning", difficulty="easy")
    lab = pack.lab_manager_observation
    spec = pack.hidden_reference_spec
    return ScientistAction(
        action_type="propose_protocol",
        sample_size=10,
        controls=["baseline", "ablation"],
        technique=spec.summary[:60] if spec.summary else "replication_plan",
        duration_days=max(1, min(2, lab.time_limit_days)),
        required_equipment=list(lab.equipment_available[:1]) if lab.equipment_available else [],
        required_reagents=list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else [],
        questions=[],
        rationale=(
            f"Plan addresses: {', '.join(spec.required_elements[:2])}. "
            f"Target metric: {spec.target_metric}. "
            f"Target value: {spec.target_value}. "
            "Stay within budget and schedule."
        ),
    )


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


# ---------------------------------------------------------------------------
# REST transport tests (uses httpx directly against TestClient-proxied app)
# ---------------------------------------------------------------------------

# We spin up a real uvicorn server on a random port for both transports
# to keep things realistic and test the actual HTTP/WS paths.

_TEST_PORT = 18765


@pytest.fixture(scope="module")
def live_server():
    """Start a live uvicorn server for the test module."""
    from server.app import app

    config = uvicorn.Config(app, host="127.0.0.1", port=_TEST_PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait until server is ready
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


# ---------------------------------------------------------------------------
# REST transport
# ---------------------------------------------------------------------------


class TestRestConnect:
    """connect() over REST verifies server health."""

    def test_connect_succeeds(self, live_server: str) -> None:
        client = ReplicaLabClient(live_server, transport="rest")
        client.connect()
        assert client.connected
        client.close()

    def test_connect_bad_url_raises(self) -> None:
        client = ReplicaLabClient("http://127.0.0.1:19999", transport="rest", timeout=1.0)
        with pytest.raises(Exception):
            client.connect()


class TestRestReset:
    """reset() over REST."""

    def test_reset_returns_observation(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="rest") as client:
            obs = client.reset(seed=42, scenario="math_reasoning", difficulty="easy")
            assert isinstance(obs, Observation)
            assert obs.scientist is not None
            assert obs.scientist.paper_title
            assert obs.lab_manager is not None
            assert obs.lab_manager.budget_total > 0

    def test_reset_sets_session_and_episode_id(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="rest") as client:
            client.reset(seed=1)
            assert client.session_id is not None
            assert client.episode_id is not None

    def test_reset_reuses_session(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="rest") as client:
            client.reset(seed=1)
            sid1 = client.session_id
            ep1 = client.episode_id
            client.reset(seed=2)
            assert client.session_id == sid1
            assert client.episode_id != ep1


class TestRestStep:
    """step() over REST."""

    def test_step_returns_step_result(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="rest") as client:
            obs = client.reset(seed=42)
            action = _propose_action(obs)
            result = client.step(action)
            assert isinstance(result, StepResult)
            assert result.done is False
            assert result.observation is not None

    def test_step_before_reset_raises(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="rest") as client:
            with pytest.raises(RuntimeError, match="reset"):
                client.step(_accept_action())

    def test_full_episode_propose_accept(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="rest") as client:
            obs = client.reset(seed=42)
            action = _propose_action(obs)
            result1 = client.step(action)
            assert result1.done is False

            result2 = client.step(_accept_action())
            assert result2.done is True
            assert result2.reward > 0.0
            assert result2.info.agreement_reached is True
            assert result2.info.verdict == "accept"
            assert result2.info.reward_breakdown is not None
            assert 0.0 <= result2.info.reward_breakdown.rigor <= 1.0


class TestRestReplay:
    """replay() over REST."""

    def test_replay_after_episode(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="rest") as client:
            obs = client.reset(seed=42)
            action = _propose_action(obs)
            client.step(action)
            client.step(_accept_action())

            episode_id = client.episode_id
            assert episode_id is not None
            replay = client.replay(episode_id)
            assert replay.agreement_reached is True
            assert replay.total_reward > 0.0
            assert replay.verdict == "accept"


class TestRestContextManager:
    """Context manager cleans up on exit."""

    def test_context_manager_closes(self, live_server: str) -> None:
        client = ReplicaLabClient(live_server, transport="rest")
        with client:
            assert client.connected
            client.reset(seed=1)
        assert not client.connected


# ---------------------------------------------------------------------------
# WebSocket transport
# ---------------------------------------------------------------------------


class TestWsConnect:
    """connect() over WebSocket."""

    def test_connect_succeeds(self, live_server: str) -> None:
        client = ReplicaLabClient(live_server, transport="websocket")
        client.connect()
        assert client.connected
        client.close()

    def test_connect_bad_url_raises(self) -> None:
        client = ReplicaLabClient("http://127.0.0.1:19999", transport="websocket", timeout=1.0)
        with pytest.raises(Exception):
            client.connect()


class TestWsReset:
    """reset() over WebSocket."""

    def test_reset_returns_observation(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="websocket") as client:
            obs = client.reset(seed=42, scenario="math_reasoning", difficulty="easy")
            assert isinstance(obs, Observation)
            assert obs.scientist is not None
            assert obs.scientist.paper_title
            assert obs.lab_manager is not None
            assert obs.lab_manager.budget_total > 0

    def test_reset_sets_episode_id(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="websocket") as client:
            client.reset(seed=42)
            assert client.episode_id is not None

    def test_ws_session_id_is_none(self, live_server: str) -> None:
        """WebSocket transport has no explicit session_id."""
        with ReplicaLabClient(live_server, transport="websocket") as client:
            client.reset(seed=42)
            assert client.session_id is None


class TestWsStep:
    """step() over WebSocket."""

    def test_step_returns_step_result(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="websocket") as client:
            obs = client.reset(seed=42)
            action = _propose_action(obs)
            result = client.step(action)
            assert isinstance(result, StepResult)
            assert result.done is False
            assert result.observation is not None

    def test_full_episode_propose_accept(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="websocket") as client:
            obs = client.reset(seed=42)
            action = _propose_action(obs)
            result1 = client.step(action)
            assert result1.done is False

            result2 = client.step(_accept_action())
            assert result2.done is True
            assert result2.reward > 0.0
            assert result2.info.agreement_reached is True
            assert result2.info.verdict == "accept"
            assert result2.info.reward_breakdown is not None
            assert 0.0 <= result2.info.reward_breakdown.rigor <= 1.0

    def test_semantic_invalid_action_step_ok_with_error(self, live_server: str) -> None:
        """Semantically invalid action → step result with info.error, not crash."""
        with ReplicaLabClient(live_server, transport="websocket") as client:
            client.reset(seed=42)
            bad_action = ScientistAction(
                action_type="propose_protocol",
                sample_size=5,
                controls=["baseline"],
                technique="some technique",
                duration_days=999,
                required_equipment=[],
                required_reagents=[],
                questions=[],
                rationale="Duration is impossibly long.",
            )
            result = client.step(bad_action)
            assert result.done is False
            assert result.info.error is not None
            assert "Validation errors" in result.info.error


class TestWsContextManager:
    """Context manager cleans up on exit."""

    def test_context_manager_closes(self, live_server: str) -> None:
        client = ReplicaLabClient(live_server, transport="websocket")
        with client:
            assert client.connected
            client.reset(seed=1)
        assert not client.connected


class TestWsUnsupported:
    """state() and replay() raise NotImplementedError on WS transport."""

    def test_state_not_supported(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="websocket") as client:
            client.reset(seed=42)
            with pytest.raises(NotImplementedError):
                client.state()

    def test_replay_not_supported(self, live_server: str) -> None:
        with ReplicaLabClient(live_server, transport="websocket") as client:
            with pytest.raises(NotImplementedError):
                client.replay("some-id")


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------


class TestConstructor:
    """Transport selection and validation."""

    def test_unknown_transport_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown transport"):
            ReplicaLabClient(transport="grpc")

    def test_not_connected_raises_on_reset(self) -> None:
        client = ReplicaLabClient(transport="rest")
        with pytest.raises(RuntimeError, match="not connected"):
            client.reset(seed=1)

    def test_default_transport_is_websocket(self) -> None:
        client = ReplicaLabClient()
        # Check internal transport type
        assert type(client._transport).__name__ == "_WsTransport"
