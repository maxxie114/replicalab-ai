from __future__ import annotations

import pytest

from replicalab.agents.scientist_policy import (
    RetryMetadata,
    ScientistCallResult,
    ScientistOutputParseError,
    build_baseline_scientist_action,
    build_scientist_system_prompt,
    call_scientist_with_retry,
    format_scientist_observation,
    parse_scientist_output,
)
from replicalab.models import (
    ConversationEntry,
    Protocol,
    ScientistActionType,
    ScientistObservation,
)
from replicalab.scenarios import generate_scenario


# ---------------------------------------------------------------------------
# Shared valid JSON payloads for retry tests
# ---------------------------------------------------------------------------

_VALID_REQUEST_INFO_JSON = """{
  "action_type": "request_info",
  "sample_size": 0,
  "controls": [],
  "technique": "",
  "duration_days": 0,
  "required_equipment": [],
  "required_reagents": [],
  "questions": ["What compute budget is available?"],
  "rationale": ""
}"""


def test_parse_scientist_output_accepts_plain_json() -> None:
    raw_text = """
    {
      "action_type": "request_info",
      "sample_size": 0,
      "controls": [],
      "technique": "",
      "duration_days": 0,
      "required_equipment": [],
      "required_reagents": [],
      "questions": ["What compute budget is available?"],
      "rationale": ""
    }
    """

    action = parse_scientist_output(raw_text)

    assert action.action_type is ScientistActionType.REQUEST_INFO
    assert action.questions == ["What compute budget is available?"]


def test_parse_scientist_output_accepts_fenced_json_with_prose() -> None:
    raw_text = """
    I would revise the plan as follows:

    ```json
    {
      "action_type": "revise_protocol",
      "sample_size": 24,
      "controls": ["baseline", "ablation"],
      "technique": "small_scale_backtest",
      "duration_days": 3,
      "required_equipment": ["gpu_node"],
      "required_reagents": [],
      "questions": [],
      "rationale": "Shrink the trial to fit the available compute window."
    }
    ```
    """

    action = parse_scientist_output(raw_text)

    assert action.action_type is ScientistActionType.REVISE_PROTOCOL
    assert action.technique == "small_scale_backtest"


def test_parse_scientist_output_raises_explicit_error_when_json_is_missing() -> None:
    with pytest.raises(ScientistOutputParseError) as exc_info:
        parse_scientist_output("I need more context before I can answer.")

    assert exc_info.value.code == "no_json"
    assert "does not contain a JSON object" in exc_info.value.message


def test_parse_scientist_output_raises_explicit_error_when_json_is_invalid() -> None:
    raw_text = """
    ```json
    {
      "action_type": "request_info",
      "questions": ["What budget do we have?"],
    }
    ```
    """

    with pytest.raises(ScientistOutputParseError) as exc_info:
        parse_scientist_output(raw_text)

    assert exc_info.value.code == "invalid_json"
    assert "could not be decoded" in exc_info.value.message


def test_parse_scientist_output_raises_explicit_error_when_schema_is_invalid() -> None:
    raw_text = """
    {
      "action_type": "request_info",
      "sample_size": 0,
      "controls": [],
      "technique": "",
      "duration_days": 0,
      "required_equipment": [],
      "required_reagents": [],
      "questions": [],
      "rationale": ""
    }
    """

    with pytest.raises(ScientistOutputParseError) as exc_info:
        parse_scientist_output(raw_text)

    assert exc_info.value.code == "invalid_action"
    assert "ScientistAction validation" in exc_info.value.message


def test_build_scientist_system_prompt_uses_normalized_scenario_data() -> None:
    scenario = generate_scenario(seed=202, template="ml_benchmark", difficulty="medium")

    prompt = build_scientist_system_prompt(scenario)

    assert "You are the Scientist agent in ReplicaLab." in prompt
    assert scenario.task_summary in prompt
    assert scenario.success_criteria[0] in prompt
    assert scenario.resources[0].label in prompt
    assert "action_type values" in prompt
    assert "propose_protocol" in prompt
    assert "request_info" in prompt


# ---------------------------------------------------------------------------
# AGT 02 — format_scientist_observation
# ---------------------------------------------------------------------------


def _base_observation(**overrides) -> ScientistObservation:
    defaults = {
        "paper_title": "Test Paper Title",
        "paper_hypothesis": "X improves Y.",
        "paper_method": "Run benchmark Z.",
        "paper_key_finding": "10% improvement.",
        "experiment_goal": "Replicate the 10% improvement.",
        "conversation_history": [],
        "current_protocol": None,
        "round_number": 0,
        "max_rounds": 6,
    }
    defaults.update(overrides)
    return ScientistObservation(**defaults)


def test_format_observation_empty_history_no_protocol() -> None:
    obs = _base_observation()
    result = format_scientist_observation(obs)

    assert "Round 0 of 6" in result
    assert "Test Paper Title" in result
    assert "X improves Y." in result
    assert "Run benchmark Z." in result
    assert "10% improvement." in result
    assert "Replicate the 10% improvement." in result
    assert "No conversation history yet" in result
    assert "No protocol has been proposed yet" in result
    assert "ScientistAction schema reminder:" in result
    assert (
        "allowed action_type values: propose_protocol, revise_protocol, "
        "request_info, accept"
    ) in result
    assert "include all ScientistAction fields in every response" in result
    assert "Respond with exactly one JSON object" in result


def test_format_observation_with_history_and_protocol() -> None:
    history = [
        ConversationEntry(
            role="scientist",
            message="I propose a grid search protocol.",
            round_number=1,
            action_type="propose_protocol",
        ),
        ConversationEntry(
            role="lab_manager",
            message="The compute cluster is booked. Consider a smaller run.",
            round_number=1,
            action_type="suggest_alternative",
        ),
    ]
    protocol = Protocol(
        sample_size=24,
        controls=["baseline", "ablation"],
        technique="grid_search",
        duration_days=3,
        required_equipment=["gpu_node"],
        required_reagents=["benchmark_dataset"],
        rationale="Standard hyperparameter sweep.",
    )
    obs = _base_observation(
        conversation_history=history,
        current_protocol=protocol,
        round_number=2,
    )
    result = format_scientist_observation(obs)

    assert "Round 2 of 6" in result
    assert "Conversation so far:" in result
    assert "[SCIENTIST r1 [propose_protocol]]" in result
    assert "I propose a grid search protocol." in result
    assert "[LAB_MANAGER r1 [suggest_alternative]]" in result
    assert "compute cluster is booked" in result
    assert "Current protocol:" in result
    assert "technique: grid_search" in result
    assert "sample_size: 24" in result
    assert "controls: baseline, ablation" in result
    assert "duration_days: 3" in result
    assert "gpu_node" in result
    assert "benchmark_dataset" in result
    assert "Standard hyperparameter sweep." in result


def test_format_observation_stable_section_order() -> None:
    obs = _base_observation(
        conversation_history=[
            ConversationEntry(
                role="scientist",
                message="First proposal.",
                round_number=1,
                action_type="propose_protocol",
            ),
        ],
        current_protocol=Protocol(
            sample_size=10,
            controls=["ctrl"],
            technique="method_a",
            duration_days=2,
            required_equipment=["tool_a"],
            required_reagents=["reagent_a"],
            rationale="Simple test.",
        ),
        round_number=1,
    )
    result = format_scientist_observation(obs)

    # Sections must appear in this fixed order
    round_pos = result.index("Round 1 of 6")
    paper_pos = result.index("Paper:")
    history_pos = result.index("Conversation so far:")
    protocol_pos = result.index("Current protocol:")
    action_pos = result.index("Respond with exactly one JSON")

    assert round_pos < paper_pos < history_pos < protocol_pos < action_pos


def test_format_observation_history_entry_without_action_type() -> None:
    obs = _base_observation(
        conversation_history=[
            ConversationEntry(
                role="system",
                message="Episode started.",
                round_number=0,
                action_type=None,
            ),
        ],
    )
    result = format_scientist_observation(obs)

    assert "[SYSTEM r0]:" in result
    assert "Episode started." in result


def test_format_observation_from_generated_scenario() -> None:
    scenario = generate_scenario(seed=77, template="finance_trading", difficulty="easy")
    obs = scenario.scientist_observation
    result = format_scientist_observation(obs)

    assert obs.paper_title in result
    assert obs.experiment_goal in result
    assert "Round 0" in result
    assert "No conversation history yet" in result
    assert "Respond with exactly one JSON" in result


# ---------------------------------------------------------------------------
# AGT 03 — call_scientist_with_retry
# ---------------------------------------------------------------------------


def _make_system_prompt() -> str:
    scenario = generate_scenario(seed=1, template="math_reasoning", difficulty="easy")
    return build_scientist_system_prompt(scenario)


def test_retry_success_on_first_try() -> None:
    def gen_fn(messages: list[dict[str, str]]) -> str:
        return _VALID_REQUEST_INFO_JSON

    obs = _base_observation()
    result = call_scientist_with_retry(gen_fn, _make_system_prompt(), obs)

    assert isinstance(result, ScientistCallResult)
    assert result.action.action_type is ScientistActionType.REQUEST_INFO
    assert result.metadata.attempt_count == 1
    assert result.metadata.retry_count == 0
    assert result.metadata.last_error_code is None
    assert result.metadata.last_error_message is None


def test_retry_malformed_json_then_valid() -> None:
    call_count = 0

    def gen_fn(messages: list[dict[str, str]]) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return '{"action_type": "request_info", trailing garbage'
        return _VALID_REQUEST_INFO_JSON

    obs = _base_observation()
    result = call_scientist_with_retry(gen_fn, _make_system_prompt(), obs)

    assert result.action.action_type is ScientistActionType.REQUEST_INFO
    assert result.metadata.attempt_count == 2
    assert result.metadata.retry_count == 1
    assert result.metadata.last_error_code == "invalid_json"


def test_retry_invalid_action_then_valid() -> None:
    # First attempt: valid JSON but questions is empty for request_info
    invalid_json = """{
      "action_type": "request_info",
      "sample_size": 0,
      "controls": [],
      "technique": "",
      "duration_days": 0,
      "required_equipment": [],
      "required_reagents": [],
      "questions": [],
      "rationale": ""
    }"""
    call_count = 0

    def gen_fn(messages: list[dict[str, str]]) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return invalid_json
        return _VALID_REQUEST_INFO_JSON

    obs = _base_observation()
    result = call_scientist_with_retry(gen_fn, _make_system_prompt(), obs)

    assert result.action.action_type is ScientistActionType.REQUEST_INFO
    assert result.metadata.attempt_count == 2
    assert result.metadata.retry_count == 1
    assert result.metadata.last_error_code == "invalid_action"
    assert "ScientistAction validation" in result.metadata.last_error_message


def test_retry_exhausted_raises_last_error() -> None:
    def gen_fn(messages: list[dict[str, str]]) -> str:
        return "I cannot produce JSON right now."

    obs = _base_observation()
    with pytest.raises(ScientistOutputParseError) as exc_info:
        call_scientist_with_retry(gen_fn, _make_system_prompt(), obs, max_retries=2)

    assert exc_info.value.code == "no_json"


def test_retry_correction_message_includes_parser_error() -> None:
    """The correction prompt sent to the model must include the specific error."""
    captured_messages: list[list[dict[str, str]]] = []

    call_count = 0

    def gen_fn(messages: list[dict[str, str]]) -> str:
        nonlocal call_count
        call_count += 1
        captured_messages.append(list(messages))
        if call_count == 1:
            return "Just some prose, no JSON here."
        return _VALID_REQUEST_INFO_JSON

    obs = _base_observation()
    call_scientist_with_retry(gen_fn, _make_system_prompt(), obs)

    # Second call should have 4 messages: system, user, assistant (bad), user (correction)
    assert len(captured_messages) == 2
    retry_messages = captured_messages[1]
    assert len(retry_messages) == 4
    assert retry_messages[2]["role"] == "assistant"
    assert retry_messages[2]["content"] == "Just some prose, no JSON here."
    assert retry_messages[3]["role"] == "user"
    correction = retry_messages[3]["content"]
    assert "did not contain a JSON object" in correction
    assert "No markdown fences, no prose" in correction


def test_retry_correction_for_invalid_action_includes_validation_detail() -> None:
    """invalid_action correction must include the schema validation message."""
    captured_messages: list[list[dict[str, str]]] = []

    invalid_json = """{
      "action_type": "request_info",
      "sample_size": 0,
      "controls": [],
      "technique": "",
      "duration_days": 0,
      "required_equipment": [],
      "required_reagents": [],
      "questions": [],
      "rationale": ""
    }"""
    call_count = 0

    def gen_fn(messages: list[dict[str, str]]) -> str:
        nonlocal call_count
        call_count += 1
        captured_messages.append(list(messages))
        if call_count == 1:
            return invalid_json
        return _VALID_REQUEST_INFO_JSON

    obs = _base_observation()
    call_scientist_with_retry(gen_fn, _make_system_prompt(), obs)

    retry_messages = captured_messages[1]
    correction = retry_messages[3]["content"]
    assert "failed ScientistAction validation" in correction
    assert "Fix the validation error" in correction


def test_retry_metadata_serializable() -> None:
    def gen_fn(messages: list[dict[str, str]]) -> str:
        return _VALID_REQUEST_INFO_JSON

    obs = _base_observation()
    result = call_scientist_with_retry(gen_fn, _make_system_prompt(), obs)

    dumped = result.metadata.model_dump_json()
    restored = RetryMetadata.model_validate_json(dumped)
    assert restored.attempt_count == 1
    assert restored.retry_count == 0


# ---------------------------------------------------------------------------
# AGT 04 - build_baseline_scientist_action
# ---------------------------------------------------------------------------


def test_baseline_scientist_proposes_protocol_for_fresh_observation() -> None:
    action = build_baseline_scientist_action(_base_observation())

    assert action.action_type is ScientistActionType.PROPOSE_PROTOCOL
    assert action.sample_size >= 1
    assert action.duration_days >= 1
    assert action.questions == []
    assert action.rationale


def test_baseline_scientist_accepts_existing_protocol_without_blocker() -> None:
    obs = _base_observation(
        current_protocol=Protocol(
            sample_size=10,
            controls=["baseline_check"],
            technique="published_split_replication",
            duration_days=2,
            required_equipment=[],
            required_reagents=[],
            rationale="Initial protocol is already in place.",
        ),
        conversation_history=[
            ConversationEntry(
                role="lab_manager",
                message="The current plan remains feasible.",
                round_number=1,
                action_type="report_feasibility",
            )
        ],
        round_number=1,
    )

    action = build_baseline_scientist_action(obs)

    assert action.action_type is ScientistActionType.ACCEPT
    assert action.sample_size == 0
    assert action.controls == []


def test_baseline_scientist_revises_when_latest_feedback_has_blocker() -> None:
    obs = _base_observation(
        current_protocol=Protocol(
            sample_size=12,
            controls=["published_split_check", "heldout_evaluation"],
            technique="published_split_replication",
            duration_days=3,
            required_equipment=[],
            required_reagents=[],
            rationale="Original scope is full-size.",
        ),
        conversation_history=[
            ConversationEntry(
                role="lab_manager",
                message="The current GPU plan is booked, so the schedule is too tight.",
                round_number=1,
                action_type="suggest_alternative",
            )
        ],
        round_number=1,
    )

    action = build_baseline_scientist_action(obs)

    assert action.action_type is ScientistActionType.REVISE_PROTOCOL
    assert action.sample_size == 6
    assert action.duration_days == 2
    assert "latest Lab Manager concern" in action.rationale


def test_baseline_scientist_finishes_stub_episode_without_crashing() -> None:
    from server.app import _StubEnv

    env = _StubEnv()

    first_observation = env.reset(
        seed=14,
        scenario="ml_benchmark",
        difficulty="easy",
    ).scientist
    assert first_observation is not None

    first_action = build_baseline_scientist_action(first_observation)
    first_step = env.step(first_action)
    assert first_step.done is False
    assert first_step.observation is not None
    assert first_step.observation.scientist is not None

    second_action = build_baseline_scientist_action(first_step.observation.scientist)
    second_step = env.step(second_action)

    assert second_step.done is True
    assert second_step.info.agreement_reached is True
