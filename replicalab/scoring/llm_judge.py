"""LLM-based judge scoring via OpenRouter.

When the LLM judge is enabled, this module sends the protocol and scenario
to an external LLM (e.g. Gemini) and parses a structured RewardBreakdown
from the response.  Falls back to the deterministic scorer on failure.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import httpx

from replicalab.models import Protocol, RewardBreakdown
from replicalab.scenarios.templates import NormalizedScenarioPack

log = logging.getLogger("replicalab.scoring.llm_judge")

_SYSTEM_PROMPT = (
    "You are an expert scientific protocol judge. Given a protocol and scenario, "
    "evaluate the protocol and return a JSON object with these float fields "
    "(all between 0.0 and 1.0): rigor, feasibility, fidelity, parsimony. "
    "Return ONLY valid JSON, no markdown fences."
)


def build_llm_reward_breakdown(
    *,
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    rounds_used: int,
    max_rounds: int,
    api_key: str,
    model: str = "google/gemini-2.5-pro-preview-03-25",
    base_url: str = "https://openrouter.ai/api/v1",
) -> RewardBreakdown:
    """Call an LLM judge via OpenRouter and parse a RewardBreakdown.

    On any failure (network, parse, validation), falls back to the
    deterministic scorer.
    """
    user_prompt = _build_user_prompt(protocol, scenario)

    try:
        response = httpx.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.0,
                "max_tokens": 512,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        scores = json.loads(content)

        breakdown = RewardBreakdown(
            rigor=_clamp(scores.get("rigor", 0.0)),
            feasibility=_clamp(scores.get("feasibility", 0.0)),
            fidelity=_clamp(scores.get("fidelity", 0.0)),
            parsimony=_clamp(scores.get("parsimony", 1.0)),
        )
        log.info("LLM judge returned scores: %s", scores)
        return breakdown

    except Exception:
        log.exception("LLM judge call failed; falling back to deterministic scorer")
        return _fallback(protocol, scenario, rounds_used, max_rounds)


def _build_user_prompt(protocol: Protocol, scenario: NormalizedScenarioPack) -> str:
    return (
        f"Scenario: {scenario.task_summary}\n"
        f"Domain: {scenario.domain_id}\n"
        f"Success criteria: {', '.join(scenario.success_criteria)}\n"
        f"Required elements: {', '.join(scenario.hidden_reference_spec.required_elements)}\n"
        f"Target: {scenario.hidden_reference_spec.target_metric} = "
        f"{scenario.hidden_reference_spec.target_value}\n\n"
        f"Protocol technique: {protocol.technique}\n"
        f"Sample size: {protocol.sample_size}\n"
        f"Controls: {', '.join(protocol.controls)}\n"
        f"Duration: {protocol.duration_days} days\n"
        f"Equipment: {', '.join(protocol.required_equipment)}\n"
        f"Reagents: {', '.join(protocol.required_reagents)}\n"
        f"Rationale: {protocol.rationale}\n\n"
        "Evaluate rigor, feasibility, fidelity, and parsimony (each 0.0-1.0)."
    )


def _clamp(value: float) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, v))


def _fallback(
    protocol: Protocol,
    scenario: NormalizedScenarioPack,
    rounds_used: int,
    max_rounds: int,
) -> RewardBreakdown:
    from replicalab.scoring.rubric import build_reward_breakdown

    return build_reward_breakdown(
        protocol=protocol,
        scenario=scenario,
        rounds_used=rounds_used,
        max_rounds=max_rounds,
    )
