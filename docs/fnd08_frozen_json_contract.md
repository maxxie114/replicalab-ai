# FND 08 Frozen JSON Contract

Status: completed on 2026-03-08
Owners: Person A and Person B
Drafted by: Person B (Ayush)
Remaining acceptance item: none

Source schema file: `replicalab/models.py`

## Purpose

This document freezes the JSON contract for the shared ReplicaLab data models so downstream work can proceed without schema drift. It is the reference for:

- Person A validators and environment state handling
- Person B prompt formatting and action parsing
- Person C API payload examples
- Person D frontend and replay mocks

## Global conventions

- All JSON keys use `snake_case`.
- Enum-like values use lowercase snake_case strings.
- All top-level keys listed in this document must be present unless explicitly marked nullable.
- Use `null` for an absent single object.
- Use `[]` for a known empty collection.
- Use `{}` only for flexible metadata objects such as `info` and `reward_breakdown`.
- `round_number` is zero-based. `0` is the state immediately after `reset()`.
- `duration_days` and `time_limit_days` are whole calendar days.
- `difficulty` values are `easy`, `medium`, or `hard`.
- Component scores such as rigor, feasibility, and fidelity are floats in the inclusive range `0.0` to `1.0`.

## Shared nested objects

### ConversationEntry

Each item in `conversation_history` or `transcript` must use this shape:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `role` | `str` | yes | One of `scientist`, `lab_manager`, `system` |
| `message` | `str` | yes | Human-readable turn text |
| `round_number` | `int` | yes | Zero-based round index for the message |
| `action_type` | `str \| null` | yes | Mirrors the action type when the message comes from an agent, otherwise `null` |

### Protocol

When `current_protocol` is not `null`, it must use this shape:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `sample_size` | `int` | yes | Non-negative integer |
| `controls` | `list[str]` | yes | Empty list when no controls are specified yet |
| `technique` | `str` | yes | Proposed experimental technique |
| `duration_days` | `int` | yes | Whole calendar days |
| `required_equipment` | `list[str]` | yes | Empty list when none is needed |
| `required_reagents` | `list[str]` | yes | Empty list when none is needed |
| `rationale` | `str` | yes | Short explanation for the protocol |

### RewardBreakdown

When `reward_breakdown` is present, it must use this shape:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `rigor` | `float` | yes | Component score in `0.0` to `1.0` |
| `feasibility` | `float` | yes | Component score in `0.0` to `1.0` |
| `fidelity` | `float` | yes | Component score in `0.0` to `1.0` |
| `efficiency_bonus` | `float` | yes | Bonus term, `0.0` if unused |
| `communication_bonus` | `float` | yes | Bonus term, `0.0` if unused |
| `penalties` | `dict[str, float]` | yes | Per-penalty values keyed by penalty name |

## Model contracts

### ScientistAction

Action types:

- `propose_protocol`
- `revise_protocol`
- `request_info`
- `accept`

Field contract:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `action_type` | `str` | yes | Must be one of the values above |
| `sample_size` | `int` | yes | Meaningful for `propose_protocol` and `revise_protocol`, otherwise `0` |
| `controls` | `list[str]` | yes | Meaningful for `propose_protocol` and `revise_protocol`, otherwise `[]` |
| `technique` | `str` | yes | Meaningful for `propose_protocol` and `revise_protocol`, otherwise `""` |
| `duration_days` | `int` | yes | Meaningful for `propose_protocol` and `revise_protocol`, otherwise `0` |
| `required_equipment` | `list[str]` | yes | Meaningful for `propose_protocol` and `revise_protocol`, otherwise `[]` |
| `required_reagents` | `list[str]` | yes | Meaningful for `propose_protocol` and `revise_protocol`, otherwise `[]` |
| `questions` | `list[str]` | yes | Meaningful for `request_info`, otherwise `[]` |
| `rationale` | `str` | yes | Required free-text explanation for protocol proposals and revisions; `""` for `accept` |

Canonical example:

```json
{
  "action_type": "propose_protocol",
  "sample_size": 48,
  "controls": ["vehicle_control", "positive_control"],
  "technique": "wst1_assay",
  "duration_days": 5,
  "required_equipment": ["plate_reader", "co2_incubator"],
  "required_reagents": ["wst1", "dmso", "drug_x"],
  "questions": [],
  "rationale": "Keeps the core readout while using equipment commonly available in teaching labs."
}
```

### LabManagerAction

Action types:

- `report_feasibility`
- `suggest_alternative`
- `reject`
- `accept`

Field contract:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `action_type` | `str` | yes | Must be one of the values above |
| `feasible` | `bool` | yes | Overall summary flag equal to the logical AND of the constraint dimension flags |
| `budget_ok` | `bool` | yes | Whether the proposed protocol fits remaining budget |
| `equipment_ok` | `bool` | yes | Whether required equipment is available in time |
| `reagents_ok` | `bool` | yes | Whether required reagents are available |
| `schedule_ok` | `bool` | yes | Whether the protocol fits the allowed timeline |
| `staff_ok` | `bool` | yes | Whether staffing is sufficient |
| `suggested_technique` | `str` | yes | Meaningful for `suggest_alternative`, otherwise `""` |
| `suggested_sample_size` | `int` | yes | Meaningful for `suggest_alternative`, otherwise `0` |
| `suggested_controls` | `list[str]` | yes | Meaningful for `suggest_alternative`, otherwise `[]` |
| `explanation` | `str` | yes | Human-readable explanation of the constraint outcome |

Conditional rules:

- `action_type = accept` implies `feasible = true` and all constraint flags are `true`.
- `action_type = reject` implies `feasible = false` and at least one constraint flag is `false`.
- `action_type = suggest_alternative` implies `feasible = false` and at least one of the suggestion fields carries a non-default value.

Canonical example:

```json
{
  "action_type": "suggest_alternative",
  "feasible": false,
  "budget_ok": true,
  "equipment_ok": false,
  "reagents_ok": true,
  "schedule_ok": true,
  "staff_ok": true,
  "suggested_technique": "manual_cell_counting",
  "suggested_sample_size": 32,
  "suggested_controls": ["vehicle_control", "positive_control"],
  "explanation": "The plate reader is fully booked, so use manual counting and reduce the sample size to stay within the timeline."
}
```

### ScientistObservation

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `paper_title` | `str` | yes | Study title |
| `paper_hypothesis` | `str` | yes | Core hypothesis being replicated |
| `paper_method` | `str` | yes | Short method summary |
| `paper_key_finding` | `str` | yes | Main finding being targeted |
| `experiment_goal` | `str` | yes | What the scientist is trying to preserve |
| `conversation_history` | `list[ConversationEntry]` | yes | Empty list at reset |
| `current_protocol` | `Protocol \| null` | yes | `null` until a protocol exists |
| `round_number` | `int` | yes | Zero-based current round |
| `max_rounds` | `int` | yes | Max allowed rounds in the episode |

Canonical example:

```json
{
  "paper_title": "Drug X reduces glioblastoma cell viability",
  "paper_hypothesis": "Drug X reduces viability in a dose-dependent manner.",
  "paper_method": "96-well viability assay with 24h incubation and absorbance readout.",
  "paper_key_finding": "The highest dose reduced viability by about 40 percent.",
  "experiment_goal": "Replicate the dose-response trend without dropping essential controls.",
  "conversation_history": [],
  "current_protocol": null,
  "round_number": 0,
  "max_rounds": 6
}
```

### LabManagerObservation

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `budget_total` | `float` | yes | Initial budget for the episode |
| `budget_remaining` | `float` | yes | Current remaining budget |
| `equipment_available` | `list[str]` | yes | Equipment that can be used |
| `equipment_booked` | `list[str]` | yes | Equipment unavailable due to booking |
| `reagents_in_stock` | `list[str]` | yes | Available reagents |
| `reagents_out_of_stock` | `list[str]` | yes | Required but unavailable reagents |
| `staff_count` | `int` | yes | Available staff count |
| `time_limit_days` | `int` | yes | Whole calendar days remaining |
| `safety_restrictions` | `list[str]` | yes | Constraints such as banned solvents or assay restrictions |
| `conversation_history` | `list[ConversationEntry]` | yes | Empty list at reset |
| `current_protocol` | `Protocol \| null` | yes | `null` until a protocol exists |
| `round_number` | `int` | yes | Zero-based current round |
| `max_rounds` | `int` | yes | Max allowed rounds in the episode |

Canonical example:

```json
{
  "budget_total": 1200.0,
  "budget_remaining": 1200.0,
  "equipment_available": ["co2_incubator", "microscope"],
  "equipment_booked": ["plate_reader"],
  "reagents_in_stock": ["dmso", "drug_x", "culture_media"],
  "reagents_out_of_stock": ["wst1"],
  "staff_count": 2,
  "time_limit_days": 7,
  "safety_restrictions": ["no_radioactive_reagents"],
  "conversation_history": [],
  "current_protocol": null,
  "round_number": 0,
  "max_rounds": 6
}
```

### Observation

Wrapper behavior:

- Serialized `Observation` objects always include both top-level keys: `scientist` and `lab_manager`.
- In shared environment state, replay, and API payloads, both branches should normally be populated.
- When a consumer is intentionally given only one role view, the non-owned branch must be `null`, not omitted.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `scientist` | `ScientistObservation \| null` | yes | Scientist-side view |
| `lab_manager` | `LabManagerObservation \| null` | yes | Lab-manager-side view |

Canonical example:

```json
{
  "scientist": {
    "paper_title": "Drug X reduces glioblastoma cell viability",
    "paper_hypothesis": "Drug X reduces viability in a dose-dependent manner.",
    "paper_method": "96-well viability assay with 24h incubation and absorbance readout.",
    "paper_key_finding": "The highest dose reduced viability by about 40 percent.",
    "experiment_goal": "Replicate the dose-response trend without dropping essential controls.",
    "conversation_history": [],
    "current_protocol": null,
    "round_number": 0,
    "max_rounds": 6
  },
  "lab_manager": {
    "budget_total": 1200.0,
    "budget_remaining": 1200.0,
    "equipment_available": ["co2_incubator", "microscope"],
    "equipment_booked": ["plate_reader"],
    "reagents_in_stock": ["dmso", "drug_x", "culture_media"],
    "reagents_out_of_stock": ["wst1"],
    "staff_count": 2,
    "time_limit_days": 7,
    "safety_restrictions": ["no_radioactive_reagents"],
    "conversation_history": [],
    "current_protocol": null,
    "round_number": 0,
    "max_rounds": 6
  }
}
```

### StepResult

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `observation` | `Observation \| null` | yes | Present on normal steps and terminal steps; may be `null` only on hard failure |
| `reward` | `float` | yes | Episode reward after the step; terminal reward on final step |
| `done` | `bool` | yes | Whether the episode is terminal |
| `info` | `dict` | yes | Flexible metadata object |

Reserved `info` keys:

- `agreement_reached`: `bool`
- `error`: `str | null`
- `reward_breakdown`: `RewardBreakdown | null`
- `judge_notes`: `str | null`
- `verdict`: `str | null`

Canonical example:

```json
{
  "observation": {
    "scientist": null,
    "lab_manager": null
  },
  "reward": 6.72,
  "done": true,
  "info": {
    "agreement_reached": true,
    "error": null,
    "reward_breakdown": {
      "rigor": 0.9,
      "feasibility": 0.8,
      "fidelity": 0.85,
      "efficiency_bonus": 0.25,
      "communication_bonus": 0.15,
      "penalties": {
        "invalid_action": 0.0,
        "timeout": 0.0
      }
    },
    "judge_notes": "Controls were preserved and the substitutions remained scientifically acceptable.",
    "verdict": "accept"
  }
}
```

### EpisodeState

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `seed` | `int` | yes | Deterministic episode seed |
| `scenario_template` | `str` | yes | Scenario family identifier |
| `difficulty` | `str` | yes | `easy`, `medium`, or `hard` |
| `paper_title` | `str` | yes | Study title |
| `paper_hypothesis` | `str` | yes | Core hypothesis |
| `paper_method` | `str` | yes | Method summary |
| `paper_key_finding` | `str` | yes | Main finding |
| `experiment_goal` | `str` | yes | Goal preserved through negotiation |
| `lab_budget_total` | `float` | yes | Initial budget |
| `lab_budget_remaining` | `float` | yes | Remaining budget |
| `lab_equipment` | `list[str]` | yes | Equipment state |
| `lab_reagents` | `list[str]` | yes | Reagent state |
| `lab_staff_count` | `int` | yes | Available staff count |
| `lab_time_limit_days` | `int` | yes | Whole calendar days remaining |
| `current_protocol` | `Protocol \| null` | yes | Current agreed or latest proposed protocol |
| `conversation_history` | `list[ConversationEntry]` | yes | Negotiation history |
| `round_number` | `int` | yes | Zero-based round counter |
| `max_rounds` | `int` | yes | Maximum rounds allowed |
| `done` | `bool` | yes | Terminal flag |
| `agreement_reached` | `bool` | yes | Whether both sides reached agreement |
| `reward` | `float` | yes | Final total reward or `0.0` until terminal scoring |
| `rigor_score` | `float` | yes | Final component score or `0.0` until terminal scoring |
| `feasibility_score` | `float` | yes | Final component score or `0.0` until terminal scoring |
| `fidelity_score` | `float` | yes | Final component score or `0.0` until terminal scoring |

Canonical example:

```json
{
  "seed": 17,
  "scenario_template": "cell_biology",
  "difficulty": "medium",
  "paper_title": "Drug X reduces glioblastoma cell viability",
  "paper_hypothesis": "Drug X reduces viability in a dose-dependent manner.",
  "paper_method": "96-well viability assay with 24h incubation and absorbance readout.",
  "paper_key_finding": "The highest dose reduced viability by about 40 percent.",
  "experiment_goal": "Replicate the dose-response trend without dropping essential controls.",
  "lab_budget_total": 1200.0,
  "lab_budget_remaining": 850.0,
  "lab_equipment": ["co2_incubator", "microscope"],
  "lab_reagents": ["dmso", "drug_x", "culture_media"],
  "lab_staff_count": 2,
  "lab_time_limit_days": 7,
  "current_protocol": {
    "sample_size": 32,
    "controls": ["vehicle_control", "positive_control"],
    "technique": "manual_cell_counting",
    "duration_days": 5,
    "required_equipment": ["microscope", "co2_incubator"],
    "required_reagents": ["dmso", "drug_x", "culture_media"],
    "rationale": "Uses available equipment while preserving control structure."
  },
  "conversation_history": [
    {
      "role": "scientist",
      "message": "I propose a manual counting protocol that keeps both controls.",
      "round_number": 0,
      "action_type": "propose_protocol"
    }
  ],
  "round_number": 1,
  "max_rounds": 6,
  "done": false,
  "agreement_reached": false,
  "reward": 0.0,
  "rigor_score": 0.0,
  "feasibility_score": 0.0,
  "fidelity_score": 0.0
}
```

### EpisodeLog

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `episode_id` | `str` | yes | Stable replay identifier |
| `seed` | `int` | yes | Episode seed |
| `scenario_template` | `str` | yes | Scenario family identifier |
| `difficulty` | `str` | yes | `easy`, `medium`, or `hard` |
| `final_state` | `EpisodeState \| null` | yes | Must be populated for completed episodes |
| `transcript` | `list[ConversationEntry]` | yes | Replayable transcript |
| `reward_breakdown` | `RewardBreakdown` | yes | Final reward components |
| `total_reward` | `float` | yes | Final total reward |
| `rounds_used` | `int` | yes | Number of completed rounds |
| `agreement_reached` | `bool` | yes | Final agreement flag |
| `judge_notes` | `str` | yes | Human-readable audit summary |
| `verdict` | `str` | yes | One of `accept`, `revise`, `reject` |

Canonical example:

```json
{
  "episode_id": "cell_biology-17-medium-0001",
  "seed": 17,
  "scenario_template": "cell_biology",
  "difficulty": "medium",
  "final_state": {
    "seed": 17,
    "scenario_template": "cell_biology",
    "difficulty": "medium",
    "paper_title": "Drug X reduces glioblastoma cell viability",
    "paper_hypothesis": "Drug X reduces viability in a dose-dependent manner.",
    "paper_method": "96-well viability assay with 24h incubation and absorbance readout.",
    "paper_key_finding": "The highest dose reduced viability by about 40 percent.",
    "experiment_goal": "Replicate the dose-response trend without dropping essential controls.",
    "lab_budget_total": 1200.0,
    "lab_budget_remaining": 850.0,
    "lab_equipment": ["co2_incubator", "microscope"],
    "lab_reagents": ["dmso", "drug_x", "culture_media"],
    "lab_staff_count": 2,
    "lab_time_limit_days": 7,
    "current_protocol": {
      "sample_size": 32,
      "controls": ["vehicle_control", "positive_control"],
      "technique": "manual_cell_counting",
      "duration_days": 5,
      "required_equipment": ["microscope", "co2_incubator"],
      "required_reagents": ["dmso", "drug_x", "culture_media"],
      "rationale": "Uses available equipment while preserving control structure."
    },
    "conversation_history": [
      {
        "role": "scientist",
        "message": "I propose a manual counting protocol that keeps both controls.",
        "round_number": 0,
        "action_type": "propose_protocol"
      },
      {
        "role": "lab_manager",
        "message": "This alternative is feasible with current equipment and budget.",
        "round_number": 0,
        "action_type": "accept"
      }
    ],
    "round_number": 1,
    "max_rounds": 6,
    "done": true,
    "agreement_reached": true,
    "reward": 6.72,
    "rigor_score": 0.9,
    "feasibility_score": 0.8,
    "fidelity_score": 0.85
  },
  "transcript": [
    {
      "role": "scientist",
      "message": "I propose a manual counting protocol that keeps both controls.",
      "round_number": 0,
      "action_type": "propose_protocol"
    },
    {
      "role": "lab_manager",
      "message": "This alternative is feasible with current equipment and budget.",
      "round_number": 0,
      "action_type": "accept"
    }
  ],
  "reward_breakdown": {
    "rigor": 0.9,
    "feasibility": 0.8,
    "fidelity": 0.85,
    "efficiency_bonus": 0.25,
    "communication_bonus": 0.15,
    "penalties": {
      "invalid_action": 0.0,
      "timeout": 0.0
    }
  },
  "total_reward": 6.72,
  "rounds_used": 1,
  "agreement_reached": true,
  "judge_notes": "Controls were preserved and the substitutions remained scientifically acceptable.",
  "verdict": "accept"
}
```

## Sign-off

| Owner | Status | Notes |
| --- | --- | --- |
| Person B (Ayush) | signed off | Draft matches current stubs and downstream parser needs |
| Kian (Person A) | signed off | Validator and environment-owner review completed; contract is frozen for `MOD 01`, `MOD 03`, `FND 09`, and downstream parser work |
