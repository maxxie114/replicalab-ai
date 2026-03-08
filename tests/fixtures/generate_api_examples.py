#!/usr/bin/env python3
"""Generate api_schema_examples.json from real Pydantic models.

MOD 10 — run this script to regenerate the fixture whenever the
contracts change.  The output is deterministic.

Usage:
    python tests/fixtures/generate_api_examples.py
"""

from __future__ import annotations

import json
from pathlib import Path

from replicalab.config import DEFAULT_DIFFICULTY, DEFAULT_SCENARIO_TEMPLATE
from replicalab.agents.judge_policy import build_judge_audit
from replicalab.models import (
    ConversationEntry,
    EpisodeLog,
    EpisodeState,
    LabManagerObservation,
    Observation,
    Protocol,
    RewardBreakdown,
    ScientistAction,
    ScientistObservation,
    StepInfo,
    StepResult,
)
from replicalab.scenarios import available_scenario_families, generate_scenario
from replicalab.scoring.rubric import compute_total_reward

OUTPUT_PATH = Path(__file__).parent / "api_schema_examples.json"

# ---------------------------------------------------------------------------
# Build realistic payloads from real models
# ---------------------------------------------------------------------------

_SEED = 42
_TEMPLATE = DEFAULT_SCENARIO_TEMPLATE
_DIFFICULTY = DEFAULT_DIFFICULTY

# Generate a real scenario to extract observation data
_pack = generate_scenario(seed=_SEED, template=_TEMPLATE, difficulty=_DIFFICULTY)
_sci_obs = _pack.scientist_observation
_lm_obs = _pack.lab_manager_observation
_TERMINAL_BREAKDOWN = RewardBreakdown(
    rigor=0.8,
    feasibility=0.8,
    fidelity=0.8,
    efficiency_bonus=0.2,
    communication_bonus=0.1,
    penalties={},
)
_TERMINAL_AUDIT = build_judge_audit(
    _TERMINAL_BREAKDOWN,
    agreement_reached=True,
    rounds_used=3,
    max_rounds=_sci_obs.max_rounds,
)
_TERMINAL_REWARD = compute_total_reward(_TERMINAL_BREAKDOWN)


def _reset_request():
    return {
        "seed": _SEED,
        "scenario": _TEMPLATE,
        "difficulty": _DIFFICULTY,
        "session_id": None,
    }


def _reset_response():
    obs = Observation(scientist=_sci_obs, lab_manager=_lm_obs)
    return {
        "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "episode_id": "ep-deadbeef-1234-5678-9abc-def012345678",
        "observation": obs.model_dump(),
    }


def _propose_action():
    return ScientistAction(
        action_type="propose_protocol",
        sample_size=30,
        controls=["positive_control", "negative_control"],
        technique=_sci_obs.paper_method,
        duration_days=5,
        required_equipment=list(_lm_obs.equipment_available[:2]) if _lm_obs.equipment_available else ["tool_a"],
        required_reagents=list(_lm_obs.reagents_in_stock[:2]) if _lm_obs.reagents_in_stock else ["ref_a"],
        questions=[],
        rationale="Initial proposal using available resources.",
    ).model_dump()


def _step_request():
    return {
        "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "action": _propose_action(),
    }


def _mid_episode_step_result():
    protocol = Protocol(
        sample_size=30,
        controls=["positive_control", "negative_control"],
        technique=_sci_obs.paper_method,
        duration_days=5,
        required_equipment=list(_lm_obs.equipment_available[:2]) if _lm_obs.equipment_available else ["tool_a"],
        required_reagents=list(_lm_obs.reagents_in_stock[:2]) if _lm_obs.reagents_in_stock else ["ref_a"],
        rationale="Initial proposal using available resources.",
    )

    history = [
        ConversationEntry(
            role="scientist",
            message="Initial proposal using available resources.",
            round_number=1,
            action_type="propose_protocol",
        ),
        ConversationEntry(
            role="lab_manager",
            message="Budget is within range. Equipment is available.",
            round_number=1,
            action_type="report_feasibility",
        ),
    ]

    obs = Observation(
        scientist=ScientistObservation(
            paper_title=_sci_obs.paper_title,
            paper_hypothesis=_sci_obs.paper_hypothesis,
            paper_method=_sci_obs.paper_method,
            paper_key_finding=_sci_obs.paper_key_finding,
            experiment_goal=_sci_obs.experiment_goal,
            conversation_history=history,
            current_protocol=protocol,
            round_number=1,
            max_rounds=_sci_obs.max_rounds,
        ),
        lab_manager=LabManagerObservation(
            budget_total=_lm_obs.budget_total,
            budget_remaining=_lm_obs.budget_remaining,
            equipment_available=list(_lm_obs.equipment_available),
            equipment_booked=list(_lm_obs.equipment_booked),
            reagents_in_stock=list(_lm_obs.reagents_in_stock),
            reagents_out_of_stock=list(_lm_obs.reagents_out_of_stock),
            staff_count=_lm_obs.staff_count,
            time_limit_days=_lm_obs.time_limit_days,
            safety_restrictions=list(_lm_obs.safety_restrictions),
            conversation_history=history,
            current_protocol=protocol,
            round_number=1,
            max_rounds=_lm_obs.max_rounds,
        ),
    )

    return StepResult(
        observation=obs,
        reward=0.0,
        done=False,
        info=StepInfo(
            agreement_reached=False,
            error=None,
            reward_breakdown=None,
            judge_notes=None,
            verdict=None,
        ),
    ).model_dump()


def _terminal_step_result():
    return StepResult(
        observation=None,
        reward=_TERMINAL_REWARD,
        done=True,
        info=StepInfo(
            agreement_reached=True,
            error=None,
            reward_breakdown=_TERMINAL_BREAKDOWN,
            judge_notes=_TERMINAL_AUDIT.judge_notes,
            verdict=_TERMINAL_AUDIT.verdict,
            top_failure_reasons=list(_TERMINAL_AUDIT.top_failure_reasons),
        ),
    ).model_dump()


def _scenarios_response():
    return {"scenarios": available_scenario_families()}


def _replay_response():
    return EpisodeLog(
        episode_id="ep-deadbeef-1234-5678-9abc-def012345678",
        seed=_SEED,
        scenario_template=_TEMPLATE,
        difficulty=_DIFFICULTY,
        final_state=EpisodeState(
            seed=_SEED,
            scenario_template=_TEMPLATE,
            difficulty=_DIFFICULTY,
            paper_title=_sci_obs.paper_title,
            paper_hypothesis=_sci_obs.paper_hypothesis,
            paper_method=_sci_obs.paper_method,
            paper_key_finding=_sci_obs.paper_key_finding,
            experiment_goal=_sci_obs.experiment_goal,
            lab_budget_total=_lm_obs.budget_total,
            lab_budget_remaining=_lm_obs.budget_remaining,
            lab_equipment=list(_lm_obs.equipment_available),
            lab_reagents=list(_lm_obs.reagents_in_stock),
            lab_staff_count=_lm_obs.staff_count,
            lab_time_limit_days=_lm_obs.time_limit_days,
            round_number=3,
            max_rounds=_sci_obs.max_rounds,
            done=True,
            agreement_reached=True,
            reward=_TERMINAL_REWARD,
            rigor_score=_TERMINAL_BREAKDOWN.rigor,
            feasibility_score=_TERMINAL_BREAKDOWN.feasibility,
            fidelity_score=_TERMINAL_BREAKDOWN.fidelity,
            judge_notes=_TERMINAL_AUDIT.judge_notes,
            verdict=_TERMINAL_AUDIT.verdict,
            top_failure_reasons=list(_TERMINAL_AUDIT.top_failure_reasons),
        ),
        transcript=[
            ConversationEntry(
                role="scientist",
                message="Initial proposal using available resources.",
                round_number=1,
                action_type="propose_protocol",
            ),
            ConversationEntry(
                role="lab_manager",
                message="Budget is within range. Equipment is available.",
                round_number=1,
                action_type="report_feasibility",
            ),
        ],
        reward_breakdown=_TERMINAL_BREAKDOWN,
        total_reward=_TERMINAL_REWARD,
        rounds_used=3,
        agreement_reached=True,
        judge_notes=_TERMINAL_AUDIT.judge_notes,
        verdict=_TERMINAL_AUDIT.verdict,
        top_failure_reasons=list(_TERMINAL_AUDIT.top_failure_reasons),
    ).model_dump()


def _ws_reset_message():
    return {
        "type": "reset",
        "seed": _SEED,
        "scenario": _TEMPLATE,
        "difficulty": _DIFFICULTY,
    }


def _ws_reset_ok_message():
    obs = Observation(scientist=_sci_obs, lab_manager=_lm_obs)
    return {
        "type": "reset_ok",
        "episode_id": "ep-deadbeef-1234-5678-9abc-def012345678",
        "observation": obs.model_dump(),
    }


def _ws_step_message():
    return {
        "type": "step",
        "action": _propose_action(),
    }


def _ws_step_ok_message():
    return {
        "type": "step_ok",
        **_mid_episode_step_result(),
    }


# ---------------------------------------------------------------------------
# Assemble and write
# ---------------------------------------------------------------------------


def main():
    examples = {
        "_meta": {
            "generated_by": "tests/fixtures/generate_api_examples.py",
            "description": "API schema examples generated from real Pydantic models. Re-run the script to regenerate after contract changes.",
            "seed": _SEED,
            "scenario_template": _TEMPLATE,
            "difficulty": _DIFFICULTY,
        },
        "rest": {
            "POST /reset": {
                "request": _reset_request(),
                "response": _reset_response(),
            },
            "POST /step": {
                "request": _step_request(),
                "response_mid_episode": _mid_episode_step_result(),
                "response_terminal": _terminal_step_result(),
            },
            "GET /scenarios": {
                "response": _scenarios_response(),
            },
            "GET /replay/{episode_id}": {
                "response": _replay_response(),
            },
        },
        "websocket": {
            "reset": {
                "client_sends": _ws_reset_message(),
                "server_responds": _ws_reset_ok_message(),
            },
            "step": {
                "client_sends": _ws_step_message(),
                "server_responds": _ws_step_ok_message(),
            },
            "ping": {
                "client_sends": {"type": "ping"},
                "server_responds": {"type": "pong"},
            },
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(examples, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
