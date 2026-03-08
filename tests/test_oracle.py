from __future__ import annotations

import json

from replicalab.agents.lab_manager_agent import LabManagerAgent
from replicalab.env import ReplicaLabEnv
from replicalab.models import ScientistAction
from replicalab.oracle import Oracle
from replicalab.oracle_models import (
    AdjudicatorRoundScore,
    EnvironmentEvent,
    OracleLabManagerObservation,
    PostMortem,
    Scenario,
)


def _scenario_payload() -> dict:
    return {
        "paper": {
            "title": "Reproducing a Small Vision Benchmark",
            "domain": "ml_benchmark",
            "claim": "A compact model can recover >90% of reference accuracy under budget.",
            "method_summary": "Train a compact CNN with fixed augmentations and evaluate on a held-out split.",
            "original_sample_size": 1200,
            "original_duration_days": 3,
            "original_technique": "compact_cnn",
            "required_controls": ["seed_control", "baseline_model"],
            "required_equipment": ["GPU cluster", "validation server"],
            "required_reagents": ["dataset snapshot"],
            "statistical_test": "accuracy_gap",
        },
        "lab_constraints": {
            "budget_total": 2400.0,
            "budget_remaining": 2400.0,
            "equipment": [
                {
                    "name": "GPU cluster",
                    "available": True,
                    "condition": "shared_booking",
                    "booking_conflicts": ["Monday"],
                    "cost_per_use": 250.0,
                },
                {
                    "name": "Validation server",
                    "available": True,
                    "condition": "operational",
                    "booking_conflicts": [],
                    "cost_per_use": 20.0,
                },
            ],
            "reagents": [
                {
                    "name": "dataset snapshot",
                    "in_stock": True,
                    "quantity_available": 1.0,
                    "unit": "copy",
                    "lead_time_days": 0,
                    "cost": 0.0,
                }
            ],
            "staff": [
                {
                    "name": "Alex",
                    "role": "engineer",
                    "available_days": ["Monday", "Tuesday"],
                    "skills": ["training", "evaluation"],
                }
            ],
            "max_duration_days": 5,
            "safety_rules": ["No external internet during training."],
            "valid_substitutions": [
                {
                    "original": "GPU cluster",
                    "substitute": "single high-memory GPU",
                    "validity": "acceptable_with_caveats",
                    "caveats": "Lower throughput is acceptable if evaluation fidelity is preserved.",
                }
            ],
        },
        "minimum_viable_spec": {
            "min_sample_size": 800,
            "must_keep_controls": ["seed_control", "baseline_model"],
            "acceptable_techniques": ["compact_cnn", "distilled_cnn"],
            "min_duration_days": 2,
            "critical_equipment": ["Validation server"],
            "flexible_equipment": ["GPU cluster"],
            "critical_reagents": ["dataset snapshot"],
            "flexible_reagents": [],
            "power_threshold": 0.8,
        },
        "difficulty": "medium",
        "narrative_hook": "The compute team just reduced your preferred GPU window.",
    }


def _round_score_payload() -> dict:
    return {
        "rigor_flags": ["kept baseline_model"],
        "feasibility_flags": ["GPU window narrowed"],
        "info_gain": 0.6,
        "protocol_delta": 0.4,
        "momentum": 0.7,
        "contradiction_detected": False,
        "stalling_detected": False,
        "step_reward": 0.55,
        "notes": "Scientist asked a useful scheduling question and preserved controls.",
    }


def _post_mortem_payload() -> dict:
    return {
        "overall_summary": "The Scientist converged on a feasible compact CNN plan.",
        "rigor_explanation": "Controls and the validation server were preserved.",
        "feasibility_explanation": "The final plan fit the available compute and duration window.",
        "fidelity_explanation": "The protocol stayed close to the benchmark setup.",
        "key_decisions": ["Kept seed control", "Accepted lower-throughput compute"],
        "missed_opportunities": ["Could have asked about booking conflicts earlier"],
        "comparison_note": "An optimal Scientist would have requested the alternate GPU window one round sooner.",
    }


class _FakeMessagesAPI:
    def __init__(self, payloads: list[dict]) -> None:
        self._payloads = payloads
        self.calls = 0

    def create(self, **_: object):
        payload = self._payloads[self.calls]
        self.calls += 1

        class _Chunk:
            def __init__(self, text: str) -> None:
                self.text = text

        class _Response:
            def __init__(self, text: str) -> None:
                self.content = [_Chunk(text)]

        return _Response(json.dumps(payload))


class _FakeClient:
    def __init__(self, payloads: list[dict]) -> None:
        self.messages = _FakeMessagesAPI(payloads)


def test_oracle_generate_scenario_parses_json() -> None:
    oracle = Oracle(_FakeClient([_scenario_payload()]))

    scenario = oracle.generate_scenario(seed=7, difficulty="medium", domain="ml_benchmark")

    assert isinstance(scenario, Scenario)
    assert scenario.paper.domain == "ml_benchmark"
    assert scenario.lab_constraints.equipment[0].name == "GPU cluster"


def test_oracle_score_round_parses_structured_payload() -> None:
    oracle = Oracle(_FakeClient([_round_score_payload()]))
    scenario = Scenario.model_validate(_scenario_payload())
    action = ScientistAction(
        action_type="request_info",
        sample_size=0,
        controls=[],
        technique="",
        duration_days=0,
        required_equipment=[],
        required_reagents=[],
        questions=["When is the GPU cluster available?"],
        rationale="",
    )
    lab_manager = LabManagerAgent(_FakeClient([{
        "response_type": "feasibility_report",
        "feasible": False,
        "issues": ["GPU cluster is shared-booked on Monday"],
        "suggestions": ["Use the single high-memory GPU instead"],
        "cost_estimate": 250.0,
        "time_estimate_days": 3,
        "message": "The GPU cluster is shared-booked Monday; the single high-memory GPU is acceptable with caveats.",
    }]))
    response = lab_manager.respond(
        OracleLabManagerObservation(
            lab_constraints=scenario.lab_constraints,
            current_protocol=None,
            scientist_action=action,
            round_number=1,
        )
    )

    score = oracle.score_round(
        scenario=scenario,
        round_number=1,
        scientist_action=action,
        lab_manager_response=response,
        conversation_history=[],
        current_protocol=None,
        previous_scores=[],
    )

    assert isinstance(score, AdjudicatorRoundScore)
    assert score.step_reward == 0.55


def test_oracle_maybe_inject_event_returns_optional_event() -> None:
    oracle = Oracle(_FakeClient([{"inject": True, "event": {
        "event_type": "budget_cut",
        "description": "Finance reduced the remaining budget.",
        "state_changes": {"lab_constraints.budget_remaining": 1800.0},
        "severity": "moderate",
    }}]))

    event = oracle.maybe_inject_event(
        scenario=Scenario.model_validate(_scenario_payload()),
        round_number=3,
        current_protocol=None,
        conversation_history=[],
        inject_enabled=True,
    )

    assert isinstance(event, EnvironmentEvent)
    assert event.event_type == "budget_cut"


def test_oracle_generate_post_mortem_parses_json() -> None:
    oracle = Oracle(_FakeClient([_post_mortem_payload()]))
    from replicalab.oracle_models import AdjudicatorTerminalScore

    post_mortem = oracle.generate_post_mortem(
        scenario=Scenario.model_validate(_scenario_payload()),
        final_protocol={"technique": "compact_cnn"},
        conversation_history=[],
        terminal_score=AdjudicatorTerminalScore(
            rigor=0.9,
            feasibility=0.8,
            fidelity=0.85,
            parsimony=0.9,
            robustness=0.8,
            power_preservation=0.8,
            efficiency_bonus=0.2,
            communication_bonus=0.1,
            penalties={},
            terminal_reward=5.0,
            total_reward=5.6,
        ),
    )

    assert isinstance(post_mortem, PostMortem)
    assert "feasible compact CNN plan" in post_mortem.overall_summary


def test_env_can_reset_from_oracle_scenario_without_changing_outer_contract() -> None:
    class _FakeOracle:
        def __init__(self) -> None:
            self.scenario = Scenario.model_validate(_scenario_payload())

        def generate_scenario(self, seed: int, difficulty: str, domain: str) -> Scenario:
            assert seed == 11
            assert difficulty == "medium"
            assert domain == "ml_benchmark"
            return self.scenario

        def score_round(self, **_: object):
            return AdjudicatorRoundScore.model_validate(_round_score_payload())

        def maybe_inject_event(self, **_: object):
            return None

        def generate_post_mortem(self, **_: object):
            return PostMortem.model_validate(_post_mortem_payload())

    env = ReplicaLabEnv(
        oracle=_FakeOracle(),
        enable_oracle_post_mortem=True,
    )
    observation = env.reset(seed=11, scenario="ml_benchmark", difficulty="medium")

    assert observation.scientist is not None
    assert observation.scientist.paper_title == "Reproducing a Small Vision Benchmark"
    assert observation.lab_manager is not None
    assert "Validation server" in observation.lab_manager.equipment_available

