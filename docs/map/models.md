# Models Map — `replicalab/models.py`

> All Pydantic data contracts. Frozen with `extra="forbid"` unless noted.
>
> **Tasks implemented:** MOD 01, 02, 03, 04, 09, 11, 12

## Enums

### `ScientistActionType(str, Enum)`
| Value | Meaning |
|-------|---------|
| `propose_protocol` | First protocol submission |
| `revise_protocol` | Modify existing protocol |
| `request_info` | Ask lab manager a question |
| `accept` | Agree to current protocol |

### `LabManagerActionType(str, Enum)`
| Value | Meaning |
|-------|---------|
| `report_feasibility` | Report on feasibility without suggestions |
| `suggest_alternative` | Propose revised protocol |
| `reject` | Reject protocol outright |
| `accept` | Approve protocol |

## Action Models

### `ScientistAction(BaseModel)` — `extra="forbid"`
MOD 01 + MOD 09. Strict contract for scientist output.

| Field | Type | Constraint | Notes |
|-------|------|-----------|-------|
| `action_type` | `ScientistActionType` | required | |
| `sample_size` | `int` | `ge=0` | Must be `>=1` for propose/revise |
| `controls` | `list[str]` | normalized | |
| `technique` | `str` | stripped | Required for propose/revise |
| `duration_days` | `int` | `ge=0` | |
| `required_equipment` | `list[str]` | normalized | |
| `required_reagents` | `list[str]` | normalized | |
| `questions` | `list[str]` | normalized | Required non-empty for request_info |
| `rationale` | `str` | stripped | Required for propose/revise |

**Validation rules:**
- `propose_protocol` / `revise_protocol`: sample_size >= 1, technique required, rationale required, questions must be empty
- `request_info`: questions non-empty, no protocol payload fields
- `accept`: no questions, no protocol payload fields

### `LabManagerAction(BaseModel)` — `extra="forbid"`
MOD 02. Strict contract with feasible-flag consistency.

| Field | Type | Constraint | Notes |
|-------|------|-----------|-------|
| `action_type` | `LabManagerActionType` | required | |
| `feasible` | `bool` | required | Must equal AND of all constraint flags |
| `budget_ok` | `bool` | required | |
| `equipment_ok` | `bool` | required | |
| `reagents_ok` | `bool` | required | |
| `schedule_ok` | `bool` | required | |
| `staff_ok` | `bool` | required | |
| `suggested_technique` | `str` | stripped | Only for suggest_alternative |
| `suggested_sample_size` | `int` | `ge=0` | Only for suggest_alternative |
| `suggested_controls` | `list[str]` | normalized | Only for suggest_alternative |
| `explanation` | `str` | required non-empty | |

**Validation rules:**
- `feasible` must equal `all(budget_ok, equipment_ok, reagents_ok, schedule_ok, staff_ok)`
- `accept` requires `feasible=True`
- `reject` requires `feasible=False`
- `suggest_alternative` requires `feasible=False` + at least one suggestion field
- Suggestion fields forbidden for non-suggest_alternative actions

## Observation Models

### `ConversationEntry(BaseModel)` — `extra="forbid"`
| Field | Type | Notes |
|-------|------|-------|
| `role` | `Literal["scientist", "lab_manager", "system"]` | |
| `message` | `str` | Required non-empty |
| `round_number` | `int` | `ge=0` |
| `action_type` | `Optional[str]` | Null or non-empty |

### `Protocol(BaseModel)` — `extra="forbid"`
Shared protocol payload used in observations and actions.

| Field | Type | Notes |
|-------|------|-------|
| `sample_size` | `int` | `ge=0` |
| `controls` | `list[str]` | normalized |
| `technique` | `str` | required non-empty |
| `duration_days` | `int` | `ge=0` |
| `required_equipment` | `list[str]` | normalized |
| `required_reagents` | `list[str]` | normalized |
| `rationale` | `str` | required non-empty |

### `ScientistObservation(BaseModel)` — `extra="forbid"`
| Field | Type |
|-------|------|
| `paper_title` | `str` |
| `paper_hypothesis` | `str` |
| `paper_method` | `str` |
| `paper_key_finding` | `str` |
| `experiment_goal` | `str` |
| `conversation_history` | `list[ConversationEntry]` |
| `current_protocol` | `Optional[Protocol]` |
| `round_number` | `int` (ge=0) |
| `max_rounds` | `int` (ge=0) |

### `LabManagerObservation(BaseModel)` — `extra="forbid"`
| Field | Type |
|-------|------|
| `budget_total` | `float` (ge=0) |
| `budget_remaining` | `float` (ge=0) |
| `equipment_available` | `list[str]` |
| `equipment_booked` | `list[str]` |
| `reagents_in_stock` | `list[str]` |
| `reagents_out_of_stock` | `list[str]` |
| `staff_count` | `int` (ge=0) |
| `time_limit_days` | `int` (ge=0) |
| `safety_restrictions` | `list[str]` |
| `conversation_history` | `list[ConversationEntry]` |
| `current_protocol` | `Optional[Protocol]` |
| `round_number` | `int` (ge=0) |
| `max_rounds` | `int` (ge=0) |

### `Observation(BaseModel)` — `extra="forbid"`
Combined wrapper. Each role receives its own view.

| Field | Type |
|-------|------|
| `scientist` | `Optional[ScientistObservation]` |
| `lab_manager` | `Optional[LabManagerObservation]` |

## Reward & Step Models

### `RewardBreakdown(BaseModel)` — default `extra="forbid"`
MOD 11. Component scores from judge rubric engine.

| Field | Type | Default | Range |
|-------|------|---------|-------|
| `rigor` | `float` | 0.0 | [0, 1] |
| `feasibility` | `float` | 0.0 | [0, 1] |
| `fidelity` | `float` | 0.0 | [0, 1] |
| `efficiency_bonus` | `float` | 0.0 | unbounded |
| `communication_bonus` | `float` | 0.0 | unbounded |
| `penalties` | `dict[str, float]` | {} | unbounded |

### `StepInfo(BaseModel)` — `extra="allow"`
MOD 11. Extensible metadata returned with each step.

| Field | Type | Default |
|-------|------|---------|
| `agreement_reached` | `bool` | False |
| `error` | `Optional[str]` | None |
| `reward_breakdown` | `Optional[RewardBreakdown]` | None |
| `judge_notes` | `Optional[str]` | None |
| `verdict` | `Optional[str]` | None |

### `StepResult(BaseModel)`
| Field | Type | Default |
|-------|------|---------|
| `observation` | `Optional[Observation]` | None |
| `reward` | `float` | 0.0 |
| `done` | `bool` | False |
| `info` | `StepInfo` | StepInfo() |

## Episode Models

### `EpisodeState(BaseModel)` — MOD 04
Full internal state for debugging and replay.

| Field | Type | Default |
|-------|------|---------|
| `seed` | `int` | 0 |
| `scenario_template` | `str` | "" |
| `difficulty` | `str` | "easy" |
| `paper_title` | `str` | "" |
| `paper_hypothesis` | `str` | "" |
| `paper_method` | `str` | "" |
| `paper_key_finding` | `str` | "" |
| `experiment_goal` | `str` | "" |
| `lab_budget_total` | `float` | 0.0 |
| `lab_budget_remaining` | `float` | 0.0 |
| `lab_equipment` | `list[str]` | [] |
| `lab_reagents` | `list[str]` | [] |
| `lab_staff_count` | `int` | 0 |
| `lab_time_limit_days` | `int` | 0 |
| `current_protocol` | `Optional[Protocol]` | None |
| `conversation_history` | `list[ConversationEntry]` | [] |
| `round_number` | `int` | 0 |
| `max_rounds` | `int` | 0 |
| `done` | `bool` | False |
| `agreement_reached` | `bool` | False |
| `reward` | `float` | 0.0 |
| `rigor_score` | `float` | 0.0 |
| `feasibility_score` | `float` | 0.0 |
| `fidelity_score` | `float` | 0.0 |

### `EpisodeLog(BaseModel)` — MOD 04
Completed episode record for logging, replay, evaluation.

| Field | Type | Default |
|-------|------|---------|
| `episode_id` | `str` | "" |
| `seed` | `int` | 0 |
| `scenario_template` | `str` | "" |
| `difficulty` | `str` | "easy" |
| `final_state` | `Optional[EpisodeState]` | None |
| `transcript` | `list[ConversationEntry]` | [] |
| `reward_breakdown` | `Optional[RewardBreakdown]` | None |
| `total_reward` | `float` | 0.0 |
| `rounds_used` | `int` | 0 |
| `agreement_reached` | `bool` | False |
| `judge_notes` | `str` | "" |
| `verdict` | `str` | "" |

## Helper Functions

| Function | Purpose |
|----------|---------|
| `_normalize_string_list(value)` | Strip whitespace, reject empty strings |
