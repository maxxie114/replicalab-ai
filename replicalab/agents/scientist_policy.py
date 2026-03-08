"""Scientist policy helpers.

MOD 09 introduced strict parsing from raw model output into
``ScientistAction``. AGT 01 adds the first domain-neutral system prompt
builder so prompt assembly can be driven by the normalized scenario pack
instead of hard-coded domain text. AGT 02 adds the per-turn observation
formatter that converts a ``ScientistObservation`` into the user message
sent to the model each round. AGT 03 wraps the formatter and parser in a
retry loop with error-specific correction prompts and exposed telemetry.
AGT 04 adds a deterministic baseline Scientist so smoke tests can run
without a trained model.
"""

from __future__ import annotations

import json
import logging
import re
from importlib import import_module
from typing import Any, Callable, Literal, Mapping

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from replicalab.models import (
    ConversationEntry,
    Protocol,
    ScientistAction,
    ScientistActionType,
    ScientistObservation,
)
from replicalab.scenarios import NormalizedScenarioPack

log = logging.getLogger(__name__)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
_ML_HINTS = (
    "benchmark",
    "dataset",
    "accuracy",
    "tokenizer",
    "train",
    "gpu",
    "cifar",
    "ag news",
    "bert",
    "resnet",
)
_FINANCE_HINTS = (
    "backtest",
    "drawdown",
    "sharpe",
    "trading",
    "slippage",
    "capital",
    "spy",
    "qqq",
    "futures",
)
_BLOCKER_HINTS = (
    "booked",
    "unavailable",
    "not available",
    "exceeds",
    "tight",
    "limited",
    "deadline",
    "budget",
    "cost",
    "drawdown",
    "slippage",
    "risk",
    "conflict",
)


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


GenerateFn = Callable[[list[dict[str, str]]], str]
"""Type alias for the injected model backend.

Takes a list of chat messages (each ``{"role": ..., "content": ...}``)
and returns the raw model output string.
"""


class RetryMetadata(BaseModel):
    """Telemetry from a single ``call_scientist_with_retry`` invocation.

    Exposed so training metrics (TRN 15) and eval (OBS 09) can track
    retry rates and failure modes without hidden state.
    """

    model_config = ConfigDict(extra="forbid")

    attempt_count: int
    retry_count: int
    last_error_code: str | None = None
    last_error_message: str | None = None


class ScientistCallResult(BaseModel):
    """Bundled action and retry telemetry from ``call_scientist_with_retry``."""

    model_config = ConfigDict(extra="forbid")

    action: ScientistAction
    metadata: RetryMetadata


def call_scientist_with_retry(
    generate_fn: GenerateFn,
    system_prompt: str,
    observation: ScientistObservation,
    *,
    max_retries: int = 2,
    user_message_override: str | None = None,
) -> ScientistCallResult:
    """Call a model backend to produce a ``ScientistAction`` with parser-driven retries.

    On parse failure the error is fed back to the model as a correction
    prompt and the model is asked to try again, up to *max_retries* times.
    No fields are silently auto-fixed.  If all attempts fail the last
    ``ScientistOutputParseError`` is raised.

    Parameters
    ----------
    generate_fn:
        Injected model backend.  Called with a list of chat message dicts
        and must return the raw text output.  No Qwen/API-specific logic
        lives here — any callable with the right signature works.
    system_prompt:
        The system prompt built by ``build_scientist_system_prompt``.
    observation:
        The current-turn ``ScientistObservation``.
    max_retries:
        Maximum number of correction attempts after the first call.
        Default is 2 (so up to 3 total attempts).
    """

    user_message = user_message_override or format_scientist_observation(observation)
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    last_error: ScientistOutputParseError | None = None
    total_attempts = 1 + max_retries

    for attempt in range(1, total_attempts + 1):
        raw_text = generate_fn(messages)

        try:
            action = parse_scientist_output(raw_text)
            return ScientistCallResult(
                action=action,
                metadata=RetryMetadata(
                    attempt_count=attempt,
                    retry_count=attempt - 1,
                    last_error_code=last_error.code if last_error else None,
                    last_error_message=last_error.message if last_error else None,
                ),
            )
        except ScientistOutputParseError as exc:
            last_error = exc
            log.info(
                "Scientist parse failure attempt=%d/%d code=%s",
                attempt,
                total_attempts,
                exc.code,
            )

            if attempt < total_attempts:
                messages.append({"role": "assistant", "content": raw_text})
                messages.append({
                    "role": "user",
                    "content": _build_correction_prompt(exc),
                })

    assert last_error is not None  # guaranteed by loop structure
    raise last_error


def _build_correction_prompt(error: ScientistOutputParseError) -> str:
    """Build an error-specific correction message for the model."""

    suffix = (
        "Return exactly one JSON object with all ScientistAction fields. "
        "No markdown fences, no prose — only the JSON object."
    )

    if error.code == "no_json":
        return (
            "Your previous response did not contain a JSON object. " + suffix
        )

    if error.code == "invalid_json":
        return (
            f"Your previous response contained malformed JSON: {error.message} "
            + suffix
        )

    # invalid_action
    return (
        "Your previous response contained valid JSON but it failed "
        f"ScientistAction validation: {error.message} "
        "Fix the validation error and return a corrected JSON object. " + suffix
    )


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
        (
            "Bounded tool policy: you have access to three bounded tools. "
            "search_evidence retrieves supporting facts from frozen evidence packs. "
            "run_code_check performs bounded code analysis, config validation, and "
            "derived-value computation. "
            "inspect_image extracts information from figures, tables, charts, and "
            "screenshots. "
            "Rules: use tools only to support or verify claims within the current "
            "scenario constraints. Tools do not override constraints, loosen limits, "
            "or reveal hidden ground truth. No unrestricted web browsing. No audio "
            "capabilities. No autonomous code execution beyond bounded analysis."
        ),
    ]

    return "\n\n".join(section for section in sections if section)


def format_scientist_observation(obs: ScientistObservation) -> str:
    """Format a per-turn ``ScientistObservation`` into a user-message string.

    The output is deterministic and side-effect free.  Sections appear in a
    fixed order so downstream tests can assert on stable labels.
    """

    sections: list[str] = []

    # Round status
    sections.append(f"Round {obs.round_number} of {obs.max_rounds}.")

    # Paper / task summary
    sections.append(
        f"Paper: {obs.paper_title}\n"
        f"Hypothesis: {obs.paper_hypothesis}\n"
        f"Method: {obs.paper_method}\n"
        f"Key finding: {obs.paper_key_finding}\n"
        f"Goal: {obs.experiment_goal}"
    )

    # Conversation history
    if obs.conversation_history:
        sections.append(
            "Conversation so far:\n" + _render_history(obs.conversation_history)
        )
    else:
        sections.append("No conversation history yet. You are making the first move.")

    # Current protocol snapshot
    if obs.current_protocol is not None:
        sections.append(
            "Current protocol:\n" + _render_protocol(obs.current_protocol)
        )
    else:
        sections.append("No protocol has been proposed yet.")

    allowed_actions = ", ".join(action.value for action in ScientistActionType)
    sections.append(
        "ScientistAction schema reminder:\n"
        f"  allowed action_type values: {allowed_actions}\n"
        "  include all ScientistAction fields in every response: action_type, "
        "sample_size, controls, technique, duration_days, required_equipment, "
        "required_reagents, questions, rationale\n"
        "  use empty lists, zero values, or empty strings for fields that do "
        "not apply to the selected action_type"
    )

    # Closing instruction
    sections.append(
        "Respond with exactly one JSON object containing your next "
        "ScientistAction and no extra text."
    )

    return "\n\n".join(sections)


def build_baseline_scientist_action(
    observation: ScientistObservation,
) -> ScientistAction:
    """Return a deterministic baseline Scientist action for smoke tests.

    The baseline follows a conservative policy:
    - propose a valid protocol when no protocol exists yet
    - revise the current protocol if the latest Lab Manager message contains
      an obvious feasibility blocker
    - otherwise accept the current protocol to complete the episode cleanly
    """

    latest_feedback = _latest_lab_manager_feedback(observation)

    if observation.current_protocol is not None:
        if observation.round_number >= max(1, observation.max_rounds - 1):
            return _build_accept_action()
        if latest_feedback and _feedback_indicates_blocker(latest_feedback):
            return _build_revision_action(observation.current_protocol, latest_feedback)
        return _build_accept_action()

    return _build_initial_protocol_action(observation)


def _render_history(entries: list[ConversationEntry]) -> str:
    lines: list[str] = []
    for entry in entries:
        tag = entry.role.upper()
        action_suffix = f" [{entry.action_type}]" if entry.action_type else ""
        lines.append(f"  [{tag} r{entry.round_number}{action_suffix}]: {entry.message}")
    return "\n".join(lines)


def _render_protocol(protocol: Protocol) -> str:
    lines = [
        f"  technique: {protocol.technique}",
        f"  sample_size: {protocol.sample_size}",
        f"  controls: {', '.join(protocol.controls) if protocol.controls else '(none)'}",
        f"  duration_days: {protocol.duration_days}",
        f"  required_equipment: {', '.join(protocol.required_equipment) if protocol.required_equipment else '(none)'}",
        f"  required_reagents: {', '.join(protocol.required_reagents) if protocol.required_reagents else '(none)'}",
        f"  rationale: {protocol.rationale}",
    ]
    return "\n".join(lines)


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


def _build_accept_action() -> ScientistAction:
    return ScientistAction(
        action_type=ScientistActionType.ACCEPT,
        sample_size=0,
        controls=[],
        technique="",
        duration_days=0,
        required_equipment=[],
        required_reagents=[],
        questions=[],
        rationale="",
    )


def _build_initial_protocol_action(
    observation: ScientistObservation,
) -> ScientistAction:
    domain = _infer_domain(observation)
    defaults = _baseline_defaults_for_domain(domain)

    return ScientistAction(
        action_type=ScientistActionType.PROPOSE_PROTOCOL,
        sample_size=defaults["sample_size"],
        controls=list(defaults["controls"]),
        technique=defaults["technique"],
        duration_days=defaults["duration_days"],
        required_equipment=[],
        required_reagents=[],
        questions=[],
        rationale=(
            f"Baseline proposal for {observation.paper_title}: "
            f"use a concise {defaults['technique']} plan aligned to the stated goal "
            f"'{observation.experiment_goal}'."
        ),
    )


def _build_revision_action(
    protocol: Protocol,
    feedback: ConversationEntry,
) -> ScientistAction:
    reduced_sample_size = max(1, protocol.sample_size // 2) if protocol.sample_size else 1
    reduced_duration = max(1, protocol.duration_days - 1) if protocol.duration_days else 1
    revised_controls = list(protocol.controls) or ["fallback_review"]

    return ScientistAction(
        action_type=ScientistActionType.REVISE_PROTOCOL,
        sample_size=reduced_sample_size,
        controls=revised_controls,
        technique=protocol.technique,
        duration_days=reduced_duration,
        required_equipment=list(protocol.required_equipment),
        required_reagents=list(protocol.required_reagents),
        questions=[],
        rationale=(
            "Baseline revision reduces scope to address the latest Lab Manager "
            f"concern: {feedback.message}"
        ),
    )


def _latest_lab_manager_feedback(
    observation: ScientistObservation,
) -> ConversationEntry | None:
    for entry in reversed(observation.conversation_history):
        if entry.role == "lab_manager":
            return entry
    return None


def _feedback_indicates_blocker(feedback: ConversationEntry) -> bool:
    """Return True only when the lab manager is flagging a real blocker.

    An ``accept`` action_type means the protocol passed — even if the
    explanation text mentions words like "budget" or "schedule".
    """
    if feedback.action_type in ("accept", "report_feasibility"):
        return False
    lowered = feedback.message.lower()
    return any(token in lowered for token in _BLOCKER_HINTS)


def _infer_domain(observation: ScientistObservation) -> str:
    haystack = " ".join(
        [
            observation.paper_title,
            observation.paper_hypothesis,
            observation.paper_method,
            observation.paper_key_finding,
            observation.experiment_goal,
        ]
    ).lower()

    if any(token in haystack for token in _ML_HINTS):
        return "machine_learning"
    if any(token in haystack for token in _FINANCE_HINTS):
        return "finance_trading"
    return "mathematics"


def _baseline_defaults_for_domain(domain: str) -> dict[str, Any]:
    if domain == "machine_learning":
        return {
            "sample_size": 8,
            "controls": ["published_split_check", "heldout_evaluation"],
            "technique": "published_split_replication",
            "duration_days": 2,
        }
    if domain == "finance_trading":
        return {
            "sample_size": 12,
            "controls": ["drawdown_guardrail", "offline_evaluation_split"],
            "technique": "offline_backtest_workflow",
            "duration_days": 2,
        }
    return {
        "sample_size": 4,
        "controls": ["equality_case_check", "final_verification_pass"],
        "technique": "structured_proof_outline",
        "duration_days": 1,
    }


def build_openai_scientist_policy(
    *,
    api_key: str,
    model: str,
    max_completion_tokens: int = 450,
    temperature: float = 0.0,
    max_retries: int = 2,
    timeout_seconds: float = 60.0,
) -> Callable[[ScientistObservation], ScientistAction]:
    """Create a sync Scientist policy callable backed by OpenAI Chat Completions API."""

    try:
        import openai as _openai  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "openai package required for openai scientist runtime. "
            "Install it with: pip install openai"
        ) from exc

    client = _openai.OpenAI(api_key=api_key, timeout=timeout_seconds)

    def generate_fn(messages: list[dict[str, str]]) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore[arg-type]
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
        )
        return _extract_message_content(response.choices[0].message.content)

    def policy_fn(
        observation: ScientistObservation,
        *,
        seed: int | None = None,
        scenario: str | None = None,
        difficulty: str | None = None,
    ) -> ScientistAction:
        result = call_scientist_with_retry(
            generate_fn,
            _build_live_scientist_system_prompt(
                observation,
                difficulty=difficulty,
                scenario=scenario,
            ),
            observation,
            max_retries=max_retries,
        )
        return result.action

    return policy_fn


def build_remote_scientist_policy(
    *,
    project: str,
    model_name: str,
    base_model: str,
    checkpoint_step: int | None = None,
    max_completion_tokens: int = 450,
    temperature: float = 0.0,
    max_retries: int = 2,
) -> Callable[[ScientistObservation], ScientistAction]:
    """Create a sync policy callable backed by an ART serverless checkpoint."""

    try:
        art_module = import_module("art")
        serverless_module = import_module("art.serverless")
        openai_module = import_module("openai")
    except ImportError as exc:
        raise RuntimeError(
            "Missing optional inference dependency for remote Scientist evaluation. "
            "Install 'openpipe-art' and 'openai' before loading a trained checkpoint."
        ) from exc

    trainable_model = art_module.TrainableModel(
        name=model_name,
        project=project,
        base_model=base_model,
    )
    backend = serverless_module.ServerlessBackend()

    import asyncio

    asyncio.run(trainable_model.register(backend))
    if trainable_model.inference_api_key is None or trainable_model.inference_base_url is None:
        raise RuntimeError("ART serverless model registration did not expose inference credentials.")

    client = openai_module.OpenAI(
        base_url=trainable_model.inference_base_url,
        api_key=trainable_model.inference_api_key,
    )
    inference_name = trainable_model.get_inference_name(step=checkpoint_step)
    training_corpus = import_module("replicalab.training.corpus")
    evidence_packs = [
        pack for pack in training_corpus.load_frozen_evidence_packs() if pack.trainable_in_env
    ]

    def generate_fn(messages: list[dict[str, str]]) -> str:
        response = client.chat.completions.create(
            model=inference_name,
            messages=messages,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
        )
        return _extract_message_content(response.choices[0].message.content)

    def policy_fn(
        observation: ScientistObservation,
        *,
        seed: int | None = None,
        scenario: str | None = None,
        difficulty: str | None = None,
    ) -> ScientistAction:
        evidence_pack = None
        if seed is not None and scenario is not None:
            try:
                evidence_pack = training_corpus.select_evidence_pack(
                    evidence_packs,
                    template=scenario,
                    seed=seed,
                )
            except Exception:
                evidence_pack = None
        user_message = format_scientist_observation(observation)
        if evidence_pack is not None:
            user_message += "\n\nFrozen evidence pack:\n" + evidence_pack.prompt_block()
        result = call_scientist_with_retry(
            generate_fn,
            _build_live_scientist_system_prompt(
                observation,
                evidence_pack=evidence_pack,
                difficulty=difficulty,
                scenario=scenario,
            ),
            observation,
            max_retries=max_retries,
            user_message_override=user_message,
        )
        return result.action

    return policy_fn


def build_anthropic_scientist_policy(
    *,
    api_key: str,
    model: str,
    max_completion_tokens: int = 450,
    temperature: float = 0.0,
    max_retries: int = 2,
    timeout_seconds: float = 60.0,
    base_url: str = "https://api.anthropic.com/v1/messages",
    client: httpx.Client | None = None,
) -> Callable[[ScientistObservation], ScientistAction]:
    """Create a sync Scientist policy callable backed by Anthropic Messages API."""

    owned_client = client is None
    transport = client or httpx.Client(timeout=timeout_seconds)

    def generate_fn(messages: list[dict[str, str]]) -> str:
        system_blocks = [msg["content"] for msg in messages if msg["role"] == "system"]
        request_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
            if msg["role"] in {"user", "assistant"}
        ]
        response = transport.post(
            base_url,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": max_completion_tokens,
                "temperature": temperature,
                "system": "\n\n".join(system_blocks),
                "messages": request_messages,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return _extract_anthropic_message_text(payload.get("content", []))

    def policy_fn(
        observation: ScientistObservation,
        *,
        seed: int | None = None,
        scenario: str | None = None,
        difficulty: str | None = None,
    ) -> ScientistAction:
        result = call_scientist_with_retry(
            generate_fn,
            _build_live_scientist_system_prompt(
                observation,
                difficulty=difficulty,
                scenario=scenario,
            ),
            observation,
            max_retries=max_retries,
        )
        return result.action

    setattr(policy_fn, "_replicalab_client", transport)
    setattr(policy_fn, "_replicalab_owned_client", owned_client)
    return policy_fn


def build_ollama_scientist_policy(
    *,
    model: str,
    max_retries: int = 2,
    temperature: float = 0.0,
    timeout_seconds: float = 60.0,
    base_url: str = "http://127.0.0.1:11434/api/chat",
    client: httpx.Client | None = None,
) -> Callable[[ScientistObservation], ScientistAction]:
    """Create a sync Scientist policy callable backed by a local Ollama model."""

    owned_client = client is None
    transport = client or httpx.Client(timeout=timeout_seconds)

    def generate_fn(messages: list[dict[str, str]]) -> str:
        response = transport.post(
            base_url,
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": temperature,
                },
            },
        )
        response.raise_for_status()
        payload = response.json()
        return _extract_message_content(payload.get("message", {}).get("content", ""))

    def policy_fn(
        observation: ScientistObservation,
        *,
        seed: int | None = None,
        scenario: str | None = None,
        difficulty: str | None = None,
    ) -> ScientistAction:
        result = call_scientist_with_retry(
            generate_fn,
            _build_live_scientist_system_prompt(
                observation,
                difficulty=difficulty,
                scenario=scenario,
            ),
            observation,
            max_retries=max_retries,
        )
        return result.action

    setattr(policy_fn, "_replicalab_client", transport)
    setattr(policy_fn, "_replicalab_owned_client", owned_client)
    return policy_fn


def _build_live_scientist_system_prompt(
    observation: ScientistObservation,
    *,
    evidence_pack: Any | None = None,
    difficulty: str | None = None,
    scenario: str | None = None,
) -> str:
    allowed_actions = ", ".join(action.value for action in ScientistActionType)
    sections = [
        "You are the Scientist agent in ReplicaLab.",
        (
            "Your job is to negotiate toward the strongest feasible plan under the "
            "provided constraints. You do not invent resources, loosen constraints, "
            "or assume hidden ground truth."
        ),
        (
            "Return exactly one JSON object with all ScientistAction fields and no "
            "extra keys or prose."
        ),
        f"Allowed action_type values: {allowed_actions}.",
        (
            "For propose_protocol and revise_protocol, include a full protocol payload "
            "with sample_size >= 1, controls, technique, duration_days >= 0, "
            "required_equipment, required_reagents, questions = [], and rationale."
        ),
        (
            "For request_info, keep protocol fields empty or zero and include at least "
            "one concrete blocking question."
        ),
        (
            "For accept, keep all protocol-edit fields empty or zero and use an empty "
            "questions list."
        ),
        (
            "Bounded tool policy: search_evidence, run_code_check, and inspect_image "
            "support the current scenario only. They do not override constraints."
        ),
        f"Paper title: {observation.paper_title}",
        f"Goal: {observation.experiment_goal}",
    ]
    if scenario:
        sections.append(f"Scenario family: {scenario}")
    if difficulty:
        sections.append(f"Difficulty: {difficulty}")
    if evidence_pack is not None:
        sections.extend(
            [
                f"Frozen evidence id: {evidence_pack.evidence_id}",
                f"Grounding paper: {evidence_pack.downloaded_paper_title}",
                f"Claim: {evidence_pack.claim}",
                f"Technique: {evidence_pack.key_technique}",
                f"Constraint tension: {evidence_pack.primary_constraint_tension}",
            ]
        )
    return "\n\n".join(sections)


def _extract_message_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
                continue
            text = getattr(item, "text", None)
            if text:
                parts.append(str(text))
        return "\n".join(parts)
    return ""


def _extract_anthropic_message_text(content: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") != "text":
            continue
        text = block.get("text")
        if text:
            parts.append(str(text))
    return "\n".join(parts)
