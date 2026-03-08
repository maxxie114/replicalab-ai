"""Contract tests for judge audit payloads (TST 11).

Verifies that terminal StepInfo and EpisodeLog contain all required
audit fields with correct types and semantics.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from replicalab.models import EpisodeLog, RewardBreakdown, StepInfo
from server.app import app


@pytest.fixture()
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _good_action_payload(client: TestClient) -> dict:
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
        "required_equipment": list(lab.equipment_available[:1]) if lab.equipment_available else [],
        "required_reagents": list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else [],
        "questions": [],
        "rationale": (
            f"Plan addresses: {', '.join(spec.required_elements[:2])}. "
            f"Target metric: {spec.target_metric}. "
            f"Target value: {spec.target_value}. "
            "Stay within budget and schedule."
        ),
    }


def _accept_action() -> dict:
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


def _run_to_terminal(client: TestClient, *, accept: bool = True) -> tuple[str, dict]:
    """Reset, propose, and optionally accept. Returns (episode_id, terminal_response_json)."""
    reset = client.post("/reset", json={"seed": 42, "scenario": "math_reasoning", "difficulty": "easy"}).json()
    session_id = reset["session_id"]
    episode_id = reset["episode_id"]

    action = _good_action_payload(client)
    client.post("/step", json={"session_id": session_id, "action": action})

    if accept:
        resp = client.post("/step", json={"session_id": session_id, "action": _accept_action()})
    else:
        # Run to timeout
        for _ in range(10):
            resp = client.post("/step", json={"session_id": session_id, "action": action})
            if resp.json()["done"]:
                break

    return episode_id, resp.json()


# ---------------------------------------------------------------------------
# StepInfo audit field contracts
# ---------------------------------------------------------------------------


class TestStepInfoAuditContract:
    """Terminal StepInfo must contain all audit fields."""

    def test_terminal_info_has_verdict(self, client: TestClient) -> None:
        _, data = _run_to_terminal(client)
        assert data["info"]["verdict"] in ("accept", "revise", "timeout")

    def test_terminal_info_has_judge_notes(self, client: TestClient) -> None:
        _, data = _run_to_terminal(client)
        assert isinstance(data["info"]["judge_notes"], str)
        assert len(data["info"]["judge_notes"]) > 0

    def test_terminal_info_has_reward_breakdown(self, client: TestClient) -> None:
        _, data = _run_to_terminal(client)
        rb = data["info"]["reward_breakdown"]
        assert rb is not None
        for key in ("rigor", "feasibility", "fidelity", "parsimony"):
            assert key in rb
            assert 0.0 <= rb[key] <= 1.0

    def test_terminal_info_has_top_failure_reasons(self, client: TestClient) -> None:
        _, data = _run_to_terminal(client)
        reasons = data["info"]["top_failure_reasons"]
        assert isinstance(reasons, list)

    def test_terminal_info_has_agreement_reached(self, client: TestClient) -> None:
        _, data = _run_to_terminal(client)
        assert isinstance(data["info"]["agreement_reached"], bool)
        assert data["info"]["agreement_reached"] is True

    def test_non_terminal_info_has_no_verdict(self, client: TestClient) -> None:
        reset = client.post("/reset", json={"seed": 42}).json()
        action = _good_action_payload(client)
        resp = client.post("/step", json={"session_id": reset["session_id"], "action": action})
        data = resp.json()
        assert data["done"] is False
        assert data["info"]["verdict"] is None
        assert data["info"]["reward_breakdown"] is None


# ---------------------------------------------------------------------------
# EpisodeLog audit field contracts
# ---------------------------------------------------------------------------


class TestEpisodeLogAuditContract:
    """GET /replay/{episode_id} must include full audit metadata."""

    def test_replay_has_verdict_and_judge_notes(self, client: TestClient) -> None:
        episode_id, _ = _run_to_terminal(client)
        replay = client.get(f"/replay/{episode_id}").json()
        assert replay["verdict"] in ("accept", "revise", "timeout")
        assert isinstance(replay["judge_notes"], str)
        assert len(replay["judge_notes"]) > 0

    def test_replay_has_reward_breakdown(self, client: TestClient) -> None:
        episode_id, _ = _run_to_terminal(client)
        replay = client.get(f"/replay/{episode_id}").json()
        rb = replay["reward_breakdown"]
        assert rb is not None
        for key in ("rigor", "feasibility", "fidelity", "parsimony"):
            assert key in rb

    def test_replay_has_top_failure_reasons(self, client: TestClient) -> None:
        episode_id, _ = _run_to_terminal(client)
        replay = client.get(f"/replay/{episode_id}").json()
        assert isinstance(replay["top_failure_reasons"], list)

    def test_replay_has_transcript(self, client: TestClient) -> None:
        episode_id, _ = _run_to_terminal(client)
        replay = client.get(f"/replay/{episode_id}").json()
        assert isinstance(replay["transcript"], list)
        assert len(replay["transcript"]) > 0

    def test_replay_has_invalid_action_fields(self, client: TestClient) -> None:
        episode_id, _ = _run_to_terminal(client)
        replay = client.get(f"/replay/{episode_id}").json()
        assert "invalid_action_count" in replay
        assert "invalid_action_rate" in replay
        assert isinstance(replay["invalid_action_count"], int)
        assert isinstance(replay["invalid_action_rate"], (int, float))
        assert replay["invalid_action_count"] >= 0
        assert 0.0 <= replay["invalid_action_rate"] <= 1.0

    def test_replay_has_total_reward(self, client: TestClient) -> None:
        episode_id, _ = _run_to_terminal(client)
        replay = client.get(f"/replay/{episode_id}").json()
        assert isinstance(replay["total_reward"], (int, float))


# ---------------------------------------------------------------------------
# Pydantic model contracts (unit-level)
# ---------------------------------------------------------------------------


class TestAuditModelContracts:
    """Pydantic model round-trip for audit fields."""

    def test_step_info_default_audit_fields(self) -> None:
        info = StepInfo()
        assert info.agreement_reached is False
        assert info.verdict is None
        assert info.judge_notes is None
        assert info.reward_breakdown is None
        assert info.top_failure_reasons == []

    def test_step_info_with_audit_fields(self) -> None:
        info = StepInfo(
            agreement_reached=True,
            verdict="accept",
            judge_notes="All clear.",
            reward_breakdown=RewardBreakdown(rigor=0.9, feasibility=0.8, fidelity=0.7),
            top_failure_reasons=["minor issue"],
        )
        assert info.verdict == "accept"
        assert info.reward_breakdown.rigor == 0.9
        assert info.top_failure_reasons == ["minor issue"]

    def test_episode_log_invalid_action_fields_default(self) -> None:
        log = EpisodeLog()
        assert log.invalid_action_count == 0
        assert log.invalid_action_rate == 0.0

    def test_episode_log_invalid_action_fields_set(self) -> None:
        log = EpisodeLog(invalid_action_count=3, invalid_action_rate=0.25)
        assert log.invalid_action_count == 3
        assert log.invalid_action_rate == 0.25

    def test_episode_log_json_round_trip_preserves_audit(self) -> None:
        log = EpisodeLog(
            episode_id="audit-test",
            verdict="accept",
            judge_notes="Solid work.",
            top_failure_reasons=["none"],
            invalid_action_count=1,
            invalid_action_rate=0.1,
            reward_breakdown=RewardBreakdown(
                rigor=0.9,
                feasibility=0.85,
                fidelity=0.8,
                penalties={"stalling": 0.05},
            ),
        )
        raw = log.model_dump_json()
        restored = EpisodeLog.model_validate_json(raw)
        assert restored.verdict == "accept"
        assert restored.invalid_action_count == 1
        assert restored.invalid_action_rate == 0.1
        assert restored.reward_breakdown.penalties == {"stalling": 0.05}
