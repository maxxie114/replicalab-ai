"""Shared data contracts for the ReplicaLab environment.

FND 04 introduced the shared model stubs. MOD 01 now hardens the
ScientistAction contract so downstream parser, API, and environment code
can reject invalid payloads early. The remaining models stay lightweight
until their follow-on tasks land.
"""

from __future__ import annotations

from enum import Enum
from typing import ClassVar, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Agent actions
# ---------------------------------------------------------------------------


def _normalize_string_list(value: list[str]) -> list[str]:
    cleaned = [item.strip() for item in value]
    if any(not item for item in cleaned):
        raise ValueError("list entries must be non-empty strings")
    return cleaned

class ScientistActionType(str, Enum):
    """Allowed Scientist action modes."""

    PROPOSE_PROTOCOL = "propose_protocol"
    REVISE_PROTOCOL = "revise_protocol"
    REQUEST_INFO = "request_info"
    ACCEPT = "accept"


class ScientistAction(BaseModel):
    """Action produced by the Scientist agent each turn.

    MOD 01 freezes this as a strict contract:
      - only the four approved action types are allowed
      - mixed-mode payloads are rejected
      - protocol proposals require the core protocol fields
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    PROTOCOL_ACTION_TYPES: ClassVar[frozenset[ScientistActionType]] = frozenset(
        {
            ScientistActionType.PROPOSE_PROTOCOL,
            ScientistActionType.REVISE_PROTOCOL,
        }
    )

    action_type: ScientistActionType
    sample_size: int = Field(ge=0)
    controls: list[str]
    technique: str
    duration_days: int = Field(ge=0)
    required_equipment: list[str]
    required_reagents: list[str]
    questions: list[str]
    rationale: str

    @field_validator("controls", "required_equipment", "required_reagents", "questions")
    @classmethod
    def _normalize_string_lists(cls, value: list[str]) -> list[str]:
        return _normalize_string_list(value)

    @model_validator(mode="after")
    def _validate_conditional_fields(self) -> "ScientistAction":
        has_protocol_payload = any(
            (
                self.sample_size != 0,
                bool(self.controls),
                bool(self.technique),
                self.duration_days != 0,
                bool(self.required_equipment),
                bool(self.required_reagents),
                bool(self.rationale),
            )
        )

        if self.action_type in self.PROTOCOL_ACTION_TYPES:
            if self.sample_size < 1:
                raise ValueError(
                    "sample_size must be >= 1 for propose_protocol and revise_protocol"
                )
            if not self.technique:
                raise ValueError("technique is required for protocol proposals and revisions")
            if not self.rationale:
                raise ValueError("rationale is required for protocol proposals and revisions")
            if self.questions:
                raise ValueError("questions must be empty unless action_type is request_info")
            return self

        if self.action_type is ScientistActionType.REQUEST_INFO:
            if not self.questions:
                raise ValueError("questions must contain at least one item for request_info")
            if has_protocol_payload:
                raise ValueError("request_info cannot include protocol proposal fields")
            return self

        if self.questions:
            raise ValueError("questions must be empty for accept")
        if has_protocol_payload:
            raise ValueError("accept cannot include protocol proposal fields")
        return self


class LabManagerActionType(str, Enum):
    """Allowed Lab Manager action modes."""

    REPORT_FEASIBILITY = "report_feasibility"
    SUGGEST_ALTERNATIVE = "suggest_alternative"
    REJECT = "reject"
    ACCEPT = "accept"


class LabManagerAction(BaseModel):
    """Action produced by the Lab Manager agent each turn.

    MOD 02 freezes this as a strict contract with feasible-flag consistency
    and action-specific suggestion rules.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    action_type: LabManagerActionType
    feasible: bool
    budget_ok: bool
    equipment_ok: bool
    reagents_ok: bool
    schedule_ok: bool
    staff_ok: bool
    suggested_technique: str
    suggested_sample_size: int = Field(ge=0)
    suggested_controls: list[str]
    explanation: str

    @field_validator("suggested_controls")
    @classmethod
    def _normalize_suggested_controls(cls, value: list[str]) -> list[str]:
        return _normalize_string_list(value)

    @field_validator("explanation")
    @classmethod
    def _require_explanation(cls, value: str) -> str:
        if not value:
            raise ValueError("explanation is required")
        return value

    @model_validator(mode="after")
    def _validate_conditional_fields(self) -> "LabManagerAction":
        flags = (
            self.budget_ok,
            self.equipment_ok,
            self.reagents_ok,
            self.schedule_ok,
            self.staff_ok,
        )
        all_flags = all(flags)
        has_suggestion = any(
            (
                bool(self.suggested_technique),
                self.suggested_sample_size != 0,
                bool(self.suggested_controls),
            )
        )

        if self.feasible != all_flags:
            raise ValueError("feasible must equal the logical AND of all constraint flags")

        if (
            self.action_type is not LabManagerActionType.SUGGEST_ALTERNATIVE
            and has_suggestion
        ):
            raise ValueError(
                "suggestion fields are only allowed for suggest_alternative"
            )

        if self.action_type is LabManagerActionType.ACCEPT and not self.feasible:
            raise ValueError("accept requires feasible=true and all constraint flags=true")

        if self.action_type is LabManagerActionType.REJECT and self.feasible:
            raise ValueError("reject requires feasible=false")

        if self.action_type is LabManagerActionType.SUGGEST_ALTERNATIVE:
            if self.feasible:
                raise ValueError("suggest_alternative requires feasible=false")
            if not has_suggestion:
                raise ValueError(
                    "suggest_alternative requires at least one suggestion field"
                )

        return self


# ---------------------------------------------------------------------------
# Observations
# ---------------------------------------------------------------------------

class ConversationEntry(BaseModel):
    """One message in the negotiation log."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    role: Literal["scientist", "lab_manager", "system"]
    message: str
    round_number: int = Field(ge=0)
    action_type: Optional[str]

    @field_validator("message")
    @classmethod
    def _require_message(cls, value: str) -> str:
        if not value:
            raise ValueError("message is required")
        return value

    @field_validator("action_type")
    @classmethod
    def _validate_action_type(cls, value: Optional[str]) -> Optional[str]:
        if value == "":
            raise ValueError("action_type must be null or a non-empty string")
        return value


class Protocol(BaseModel):
    """Structured protocol payload shared across observations."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    sample_size: int = Field(ge=0)
    controls: list[str]
    technique: str
    duration_days: int = Field(ge=0)
    required_equipment: list[str]
    required_reagents: list[str]
    rationale: str

    @field_validator("controls", "required_equipment", "required_reagents")
    @classmethod
    def _normalize_protocol_lists(cls, value: list[str]) -> list[str]:
        return _normalize_string_list(value)

    @field_validator("technique", "rationale")
    @classmethod
    def _require_protocol_text(cls, value: str) -> str:
        if not value:
            raise ValueError("protocol text fields must be non-empty")
        return value


class ScientistObservation(BaseModel):
    """What the Scientist sees at the start of each turn."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    paper_title: str
    paper_hypothesis: str
    paper_method: str
    paper_key_finding: str
    experiment_goal: str
    conversation_history: list[ConversationEntry]
    current_protocol: Optional[Protocol]
    round_number: int = Field(ge=0)
    max_rounds: int = Field(ge=0)


class LabManagerObservation(BaseModel):
    """What the Lab Manager sees at the start of each turn."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    budget_total: float = Field(ge=0)
    budget_remaining: float = Field(ge=0)
    equipment_available: list[str]
    equipment_booked: list[str]
    reagents_in_stock: list[str]
    reagents_out_of_stock: list[str]
    staff_count: int = Field(ge=0)
    time_limit_days: int = Field(ge=0)
    safety_restrictions: list[str]
    conversation_history: list[ConversationEntry]
    current_protocol: Optional[Protocol]
    round_number: int = Field(ge=0)
    max_rounds: int = Field(ge=0)

    @field_validator(
        "equipment_available",
        "equipment_booked",
        "reagents_in_stock",
        "reagents_out_of_stock",
        "safety_restrictions",
    )
    @classmethod
    def _normalize_inventory_lists(cls, value: list[str]) -> list[str]:
        return _normalize_string_list(value)


class Observation(BaseModel):
    """Combined observation wrapper. Each role receives its own view."""

    model_config = ConfigDict(extra="forbid")

    scientist: Optional[ScientistObservation]
    lab_manager: Optional[LabManagerObservation]


# ---------------------------------------------------------------------------
# Reward breakdown and step metadata
# ---------------------------------------------------------------------------


class RewardBreakdown(BaseModel):
    """Component scores and adjustments produced by the judge rubric engine."""

    rigor: float = Field(default=0.0, ge=0, le=1)
    feasibility: float = Field(default=0.0, ge=0, le=1)
    fidelity: float = Field(default=0.0, ge=0, le=1)
    # Defaults to 1.0 so existing exact-value tests and manual breakdowns
    # preserve the prior reward semantics unless parsimony is computed.
    parsimony: float = Field(default=1.0, ge=0, le=1)
    efficiency_bonus: float = 0.0
    communication_bonus: float = 0.0
    penalties: dict[str, float] = Field(default_factory=dict)


class StepInfo(BaseModel):
    """Typed metadata returned alongside each step result.

    Reserved keys from the frozen contract are typed fields.
    Additional debug or runtime metadata is allowed via extra="allow".
    """

    model_config = ConfigDict(extra="allow")

    agreement_reached: bool = False
    error: Optional[str] = None
    reward_breakdown: Optional[RewardBreakdown] = None
    judge_notes: Optional[str] = None
    verdict: Optional[str] = None
    top_failure_reasons: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Step result
# ---------------------------------------------------------------------------

class StepResult(BaseModel):
    """Returned by env.step(). Contains the next observation, reward,
    termination flag, and typed step info."""

    observation: Optional[Observation] = None
    reward: float = 0.0
    done: bool = False
    info: StepInfo = Field(default_factory=StepInfo)


# ---------------------------------------------------------------------------
# Episode state and logging
# ---------------------------------------------------------------------------

class EpisodeState(BaseModel):
    """Full internal state of one episode. Used for debugging and replay."""

    seed: int = 0
    scenario_template: str = ""
    difficulty: str = "easy"
    paper_title: str = ""
    paper_hypothesis: str = ""
    paper_method: str = ""
    paper_key_finding: str = ""
    experiment_goal: str = ""
    lab_budget_total: float = 0.0
    lab_budget_remaining: float = 0.0
    lab_equipment: list[str] = Field(default_factory=list)
    lab_reagents: list[str] = Field(default_factory=list)
    lab_staff_count: int = 0
    lab_time_limit_days: int = 0
    current_protocol: Optional[Protocol] = None
    conversation_history: list[ConversationEntry] = Field(default_factory=list)
    round_number: int = 0
    max_rounds: int = 0
    done: bool = False
    agreement_reached: bool = False
    reward: float = 0.0
    rigor_score: float = 0.0
    feasibility_score: float = 0.0
    fidelity_score: float = 0.0
    judge_notes: str = ""
    verdict: str = ""
    top_failure_reasons: list[str] = Field(default_factory=list)


class EpisodeLog(BaseModel):
    """Completed episode record for logging, replay, and evaluation."""

    episode_id: str = ""
    seed: int = 0
    scenario_template: str = ""
    difficulty: str = "easy"
    final_state: Optional[EpisodeState] = None
    transcript: list[ConversationEntry] = Field(default_factory=list)
    reward_breakdown: Optional[RewardBreakdown] = None
    total_reward: float = 0.0
    rounds_used: int = 0
    agreement_reached: bool = False
    judge_notes: str = ""
    verdict: str = ""
    top_failure_reasons: list[str] = Field(default_factory=list)
    invalid_action_count: int = 0
    invalid_action_rate: float = 0.0
