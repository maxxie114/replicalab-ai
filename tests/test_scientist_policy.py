from __future__ import annotations

import pytest

from replicalab.agents.scientist_policy import (
    ScientistOutputParseError,
    build_scientist_system_prompt,
    parse_scientist_output,
)
from replicalab.models import ScientistActionType
from replicalab.scenarios import generate_scenario


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
