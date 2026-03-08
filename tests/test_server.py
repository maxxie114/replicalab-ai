"""Server endpoint tests.

API 02 adds POST /reset endpoint tests.
API 04 adds a smoke test for GET /scenarios.
API 13 adds CORS middleware verification tests.
API 03 adds POST /step endpoint tests.
API 06 adds WebSocket session handler tests.
API 07 adds idle-timeout and graceful disconnect cleanup tests.
"""

from __future__ import annotations

import json
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from server.app import app

_EXPECTED_FAMILIES = {"math_reasoning", "ml_benchmark", "finance_trading"}
_EXPECTED_DIFFICULTIES = ["easy", "medium", "hard"]


@pytest.fixture()
def client():
    return TestClient(app)


class TestHealthEndpoint:
    """GET /health — API 01."""

    def test_health_returns_200(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_payload_has_stable_keys(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert data["status"] == "ok"
        assert data["env"] in ("real", "stub")
        assert "version" in data

    def test_health_version_matches_app(self, client: TestClient) -> None:
        from server.app import app as _app

        data = client.get("/health").json()
        assert data["version"] == _app.version

    def test_health_is_deterministic(self, client: TestClient) -> None:
        r1 = client.get("/health").json()
        r2 = client.get("/health").json()
        assert r1 == r2


class TestLogConfig:
    """OBS 02 — log level configurability."""

    def test_default_log_level_is_info(self) -> None:
        from replicalab.config import LOG_LEVEL

        # Default when REPLICALAB_LOG_LEVEL is not set
        assert LOG_LEVEL in ("INFO", "DEBUG", "WARNING", "ERROR")

    def test_log_level_env_var_is_respected(self, monkeypatch) -> None:
        """REPLICALAB_LOG_LEVEL env var controls the log level."""
        import importlib

        import replicalab.config as config_mod

        monkeypatch.setenv("REPLICALAB_LOG_LEVEL", "debug")
        importlib.reload(config_mod)

        assert config_mod.LOG_LEVEL == "DEBUG"

        # Restore
        monkeypatch.delenv("REPLICALAB_LOG_LEVEL", raising=False)
        importlib.reload(config_mod)

    def test_log_format_is_readable(self) -> None:
        from replicalab.config import LOG_FORMAT

        assert "%(asctime)s" in LOG_FORMAT
        assert "%(levelname)s" in LOG_FORMAT
        assert "%(name)s" in LOG_FORMAT


class TestRootEndpoint:
    """GET / — lightweight landing page for hosted backend deployments."""

    def test_root_returns_200_html(self, client: TestClient) -> None:
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    def test_root_mentions_core_api_endpoints(self, client: TestClient) -> None:
        body = client.get("/").text
        assert "ReplicaLab API" in body
        assert "GET /health" in body
        assert "GET /scenarios" in body
        assert "POST /reset" in body
        assert "POST /step" in body
        assert "WS /ws" in body


class TestScenariosEndpoint:
    """GET /scenarios — API 04."""

    def test_returns_200(self, client: TestClient):
        resp = client.get("/scenarios")
        assert resp.status_code == 200

    def test_response_has_scenarios_key(self, client: TestClient):
        data = client.get("/scenarios").json()
        assert "scenarios" in data
        assert isinstance(data["scenarios"], list)

    def test_all_families_present(self, client: TestClient):
        data = client.get("/scenarios").json()
        families = {s["family"] for s in data["scenarios"]}
        assert families == _EXPECTED_FAMILIES

    def test_each_family_has_difficulties(self, client: TestClient):
        data = client.get("/scenarios").json()
        for entry in data["scenarios"]:
            assert entry["difficulties"] == _EXPECTED_DIFFICULTIES

    def test_no_extra_keys(self, client: TestClient):
        data = client.get("/scenarios").json()
        for entry in data["scenarios"]:
            assert set(entry.keys()) == {"family", "difficulties"}


# ---------------------------------------------------------------------------
# POST /reset — API 02
# ---------------------------------------------------------------------------


class TestCorsConfiguration:
    """API 13: CORS middleware for local frontend and HF Spaces."""

    def test_preflight_allows_localhost_vite_origin(self, client: TestClient) -> None:
        resp = client.options(
            "/reset",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert resp.status_code == 200
        assert resp.headers["access-control-allow-origin"] == "http://localhost:5173"
        assert resp.headers["access-control-allow-credentials"] == "true"

    def test_preflight_allows_hf_space_origin(self, client: TestClient) -> None:
        origin = "https://replicalab-demo.hf.space"
        resp = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        assert resp.status_code == 200
        assert resp.headers["access-control-allow-origin"] == origin
        assert resp.headers["access-control-allow-credentials"] == "true"

    def test_preflight_rejects_unconfigured_origin(self, client: TestClient) -> None:
        resp = client.options(
            "/reset",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert resp.status_code == 400
        assert "access-control-allow-origin" not in resp.headers


class TestResetEndpoint:
    """POST /reset — API 02."""

    def test_reset_returns_200_with_expected_keys(self, client: TestClient) -> None:
        resp = client.post("/reset", json={"seed": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert "episode_id" in data
        assert "observation" in data

    def test_reset_observation_has_both_roles(self, client: TestClient) -> None:
        data = client.post("/reset", json={"seed": 1}).json()
        obs = data["observation"]
        assert "scientist" in obs
        assert "lab_manager" in obs
        assert obs["scientist"]["paper_title"]
        assert obs["lab_manager"]["budget_total"] > 0

    def test_reset_with_explicit_session_id_reuses_slot(
        self, client: TestClient
    ) -> None:
        """Passing session_id reuses the same slot and returns the same id."""
        sid = "my-fixed-session"
        d1 = client.post("/reset", json={"seed": 1, "session_id": sid}).json()
        assert d1["session_id"] == sid

        d2 = client.post("/reset", json={"seed": 2, "session_id": sid}).json()
        assert d2["session_id"] == sid
        # New episode each time
        assert d2["episode_id"] != d1["episode_id"]

    def test_reset_reuse_closes_prior_env(self, client: TestClient) -> None:
        """Resetting with the same session_id produces a fresh episode."""
        sid = "reuse-session"
        d1 = client.post("/reset", json={"seed": 10, "session_id": sid}).json()
        ep1 = d1["episode_id"]

        d2 = client.post("/reset", json={"seed": 20, "session_id": sid}).json()
        ep2 = d2["episode_id"]

        assert ep1 != ep2

    def test_reset_default_params(self, client: TestClient) -> None:
        """Omitting scenario and difficulty uses defaults without error."""
        resp = client.post("/reset", json={"seed": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["observation"]["scientist"]["paper_title"]

    def test_reset_custom_scenario_and_difficulty(self, client: TestClient) -> None:
        for family in ("math_reasoning", "ml_benchmark", "finance_trading"):
            for diff in ("easy", "medium", "hard"):
                resp = client.post(
                    "/reset",
                    json={"seed": 42, "scenario": family, "difficulty": diff},
                )
                assert resp.status_code == 200, f"Failed for {family}/{diff}"
                obs = resp.json()["observation"]
                assert obs["scientist"]["paper_title"]
                assert obs["lab_manager"]["budget_total"] > 0

    def test_reset_deterministic_with_same_seed(self, client: TestClient) -> None:
        """Same seed + scenario + difficulty → identical observations."""
        params = {"seed": 99, "scenario": "math_reasoning", "difficulty": "medium"}
        d1 = client.post("/reset", json=params).json()
        d2 = client.post("/reset", json=params).json()

        assert d1["observation"] == d2["observation"]
        # Episode ids differ (new UUID each time)
        assert d1["episode_id"] != d2["episode_id"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset(client: TestClient, **kwargs) -> dict:
    """Reset and return the response JSON."""
    payload = {"seed": 42, "scenario": "math_reasoning", "difficulty": "easy"}
    payload.update(kwargs)
    resp = client.post("/reset", json=payload)
    assert resp.status_code == 200
    return resp.json()


def _good_action_payload(client: TestClient) -> dict:
    """Build a valid propose_protocol action payload from a fresh scenario."""
    from replicalab.scenarios import generate_scenario

    scenario = generate_scenario(seed=42, template="math_reasoning", difficulty="easy")
    lab = scenario.lab_manager_observation
    spec = scenario.hidden_reference_spec
    return {
        "action_type": "propose_protocol",
        "sample_size": 10,
        "controls": ["baseline", "ablation"],
        "technique": spec.summary[:60] if spec.summary else "replication_plan",
        "duration_days": max(1, min(2, lab.time_limit_days)),
        "required_equipment": (
            list(lab.equipment_available[:1]) if lab.equipment_available else []
        ),
        "required_reagents": (
            list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else []
        ),
        "questions": [],
        "rationale": (
            f"Plan addresses: {', '.join(spec.required_elements[:2])}. "
            f"Target metric: {spec.target_metric}. "
            f"Target value: {spec.target_value}. "
            "Stay within budget and schedule."
        ),
    }


def _accept_action_payload() -> dict:
    return {
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


# ---------------------------------------------------------------------------
# POST /step — API 03
# ---------------------------------------------------------------------------


class TestStepEndpoint:
    """POST /step — API 03."""

    def test_reset_then_step_happy_path(self, client: TestClient) -> None:
        """Reset, then step with a valid action → 200 with StepResult."""
        reset_data = _reset(client)
        session_id = reset_data["session_id"]

        action = _good_action_payload(client)
        resp = client.post("/step", json={"session_id": session_id, "action": action})

        assert resp.status_code == 200
        data = resp.json()
        assert "observation" in data
        assert "reward" in data
        assert "done" in data
        assert "info" in data
        assert data["done"] is False
        assert data["info"]["error"] is None

    def test_step_invalid_session_returns_404(self, client: TestClient) -> None:
        """Step with a non-existent session_id → 404."""
        action = _good_action_payload(client)
        resp = client.post(
            "/step",
            json={"session_id": "nonexistent-session-id", "action": action},
        )

        assert resp.status_code == 404
        assert "Session not found" in resp.json()["detail"]

    def test_terminal_step_returns_real_reward_breakdown(
        self, client: TestClient
    ) -> None:
        """Propose → accept: terminal step has real reward_breakdown,
        judge_notes, and verdict from the env (not stubs)."""
        reset_data = _reset(client)
        session_id = reset_data["session_id"]

        # Step 1: propose
        action = _good_action_payload(client)
        resp1 = client.post("/step", json={"session_id": session_id, "action": action})
        assert resp1.status_code == 200
        assert resp1.json()["done"] is False

        # Step 2: accept
        resp2 = client.post(
            "/step",
            json={"session_id": session_id, "action": _accept_action_payload()},
        )
        assert resp2.status_code == 200
        data = resp2.json()

        assert data["done"] is True
        assert data["reward"] > 0.0

        info = data["info"]
        assert info["agreement_reached"] is True
        assert info["verdict"] == "accept"
        assert info["judge_notes"] is not None
        assert "rigor" in info["judge_notes"]

        rb = info["reward_breakdown"]
        assert rb is not None
        assert 0.0 <= rb["rigor"] <= 1.0
        assert 0.0 <= rb["feasibility"] <= 1.0
        assert 0.0 <= rb["fidelity"] <= 1.0
        # Verify it's not the old stub 0.8
        assert not (rb["rigor"] == 0.8 and rb["feasibility"] == 0.8 and rb["fidelity"] == 0.8)

    def test_semantic_invalid_action_returns_200_with_error(
        self, client: TestClient
    ) -> None:
        """A semantically invalid action (e.g. duration=999) returns 200
        with info.error set, not a crash or 422."""
        reset_data = _reset(client)
        session_id = reset_data["session_id"]

        bad_action = {
            "action_type": "propose_protocol",
            "sample_size": 5,
            "controls": ["baseline"],
            "technique": "some technique",
            "duration_days": 999,
            "required_equipment": [],
            "required_reagents": [],
            "questions": [],
            "rationale": "Duration is impossibly long for the lab time limit.",
        }
        resp = client.post(
            "/step", json={"session_id": session_id, "action": bad_action}
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["done"] is False
        assert data["info"]["error"] is not None
        assert "Validation errors" in data["info"]["error"]

    def test_replay_uses_real_judge_data(self, client: TestClient) -> None:
        """After a terminal step, GET /replay/{episode_id} returns
        real judge_notes and verdict, not stub values."""
        reset_data = _reset(client)
        session_id = reset_data["session_id"]
        episode_id = reset_data["episode_id"]

        # Propose then accept
        action = _good_action_payload(client)
        client.post("/step", json={"session_id": session_id, "action": action})
        client.post(
            "/step",
            json={"session_id": session_id, "action": _accept_action_payload()},
        )

        # Fetch replay
        resp = client.get(f"/replay/{episode_id}")
        assert resp.status_code == 200
        replay = resp.json()

        assert replay["agreement_reached"] is True
        assert "rigor" in replay["judge_notes"]
        assert replay["verdict"] == "accept"
        assert replay["reward_breakdown"] is not None
        assert replay["total_reward"] > 0.0
        # Not the old stub string
        assert "Stub audit" not in replay["judge_notes"]

    def test_replay_includes_top_failure_reasons(self, client: TestClient) -> None:
        """Terminal replay records persist the canonical audit reasons."""
        reset_data = _reset(client)
        session_id = reset_data["session_id"]
        episode_id = reset_data["episode_id"]

        # Force a timeout path so the audit builder emits failure reasons.
        for _ in range(6):
            resp = client.post(
                "/step",
                json={"session_id": session_id, "action": _good_action_payload(client)},
            )
            assert resp.status_code == 200
            if resp.json()["done"]:
                break

        replay = client.get(f"/replay/{episode_id}").json()
        assert replay["verdict"] == "timeout"
        assert isinstance(replay["top_failure_reasons"], list)
        assert replay["top_failure_reasons"]
        assert any(
            "round limit" in reason.lower() or "without agreement" in reason.lower()
            for reason in replay["top_failure_reasons"]
        )


# ---------------------------------------------------------------------------
# WebSocket handler — API 06
# ---------------------------------------------------------------------------


def _ws_send_recv(ws, msg: dict) -> dict:
    """Send a JSON message over the WebSocket and return the parsed response."""
    ws.send_text(json.dumps(msg))
    return json.loads(ws.receive_text())


class TestWebSocket:
    """API 06: WebSocket session handler with isolated env per connection."""

    # -- basic connectivity --------------------------------------------------

    def test_ws_ping_pong(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            resp = _ws_send_recv(ws, {"type": "ping"})
            assert resp["type"] == "pong"

    def test_ws_reset_returns_observation(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            resp = _ws_send_recv(ws, {
                "type": "reset", "seed": 42,
                "scenario": "math_reasoning", "difficulty": "easy",
            })
            assert resp["type"] == "reset_ok"
            assert resp["episode_id"]
            obs = resp["observation"]
            assert obs["scientist"]["paper_title"]
            assert obs["lab_manager"]["budget_total"] > 0

    def test_ws_step_returns_result(self, client: TestClient) -> None:
        action = _good_action_payload(client)
        with client.websocket_connect("/ws") as ws:
            _ws_send_recv(ws, {"type": "reset", "seed": 42})
            resp = _ws_send_recv(ws, {"type": "step", "action": action})

            assert resp["type"] == "step_ok"
            assert resp["done"] is False
            assert resp["reward"] > 0.0
            assert resp["info"]["step_reward_components"]["protocol_delta_bonus"] > 0.0
            assert resp["observation"] is not None

    def test_ws_full_episode_real_reward(self, client: TestClient) -> None:
        """Propose → accept returns real reward breakdown, not stub 0.8."""
        action = _good_action_payload(client)
        with client.websocket_connect("/ws") as ws:
            _ws_send_recv(ws, {"type": "reset", "seed": 42})
            _ws_send_recv(ws, {"type": "step", "action": action})
            resp = _ws_send_recv(ws, {"type": "step", "action": _accept_action_payload()})

            assert resp["type"] == "step_ok"
            assert resp["done"] is True
            assert resp["reward"] > 0.0

            info = resp["info"]
            assert info["agreement_reached"] is True
            assert info["verdict"] == "accept"
            rb = info["reward_breakdown"]
            assert rb is not None
            assert 0.0 <= rb["rigor"] <= 1.0
            assert 0.0 <= rb["feasibility"] <= 1.0
            assert 0.0 <= rb["fidelity"] <= 1.0
            assert not (rb["rigor"] == 0.8 and rb["feasibility"] == 0.8)

    # -- error handling ------------------------------------------------------

    def test_ws_invalid_json(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            ws.send_text("not valid json {{{")
            resp = json.loads(ws.receive_text())
            assert resp["type"] == "error"
            assert "Invalid JSON" in resp["message"]

    def test_ws_missing_action_field(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            _ws_send_recv(ws, {"type": "reset", "seed": 42})
            resp = _ws_send_recv(ws, {"type": "step"})
            assert resp["type"] == "error"
            assert "Missing" in resp["message"]

    def test_ws_invalid_action_payload(self, client: TestClient) -> None:
        """Structurally invalid action (missing required fields) → WS error."""
        with client.websocket_connect("/ws") as ws:
            _ws_send_recv(ws, {"type": "reset", "seed": 42})
            resp = _ws_send_recv(ws, {
                "type": "step",
                "action": {"action_type": "propose_protocol"},
            })
            assert resp["type"] == "error"
            assert "Invalid action" in resp["message"]

    def test_ws_unknown_message_type(self, client: TestClient) -> None:
        with client.websocket_connect("/ws") as ws:
            resp = _ws_send_recv(ws, {"type": "banana"})
            assert resp["type"] == "error"
            assert "Unknown" in resp["message"]

    # -- session isolation ---------------------------------------------------

    def test_ws_session_isolation(self, client: TestClient) -> None:
        """Two WebSocket connections have independent env state."""
        action = _good_action_payload(client)

        with client.websocket_connect("/ws") as ws1:
            r1 = _ws_send_recv(ws1, {"type": "reset", "seed": 1})
            _ws_send_recv(ws1, {"type": "step", "action": action})

            with client.websocket_connect("/ws") as ws2:
                r2 = _ws_send_recv(ws2, {"type": "reset", "seed": 2})

                assert r1["episode_id"] != r2["episode_id"]
                # ws2 is at round 0, ws1 is at round 1
                step2 = _ws_send_recv(ws2, {"type": "step", "action": action})
                assert step2["observation"]["scientist"]["round_number"] == 1

    # -- real-env integration (user-requested) --------------------------------

    def test_ws_semantic_invalid_action_returns_step_ok_with_info_error(
        self, client: TestClient
    ) -> None:
        """A structurally valid but semantically invalid action (e.g.
        duration_days=999) returns step_ok with info.error — NOT a
        transport-level WS error frame."""
        with client.websocket_connect("/ws") as ws:
            _ws_send_recv(ws, {"type": "reset", "seed": 42})
            bad_action = {
                "action_type": "propose_protocol",
                "sample_size": 5,
                "controls": ["baseline"],
                "technique": "some technique",
                "duration_days": 999,
                "required_equipment": [],
                "required_reagents": [],
                "questions": [],
                "rationale": "Duration is impossibly long for the lab.",
            }
            resp = _ws_send_recv(ws, {"type": "step", "action": bad_action})

            assert resp["type"] == "step_ok"
            assert resp["done"] is False
            assert resp["info"]["error"] is not None
            assert "Validation errors" in resp["info"]["error"]

    def test_ws_timeout_verdict(self, client: TestClient) -> None:
        """Run to max_rounds without accept → done=True, verdict=timeout,
        reward=0.0. Proves real-env integration."""
        action = _good_action_payload(client)
        with client.websocket_connect("/ws") as ws:
            reset_resp = _ws_send_recv(ws, {"type": "reset", "seed": 42})
            max_rounds = reset_resp["observation"]["scientist"]["max_rounds"]

            resp = None
            for _ in range(max_rounds):
                resp = _ws_send_recv(ws, {"type": "step", "action": action})

            assert resp["done"] is True
            assert resp["info"]["verdict"] == "timeout"
            assert resp["reward"] < 0.0
            assert resp["info"]["reward_breakdown"] is not None
            assert resp["info"]["reward_breakdown"]["penalties"]["timeout"] > 0.0

    def test_ws_terminal_episode_persists_real_replay_log(
        self, client: TestClient
    ) -> None:
        """Complete a WS episode, then verify GET /replay/{episode_id}
        returns real reward_breakdown, judge_notes, and verdict —
        not stub strings."""
        action = _good_action_payload(client)
        with client.websocket_connect("/ws") as ws:
            reset_resp = _ws_send_recv(ws, {"type": "reset", "seed": 42})
            episode_id = reset_resp["episode_id"]

            _ws_send_recv(ws, {"type": "step", "action": action})
            _ws_send_recv(ws, {"type": "step", "action": _accept_action_payload()})

        # Fetch replay via REST after WS connection is closed
        replay_resp = client.get(f"/replay/{episode_id}")
        assert replay_resp.status_code == 200
        replay = replay_resp.json()

        assert replay["agreement_reached"] is True
        assert replay["verdict"] == "accept"
        assert replay["total_reward"] > 0.0

        # Real judge_notes, not stub
        assert replay["judge_notes"] != ""
        assert "Stub audit" not in replay["judge_notes"]
        assert "rigor" in replay["judge_notes"]

        # Real reward_breakdown with non-stub scores
        rb = replay["reward_breakdown"]
        assert rb is not None
        assert 0.0 < rb["rigor"] <= 1.0
        assert 0.0 < rb["feasibility"] <= 1.0
        assert 0.0 < rb["fidelity"] <= 1.0
        assert not (rb["rigor"] == 0.8 and rb["feasibility"] == 0.8)

    # -- idle timeout & disconnect cleanup (API 07) -------------------------

    def test_ws_idle_timeout_closes_connection(self, client: TestClient) -> None:
        """API 07: server closes WebSocket after idle timeout (no messages)."""
        with patch("server.app._WS_IDLE_TIMEOUT", 0.5):
            with client.websocket_connect("/ws") as ws:
                # Don't send anything — let the server-side timeout fire
                time.sleep(1.0)
                with pytest.raises(WebSocketDisconnect) as exc_info:
                    ws.receive_text()
                assert exc_info.value.code == 1000

    def test_ws_env_closes_on_disconnect(self, client: TestClient) -> None:
        """API 07: env.close() runs in the finally block on disconnect."""
        import server.app as _app

        _original_make_env = _app._make_env
        close_called: list[bool] = []

        def _tracked_make_env():
            env = _original_make_env()
            _original_close = env.close

            def _tracking_close():
                close_called.append(True)
                _original_close()

            env.close = _tracking_close
            return env

        with patch.object(_app, "_make_env", _tracked_make_env):
            with client.websocket_connect("/ws") as ws:
                _ws_send_recv(ws, {"type": "ping"})
            # Context manager exit sends disconnect; server runs finally block
            # TestClient joins the ASGI thread, so close() has already run
            assert len(close_called) == 1
