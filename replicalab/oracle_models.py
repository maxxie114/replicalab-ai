"""Typed models for the optional Oracle-driven environment layer.

These models are additive to the existing ReplicaLab contracts. The
deterministic env, reward, and API surface remain canonical; Oracle models
power richer scenario generation, optional live Lab Manager responses,
optional event injection, and post-mortem analysis.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from replicalab.models import ScientistAction


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Equipment(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str
    available: bool
    condition: str
    booking_conflicts: list[str] = Field(default_factory=list)
    cost_per_use: float = 0.0


class Reagent(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str
    in_stock: bool
    quantity_available: float = 0.0
    unit: str = "mL"
    lead_time_days: int = 0
    cost: float = 0.0


class StaffMember(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str
    role: str
    available_days: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class Substitution(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    original: str
    substitute: str
    validity: str
    caveats: str = ""


class Paper(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str
    domain: Literal["math_reasoning", "ml_benchmark", "finance_trading"]
    claim: str
    method_summary: str
    original_sample_size: int
    original_duration_days: int
    original_technique: str
    required_controls: list[str] = Field(default_factory=list)
    required_equipment: list[str] = Field(default_factory=list)
    required_reagents: list[str] = Field(default_factory=list)
    statistical_test: str


class LabConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    budget_total: float
    budget_remaining: float
    equipment: list[Equipment] = Field(default_factory=list)
    reagents: list[Reagent] = Field(default_factory=list)
    staff: list[StaffMember] = Field(default_factory=list)
    max_duration_days: int
    safety_rules: list[str] = Field(default_factory=list)
    valid_substitutions: list[Substitution] = Field(default_factory=list)


class MinimumViableSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    min_sample_size: int
    must_keep_controls: list[str] = Field(default_factory=list)
    acceptable_techniques: list[str] = Field(default_factory=list)
    min_duration_days: int
    critical_equipment: list[str] = Field(default_factory=list)
    flexible_equipment: list[str] = Field(default_factory=list)
    critical_reagents: list[str] = Field(default_factory=list)
    flexible_reagents: list[str] = Field(default_factory=list)
    power_threshold: float


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    paper: Paper
    lab_constraints: LabConstraints
    minimum_viable_spec: MinimumViableSpec
    difficulty: Difficulty
    narrative_hook: str


class OracleScientistObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    paper: Paper
    round_number: int
    max_rounds: int
    conversation_history: list[dict] = Field(default_factory=list)
    current_protocol: Optional[dict] = None


class OracleLabManagerObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    lab_constraints: LabConstraints
    current_protocol: Optional[dict] = None
    scientist_action: ScientistAction
    round_number: int


class LabManagerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    response_type: Literal[
        "feasibility_report",
        "suggest_substitution",
        "reject",
        "accept",
    ]
    feasible: bool
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    cost_estimate: float = 0.0
    time_estimate_days: int = 0
    message: str


class AdjudicatorRoundScore(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    rigor_flags: list[str] = Field(default_factory=list)
    feasibility_flags: list[str] = Field(default_factory=list)
    info_gain: float
    protocol_delta: float
    momentum: float
    contradiction_detected: bool
    stalling_detected: bool
    step_reward: float
    notes: str


class AdjudicatorTerminalScore(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    rigor: float
    feasibility: float
    fidelity: float
    parsimony: float
    robustness: float
    power_preservation: float
    efficiency_bonus: float
    communication_bonus: float
    penalties: dict[str, float] = Field(default_factory=dict)
    terminal_reward: float
    total_reward: float


class EnvironmentEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    event_type: str
    description: str
    state_changes: dict[str, object] = Field(default_factory=dict)
    severity: Literal["minor", "moderate", "major"]


class PostMortem(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    overall_summary: str
    rigor_explanation: str
    feasibility_explanation: str
    fidelity_explanation: str
    key_decisions: list[str] = Field(default_factory=list)
    missed_opportunities: list[str] = Field(default_factory=list)
    comparison_note: str


__all__ = [
    "AdjudicatorRoundScore",
    "AdjudicatorTerminalScore",
    "Difficulty",
    "EnvironmentEvent",
    "Equipment",
    "LabConstraints",
    "LabManagerResponse",
    "MinimumViableSpec",
    "OracleLabManagerObservation",
    "OracleScientistObservation",
    "Paper",
    "PostMortem",
    "Reagent",
    "Scenario",
    "StaffMember",
    "Substitution",
]
