"""Scientist policy helpers.

MOD 09 introduced strict parsing from raw model output into
``ScientistAction``. AGT 01 adds the first domain-neutral system prompt
builder so prompt assembly can be driven by the normalized scenario pack
instead of hard-coded domain text.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal, Mapping

from pydantic import ValidationError

from replicalab.models import ScientistAction, ScientistActionType
from replicalab.scenarios import NormalizedScenarioPack

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


class ScientistOutputParseError(ValueError):
    """Explicit parser error for malformed or invalid Scientist output."""

    def __init__(
        self,
        code: Literal["no_json", "invalid_json", "invalid_action"],
        message: str,
        raw_text: str,
        *,
        parsed_payload: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.raw_text = raw_text
        self.parsed_payload = parsed_payload

    def to_dict(self) -> dict[str, Any]:
        """Return a stable error shape for callers and future retries."""

        return {
            "code": self.code,
            "message": self.message,
            "raw_text": self.raw_text,
            "parsed_payload": self.parsed_payload,
        }


def build_scientist_system_prompt(
    scenario: NormalizedScenarioPack | Mapping[str, Any],
) -> str:
    """Build a domain-neutral Scientist system prompt from normalized data."""

    pack = _coerce_scenario_pack(scenario)
    allowed_actions = ", ".join(action.value for action in ScientistActionType)

    sections = [
        "You are the Scientist agent in ReplicaLab.",
        (
            "Your job is to negotiate toward the strongest feasible plan under the "
            "provided constraints. You do not invent resources, loosen constraints, "
            "or assume access to hidden ground truth."
        ),
        f"Domain: {pack.domain_id}",
        f"Task: {pack.task_summary}",
        "Success criteria:",
        _render_bullets(pack.success_criteria),
        "Constraints:",
        _render_constraints(pack),
        "Available resources:",
        _render_resources(pack),
        "Allowed substitutions:",
        _render_substitutions(pack),
        (
            "Output contract: return exactly one JSON object with all "
            "ScientistAction fields and no extra keys."
        ),
        f"Allowed action_type values: {allowed_actions}.",
        (
            "Use propose_protocol or revise_protocol only when you can provide a full "
            "protocol payload. Use request_info only when a blocking question remains. "
            "Use accept only when the plan is ready without further edits."
        ),
        (
            "For propose_protocol and revise_protocol, the JSON must include: "
            "sample_size >= 1, controls, technique, duration_days >= 0, "
            "required_equipment, required_reagents, questions = [], and rationale."
        ),
        (
            "For request_info, all protocol fields must stay empty or zero and "
            "questions must contain at least one concrete question."
        ),
        (
            "For accept, questions must be empty and protocol-edit fields must stay "
            "empty or zero."
        ),
    ]

    return "\n\n".join(section for section in sections if section)


def parse_scientist_output(raw_text: str) -> ScientistAction:
    """Parse raw model text into a validated ``ScientistAction``.

    The parser accepts:
    - plain JSON objects
    - fenced JSON blocks
    - prose that contains one JSON object
    """

    payload = _parse_json_payload(raw_text)
    try:
        return ScientistAction.model_validate(payload)
    except ValidationError as exc:
        raise ScientistOutputParseError(
            "invalid_action",
            _format_validation_error(exc),
            raw_text,
            parsed_payload=payload,
        ) from exc


def _parse_json_payload(raw_text: str) -> dict[str, Any]:
    if not raw_text.strip():
        raise ScientistOutputParseError(
            "no_json",
            "Scientist output is empty and does not contain a JSON object.",
            raw_text,
        )

    saw_json_like_text = False
    last_json_error: json.JSONDecodeError | None = None

    for candidate in _iter_json_candidates(raw_text):
        saw_json_like_text = True
        try:
            decoded = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_json_error = exc
            continue

        if not isinstance(decoded, dict):
            raise ScientistOutputParseError(
                "invalid_json",
                "Scientist output must decode to a JSON object.",
                raw_text,
            )
        return decoded

    if saw_json_like_text and last_json_error is not None:
        raise ScientistOutputParseError(
            "invalid_json",
            (
                "Scientist output contains JSON-like text but it could not be decoded: "
                f"{last_json_error.msg} at line {last_json_error.lineno}, "
                f"column {last_json_error.colno}."
            ),
            raw_text,
        ) from last_json_error

    raise ScientistOutputParseError(
        "no_json",
        "Scientist output does not contain a JSON object.",
        raw_text,
    )


def _iter_json_candidates(raw_text: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()

    def add(candidate: str | None) -> None:
        if candidate is None:
            return
        cleaned = candidate.strip()
        if not cleaned or cleaned in seen:
            return
        seen.add(cleaned)
        candidates.append(cleaned)

    stripped = raw_text.strip()
    if stripped.startswith("{") or stripped.startswith("```"):
        add(raw_text)
    add(_extract_first_json_object(raw_text))

    for match in _JSON_FENCE_RE.finditer(raw_text):
        fenced = match.group(1)
        add(fenced)
        add(_extract_first_json_object(fenced))

    return candidates


def _extract_first_json_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None


def _format_validation_error(error: ValidationError) -> str:
    parts: list[str] = []
    for item in error.errors():
        path = ".".join(str(segment) for segment in item.get("loc", ()))
        message = item.get("msg", "Validation error")
        parts.append(f"{path}: {message}" if path else message)

    detail = "; ".join(parts) if parts else str(error)
    return f"Scientist output JSON failed ScientistAction validation: {detail}"


def _coerce_scenario_pack(
    scenario: NormalizedScenarioPack | Mapping[str, Any],
) -> NormalizedScenarioPack:
    if isinstance(scenario, NormalizedScenarioPack):
        return scenario
    return NormalizedScenarioPack.model_validate(scenario)


def _render_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _render_constraints(pack: NormalizedScenarioPack) -> str:
    lines = []
    for constraint in pack.constraints:
        amount = ""
        if constraint.quantity is not None:
            unit = f" {constraint.unit}" if constraint.unit else ""
            amount = f" ({constraint.comparator} {constraint.quantity}{unit})"
        hardness = "hard" if constraint.hard else "soft"
        lines.append(f"- [{hardness}] {constraint.label}{amount}: {constraint.details}")
    return "\n".join(lines)


def _render_resources(pack: NormalizedScenarioPack) -> str:
    lines = []
    for resource in pack.resources:
        availability = "available" if resource.available else "unavailable"
        amount = ""
        if resource.quantity is not None:
            unit = f" {resource.unit}" if resource.unit else ""
            amount = f" ({resource.quantity}{unit})"
        lines.append(
            f"- [{availability}] {resource.label}{amount}: {resource.details}"
        )
    return "\n".join(lines)


def _render_substitutions(pack: NormalizedScenarioPack) -> str:
    if not pack.allowed_substitutions:
        return "- No substitutions are pre-approved."

    lines = []
    for substitution in pack.allowed_substitutions:
        lines.append(
            (
                f"- {substitution.original} -> {substitution.alternative}. "
                f"Condition: {substitution.condition} Tradeoff: {substitution.tradeoff}"
            )
        )
    return "\n".join(lines)
