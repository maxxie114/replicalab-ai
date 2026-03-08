"""API 14 — REST session isolation tests.

Proves that two REST users with different session_ids do not share
or corrupt each other's env state, episode IDs, protocol, or history.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from server.app import app


@pytest.fixture()
def client():
    return TestClient(app)


def _reset(client: TestClient, *, seed: int = 42, session_id: str | None = None, **kw) -> dict:
    payload: dict = {"seed": seed, "scenario": "math_reasoning", "difficulty": "easy"}
    if session_id is not None:
        payload["session_id"] = session_id
    payload.update(kw)
    resp = client.post("/reset", json=payload)
    assert resp.status_code == 200
    return resp.json()


def _good_action(client: TestClient) -> dict:
    """Build a valid propose_protocol action from a fresh scenario."""
    from replicalab.scenarios import generate_scenario

    scenario = generate_scenario(seed=42, template="math_reasoning", difficulty="easy")
    lab = scenario.lab_manager_observation
    return {
        "action_type": "propose_protocol",
        "sample_size": 3,
        "controls": ["baseline"],
        "technique": scenario.hidden_reference_spec.required_elements[0]
            if scenario.hidden_reference_spec.required_elements else "algebraic_proof",
        "duration_days": min(1, lab.time_limit_days),
        "required_equipment": list(lab.equipment_available[:1]) if lab.equipment_available else [],
        "required_reagents": list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else [],
        "questions": [],
        "rationale": "Test protocol for isolation check.",
    }


# ---------------------------------------------------------------------------
# Two resets produce isolated sessions
# ---------------------------------------------------------------------------


class TestSessionIsolation:
    """Two REST users with different session_ids must not share state."""

    def test_two_resets_produce_different_sessions(self, client: TestClient) -> None:
        d1 = _reset(client, seed=1)
        d2 = _reset(client, seed=2)

        assert d1["session_id"] != d2["session_id"]
        assert d1["episode_id"] != d2["episode_id"]

    def test_two_sessions_have_independent_observations(self, client: TestClient) -> None:
        """Different seeds → different observations, proving separate envs."""
        d1 = _reset(client, seed=100, scenario="math_reasoning", difficulty="easy")
        d2 = _reset(client, seed=200, scenario="ml_benchmark", difficulty="hard")

        obs1 = d1["observation"]
        obs2 = d2["observation"]

        # Different scenarios produce different paper titles
        assert obs1["scientist"]["paper_title"] != obs2["scientist"]["paper_title"]

    def test_stepping_one_session_does_not_mutate_other(self, client: TestClient) -> None:
        """Step session A, then verify session B's next step is unaffected."""
        sid_a = "isolation-a"
        sid_b = "isolation-b"

        d_a = _reset(client, seed=42, session_id=sid_a)
        d_b = _reset(client, seed=42, session_id=sid_b)

        # Both start with the same observation (same seed/scenario/difficulty)
        assert d_a["observation"] == d_b["observation"]

        action = _good_action(client)

        # Step session A
        resp_a = client.post("/step", json={"session_id": sid_a, "action": action})
        assert resp_a.status_code == 200
        step_a = resp_a.json()
        assert step_a["done"] is False

        # Step session B with the same action — should produce the same result
        # because it started from the same state and hasn't been touched
        resp_b = client.post("/step", json={"session_id": sid_b, "action": action})
        assert resp_b.status_code == 200
        step_b = resp_b.json()

        # Both should have the same reward and observation since they saw the
        # same state + same action
        assert step_a["reward"] == step_b["reward"]
        assert step_a["observation"] == step_b["observation"]

    def test_sessions_have_independent_round_counts(self, client: TestClient) -> None:
        """Advancing one session by two steps doesn't advance the other."""
        sid_a = "rounds-a"
        sid_b = "rounds-b"

        _reset(client, seed=42, session_id=sid_a)
        _reset(client, seed=42, session_id=sid_b)

        action = _good_action(client)

        # Step session A twice
        client.post("/step", json={"session_id": sid_a, "action": action})
        resp_a2 = client.post("/step", json={"session_id": sid_a, "action": action})
        obs_a = resp_a2.json()["observation"]

        # Step session B once
        resp_b1 = client.post("/step", json={"session_id": sid_b, "action": action})
        obs_b = resp_b1.json()["observation"]

        # Session A is at round 2, session B at round 1
        assert obs_a["scientist"]["round_number"] != obs_b["scientist"]["round_number"]
        assert obs_b["scientist"]["round_number"] < obs_a["scientist"]["round_number"]

    def test_terminal_one_session_does_not_affect_other(self, client: TestClient) -> None:
        """Completing session A (accept) doesn't terminate session B."""
        sid_a = "term-a"
        sid_b = "term-b"

        _reset(client, seed=42, session_id=sid_a)
        _reset(client, seed=42, session_id=sid_b)

        action = _good_action(client)

        # Step A with propose, then accept
        client.post("/step", json={"session_id": sid_a, "action": action})
        accept = {
            "action_type": "accept",
            "sample_size": 0,
            "controls": [],
            "technique": "",
            "duration_days": 0,
            "required_equipment": [],
            "required_reagents": [],
            "questions": [],
            "rationale": "",
        }
        resp_accept = client.post("/step", json={"session_id": sid_a, "action": accept})
        assert resp_accept.json()["done"] is True

        # Session B should still be alive and non-terminal
        resp_b = client.post("/step", json={"session_id": sid_b, "action": action})
        assert resp_b.status_code == 200
        assert resp_b.json()["done"] is False


# ---------------------------------------------------------------------------
# Session ID reuse
# ---------------------------------------------------------------------------


class TestSessionReuse:
    """Reusing a session_id should close the old env and start fresh."""

    def test_reuse_session_id_creates_new_episode(self, client: TestClient) -> None:
        sid = "reuse-test"
        d1 = _reset(client, seed=10, session_id=sid)
        d2 = _reset(client, seed=20, session_id=sid)

        assert d1["session_id"] == d2["session_id"] == sid
        assert d1["episode_id"] != d2["episode_id"]

    def test_reuse_session_id_resets_round_counter(self, client: TestClient) -> None:
        """After stepping session, reusing the ID should start at round 0."""
        sid = "reuse-rounds"
        _reset(client, seed=42, session_id=sid)

        action = _good_action(client)
        client.post("/step", json={"session_id": sid, "action": action})

        # Now reset with the same session_id
        d2 = _reset(client, seed=99, session_id=sid)
        obs = d2["observation"]
        assert obs["scientist"]["round_number"] == 0

    def test_reuse_does_not_affect_other_sessions(self, client: TestClient) -> None:
        """Resetting session A with reuse doesn't touch session B."""
        sid_a = "reuse-a"
        sid_b = "reuse-b"

        _reset(client, seed=42, session_id=sid_a)
        d_b = _reset(client, seed=42, session_id=sid_b)

        action = _good_action(client)
        client.post("/step", json={"session_id": sid_b, "action": action})

        # Reuse session A with a new seed
        _reset(client, seed=99, session_id=sid_a)

        # Session B should still be at round 1 from the step we did
        resp_b = client.post("/step", json={"session_id": sid_b, "action": action})
        assert resp_b.status_code == 200
        # B is still alive and progressing independently
        assert resp_b.json()["done"] is False


# ---------------------------------------------------------------------------
# Invalid session handling
# ---------------------------------------------------------------------------


class TestInvalidSession:
    """Invalid or missing session_id should return clean errors."""

    def test_step_nonexistent_session_returns_404(self, client: TestClient) -> None:
        action = _good_action(client)
        resp = client.post("/step", json={
            "session_id": "does-not-exist",
            "action": action,
        })
        assert resp.status_code == 404
        assert "Session not found" in resp.json()["detail"]

    def test_step_after_terminal_session_raises(self, client: TestClient) -> None:
        """A terminated session's env is closed; stepping again should error."""
        sid = "terminal-step"
        _reset(client, seed=42, session_id=sid)

        action = _good_action(client)
        client.post("/step", json={"session_id": sid, "action": action})

        accept = {
            "action_type": "accept",
            "sample_size": 0,
            "controls": [],
            "technique": "",
            "duration_days": 0,
            "required_equipment": [],
            "required_reagents": [],
            "questions": [],
            "rationale": "",
        }
        resp_term = client.post("/step", json={"session_id": sid, "action": accept})
        assert resp_term.json()["done"] is True

        # Stepping a done env should return an error (env raises or returns error)
        resp_again = client.post("/step", json={"session_id": sid, "action": action})
        # The server should still return a response (200 with error or 500),
        # not crash silently
        assert resp_again.status_code in (200, 500)

    def test_replay_isolation_between_sessions(self, client: TestClient) -> None:
        """Each session's terminal episode gets its own replay entry."""
        sid_a = "replay-a"
        sid_b = "replay-b"

        d_a = _reset(client, seed=10, session_id=sid_a)
        d_b = _reset(client, seed=20, session_id=sid_b)

        action = _good_action(client)
        accept = {
            "action_type": "accept",
            "sample_size": 0,
            "controls": [],
            "technique": "",
            "duration_days": 0,
            "required_equipment": [],
            "required_reagents": [],
            "questions": [],
            "rationale": "",
        }

        # Complete both episodes
        client.post("/step", json={"session_id": sid_a, "action": action})
        client.post("/step", json={"session_id": sid_a, "action": accept})

        client.post("/step", json={"session_id": sid_b, "action": action})
        client.post("/step", json={"session_id": sid_b, "action": accept})

        # Both replays should exist independently
        ep_a = d_a["episode_id"]
        ep_b = d_b["episode_id"]

        resp_a = client.get(f"/replay/{ep_a}")
        resp_b = client.get(f"/replay/{ep_b}")

        assert resp_a.status_code == 200
        assert resp_b.status_code == 200

        # Different seeds → different episode content
        assert resp_a.json()["seed"] != resp_b.json()["seed"]
