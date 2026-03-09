"""Tests for the LLM judge module.

Uses mocked HTTP responses to test the OpenRouter integration without
making real API calls.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from replicalab.models import Protocol, RewardBreakdown
from replicalab.scenarios import generate_scenario
from replicalab.scoring.llm_judge import build_llm_reward_breakdown


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _scenario():
    return generate_scenario(seed=42, template="math_reasoning", difficulty="easy")


def _protocol(scenario) -> Protocol:
    lab = scenario.lab_manager_observation
    spec = scenario.hidden_reference_spec
    return Protocol(
        sample_size=10,
        controls=["baseline"],
        technique=spec.summary[:60] if spec.summary else "replication",
        duration_days=max(1, min(2, lab.time_limit_days)),
        required_equipment=list(lab.equipment_available[:1]) if lab.equipment_available else [],
        required_reagents=list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else [],
        rationale="Test rationale for the protocol.",
    )


def _mock_response(scores: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = 200
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {
        "choices": [
            {"message": {"content": json.dumps(scores)}}
        ]
    }
    return mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestLlmJudgeSuccess:
    """LLM judge returns valid scores from mocked API."""

    @patch("replicalab.scoring.llm_judge.httpx")
    def test_returns_breakdown_from_llm(self, mock_httpx) -> None:
        scenario = _scenario()
        protocol = _protocol(scenario)

        scores = {"rigor": 0.8, "feasibility": 0.9, "fidelity": 0.7, "parsimony": 0.95}
        mock_httpx.post.return_value = _mock_response(scores)

        breakdown = build_llm_reward_breakdown(
            protocol=protocol,
            scenario=scenario,
            rounds_used=2,
            max_rounds=6,
            api_key="test-key",
        )

        assert isinstance(breakdown, RewardBreakdown)
        assert breakdown.rigor == 0.8
        assert breakdown.feasibility == 0.9
        assert breakdown.fidelity == 0.7
        assert breakdown.parsimony == 0.95

    @patch("replicalab.scoring.llm_judge.httpx")
    def test_clamps_out_of_range_scores(self, mock_httpx) -> None:
        scenario = _scenario()
        protocol = _protocol(scenario)

        scores = {"rigor": 1.5, "feasibility": -0.2, "fidelity": 0.5, "parsimony": 2.0}
        mock_httpx.post.return_value = _mock_response(scores)

        breakdown = build_llm_reward_breakdown(
            protocol=protocol,
            scenario=scenario,
            rounds_used=2,
            max_rounds=6,
            api_key="test-key",
        )

        assert breakdown.rigor == 1.0
        assert breakdown.feasibility == 0.0
        assert breakdown.fidelity == 0.5
        assert breakdown.parsimony == 1.0


class TestLlmJudgeFallback:
    """LLM judge falls back to deterministic scorer on failure."""

    @patch("replicalab.scoring.llm_judge.httpx")
    def test_fallback_on_http_error(self, mock_httpx) -> None:
        scenario = _scenario()
        protocol = _protocol(scenario)

        mock_httpx.post.side_effect = Exception("Connection failed")

        breakdown = build_llm_reward_breakdown(
            protocol=protocol,
            scenario=scenario,
            rounds_used=2,
            max_rounds=6,
            api_key="test-key",
        )

        assert isinstance(breakdown, RewardBreakdown)
        assert breakdown.rigor >= 0.0
        assert breakdown.feasibility >= 0.0
        assert breakdown.fidelity >= 0.0

    @patch("replicalab.scoring.llm_judge.httpx")
    def test_fallback_on_json_parse_error(self, mock_httpx) -> None:
        scenario = _scenario()
        protocol = _protocol(scenario)

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "not valid json"}}]
        }
        mock_httpx.post.return_value = mock_resp

        breakdown = build_llm_reward_breakdown(
            protocol=protocol,
            scenario=scenario,
            rounds_used=2,
            max_rounds=6,
            api_key="test-key",
        )

        assert isinstance(breakdown, RewardBreakdown)

    @patch("replicalab.scoring.llm_judge.httpx")
    def test_fallback_on_missing_keys(self, mock_httpx) -> None:
        scenario = _scenario()
        protocol = _protocol(scenario)

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"choices": []}
        mock_httpx.post.return_value = mock_resp

        breakdown = build_llm_reward_breakdown(
            protocol=protocol,
            scenario=scenario,
            rounds_used=2,
            max_rounds=6,
            api_key="test-key",
        )

        assert isinstance(breakdown, RewardBreakdown)


class TestLlmJudgePrompt:
    """Verify the prompt construction includes key scenario details."""

    @patch("replicalab.scoring.llm_judge.httpx")
    def test_prompt_includes_protocol_details(self, mock_httpx) -> None:
        scenario = _scenario()
        protocol = _protocol(scenario)

        scores = {"rigor": 0.5, "feasibility": 0.5, "fidelity": 0.5, "parsimony": 0.5}
        mock_httpx.post.return_value = _mock_response(scores)

        build_llm_reward_breakdown(
            protocol=protocol,
            scenario=scenario,
            rounds_used=2,
            max_rounds=6,
            api_key="test-key",
        )

        call_args = mock_httpx.post.call_args
        request_body = call_args.kwargs.get("json") or call_args[1].get("json")
        messages = request_body["messages"]
        user_msg = messages[1]["content"]

        assert protocol.technique in user_msg
        assert scenario.domain_id in user_msg
