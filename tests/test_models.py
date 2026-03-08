from __future__ import annotations

import pytest
from pydantic import ValidationError

from replicalab.models import (
    ConversationEntry,
    EpisodeLog,
    EpisodeState,
    LabManagerAction,
    LabManagerActionType,
    LabManagerObservation,
    Observation,
    Protocol,
    RewardBreakdown,
    ScientistAction,
    ScientistActionType,
    ScientistObservation,
    StepInfo,
    StepResult,
)


def _valid_protocol_action() -> dict:
    return {
        "action_type": "propose_protocol",
        "sample_size": 48,
        "controls": ["vehicle_control", "positive_control"],
        "technique": "wst1_assay",
        "duration_days": 5,
        "required_equipment": ["plate_reader", "co2_incubator"],
        "required_reagents": ["wst1", "dmso", "drug_x"],
        "questions": [],
        "rationale": "Keeps the core readout while using common lab equipment.",
    }


def _valid_lab_manager_action() -> dict:
    return {
        "action_type": "suggest_alternative",
        "feasible": False,
        "budget_ok": True,
        "equipment_ok": False,
        "reagents_ok": True,
        "schedule_ok": True,
        "staff_ok": True,
        "suggested_technique": "manual_cell_counting",
        "suggested_sample_size": 32,
        "suggested_controls": ["vehicle_control", "positive_control"],
        "explanation": "The plate reader is booked, so use manual counting.",
    }


def _valid_observation_payload() -> dict:
    return {
        "scientist": {
            "paper_title": "Drug X reduces glioblastoma cell viability",
            "paper_hypothesis": "Drug X reduces viability in a dose-dependent manner.",
            "paper_method": "96-well viability assay with 24h incubation and absorbance readout.",
            "paper_key_finding": "The highest dose reduced viability by about 40 percent.",
            "experiment_goal": "Replicate the dose-response trend without dropping essential controls.",
            "conversation_history": [
                {
                    "role": "scientist",
                    "message": "I propose a manual counting protocol.",
                    "round_number": 0,
                    "action_type": "propose_protocol",
                }
            ],
            "current_protocol": {
                "sample_size": 32,
                "controls": ["vehicle_control", "positive_control"],
                "technique": "manual_cell_counting",
                "duration_days": 5,
                "required_equipment": ["microscope", "co2_incubator"],
                "required_reagents": ["dmso", "drug_x", "culture_media"],
                "rationale": "Uses available equipment while preserving controls.",
            },
            "round_number": 1,
            "max_rounds": 6,
        },
        "lab_manager": {
            "budget_total": 1200.0,
            "budget_remaining": 850.0,
            "equipment_available": ["co2_incubator", "microscope"],
            "equipment_booked": ["plate_reader"],
            "reagents_in_stock": ["dmso", "drug_x", "culture_media"],
            "reagents_out_of_stock": ["wst1"],
            "staff_count": 2,
            "time_limit_days": 7,
            "safety_restrictions": ["no_radioactive_reagents"],
            "conversation_history": [
                {
                    "role": "lab_manager",
                    "message": "The plate reader is unavailable.",
                    "round_number": 1,
                    "action_type": "suggest_alternative",
                }
            ],
            "current_protocol": {
                "sample_size": 32,
                "controls": ["vehicle_control", "positive_control"],
                "technique": "manual_cell_counting",
                "duration_days": 5,
                "required_equipment": ["microscope", "co2_incubator"],
                "required_reagents": ["dmso", "drug_x", "culture_media"],
                "rationale": "Uses available equipment while preserving controls.",
            },
            "round_number": 1,
            "max_rounds": 6,
        },
    }


def test_scientist_action_accepts_valid_protocol_payload() -> None:
    action = ScientistAction.model_validate(_valid_protocol_action())

    assert action.action_type is ScientistActionType.PROPOSE_PROTOCOL
    assert action.sample_size == 48
    assert action.questions == []


def test_scientist_action_rejects_unknown_action_type() -> None:
    payload = _valid_protocol_action()
    payload["action_type"] = "banana"

    with pytest.raises(ValidationError):
        ScientistAction.model_validate(payload)


def test_scientist_action_rejects_request_info_without_questions() -> None:
    payload = {
        "action_type": "request_info",
        "sample_size": 0,
        "controls": [],
        "technique": "",
        "duration_days": 0,
        "required_equipment": [],
        "required_reagents": [],
        "questions": [],
        "rationale": "",
    }

    with pytest.raises(ValidationError, match="questions must contain at least one item"):
        ScientistAction.model_validate(payload)


def test_scientist_action_rejects_protocol_payload_for_request_info() -> None:
    payload = {
        "action_type": "request_info",
        "sample_size": 24,
        "controls": [],
        "technique": "",
        "duration_days": 0,
        "required_equipment": [],
        "required_reagents": [],
        "questions": ["What plate reader is available?"],
        "rationale": "",
    }

    with pytest.raises(ValidationError, match="request_info cannot include protocol"):
        ScientistAction.model_validate(payload)


def test_scientist_action_rejects_protocol_with_zero_sample_size() -> None:
    payload = _valid_protocol_action()
    payload["sample_size"] = 0

    with pytest.raises(ValidationError, match="sample_size must be >= 1"):
        ScientistAction.model_validate(payload)


def test_scientist_action_rejects_extra_fields() -> None:
    payload = _valid_protocol_action()
    payload["unexpected"] = "value"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ScientistAction.model_validate(payload)


def test_lab_manager_action_accepts_valid_suggestion_payload() -> None:
    action = LabManagerAction.model_validate(_valid_lab_manager_action())

    assert action.action_type is LabManagerActionType.SUGGEST_ALTERNATIVE
    assert action.feasible is False
    assert action.suggested_sample_size == 32


def test_lab_manager_action_rejects_feasible_flag_mismatch() -> None:
    payload = _valid_lab_manager_action()
    payload["equipment_ok"] = True

    with pytest.raises(ValidationError, match="feasible must equal the logical AND"):
        LabManagerAction.model_validate(payload)


def test_lab_manager_action_rejects_missing_suggestion_fields() -> None:
    payload = _valid_lab_manager_action()
    payload["suggested_technique"] = ""
    payload["suggested_sample_size"] = 0
    payload["suggested_controls"] = []

    with pytest.raises(ValidationError, match="requires at least one suggestion field"):
        LabManagerAction.model_validate(payload)


def test_lab_manager_action_rejects_suggestions_for_report_feasibility() -> None:
    payload = _valid_lab_manager_action()
    payload["action_type"] = "report_feasibility"

    with pytest.raises(ValidationError, match="suggestion fields are only allowed"):
        LabManagerAction.model_validate(payload)


def test_observation_coerces_nested_dicts_to_typed_models() -> None:
    observation = Observation.model_validate(_valid_observation_payload())

    assert isinstance(observation.scientist, ScientistObservation)
    assert isinstance(observation.lab_manager, LabManagerObservation)
    assert isinstance(observation.scientist.conversation_history[0], ConversationEntry)
    assert isinstance(observation.scientist.current_protocol, Protocol)


def test_observation_rejects_invalid_conversation_role() -> None:
    payload = _valid_observation_payload()
    payload["scientist"]["conversation_history"][0]["role"] = "reviewer"

    with pytest.raises(ValidationError):
        Observation.model_validate(payload)


def test_observation_rejects_negative_budget() -> None:
    payload = _valid_observation_payload()
    payload["lab_manager"]["budget_total"] = -1.0

    with pytest.raises(ValidationError):
        Observation.model_validate(payload)


# ---------------------------------------------------------------------------
# MOD 04 — Typed EpisodeState and EpisodeLog
# ---------------------------------------------------------------------------


def _sample_protocol() -> Protocol:
    return Protocol(
        sample_size=32,
        controls=["vehicle_control", "positive_control"],
        technique="manual_cell_counting",
        duration_days=5,
        required_equipment=["microscope", "co2_incubator"],
        required_reagents=["dmso", "drug_x", "culture_media"],
        rationale="Uses available equipment while preserving controls.",
    )


def _sample_conversation_entry() -> ConversationEntry:
    return ConversationEntry(
        role="scientist",
        message="I propose a manual counting protocol.",
        round_number=1,
        action_type="propose_protocol",
    )


def test_episode_state_accepts_typed_protocol_and_history() -> None:
    protocol = _sample_protocol()
    entry = _sample_conversation_entry()
    state = EpisodeState(
        seed=42,
        current_protocol=protocol,
        conversation_history=[entry],
        round_number=1,
        max_rounds=6,
    )

    assert isinstance(state.current_protocol, Protocol)
    assert state.current_protocol.technique == "manual_cell_counting"
    assert isinstance(state.conversation_history[0], ConversationEntry)
    assert state.conversation_history[0].role == "scientist"


def test_episode_state_accepts_none_protocol() -> None:
    state = EpisodeState(current_protocol=None, conversation_history=[])
    assert state.current_protocol is None
    assert state.conversation_history == []


def test_episode_state_json_round_trip() -> None:
    protocol = _sample_protocol()
    entry = _sample_conversation_entry()
    state = EpisodeState(
        seed=7,
        scenario_template="math_reasoning",
        difficulty="hard",
        paper_title="Test Paper",
        current_protocol=protocol,
        conversation_history=[entry],
        round_number=2,
        max_rounds=6,
    )

    dumped = state.model_dump_json()
    restored = EpisodeState.model_validate_json(dumped)

    assert isinstance(restored.current_protocol, Protocol)
    assert restored.current_protocol.sample_size == 32
    assert isinstance(restored.conversation_history[0], ConversationEntry)
    assert restored.conversation_history[0].action_type == "propose_protocol"
    assert restored.seed == 7


def test_episode_log_accepts_typed_fields() -> None:
    entry = _sample_conversation_entry()
    breakdown = RewardBreakdown(rigor=0.8, feasibility=0.7, fidelity=0.9)
    log = EpisodeLog(
        episode_id="ep-001",
        seed=42,
        transcript=[entry],
        reward_breakdown=breakdown,
        total_reward=5.0,
        rounds_used=3,
        agreement_reached=True,
    )

    assert isinstance(log.transcript[0], ConversationEntry)
    assert isinstance(log.reward_breakdown, RewardBreakdown)
    assert log.reward_breakdown.rigor == 0.8


def test_episode_log_none_reward_breakdown() -> None:
    log = EpisodeLog(episode_id="ep-002")
    assert log.reward_breakdown is None
    assert log.transcript == []


def test_episode_log_json_round_trip() -> None:
    entry = _sample_conversation_entry()
    breakdown = RewardBreakdown(
        rigor=0.6, feasibility=0.5, fidelity=0.7,
        efficiency_bonus=0.1, communication_bonus=0.05,
        penalties={"timeout": 0.02},
    )
    state = EpisodeState(
        seed=99,
        current_protocol=_sample_protocol(),
        conversation_history=[entry],
        round_number=3,
        max_rounds=6,
        done=True,
        agreement_reached=True,
        reward=5.0,
        rigor_score=0.6,
    )
    log = EpisodeLog(
        episode_id="ep-round-trip",
        seed=99,
        final_state=state,
        transcript=[entry],
        reward_breakdown=breakdown,
        total_reward=5.0,
        rounds_used=3,
        agreement_reached=True,
        judge_notes="Good protocol.",
        verdict="accept",
    )

    dumped = log.model_dump_json()
    restored = EpisodeLog.model_validate_json(dumped)

    assert isinstance(restored.final_state, EpisodeState)
    assert isinstance(restored.final_state.current_protocol, Protocol)
    assert isinstance(restored.final_state.conversation_history[0], ConversationEntry)
    assert isinstance(restored.transcript[0], ConversationEntry)
    assert isinstance(restored.reward_breakdown, RewardBreakdown)
    assert restored.reward_breakdown.penalties == {"timeout": 0.02}
    assert restored.episode_id == "ep-round-trip"


def test_episode_log_nested_state_preserves_typed_fields() -> None:
    protocol = _sample_protocol()
    entry = _sample_conversation_entry()
    state = EpisodeState(
        current_protocol=protocol,
        conversation_history=[entry],
    )
    log = EpisodeLog(final_state=state)

    assert isinstance(log.final_state.current_protocol, Protocol)
    assert log.final_state.current_protocol.technique == "manual_cell_counting"
    assert isinstance(log.final_state.conversation_history[0], ConversationEntry)


def test_step_result_with_typed_info() -> None:
    breakdown = RewardBreakdown(rigor=0.8, feasibility=0.8, fidelity=0.8)
    info = StepInfo(
        agreement_reached=True,
        reward_breakdown=breakdown,
        judge_notes="All checks passed.",
        verdict="accept",
        round=3,
        stub=True,
    )
    result = StepResult(reward=5.0, done=True, info=info)

    dumped = result.model_dump_json()
    restored = StepResult.model_validate_json(dumped)

    assert isinstance(restored.info, StepInfo)
    assert isinstance(restored.info.reward_breakdown, RewardBreakdown)
    assert restored.info.agreement_reached is True
    assert restored.info.verdict == "accept"
