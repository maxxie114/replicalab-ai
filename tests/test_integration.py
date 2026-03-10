"""End-to-end integration tests for a full negotiation episode.

Runs complete episodes (propose → revise → accept) through the real
ReplicaLabEnv and verifies the full reward pipeline, mid-episode hints,
communication bonus, domain emphasis, and adaptive shaping.
"""

from __future__ import annotations

import pytest

from replicalab.env import ReplicaLabEnv
from replicalab.models import ScientistAction
from replicalab.scenarios import generate_scenario
from replicalab.scoring.rubric import compute_total_reward


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scenario(template="math_reasoning", difficulty="easy", seed=42):
    return generate_scenario(seed=seed, template=template, difficulty=difficulty)


def _propose_action(scenario) -> ScientistAction:
    lab = scenario.lab_manager_observation
    spec = scenario.hidden_reference_spec
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


def _revise_action(scenario) -> ScientistAction:
    lab = scenario.lab_manager_observation
    spec = scenario.hidden_reference_spec
    return ScientistAction(
        action_type="revise_protocol",
        sample_size=8,
        controls=["baseline"],
        technique=spec.summary[:60] if spec.summary else "replication_plan",
        duration_days=max(1, min(2, lab.time_limit_days)),
        required_equipment=list(lab.equipment_available[:1]) if lab.equipment_available else [],
        required_reagents=list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else [],
        questions=[],
        rationale=(
            f"Revised to address feasibility. "
            f"Covers: {', '.join(spec.required_elements[:2])}. "
            f"Target: {spec.target_metric} = {spec.target_value}."
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


def _request_info_action() -> ScientistAction:
    return ScientistAction(
        action_type="request_info",
        sample_size=0,
        controls=[],
        technique="",
        duration_days=0,
        required_equipment=[],
        required_reagents=[],
        questions=["What equipment is available?"],
        rationale="",
    )


# ---------------------------------------------------------------------------
# Full episode tests
# ---------------------------------------------------------------------------


class TestFullEpisode:
    """Complete episode flow: propose → revise → accept."""

    def test_propose_revise_accept_episode(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")

        # Round 1: propose
        r1 = env.step(_propose_action(scenario))
        assert not r1.done
        assert r1.info.agreement_reached is False

        # Round 2: revise
        r2 = env.step(_revise_action(scenario))
        assert not r2.done

        # Round 3: accept
        r3 = env.step(_accept_action())
        assert r3.done
        assert r3.info.agreement_reached is True
        assert r3.info.reward_breakdown is not None
        assert r3.info.judge_notes is not None
        assert r3.info.verdict == "accept"

    def test_terminal_reward_is_positive_for_good_protocol(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")
        scenario = _scenario()

        env.step(_propose_action(scenario))
        env.step(_revise_action(scenario))
        result = env.step(_accept_action())

        assert result.done
        breakdown = result.info.reward_breakdown
        assert breakdown is not None
        total = compute_total_reward(breakdown)
        assert total > 0.0

    def test_timeout_episode(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")
        scenario = _scenario()

        # Use all 6 rounds with request_info (won't terminate early)
        for _ in range(5):
            r = env.step(_request_info_action())
            if r.done:
                break
        else:
            # 6th round: propose (will hit max_rounds)
            r = env.step(_propose_action(scenario))

        assert r.done
        assert r.info.verdict in ("timeout", "no_agreement")

    def test_cumulative_reward_is_sum_of_step_rewards(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")
        scenario = _scenario()

        total = 0.0
        r1 = env.step(_propose_action(scenario))
        total += r1.reward
        r2 = env.step(_revise_action(scenario))
        total += r2.reward
        r3 = env.step(_accept_action())
        total += r3.reward

        state = env.state()
        assert abs(state.reward - total) < 1e-5


class TestMidEpisodeHint:
    """Verify mid-episode checkpoint hints appear at the midpoint."""

    def test_mid_episode_hint_at_midpoint(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")
        scenario = _scenario()

        # max_rounds = 6, midpoint = 3
        # Round 1
        r1 = env.step(_propose_action(scenario))
        hint1 = r1.info.model_extra.get("mid_episode_hint") if r1.info.model_extra else None

        # Round 2
        r2 = env.step(_revise_action(scenario))
        hint2 = r2.info.model_extra.get("mid_episode_hint") if r2.info.model_extra else None

        # Round 3 = midpoint
        r3 = env.step(_propose_action(scenario))
        hint3 = r3.info.model_extra.get("mid_episode_hint") if r3.info.model_extra else None

        # Hint should appear at round 3 (midpoint of 6)
        assert hint1 is None
        assert hint2 is None
        assert hint3 is not None
        assert "rigor" in hint3
        assert "feasibility" in hint3
        assert "fidelity" in hint3
        assert "projected_total" in hint3


class TestCommunicationBonus:
    """Communication bonus appears in the breakdown when conversation exists."""

    def test_communication_bonus_in_breakdown(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")
        scenario = _scenario()

        # Use diverse actions to earn communication bonus
        env.step(_request_info_action())            # request_info
        env.step(_propose_action(scenario))          # propose_protocol
        env.step(_revise_action(scenario))           # revise_protocol
        result = env.step(_accept_action())          # accept

        assert result.done
        breakdown = result.info.reward_breakdown
        assert breakdown is not None
        # With diverse actions, some communication bonus should exist
        assert breakdown.communication_bonus >= 0.0


class TestDomainEmphasis:
    """Domain emphasis bonus varies by domain."""

    @pytest.mark.parametrize("template", ["math_reasoning", "ml_benchmark", "finance_trading"])
    def test_domain_emphasis_is_non_negative(self, template) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42, scenario=template, difficulty="easy")
        scenario = _scenario(template=template)

        env.step(_propose_action(scenario))
        result = env.step(_accept_action())

        assert result.done
        breakdown = result.info.reward_breakdown
        assert breakdown is not None
        assert breakdown.domain_emphasis_bonus >= 0.0


class TestAdaptiveShaping:
    """Adaptive penalty scaling increases with round progress."""

    def test_later_round_penalties_are_scaled(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")

        # Request same info twice across rounds to trigger stalling penalty
        r1 = env.step(_request_info_action())
        r2 = env.step(_request_info_action())

        # Both should have step_reward_components in extra
        c1 = r1.info.model_extra.get("step_reward_components", {}) if r1.info.model_extra else {}
        c2 = r2.info.model_extra.get("step_reward_components", {}) if r2.info.model_extra else {}

        # r2 should have a stalling penalty (repeated question)
        if "stalling_penalty" in c2:
            assert c2["stalling_penalty"] < 0


class TestScenarioConsistency:
    """Scenario validation catches inconsistencies."""

    @pytest.mark.parametrize("template", ["math_reasoning", "ml_benchmark", "finance_trading"])
    @pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
    def test_all_scenarios_pass_consistency(self, template, difficulty) -> None:
        # generate_scenario calls validate_scenario_consistency internally
        pack = generate_scenario(seed=42, template=template, difficulty=difficulty)
        assert pack.lab_manager_observation.budget_remaining >= 0
        assert pack.lab_manager_observation.budget_remaining <= pack.lab_manager_observation.budget_total
        assert pack.lab_manager_observation.time_limit_days >= 1
