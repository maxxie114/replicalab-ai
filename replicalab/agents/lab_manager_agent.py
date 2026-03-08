"""Optional LLM-backed Lab Manager narration layer."""

from __future__ import annotations

import json
from typing import Any

from replicalab.oracle import call_json_model
from replicalab.oracle_models import LabManagerResponse, OracleLabManagerObservation
from replicalab.prompts import load_prompt_asset


class LabManagerAgent:
    """LLM-based Lab Manager driven by Oracle-generated constraints.

    This is additive to the deterministic feasibility checker. The current
    env can use this agent to narrate or enrich responses while keeping
    canonical feasibility and reward logic deterministic.
    """

    def __init__(self, client: Any, model: str = "frontier-oracle") -> None:
        self.client = client
        self.model = model

    def respond(self, observation: OracleLabManagerObservation) -> LabManagerResponse:
        system = load_prompt_asset("oracle_lab_manager")
        user = (
            "A Scientist has taken an action. Respond as the Lab Manager.\n\n"
            "YOUR LAB CONSTRAINTS (ground truth, do not deviate):\n"
            f"{observation.lab_constraints.model_dump_json(indent=2)}\n\n"
            "CURRENT PROTOCOL ON THE TABLE:\n"
            f"{json.dumps(observation.current_protocol, indent=2) if observation.current_protocol else 'None yet'}\n\n"
            f"SCIENTIST'S ACTION (round {observation.round_number}):\n"
            f"{observation.scientist_action.model_dump_json(indent=2)}\n\n"
            "Respond ONLY with valid JSON matching LabManagerResponse.\n"
            "No markdown. No preamble."
        )
        return call_json_model(
            self.client,
            model=self.model,
            system=system,
            user=user,
            response_model=LabManagerResponse,
        )


__all__ = ["LabManagerAgent"]
