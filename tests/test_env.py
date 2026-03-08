"""Tests for ENV 01–08 and JDG 04–05.

TST 01: reset returns valid observations
TST 02: valid step advances round, terminal path returns correct shape
TST 03: invalid action returns structured error, env survives
"""

from __future__ import annotations

import pytest

from replicalab.env import ReplicaLabEnv
from replicalab.models import (
    Protocol,
    RewardBreakdown,
    ScientistAction,
)
from replicalab.scenarios import generate_scenario
from replicalab.scoring.rubric import build_reward_breakdown, compute_total_reward


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scenario(
    template: str = "math_reasoning",
    difficulty: str = "easy",
    seed: int = 42,
):
    return generate_scenario(seed=seed, template=template, difficulty=difficulty)


def _good_action(scenario) -> ScientistAction:
    """Build a valid propose_protocol action that fits the scenario."""
    lab = scenario.lab_manager_observation
    spec = scenario.hidden_reference_spec
    return ScientistAction(
        action_type="propose_protocol",
        sample_size=10,
        controls=["baseline", "ablation"],
        technique=spec.summary[:60] if spec.summary else "replication_plan",
        duration_days=max(1, min(2, lab.time_limit_days)),
        required_equipment=(
            list(lab.equipment_available[:1]) if lab.equipment_available else []
        ),
        required_reagents=(
            list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else []
        ),
        questions=[],
        rationale=(
            f"Plan addresses: {', '.join(spec.required_elements[:2])}. "
            f"Target metric: {spec.target_metric}. "
            f"Target value: {spec.target_value}. "
            "Stay within budget and schedule."
        ),
    )


def _accept_action() -> ScientistAction:
    """Build a valid accept action."""
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


def _good_protocol(scenario) -> Protocol:
    """Build a well-formed protocol aligned to the scenario."""
    lab = scenario.lab_manager_observation
    spec = scenario.hidden_reference_spec
    return Protocol(
        sample_size=10,
        controls=["baseline", "ablation"],
        technique=spec.summary[:60] if spec.summary else "replication_plan",
        duration_days=max(1, min(2, lab.time_limit_days)),
        required_equipment=(
            list(lab.equipment_available[:1]) if lab.equipment_available else []
        ),
        required_reagents=(
            list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else []
        ),
        rationale=(
            f"Plan addresses: {', '.join(spec.required_elements[:2])}. "
            f"Target metric: {spec.target_metric}. "
            f"Target value: {spec.target_value}. "
            "Stay within budget and schedule."
        ),
    )


def _bad_duration_action() -> ScientistAction:
    return ScientistAction(
        action_type="propose_protocol",
        sample_size=5,
        controls=["baseline"],
        technique="some technique",
        duration_days=999,
        required_equipment=[],
        required_reagents=[],
        questions=[],
        rationale="Duration is impossibly long for this scenario.",
    )


def _canonical_step(result) -> dict:
    data = result.model_dump()
    data["info"].pop("episode_id", None)
    return data


def _run_seeded_sequence(
    *,
    seed: int,
    template: str,
    difficulty: str,
    action_builder,
):
    env = ReplicaLabEnv()
    obs = env.reset(seed=seed, scenario=template, difficulty=difficulty)
    scenario = _scenario(template, difficulty, seed=seed)
    actions = action_builder(scenario)
    results = [env.step(action) for action in actions]
    return obs.model_dump(), [_canonical_step(r) for r in results], env.state().model_dump()


# ---------------------------------------------------------------------------
# TST 01 — reset returns valid observations
# ---------------------------------------------------------------------------


class TestReset:
    """TST 01: reset() returns a well-formed Observation."""

    def test_reset_returns_observation_with_both_roles(self) -> None:
        env = ReplicaLabEnv()
        obs = env.reset(seed=42, scenario="math_reasoning", difficulty="easy")

        assert obs.scientist is not None
        assert obs.lab_manager is not None

    def test_reset_scientist_fields_populated(self) -> None:
        env = ReplicaLabEnv()
        obs = env.reset(seed=42, scenario="ml_benchmark", difficulty="easy")

        s = obs.scientist
        assert s.paper_title
        assert s.paper_hypothesis
        assert s.experiment_goal
        assert s.round_number == 0
        assert s.max_rounds > 0
        assert s.current_protocol is None
        assert s.conversation_history == []

    def test_reset_lab_manager_fields_populated(self) -> None:
        env = ReplicaLabEnv()
        obs = env.reset(seed=42, scenario="finance_trading", difficulty="easy")

        lm = obs.lab_manager
        assert lm.budget_total > 0
        assert lm.budget_remaining > 0
        assert lm.staff_count > 0
        assert lm.time_limit_days > 0
        assert lm.round_number == 0

    def test_reset_preserves_booked_and_out_of_stock(self) -> None:
        """ENV 02: booked/out-of-stock data comes from the scenario pack,
        not hardcoded empty lists."""
        env = ReplicaLabEnv()
        # hard difficulty is more likely to have unavailable resources
        obs = env.reset(seed=42, scenario="ml_benchmark", difficulty="hard")
        lm = obs.lab_manager

        # The observation should carry scenario data (may or may not have
        # booked items depending on scenario, but the lists should exist)
        assert isinstance(lm.equipment_booked, list)
        assert isinstance(lm.reagents_out_of_stock, list)
        assert isinstance(lm.safety_restrictions, list)
        assert len(lm.safety_restrictions) > 0  # always has at least one

    def test_reset_state_round_zero(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=1)

        s = env.state()
        assert s.round_number == 0
        assert s.done is False
        assert s.agreement_reached is False

    def test_reset_generates_episode_id(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=1)

        eid = env.episode_id()
        assert eid
        assert len(eid) > 10  # UUID

    def test_reset_clears_previous_episode(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=1, scenario="math_reasoning")
        first_id = env.episode_id()

        env.reset(seed=2, scenario="ml_benchmark")
        second_id = env.episode_id()

        assert first_id != second_id
        assert env.state().round_number == 0

    def test_reset_all_templates_and_difficulties(self) -> None:
        env = ReplicaLabEnv()
        for template in ("math_reasoning", "ml_benchmark", "finance_trading"):
            for difficulty in ("easy", "medium", "hard"):
                obs = env.reset(seed=7, scenario=template, difficulty=difficulty)
                assert obs.scientist is not None
                assert obs.lab_manager is not None


# ---------------------------------------------------------------------------
# TST 03 — invalid action returns structured error, env survives
# ---------------------------------------------------------------------------


class TestInvalidAction:
    """TST 03: env returns structured error for invalid proposals."""

    def test_invalid_duration_returns_error_string(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario("math_reasoning", "easy")
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")

        # duration exceeds time limit
        bad_action = ScientistAction(
            action_type="propose_protocol",
            sample_size=5,
            controls=["baseline"],
            technique="some technique",
            duration_days=999,
            required_equipment=[],
            required_reagents=[],
            questions=[],
            rationale="This has way too long a duration for the lab.",
        )
        result = env.step(bad_action)

        assert result.done is False
        assert result.info.error is not None
        assert "Validation errors" in result.info.error

    def test_env_survives_after_invalid_action(self) -> None:
        """After returning an error, the env still accepts valid actions."""
        env = ReplicaLabEnv()
        scenario = _scenario("math_reasoning", "easy")
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")

        # Send invalid action
        bad_action = ScientistAction(
            action_type="propose_protocol",
            sample_size=5,
            controls=["baseline"],
            technique="some technique",
            duration_days=999,
            required_equipment=[],
            required_reagents=[],
            questions=[],
            rationale="Way too long duration for the lab to handle.",
        )
        error_result = env.step(bad_action)
        assert error_result.info.error is not None

        # Now send a valid action — env should still work
        good = _good_action(scenario)
        result = env.step(good)
        assert result.info.error is None
        assert result.done is False

    def test_invalid_action_does_not_advance_round(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42, scenario="math_reasoning", difficulty="easy")

        bad_action = ScientistAction(
            action_type="propose_protocol",
            sample_size=5,
            controls=["baseline"],
            technique="some technique",
            duration_days=999,
            required_equipment=[],
            required_reagents=[],
            questions=[],
            rationale="Duration is impossibly long for this scenario.",
        )
        result = env.step(bad_action)

        assert result.info.error is not None
        assert env.state().round_number == 0

    def test_request_info_always_passes_validation(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42)
        result = env.step(_request_info_action())

        assert result.info.error is None
        assert result.done is False


# ---------------------------------------------------------------------------
# TST 02 — valid step advances round, terminal path
# ---------------------------------------------------------------------------


class TestStep:
    """TST 02: step() advances rounds and terminal path returns correct shape."""

    def test_step_advances_round_number(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        action = _good_action(scenario)
        result = env.step(action)

        assert env.state().round_number == 1
        assert result.done is False
        assert result.reward == 0.0

    def test_step_returns_observations(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        result = env.step(_good_action(scenario))

        assert result.observation is not None
        assert result.observation.scientist is not None
        assert result.observation.lab_manager is not None
        assert result.observation.scientist.round_number == 1

    def test_step_records_conversation_history(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        env.step(_good_action(scenario))

        s = env.state()
        # Should have 2 entries: scientist + lab manager
        assert len(s.conversation_history) == 2
        assert s.conversation_history[0].role == "scientist"
        assert s.conversation_history[1].role == "lab_manager"

    def test_accept_with_protocol_terminates(self) -> None:
        """Scientist accept with an existing protocol → done."""
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        # First propose a protocol
        env.step(_good_action(scenario))

        # Then accept
        result = env.step(_accept_action())

        assert result.done is True
        assert result.info.agreement_reached is True

    def test_accept_terminal_step_has_real_reward(self) -> None:
        """ENV 06: terminal accept computes real judge scores, not stub 0.8."""
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        env.step(_good_action(scenario))
        result = env.step(_accept_action())

        assert result.done is True
        assert result.reward > 0.0
        assert result.info.reward_breakdown is not None

        rb = result.info.reward_breakdown
        assert 0.0 <= rb.rigor <= 1.0
        assert 0.0 <= rb.feasibility <= 1.0
        assert 0.0 <= rb.fidelity <= 1.0
        # Verify it's not the old stub 0.8
        assert not (rb.rigor == 0.8 and rb.feasibility == 0.8 and rb.fidelity == 0.8)

    def test_max_rounds_terminates(self) -> None:
        """Reaching max_rounds terminates without agreement."""
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        max_r = env.state().max_rounds
        for i in range(max_r):
            result = env.step(_good_action(scenario))

        assert result.done is True
        assert result.info.agreement_reached is False
        assert result.reward == 0.0

    def test_step_info_has_round_and_episode_id(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        result = env.step(_good_action(scenario))

        assert result.info.round == 1
        assert result.info.episode_id == env.episode_id()

    def test_full_episode_propose_then_accept(self) -> None:
        """Full 2-step episode: propose → accept."""
        env = ReplicaLabEnv()
        scenario = _scenario("ml_benchmark", "easy")
        env.reset(seed=42, scenario="ml_benchmark", difficulty="easy")

        r1 = env.step(_good_action(scenario))
        assert not r1.done

        r2 = env.step(_accept_action())
        assert r2.done
        assert r2.info.agreement_reached
        assert r2.reward > 0


# ---------------------------------------------------------------------------
# ENV 07 — state() returns deep snapshot
# ---------------------------------------------------------------------------


class TestStateSnapshot:
    """ENV 07: state() returns a deep copy, not a reference."""

    def test_state_is_deep_copy(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=42)

        s1 = env.state()
        s1.round_number = 999  # mutate the snapshot

        s2 = env.state()
        assert s2.round_number == 0  # env state unaffected

    def test_state_history_is_independent(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)
        env.step(_good_action(scenario))

        s1 = env.state()
        original_len = len(s1.conversation_history)
        s1.conversation_history.clear()

        s2 = env.state()
        assert len(s2.conversation_history) == original_len


# ---------------------------------------------------------------------------
# ENV 08 — close() and _ensure_open()
# ---------------------------------------------------------------------------


class TestCloseReopen:
    """ENV 08: close/reopen lifecycle."""

    def test_close_is_idempotent(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=1)
        env.close()
        env.close()  # should not raise

    def test_step_after_close_raises(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=1)
        env.close()

        with pytest.raises(RuntimeError, match="closed"):
            env.step(_good_action(scenario))

    def test_reset_reopens_closed_env(self) -> None:
        env = ReplicaLabEnv()
        env.reset(seed=1)
        env.close()

        # reset should reopen
        obs = env.reset(seed=2)
        assert obs.scientist is not None

        # step should work again
        scenario = _scenario()
        result = env.step(_good_action(scenario))
        assert result.info.error is None


# ---------------------------------------------------------------------------
# JDG 04-05 — rubric unit tests
# ---------------------------------------------------------------------------


class TestRubric:
    """JDG 04-05: compute_total_reward and build_reward_breakdown."""

    def test_compute_total_reward_formula(self) -> None:
        """10 × rigor × feasibility × fidelity + bonuses − penalties."""
        rb = RewardBreakdown(
            rigor=1.0,
            feasibility=1.0,
            fidelity=1.0,
            efficiency_bonus=0.5,
            communication_bonus=0.0,
            penalties={},
        )
        total = compute_total_reward(rb)
        assert total == 10.5  # 10*1*1*1 + 0.5

    def test_compute_total_reward_with_penalties(self) -> None:
        rb = RewardBreakdown(
            rigor=0.8,
            feasibility=0.9,
            fidelity=0.7,
            efficiency_bonus=0.0,
            communication_bonus=0.0,
            penalties={"timeout": 1.0, "invalid": 0.5},
        )
        expected = 10 * 0.8 * 0.9 * 0.7 - 1.5  # 5.04 - 1.5 = 3.54
        assert abs(compute_total_reward(rb) - expected) < 0.001

    def test_compute_total_reward_zero_scores(self) -> None:
        rb = RewardBreakdown(rigor=0.0, feasibility=0.5, fidelity=0.5)
        assert compute_total_reward(rb) == 0.0

    def test_build_reward_breakdown_returns_valid_scores(self) -> None:
        scenario = _scenario("ml_benchmark", "easy")
        protocol = _good_protocol(scenario)

        breakdown = build_reward_breakdown(
            protocol=protocol,
            scenario=scenario,
            rounds_used=1,
            max_rounds=6,
        )

        assert 0.0 <= breakdown.rigor <= 1.0
        assert 0.0 <= breakdown.feasibility <= 1.0
        assert 0.0 <= breakdown.fidelity <= 1.0
        assert breakdown.efficiency_bonus >= 0.0

    def test_build_reward_breakdown_efficiency_bonus(self) -> None:
        """Finishing in fewer rounds gives a higher bonus."""
        scenario = _scenario()
        protocol = _good_protocol(scenario)

        fast = build_reward_breakdown(protocol, scenario, rounds_used=1, max_rounds=6)
        slow = build_reward_breakdown(protocol, scenario, rounds_used=5, max_rounds=6)

        assert fast.efficiency_bonus > slow.efficiency_bonus

    def test_build_reward_breakdown_is_deterministic(self) -> None:
        scenario = _scenario("finance_trading", "medium")
        protocol = _good_protocol(scenario)

        b1 = build_reward_breakdown(protocol, scenario, rounds_used=2, max_rounds=6)
        b2 = build_reward_breakdown(protocol, scenario, rounds_used=2, max_rounds=6)

        assert b1.rigor == b2.rigor
        assert b1.feasibility == b2.feasibility
        assert b1.fidelity == b2.fidelity
        assert b1.efficiency_bonus == b2.efficiency_bonus

    def test_total_reward_matches_manual_calculation(self) -> None:
        scenario = _scenario("math_reasoning", "easy")
        protocol = _good_protocol(scenario)

        breakdown = build_reward_breakdown(protocol, scenario, rounds_used=2, max_rounds=6)
        total = compute_total_reward(breakdown)
        expected = (
            10.0 * breakdown.rigor * breakdown.feasibility * breakdown.fidelity
            + breakdown.efficiency_bonus
            + breakdown.communication_bonus
            - sum(breakdown.penalties.values())
        )
        assert abs(total - expected) < 0.0001


# ---------------------------------------------------------------------------
# ENV 06 — terminal reward wiring
# ---------------------------------------------------------------------------


class TestEnvReward:
    """ENV 06: real judge scoring at terminal steps."""

    def test_agreement_terminal_has_breakdown_notes_verdict(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        env.step(_good_action(scenario))
        result = env.step(_accept_action())

        assert result.done
        assert result.info.reward_breakdown is not None
        assert result.info.judge_notes is not None
        assert result.info.verdict == "accept"
        assert "rigor" in result.info.judge_notes

    def test_no_agreement_terminal_is_deterministic(self) -> None:
        def run_timeout_episode():
            env = ReplicaLabEnv()
            scenario = _scenario()
            env.reset(seed=42)
            max_r = env.state().max_rounds
            result = None
            for _ in range(max_r):
                result = env.step(_good_action(scenario))
            return result

        r1 = run_timeout_episode()
        r2 = run_timeout_episode()

        assert r1.reward == r2.reward
        assert r1.info.verdict == r2.info.verdict

    def test_timeout_verdict(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        max_r = env.state().max_rounds
        result = None
        for _ in range(max_r):
            result = env.step(_good_action(scenario))

        assert result.done
        assert result.info.verdict == "timeout"
        assert result.info.reward_breakdown is not None
        assert result.reward == 0.0

    def test_episode_state_stores_final_scores(self) -> None:
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        env.step(_good_action(scenario))
        env.step(_accept_action())

        s = env.state()
        assert s.done
        assert s.agreement_reached
        assert s.rigor_score > 0.0
        assert s.feasibility_score > 0.0
        assert s.fidelity_score > 0.0
        assert s.reward > 0.0


# ---------------------------------------------------------------------------
# ENV 11 — canonical judge audit payload in terminal outputs
# ---------------------------------------------------------------------------


class TestJudgeAudit:
    """ENV 11: structured audit from JDG 11 threaded into terminal outputs."""

    def test_accept_terminal_has_full_audit(self) -> None:
        """Agreement terminal step exposes all audit fields."""
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        env.step(_good_action(scenario))
        result = env.step(_accept_action())

        assert result.done
        assert result.info.verdict == "accept"
        assert result.info.judge_notes is not None
        assert len(result.info.judge_notes) > 0
        # judge_notes from explain_reward includes rubric component labels
        assert "Rigor:" in result.info.judge_notes
        assert "Feasibility:" in result.info.judge_notes
        assert "Fidelity:" in result.info.judge_notes
        assert "Total reward:" in result.info.judge_notes
        assert isinstance(result.info.top_failure_reasons, list)

    def test_timeout_terminal_has_audit_with_timeout_reason(self) -> None:
        """Timeout terminal step has verdict=timeout and failure reason."""
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        max_r = env.state().max_rounds
        result = None
        for _ in range(max_r):
            result = env.step(_good_action(scenario))

        assert result.done
        assert result.info.verdict == "timeout"
        assert isinstance(result.info.top_failure_reasons, list)
        assert any(
            "round limit" in reason.lower()
            for reason in result.info.top_failure_reasons
        )

    def test_non_terminal_step_has_empty_audit(self) -> None:
        """Non-terminal steps do not carry audit payload."""
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        result = env.step(_good_action(scenario))

        assert not result.done
        assert result.info.judge_notes is None
        assert result.info.verdict is None
        assert result.info.top_failure_reasons == []

    def test_state_after_accept_carries_audit_fields(self) -> None:
        """EpisodeState contains judge_notes, verdict, top_failure_reasons."""
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        env.step(_good_action(scenario))
        env.step(_accept_action())

        s = env.state()
        assert s.verdict == "accept"
        assert len(s.judge_notes) > 0
        assert "Rigor:" in s.judge_notes
        assert isinstance(s.top_failure_reasons, list)

    def test_state_after_timeout_carries_audit_fields(self) -> None:
        """EpisodeState after timeout has correct verdict and reasons."""
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        max_r = env.state().max_rounds
        for _ in range(max_r):
            env.step(_good_action(scenario))

        s = env.state()
        assert s.verdict == "timeout"
        assert len(s.judge_notes) > 0
        assert any(
            "round limit" in reason.lower()
            for reason in s.top_failure_reasons
        )

    def test_audit_deterministic(self) -> None:
        """Same episode produces identical audit output."""
        def run_episode():
            env = ReplicaLabEnv()
            scenario = _scenario()
            env.reset(seed=42)
            env.step(_good_action(scenario))
            return env.step(_accept_action())

        r1 = run_episode()
        r2 = run_episode()

        assert r1.info.judge_notes == r2.info.judge_notes
        assert r1.info.verdict == r2.info.verdict
        assert r1.info.top_failure_reasons == r2.info.top_failure_reasons

    def test_state_audit_fields_empty_before_terminal(self) -> None:
        """EpisodeState audit fields are empty before a terminal step."""
        env = ReplicaLabEnv()
        scenario = _scenario()
        env.reset(seed=42)

        env.step(_good_action(scenario))

        s = env.state()
        assert s.judge_notes == ""
        assert s.verdict == ""
        assert s.top_failure_reasons == []


# ---------------------------------------------------------------------------
# ENV 10 — deterministic replay and broader environment regression
# ---------------------------------------------------------------------------


class TestReplayDeterminism:
    """ENV 10: same seed + same actions => same trajectory and final state."""

    @pytest.mark.parametrize(
        ("template", "difficulty"),
        [
            ("math_reasoning", "easy"),
            ("ml_benchmark", "medium"),
            ("finance_trading", "hard"),
        ],
    )
    def test_same_seed_same_initial_observation(
        self,
        template: str,
        difficulty: str,
    ) -> None:
        env1 = ReplicaLabEnv()
        env2 = ReplicaLabEnv()

        obs1 = env1.reset(seed=17, scenario=template, difficulty=difficulty)
        obs2 = env2.reset(seed=17, scenario=template, difficulty=difficulty)

        assert obs1.model_dump() == obs2.model_dump()

    @pytest.mark.parametrize(
        ("template", "difficulty"),
        [
            ("math_reasoning", "easy"),
            ("ml_benchmark", "medium"),
            ("finance_trading", "hard"),
        ],
    )
    def test_same_seed_same_action_sequence_same_trajectory(
        self,
        template: str,
        difficulty: str,
    ) -> None:
        def build_actions(scenario):
            return [_good_action(scenario), _accept_action()]

        first = _run_seeded_sequence(
            seed=23,
            template=template,
            difficulty=difficulty,
            action_builder=build_actions,
        )
        second = _run_seeded_sequence(
            seed=23,
            template=template,
            difficulty=difficulty,
            action_builder=build_actions,
        )

        assert first == second

    @pytest.mark.parametrize("template", ["math_reasoning", "ml_benchmark", "finance_trading"])
    def test_timeout_replay_is_deterministic(self, template: str) -> None:
        def build_actions(scenario):
            return [
                _good_action(scenario)
                for _ in range(scenario.scientist_observation.max_rounds)
            ]

        first = _run_seeded_sequence(
            seed=31,
            template=template,
            difficulty="medium",
            action_builder=build_actions,
        )
        second = _run_seeded_sequence(
            seed=31,
            template=template,
            difficulty="medium",
            action_builder=build_actions,
        )

        _obs1, steps1, state1 = first
        _obs2, steps2, state2 = second
        assert steps1 == steps2
        assert state1 == state2
        assert steps1[-1]["done"] is True
        assert steps1[-1]["info"]["verdict"] == "timeout"

    def test_invalid_action_replay_is_deterministic(self) -> None:
        def build_actions(_scenario):
            return [_bad_duration_action(), _bad_duration_action()]

        first = _run_seeded_sequence(
            seed=41,
            template="math_reasoning",
            difficulty="easy",
            action_builder=build_actions,
        )
        second = _run_seeded_sequence(
            seed=41,
            template="math_reasoning",
            difficulty="easy",
            action_builder=build_actions,
        )

        assert first == second
        _obs, steps, state = first
        assert steps[0]["info"]["error"] is not None
        assert steps[0]["done"] is False
        assert state["round_number"] == 0

    @pytest.mark.parametrize("template", ["math_reasoning", "ml_benchmark", "finance_trading"])
    def test_terminal_audit_payload_is_replay_stable(self, template: str) -> None:
        def build_actions(scenario):
            return [_good_action(scenario), _accept_action()]

        _obs1, steps1, state1 = _run_seeded_sequence(
            seed=59,
            template=template,
            difficulty="easy",
            action_builder=build_actions,
        )
        _obs2, steps2, state2 = _run_seeded_sequence(
            seed=59,
            template=template,
            difficulty="easy",
            action_builder=build_actions,
        )

        assert steps1[-1]["info"]["judge_notes"] == steps2[-1]["info"]["judge_notes"]
        assert steps1[-1]["info"]["verdict"] == steps2[-1]["info"]["verdict"]
        assert (
            steps1[-1]["info"]["top_failure_reasons"]
            == steps2[-1]["info"]["top_failure_reasons"]
        )
        assert state1["judge_notes"] == state2["judge_notes"]
        assert state1["verdict"] == state2["verdict"]
        assert state1["top_failure_reasons"] == state2["top_failure_reasons"]
