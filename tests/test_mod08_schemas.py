"""MOD 08 — Comprehensive unit tests for schemas and validators.

Covers edge cases in every Pydantic model from replicalab.models and
validator behaviour from replicalab.utils.validation that are not
already tested in test_models.py and test_validation.py.
"""

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_accept() -> dict:
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


def _minimal_request_info() -> dict:
    return {
        "action_type": "request_info",
        "sample_size": 0,
        "controls": [],
        "technique": "",
        "duration_days": 0,
        "required_equipment": [],
        "required_reagents": [],
        "questions": ["What equipment is available?"],
        "rationale": "",
    }


def _minimal_propose() -> dict:
    return {
        "action_type": "propose_protocol",
        "sample_size": 10,
        "controls": ["baseline"],
        "technique": "grid_search",
        "duration_days": 5,
        "required_equipment": ["compute"],
        "required_reagents": ["data"],
        "questions": [],
        "rationale": "A simple plan.",
    }


def _lm_accept() -> dict:
    return {
        "action_type": "accept",
        "feasible": True,
        "budget_ok": True,
        "equipment_ok": True,
        "reagents_ok": True,
        "schedule_ok": True,
        "staff_ok": True,
        "suggested_technique": "",
        "suggested_sample_size": 0,
        "suggested_controls": [],
        "explanation": "All constraints are satisfied.",
    }


def _lm_reject() -> dict:
    return {
        "action_type": "reject",
        "feasible": False,
        "budget_ok": True,
        "equipment_ok": False,
        "reagents_ok": True,
        "schedule_ok": True,
        "staff_ok": True,
        "suggested_technique": "",
        "suggested_sample_size": 0,
        "suggested_controls": [],
        "explanation": "The equipment is unavailable.",
    }


def _lm_report() -> dict:
    return {
        "action_type": "report_feasibility",
        "feasible": True,
        "budget_ok": True,
        "equipment_ok": True,
        "reagents_ok": True,
        "schedule_ok": True,
        "staff_ok": True,
        "suggested_technique": "",
        "suggested_sample_size": 0,
        "suggested_controls": [],
        "explanation": "Feasible as proposed.",
    }


# ===================================================================
# ScientistAction — edge cases
# ===================================================================


class TestScientistActionEdgeCases:
    def test_accept_valid_minimal(self) -> None:
        action = ScientistAction.model_validate(_minimal_accept())
        assert action.action_type is ScientistActionType.ACCEPT

    def test_accept_rejects_questions(self) -> None:
        payload = _minimal_accept()
        payload["questions"] = ["Why?"]
        with pytest.raises(ValidationError, match="questions must be empty for accept"):
            ScientistAction.model_validate(payload)

    def test_accept_rejects_protocol_payload(self) -> None:
        payload = _minimal_accept()
        payload["sample_size"] = 10
        with pytest.raises(ValidationError, match="accept cannot include protocol"):
            ScientistAction.model_validate(payload)

    def test_revise_protocol_valid(self) -> None:
        payload = _minimal_propose()
        payload["action_type"] = "revise_protocol"
        action = ScientistAction.model_validate(payload)
        assert action.action_type is ScientistActionType.REVISE_PROTOCOL

    def test_revise_rejects_zero_sample(self) -> None:
        payload = _minimal_propose()
        payload["action_type"] = "revise_protocol"
        payload["sample_size"] = 0
        with pytest.raises(ValidationError, match="sample_size must be >= 1"):
            ScientistAction.model_validate(payload)

    def test_propose_rejects_empty_technique(self) -> None:
        payload = _minimal_propose()
        payload["technique"] = ""
        with pytest.raises(ValidationError, match="technique is required"):
            ScientistAction.model_validate(payload)

    def test_propose_rejects_empty_rationale(self) -> None:
        payload = _minimal_propose()
        payload["rationale"] = ""
        with pytest.raises(ValidationError, match="rationale is required"):
            ScientistAction.model_validate(payload)

    def test_propose_rejects_questions(self) -> None:
        payload = _minimal_propose()
        payload["questions"] = ["Why?"]
        with pytest.raises(ValidationError, match="questions must be empty"):
            ScientistAction.model_validate(payload)

    def test_request_info_valid(self) -> None:
        action = ScientistAction.model_validate(_minimal_request_info())
        assert action.action_type is ScientistActionType.REQUEST_INFO

    def test_whitespace_stripping_in_lists(self) -> None:
        payload = _minimal_propose()
        payload["controls"] = ["  baseline  ", " positive "]
        action = ScientistAction.model_validate(payload)
        assert action.controls == ["baseline", "positive"]

    def test_empty_string_in_list_rejects(self) -> None:
        payload = _minimal_propose()
        payload["controls"] = ["baseline", ""]
        with pytest.raises(ValidationError, match="non-empty"):
            ScientistAction.model_validate(payload)

    def test_whitespace_only_in_list_rejects(self) -> None:
        payload = _minimal_propose()
        payload["required_equipment"] = ["compute", "   "]
        with pytest.raises(ValidationError, match="non-empty"):
            ScientistAction.model_validate(payload)

    def test_negative_sample_size_rejects(self) -> None:
        payload = _minimal_propose()
        payload["sample_size"] = -1
        with pytest.raises(ValidationError):
            ScientistAction.model_validate(payload)

    def test_negative_duration_days_rejects(self) -> None:
        payload = _minimal_propose()
        payload["duration_days"] = -5
        with pytest.raises(ValidationError):
            ScientistAction.model_validate(payload)

    def test_enum_value_access(self) -> None:
        assert ScientistActionType.PROPOSE_PROTOCOL.value == "propose_protocol"
        assert ScientistActionType.REVISE_PROTOCOL.value == "revise_protocol"
        assert ScientistActionType.REQUEST_INFO.value == "request_info"
        assert ScientistActionType.ACCEPT.value == "accept"


# ===================================================================
# LabManagerAction — edge cases
# ===================================================================


class TestLabManagerActionEdgeCases:
    def test_accept_valid(self) -> None:
        action = LabManagerAction.model_validate(_lm_accept())
        assert action.action_type is LabManagerActionType.ACCEPT
        assert action.feasible is True

    def test_accept_rejects_infeasible(self) -> None:
        payload = _lm_accept()
        payload["feasible"] = False
        payload["equipment_ok"] = False
        with pytest.raises(ValidationError, match="accept requires feasible=true"):
            LabManagerAction.model_validate(payload)

    def test_reject_valid(self) -> None:
        action = LabManagerAction.model_validate(_lm_reject())
        assert action.action_type is LabManagerActionType.REJECT
        assert action.feasible is False

    def test_reject_rejects_feasible(self) -> None:
        payload = _lm_reject()
        payload["feasible"] = True
        payload["equipment_ok"] = True
        with pytest.raises(ValidationError, match="reject requires feasible=false"):
            LabManagerAction.model_validate(payload)

    def test_report_feasibility_valid(self) -> None:
        action = LabManagerAction.model_validate(_lm_report())
        assert action.action_type is LabManagerActionType.REPORT_FEASIBILITY

    def test_report_rejects_suggestion_fields(self) -> None:
        payload = _lm_report()
        payload["suggested_technique"] = "alternative_method"
        with pytest.raises(ValidationError, match="suggestion fields are only allowed"):
            LabManagerAction.model_validate(payload)

    def test_suggest_alternative_rejects_feasible(self) -> None:
        payload = _lm_reject()
        payload["action_type"] = "suggest_alternative"
        payload["feasible"] = True
        payload["equipment_ok"] = True
        payload["suggested_technique"] = "alt"
        with pytest.raises(ValidationError, match="suggest_alternative requires feasible=false"):
            LabManagerAction.model_validate(payload)

    def test_empty_explanation_rejects(self) -> None:
        payload = _lm_accept()
        payload["explanation"] = ""
        with pytest.raises(ValidationError, match="explanation is required"):
            LabManagerAction.model_validate(payload)

    def test_extra_fields_rejected(self) -> None:
        payload = _lm_accept()
        payload["extra"] = "nope"
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            LabManagerAction.model_validate(payload)

    def test_feasible_flag_mismatch_single_false(self) -> None:
        payload = _lm_accept()
        payload["schedule_ok"] = False
        with pytest.raises(ValidationError, match="feasible must equal the logical AND"):
            LabManagerAction.model_validate(payload)

    def test_enum_value_access(self) -> None:
        assert LabManagerActionType.REPORT_FEASIBILITY.value == "report_feasibility"
        assert LabManagerActionType.SUGGEST_ALTERNATIVE.value == "suggest_alternative"
        assert LabManagerActionType.REJECT.value == "reject"
        assert LabManagerActionType.ACCEPT.value == "accept"


# ===================================================================
# Protocol — edge cases
# ===================================================================


class TestProtocolEdgeCases:
    def test_valid_minimal(self) -> None:
        p = Protocol(
            sample_size=1,
            controls=[],
            technique="method",
            duration_days=1,
            required_equipment=[],
            required_reagents=[],
            rationale="Reason.",
        )
        assert p.sample_size == 1

    def test_zero_sample_size_allowed(self) -> None:
        p = Protocol(
            sample_size=0,
            controls=[],
            technique="method",
            duration_days=1,
            required_equipment=[],
            required_reagents=[],
            rationale="Reason.",
        )
        assert p.sample_size == 0

    def test_empty_technique_rejects(self) -> None:
        with pytest.raises(ValidationError, match="non-empty"):
            Protocol(
                sample_size=1,
                controls=[],
                technique="",
                duration_days=1,
                required_equipment=[],
                required_reagents=[],
                rationale="Reason.",
            )

    def test_empty_rationale_rejects(self) -> None:
        with pytest.raises(ValidationError, match="non-empty"):
            Protocol(
                sample_size=1,
                controls=[],
                technique="method",
                duration_days=1,
                required_equipment=[],
                required_reagents=[],
                rationale="",
            )

    def test_negative_sample_size_rejects(self) -> None:
        with pytest.raises(ValidationError):
            Protocol(
                sample_size=-1,
                controls=[],
                technique="method",
                duration_days=1,
                required_equipment=[],
                required_reagents=[],
                rationale="Reason.",
            )

    def test_negative_duration_rejects(self) -> None:
        with pytest.raises(ValidationError):
            Protocol(
                sample_size=1,
                controls=[],
                technique="method",
                duration_days=-1,
                required_equipment=[],
                required_reagents=[],
                rationale="Reason.",
            )

    def test_whitespace_stripping(self) -> None:
        p = Protocol(
            sample_size=1,
            controls=["  ctrl  "],
            technique="  method  ",
            duration_days=1,
            required_equipment=["  equip  "],
            required_reagents=["  reagent  "],
            rationale="  reason  ",
        )
        assert p.controls == ["ctrl"]
        assert p.technique == "method"
        assert p.required_equipment == ["equip"]
        assert p.required_reagents == ["reagent"]
        assert p.rationale == "reason"

    def test_empty_string_in_controls_rejects(self) -> None:
        with pytest.raises(ValidationError, match="non-empty"):
            Protocol(
                sample_size=1,
                controls=["good", ""],
                technique="method",
                duration_days=1,
                required_equipment=[],
                required_reagents=[],
                rationale="Reason.",
            )

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Protocol(
                sample_size=1,
                controls=[],
                technique="method",
                duration_days=1,
                required_equipment=[],
                required_reagents=[],
                rationale="Reason.",
                extra_field="bad",
            )

    def test_json_round_trip(self) -> None:
        p = Protocol(
            sample_size=10,
            controls=["baseline", "positive"],
            technique="grid_search",
            duration_days=5,
            required_equipment=["compute"],
            required_reagents=["data"],
            rationale="Full plan.",
        )
        restored = Protocol.model_validate_json(p.model_dump_json())
        assert restored == p


# ===================================================================
# ConversationEntry — edge cases
# ===================================================================


class TestConversationEntryEdgeCases:
    def test_null_action_type_valid(self) -> None:
        entry = ConversationEntry(
            role="scientist",
            message="Hello",
            round_number=0,
            action_type=None,
        )
        assert entry.action_type is None

    def test_empty_string_action_type_rejects(self) -> None:
        with pytest.raises(ValidationError, match="action_type must be null or a non-empty"):
            ConversationEntry(
                role="scientist",
                message="Hello",
                round_number=0,
                action_type="",
            )

    def test_empty_message_rejects(self) -> None:
        with pytest.raises(ValidationError, match="message is required"):
            ConversationEntry(
                role="scientist",
                message="",
                round_number=0,
                action_type=None,
            )

    def test_system_role_valid(self) -> None:
        entry = ConversationEntry(
            role="system",
            message="Round started.",
            round_number=0,
            action_type=None,
        )
        assert entry.role == "system"

    def test_invalid_role_rejects(self) -> None:
        with pytest.raises(ValidationError):
            ConversationEntry(
                role="judge",
                message="Verdict.",
                round_number=0,
                action_type=None,
            )

    def test_negative_round_number_rejects(self) -> None:
        with pytest.raises(ValidationError):
            ConversationEntry(
                role="scientist",
                message="Hello",
                round_number=-1,
                action_type=None,
            )

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ConversationEntry(
                role="scientist",
                message="Hello",
                round_number=0,
                action_type=None,
                extra="bad",
            )


# ===================================================================
# RewardBreakdown — edge cases
# ===================================================================


class TestRewardBreakdownEdgeCases:
    def test_default_values(self) -> None:
        rb = RewardBreakdown()
        assert rb.rigor == 0.0
        assert rb.feasibility == 0.0
        assert rb.fidelity == 0.0
        assert rb.parsimony == 1.0
        assert rb.efficiency_bonus == 0.0
        assert rb.communication_bonus == 0.0
        assert rb.penalties == {}

    def test_boundary_values_valid(self) -> None:
        rb = RewardBreakdown(rigor=0.0, feasibility=1.0, fidelity=0.5, parsimony=0.0)
        assert rb.rigor == 0.0
        assert rb.feasibility == 1.0
        assert rb.parsimony == 0.0

    def test_rigor_above_one_rejects(self) -> None:
        with pytest.raises(ValidationError):
            RewardBreakdown(rigor=1.1)

    def test_rigor_below_zero_rejects(self) -> None:
        with pytest.raises(ValidationError):
            RewardBreakdown(rigor=-0.1)

    def test_feasibility_above_one_rejects(self) -> None:
        with pytest.raises(ValidationError):
            RewardBreakdown(feasibility=1.5)

    def test_fidelity_below_zero_rejects(self) -> None:
        with pytest.raises(ValidationError):
            RewardBreakdown(fidelity=-0.01)

    def test_parsimony_above_one_rejects(self) -> None:
        with pytest.raises(ValidationError):
            RewardBreakdown(parsimony=2.0)

    def test_penalties_dict_preserved(self) -> None:
        rb = RewardBreakdown(penalties={"timeout": 0.2, "stalling": 0.05})
        assert rb.penalties["timeout"] == 0.2
        assert rb.penalties["stalling"] == 0.05

    def test_json_round_trip(self) -> None:
        rb = RewardBreakdown(
            rigor=0.7,
            feasibility=0.8,
            fidelity=0.6,
            parsimony=0.9,
            efficiency_bonus=0.3,
            penalties={"invalid_tool_use": 0.1},
        )
        restored = RewardBreakdown.model_validate_json(rb.model_dump_json())
        assert restored == rb


# ===================================================================
# Observation — edge cases
# ===================================================================


class TestObservationEdgeCases:
    def test_both_none_valid(self) -> None:
        obs = Observation(scientist=None, lab_manager=None)
        assert obs.scientist is None
        assert obs.lab_manager is None

    def test_scientist_only_valid(self) -> None:
        obs = Observation(
            scientist=ScientistObservation(
                paper_title="T",
                paper_hypothesis="H",
                paper_method="M",
                paper_key_finding="F",
                experiment_goal="G",
                conversation_history=[],
                current_protocol=None,
                round_number=0,
                max_rounds=6,
            ),
            lab_manager=None,
        )
        assert obs.scientist is not None
        assert obs.lab_manager is None

    def test_lab_manager_only_valid(self) -> None:
        obs = Observation(
            scientist=None,
            lab_manager=LabManagerObservation(
                budget_total=1000.0,
                budget_remaining=800.0,
                equipment_available=["compute"],
                equipment_booked=[],
                reagents_in_stock=["data"],
                reagents_out_of_stock=[],
                staff_count=2,
                time_limit_days=7,
                safety_restrictions=[],
                conversation_history=[],
                current_protocol=None,
                round_number=0,
                max_rounds=6,
            ),
        )
        assert obs.scientist is None
        assert obs.lab_manager is not None

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Observation(scientist=None, lab_manager=None, judge=None)


# ===================================================================
# LabManagerObservation — edge cases
# ===================================================================


class TestLabManagerObservationEdgeCases:
    def test_negative_staff_count_rejects(self) -> None:
        with pytest.raises(ValidationError):
            LabManagerObservation(
                budget_total=1000.0,
                budget_remaining=800.0,
                equipment_available=[],
                equipment_booked=[],
                reagents_in_stock=[],
                reagents_out_of_stock=[],
                staff_count=-1,
                time_limit_days=7,
                safety_restrictions=[],
                conversation_history=[],
                current_protocol=None,
                round_number=0,
                max_rounds=6,
            )

    def test_empty_string_in_equipment_rejects(self) -> None:
        with pytest.raises(ValidationError, match="non-empty"):
            LabManagerObservation(
                budget_total=1000.0,
                budget_remaining=800.0,
                equipment_available=["compute", ""],
                equipment_booked=[],
                reagents_in_stock=[],
                reagents_out_of_stock=[],
                staff_count=2,
                time_limit_days=7,
                safety_restrictions=[],
                conversation_history=[],
                current_protocol=None,
                round_number=0,
                max_rounds=6,
            )

    def test_whitespace_stripping_in_inventory(self) -> None:
        obs = LabManagerObservation(
            budget_total=1000.0,
            budget_remaining=800.0,
            equipment_available=["  compute  "],
            equipment_booked=["  scope  "],
            reagents_in_stock=["  data  "],
            reagents_out_of_stock=["  unobtainium  "],
            staff_count=2,
            time_limit_days=7,
            safety_restrictions=["  no_fire  "],
            conversation_history=[],
            current_protocol=None,
            round_number=0,
            max_rounds=6,
        )
        assert obs.equipment_available == ["compute"]
        assert obs.equipment_booked == ["scope"]
        assert obs.reagents_in_stock == ["data"]
        assert obs.reagents_out_of_stock == ["unobtainium"]
        assert obs.safety_restrictions == ["no_fire"]


# ===================================================================
# StepInfo — edge cases
# ===================================================================


class TestStepInfoEdgeCases:
    def test_defaults(self) -> None:
        info = StepInfo()
        assert info.agreement_reached is False
        assert info.error is None
        assert info.reward_breakdown is None
        assert info.judge_notes is None
        assert info.verdict is None
        assert info.top_failure_reasons == []

    def test_extra_fields_allowed(self) -> None:
        info = StepInfo(custom_key="value", debug_round=3)
        assert info.custom_key == "value"  # type: ignore[attr-defined]
        assert info.debug_round == 3  # type: ignore[attr-defined]

    def test_json_round_trip_with_extras(self) -> None:
        info = StepInfo(
            agreement_reached=True,
            reward_breakdown=RewardBreakdown(rigor=0.9),
            judge_notes="Good.",
            verdict="accept",
            extra_metric=42,
        )
        dumped = info.model_dump_json()
        restored = StepInfo.model_validate_json(dumped)
        assert restored.agreement_reached is True
        assert restored.reward_breakdown.rigor == 0.9
        assert restored.model_extra.get("extra_metric") == 42


# ===================================================================
# StepResult — edge cases
# ===================================================================


class TestStepResultEdgeCases:
    def test_defaults(self) -> None:
        result = StepResult()
        assert result.observation is None
        assert result.reward == 0.0
        assert result.done is False
        assert isinstance(result.info, StepInfo)

    def test_with_observation(self) -> None:
        result = StepResult(
            observation=Observation(scientist=None, lab_manager=None),
            reward=3.5,
            done=True,
        )
        assert result.reward == 3.5
        assert result.done is True

    def test_json_round_trip(self) -> None:
        info = StepInfo(agreement_reached=True, verdict="accept")
        result = StepResult(reward=5.0, done=True, info=info)
        restored = StepResult.model_validate_json(result.model_dump_json())
        assert restored.reward == 5.0
        assert restored.info.verdict == "accept"


# ===================================================================
# EpisodeState — edge cases
# ===================================================================


class TestEpisodeStateEdgeCases:
    def test_defaults(self) -> None:
        state = EpisodeState()
        assert state.seed == 0
        assert state.scenario_template == ""
        assert state.done is False
        assert state.current_protocol is None
        assert state.conversation_history == []
        assert state.top_failure_reasons == []

    def test_top_failure_reasons_preserved(self) -> None:
        state = EpisodeState(
            top_failure_reasons=["Low feasibility.", "Timeout applied."],
        )
        assert len(state.top_failure_reasons) == 2
        assert "Low feasibility." in state.top_failure_reasons


# ===================================================================
# EpisodeLog — edge cases
# ===================================================================


class TestEpisodeLogEdgeCases:
    def test_defaults(self) -> None:
        log = EpisodeLog()
        assert log.episode_id == ""
        assert log.seed == 0
        assert log.final_state is None
        assert log.transcript == []
        assert log.reward_breakdown is None
        assert log.top_failure_reasons == []
        assert log.verdict == ""

    def test_top_failure_reasons_in_json_round_trip(self) -> None:
        log = EpisodeLog(
            episode_id="ep-fr",
            top_failure_reasons=["Feasibility too low.", "Timeout."],
            verdict="timeout",
        )
        restored = EpisodeLog.model_validate_json(log.model_dump_json())
        assert restored.top_failure_reasons == ["Feasibility too low.", "Timeout."]
        assert restored.verdict == "timeout"

    def test_model_dump_contains_all_keys(self) -> None:
        log = EpisodeLog(episode_id="ep-keys")
        dumped = log.model_dump()
        expected_keys = {
            "episode_id", "seed", "scenario_template", "difficulty",
            "final_state", "transcript", "reward_breakdown", "total_reward",
            "rounds_used", "agreement_reached", "judge_notes", "verdict",
            "top_failure_reasons",
        }
        assert expected_keys.issubset(set(dumped.keys()))
