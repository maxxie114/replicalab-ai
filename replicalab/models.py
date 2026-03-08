"""Shared data contracts for the ReplicaLab environment.

FND 04: Empty Pydantic model stubs. Field names and types define the
contract shape. Full validators, constraints, and methods are added
in MOD 01-06 and MOD 11 by Person A.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Agent actions
# ---------------------------------------------------------------------------

class ScientistAction(BaseModel):
    """Action produced by the Scientist agent each turn.

    action_type values (to be constrained in MOD 01):
        propose_protocol, revise_protocol, request_info, accept
    """

    action_type: str = ""
    sample_size: int = 0
    controls: list[str] = []
    technique: str = ""
    duration_days: int = 0
    required_equipment: list[str] = []
    required_reagents: list[str] = []
    questions: list[str] = []
    rationale: str = ""


class LabManagerAction(BaseModel):
    """Action produced by the Lab Manager agent each turn.

    action_type values (to be constrained in MOD 02):
        report_feasibility, suggest_alternative, reject, accept
    """

    action_type: str = ""
    feasible: bool = True
    budget_ok: bool = True
    equipment_ok: bool = True
    reagents_ok: bool = True
    schedule_ok: bool = True
    staff_ok: bool = True
    suggested_technique: str = ""
    suggested_sample_size: int = 0
    suggested_controls: list[str] = []
    explanation: str = ""


# ---------------------------------------------------------------------------
# Observations
# ---------------------------------------------------------------------------

class ScientistObservation(BaseModel):
    """What the Scientist sees at the start of each turn."""

    paper_title: str = ""
    paper_hypothesis: str = ""
    paper_method: str = ""
    paper_key_finding: str = ""
    experiment_goal: str = ""
    conversation_history: list[dict] = []
    current_protocol: Optional[dict] = None
    round_number: int = 0
    max_rounds: int = 0


class LabManagerObservation(BaseModel):
    """What the Lab Manager sees at the start of each turn."""

    budget_total: float = 0.0
    budget_remaining: float = 0.0
    equipment_available: list[str] = []
    equipment_booked: list[str] = []
    reagents_in_stock: list[str] = []
    reagents_out_of_stock: list[str] = []
    staff_count: int = 0
    time_limit_days: int = 0
    safety_restrictions: list[str] = []
    conversation_history: list[dict] = []
    current_protocol: Optional[dict] = None
    round_number: int = 0
    max_rounds: int = 0


class Observation(BaseModel):
    """Combined observation wrapper. Each role receives its own view."""

    scientist: Optional[ScientistObservation] = None
    lab_manager: Optional[LabManagerObservation] = None


# ---------------------------------------------------------------------------
# Step result
# ---------------------------------------------------------------------------

class StepResult(BaseModel):
    """Returned by env.step(). Contains the next observation, reward,
    termination flag, and optional info dict."""

    observation: Optional[Observation] = None
    reward: float = 0.0
    done: bool = False
    info: dict = {}


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
    lab_equipment: list[str] = []
    lab_reagents: list[str] = []
    lab_staff_count: int = 0
    lab_time_limit_days: int = 0
    current_protocol: Optional[dict] = None
    conversation_history: list[dict] = []
    round_number: int = 0
    max_rounds: int = 0
    done: bool = False
    agreement_reached: bool = False
    reward: float = 0.0
    rigor_score: float = 0.0
    feasibility_score: float = 0.0
    fidelity_score: float = 0.0


class EpisodeLog(BaseModel):
    """Completed episode record for logging, replay, and evaluation."""

    episode_id: str = ""
    seed: int = 0
    scenario_template: str = ""
    difficulty: str = "easy"
    final_state: Optional[EpisodeState] = None
    transcript: list[dict] = []
    reward_breakdown: dict = {}
    total_reward: float = 0.0
    rounds_used: int = 0
    agreement_reached: bool = False
    judge_notes: str = ""
    verdict: str = ""
