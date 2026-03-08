"""Optional frontier-model Oracle wrapper for ReplicaLab.

The Oracle is an additive intelligence layer. It can generate richer
scenarios, optional round commentary, optional events, and post-mortem
analyses, while the existing deterministic reward pipeline remains
canonical for RL training.
"""

from __future__ import annotations

import json
from typing import Any, Optional, TypeVar

from pydantic import BaseModel

from replicalab.oracle_models import (
    AdjudicatorRoundScore,
    AdjudicatorTerminalScore,
    EnvironmentEvent,
    LabManagerResponse,
    PostMortem,
    Scenario,
)
from replicalab.prompts import load_prompt_asset

T = TypeVar("T", bound=BaseModel)


def _strip_markdown_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _extract_response_text(response: Any) -> str:
    if isinstance(response, str):
        return response

    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    content = getattr(response, "content", None)
    if content:
        chunks: list[str] = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                chunks.append(text)
        if chunks:
            return "\n".join(chunks)

    output = getattr(response, "output", None)
    if output:
        parts: list[str] = []
        for item in output:
            inner = getattr(item, "content", None)
            if not inner:
                continue
            for piece in inner:
                text = getattr(piece, "text", None)
                if text:
                    parts.append(text)
        if parts:
            return "\n".join(parts)

    raise ValueError("Could not extract text from Oracle client response")


def _invoke_client(client: Any, *, model: str, system: str, user: str) -> str:
    if hasattr(client, "messages") and hasattr(client.messages, "create"):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return _extract_response_text(response)

    if hasattr(client, "responses") and hasattr(client.responses, "create"):
        response = client.responses.create(
            model=model,
            instructions=system,
            input=user,
        )
        return _extract_response_text(response)

    if callable(client):
        try:
            response = client(system=system, user=user, model=model)
        except TypeError:
            response = client(system, user)
        return _extract_response_text(response)

    raise TypeError("Unsupported Oracle client: expected Anthropic/OpenAI-style client or callable")


def call_json_model(
    client: Any,
    *,
    model: str,
    system: str,
    user: str,
    response_model: type[T],
) -> T:
    raw = _invoke_client(client, model=model, system=system, user=user)
    cleaned = _strip_markdown_fences(raw)
    data = json.loads(cleaned)
    return response_model.model_validate(data)


class Oracle:
    """Single frontier model operating in multiple roles/personas."""

    def __init__(self, client: Any, model: str = "frontier-oracle") -> None:
        self.client = client
        self.model = model

    def generate_scenario(self, seed: int, difficulty: str, domain: str) -> Scenario:
        system = load_prompt_asset("oracle_world_architect")
        user = (
            "Generate a complete replication scenario.\n\n"
            f"Seed: {seed}\n"
            f"Difficulty: {difficulty}\n"
            f"Domain: {domain}\n\n"
            "Respond with a single JSON object matching the Scenario schema.\n"
            "No markdown, no explanation, only valid JSON."
        )
        return call_json_model(
            self.client,
            model=self.model,
            system=system,
            user=user,
            response_model=Scenario,
        )

    def score_round(
        self,
        *,
        scenario: Scenario,
        round_number: int,
        scientist_action: BaseModel,
        lab_manager_response: LabManagerResponse,
        conversation_history: list[dict],
        current_protocol: Optional[dict],
        previous_scores: list[AdjudicatorRoundScore],
    ) -> AdjudicatorRoundScore:
        system = load_prompt_asset("oracle_adjudicator")
        user = (
            "Score this negotiation round.\n\n"
            f"SCENARIO:\n{scenario.model_dump_json(indent=2)}\n\n"
            f"ROUND: {round_number}\n"
            f"SCIENTIST ACTION: {scientist_action.model_dump_json(indent=2)}\n"
            f"LAB MANAGER RESPONSE: {lab_manager_response.model_dump_json(indent=2)}\n"
            f"CURRENT PROTOCOL: {json.dumps(current_protocol, indent=2)}\n"
            f"PREVIOUS SCORES: {json.dumps([score.model_dump() for score in previous_scores], indent=2)}\n\n"
            "Respond with a single JSON object matching AdjudicatorRoundScore.\n"
            "No markdown, no explanation, only valid JSON."
        )
        return call_json_model(
            self.client,
            model=self.model,
            system=system,
            user=user,
            response_model=AdjudicatorRoundScore,
        )

    def score_terminal(
        self,
        *,
        scenario: Scenario,
        final_protocol: dict,
        conversation_history: list[dict],
        round_scores: list[AdjudicatorRoundScore],
    ) -> AdjudicatorTerminalScore:
        system = load_prompt_asset("oracle_adjudicator")
        user = (
            "Compute the terminal score for this completed episode.\n\n"
            f"SCENARIO:\n{scenario.model_dump_json(indent=2)}\n\n"
            f"FINAL PROTOCOL: {json.dumps(final_protocol, indent=2)}\n"
            f"CONVERSATION HISTORY: {json.dumps(conversation_history, indent=2)}\n"
            f"ROUND SCORES: {json.dumps([score.model_dump() for score in round_scores], indent=2)}\n"
            f"SUM OF STEP REWARDS: {sum(score.step_reward for score in round_scores)}\n\n"
            "Respond with a single JSON object matching AdjudicatorTerminalScore.\n"
            "No markdown, no explanation, only valid JSON."
        )
        return call_json_model(
            self.client,
            model=self.model,
            system=system,
            user=user,
            response_model=AdjudicatorTerminalScore,
        )

    def maybe_inject_event(
        self,
        *,
        scenario: Scenario,
        round_number: int,
        current_protocol: Optional[dict],
        conversation_history: list[dict],
        inject_enabled: bool = False,
    ) -> Optional[EnvironmentEvent]:
        if not inject_enabled:
            return None

        system = load_prompt_asset("oracle_event_injector")
        user = (
            "Decide whether to inject an event this round.\n\n"
            f"SCENARIO:\n{scenario.model_dump_json(indent=2)}\n\n"
            f"ROUND: {round_number}\n"
            f"CURRENT PROTOCOL: {json.dumps(current_protocol, indent=2)}\n"
            f"CONVERSATION SO FAR: {json.dumps(conversation_history, indent=2)}\n\n"
            'If no event is needed, respond with: {"inject": false}\n'
            'If injecting, respond with: {"inject": true, "event": <EnvironmentEvent JSON>}\n'
            "No markdown, no explanation, only valid JSON."
        )
        raw = _invoke_client(self.client, model=self.model, system=system, user=user)
        cleaned = _strip_markdown_fences(raw)
        data = json.loads(cleaned)
        if not data.get("inject", False):
            return None
        return EnvironmentEvent.model_validate(data["event"])

    def generate_post_mortem(
        self,
        *,
        scenario: Scenario,
        final_protocol: dict,
        conversation_history: list[dict],
        terminal_score: AdjudicatorTerminalScore,
    ) -> PostMortem:
        system = load_prompt_asset("oracle_post_mortem")
        user = (
            "Generate a post-mortem analysis of this episode.\n\n"
            f"PAPER: {scenario.paper.model_dump_json(indent=2)}\n"
            f"LAB CONSTRAINTS: {scenario.lab_constraints.model_dump_json(indent=2)}\n"
            f"HIDDEN SPEC: {scenario.minimum_viable_spec.model_dump_json(indent=2)}\n"
            f"FINAL PROTOCOL: {json.dumps(final_protocol, indent=2)}\n"
            f"CONVERSATION: {json.dumps(conversation_history, indent=2)}\n"
            f"TERMINAL SCORE: {terminal_score.model_dump_json(indent=2)}\n\n"
            "Respond with a single JSON object matching PostMortem.\n"
            "No markdown, no explanation, only valid JSON."
        )
        return call_json_model(
            self.client,
            model=self.model,
            system=system,
            user=user,
            response_model=PostMortem,
        )


__all__ = [
    "Oracle",
    "call_json_model",
]
