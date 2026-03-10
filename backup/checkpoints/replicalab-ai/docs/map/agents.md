# Agents Map — `replicalab/agents/`

> Deterministic policy helpers for Scientist and Lab Manager agents.
> No LLM calls in this module — the LLM backend is injected via `GenerateFn`.
>
> **Tasks implemented:** AGT 01-07, 11

## Exports — `__init__.py`

```python
# From lab_manager_policy
AlternativeSuggestion, FeasibilityCheckResult, SuggestionChange
check_feasibility, compose_lab_manager_response, suggest_alternative

# From scientist_policy
RetryMetadata, ScientistCallResult, ScientistOutputParseError
build_baseline_scientist_action, build_scientist_system_prompt
call_scientist_with_retry, format_scientist_observation, parse_scientist_output
```

---

## Scientist Policy — `scientist_policy.py`

### Pipeline Flow

```
scenario → build_scientist_system_prompt() → system_prompt
                                                    ↓
observation → format_scientist_observation() → user_message
                                                    ↓
              call_scientist_with_retry(generate_fn, system_prompt, obs)
                   ↓ calls generate_fn(messages)
                   ↓ calls parse_scientist_output(raw_text)
                   ↓ on failure: _build_correction_prompt(error)
                   ↓ retries up to max_retries times
                   → ScientistCallResult(action, metadata)
```

### Public Functions

#### `build_scientist_system_prompt(scenario) -> str` — AGT 01
Builds a domain-neutral system prompt from a `NormalizedScenarioPack`.

**Sections rendered (in order):**
1. Role statement ("You are the Scientist agent in ReplicaLab")
2. Job description (negotiate strongest feasible plan)
3. Domain ID
4. Task summary
5. Success criteria (bulleted)
6. Constraints (with hard/soft labels, quantities, comparators)
7. Available resources (with availability status)
8. Allowed substitutions (original → alternative with conditions)
9. Output contract (exactly one JSON, no extra keys)
10. Allowed action_type values
11. Action-specific field requirements

#### `format_scientist_observation(obs: ScientistObservation) -> str` — AGT 02
Converts a per-turn observation into the user message string.

**Sections (fixed order, tested):**
1. Round status: `"Round {n} of {max}"`
2. Paper summary: title, hypothesis, method, key finding, goal
3. Conversation history or "No conversation history yet"
4. Current protocol or "No protocol has been proposed yet"
5. ScientistAction schema reminder (field list, action_type values)
6. Closing instruction: "Respond with exactly one JSON object"

#### `parse_scientist_output(raw_text: str) -> ScientistAction` — MOD 09
Strict parser from raw model text into validated `ScientistAction`.

**Accepts:**
- Plain JSON objects
- `\`\`\`json` fenced blocks
- Prose containing one JSON object

**Error codes:**
| Code | Meaning |
|------|---------|
| `no_json` | No JSON object found in output |
| `invalid_json` | JSON syntax error (trailing comma, etc.) |
| `invalid_action` | Valid JSON but fails ScientistAction validation |

#### `call_scientist_with_retry(generate_fn, system_prompt, observation, max_retries=2) -> ScientistCallResult` — AGT 03
Retry loop with error-specific correction prompts.

**Behavior:**
1. Builds messages: `[system, user]`
2. Calls `generate_fn(messages)` → raw text
3. Calls `parse_scientist_output(raw_text)`
4. On success: returns `ScientistCallResult(action, metadata)`
5. On failure: appends `[assistant(bad_output), user(correction)]` to messages, retries
6. After `max_retries` failures: raises last `ScientistOutputParseError`

**Correction prompts (`_build_correction_prompt`):**
- `no_json`: "Your previous response did not contain a JSON object..."
- `invalid_json`: "Your previous response contained malformed JSON: {error}..."
- `invalid_action`: "...failed ScientistAction validation: {detail}. Fix the validation error..."

#### `build_baseline_scientist_action(observation) -> ScientistAction` — AGT 04
Deterministic non-LLM action for smoke tests. No API calls.

**Decision tree:**
1. If protocol exists AND at max rounds → `accept`
2. If protocol exists AND latest lab_manager feedback indicates blocker → `revise_protocol` (halve sample, reduce duration)
3. If protocol exists AND no blocker → `accept`
4. If no protocol → `propose_protocol` (domain-inferred defaults)

**Domain inference (`_infer_domain`):**
- Checks paper fields for ML hints (benchmark, dataset, gpu, bert...) → `machine_learning`
- Checks for finance hints (backtest, sharpe, trading...) → `finance_trading`
- Default → `mathematics`

**Blocker detection (`_feedback_indicates_blocker`):**
- Returns `False` if action_type is `accept` or `report_feasibility`
- Otherwise checks message for blocker hints: booked, unavailable, exceeds, tight, budget, cost, etc.

### Classes

#### `ScientistOutputParseError(ValueError)`
| Attribute | Type | Purpose |
|-----------|------|---------|
| `code` | `Literal["no_json", "invalid_json", "invalid_action"]` | Machine-readable error type |
| `message` | `str` | Human-readable detail |
| `raw_text` | `str` | Original model output |
| `parsed_payload` | `dict \| None` | Decoded JSON if parsing succeeded |

#### `RetryMetadata(BaseModel)` — `extra="forbid"`
| Field | Type | Purpose |
|-------|------|---------|
| `attempt_count` | `int` | Total attempts (1 = success on first try) |
| `retry_count` | `int` | `attempt_count - 1` |
| `last_error_code` | `str \| None` | Error code from last failure |
| `last_error_message` | `str \| None` | Error message from last failure |

#### `ScientistCallResult(BaseModel)` — `extra="forbid"`
| Field | Type |
|-------|------|
| `action` | `ScientistAction` |
| `metadata` | `RetryMetadata` |

### Type Aliases

```python
GenerateFn = Callable[[list[dict[str, str]]], str]
```

### Constants

```python
_ML_HINTS = ("benchmark", "dataset", "accuracy", "tokenizer", "train", "gpu", ...)
_FINANCE_HINTS = ("backtest", "drawdown", "sharpe", "trading", "slippage", ...)
_BLOCKER_HINTS = ("booked", "unavailable", "exceeds", "tight", "budget", "cost", ...)
```

---

## Lab Manager Policy — `lab_manager_policy.py`

### Pipeline Flow

```
protocol + scenario → check_feasibility()
                           ↓
                    FeasibilityCheckResult (7 dimensions)
                           ↓
              suggest_alternative(protocol, check, scenario)
                           ↓
              AlternativeSuggestion | None
                           ↓
              compose_lab_manager_response(check, suggestion)
                           ↓
                    LabManagerAction (typed, with explanation)
```

### Public Functions

#### `check_feasibility(protocol, scenario) -> FeasibilityCheckResult` — AGT 05
Runs 7 deterministic dimension checks. No LLM calls.

**Checks performed:**
| Dimension | Function | What it checks |
|-----------|----------|---------------|
| `protocol` | `_build_protocol_check` | Wraps `validate_protocol()` from MOD 05 |
| `budget` | `_check_budget` | `_estimate_protocol_cost()` vs `budget_remaining` |
| `equipment` | `_check_equipment` | Items available/booked, finds substitutions |
| `reagents` | `_check_reagents` | Items in-stock/out-of-stock, finds substitutions |
| `schedule` | `_check_schedule` | `duration_days` vs `time_limit_days` |
| `staff` | `_check_staff` | `_estimate_staff_load()` vs `staff_count` |
| `policy` | `_check_policy` | Safety restrictions (e.g., offline-only execution) |

**Cost estimation (`_estimate_protocol_cost`):**
```
base = sample_size * 10
+ duration_days * 50
+ len(controls) * 25
+ len(required_equipment) * 100
+ len(required_reagents) * 75
```

**Staff estimation (`_estimate_staff_load`):**
```
base = 1
+ (1 if sample_size > 20)
+ (1 if len(controls) > 2)
+ (1 if duration_days > 5)
+ (1 if len(required_equipment) > 2)
```

#### `suggest_alternative(protocol, check_result, scenario) -> AlternativeSuggestion | None` — AGT 06
Deterministic revision engine. Returns `None` if already feasible.

**Fix order (deterministic):**
1. Equipment substitutions — replace booked items with alternatives
2. Reagent substitutions — replace out-of-stock items with alternatives
3. Duration clamp — reduce to `time_limit_days` if over
4. Sample size reduction — iterative halving until budget fits (max 10 iterations)

**Post-fix recheck:** runs `check_feasibility()` on revised protocol.
**Returns:** revised protocol, list of changes, remaining failures, pre/post checks.

#### `compose_lab_manager_response(check_result, suggestion=None, explanation_renderer=None) -> LabManagerAction` — AGT 07
Converts grounded results into a typed `LabManagerAction`.

**Action type selection (`_select_lab_manager_action_type`):**
| Condition | Action |
|-----------|--------|
| All 7 dimensions pass | `ACCEPT` |
| Suggestion exists AND improved AND only non-lab failures remain | `SUGGEST_ALTERNATIVE` |
| Lab constraints fail AND no suggestion | `REJECT` |
| Only policy/protocol fail (not lab constraints) | `REPORT_FEASIBILITY` |
| Suggestion exists but didn't improve | `REJECT` |

**Lab constraints = budget, equipment, reagents, schedule, staff (not protocol, not policy).**

### Classes

#### `DimensionCheck(BaseModel)` — `extra="forbid"`
| Field | Type | Default |
|-------|------|---------|
| `ok` | `bool` | `True` |
| `reasons` | `list[str]` | `[]` |

#### `FeasibilityCheckResult(BaseModel)` — `extra="forbid"`
| Field | Type |
|-------|------|
| `protocol` | `DimensionCheck` |
| `budget` | `DimensionCheck` |
| `equipment` | `DimensionCheck` |
| `reagents` | `DimensionCheck` |
| `schedule` | `DimensionCheck` |
| `staff` | `DimensionCheck` |
| `policy` | `DimensionCheck` |
| `estimated_cost` | `float` |
| `required_staff` | `int` |
| `substitution_options` | `dict[str, list[str]]` |
| `validation_result` | `ValidationResult` |

**Computed properties:** `protocol_ok`, `budget_ok`, `equipment_ok`, `reagents_ok`, `schedule_ok`, `staff_ok`, `feasible`, `summary`

#### `SuggestionChange(BaseModel)` — `extra="forbid"`
| Field | Type | Purpose |
|-------|------|---------|
| `field` | `str` | Which protocol field was changed |
| `original` | `str` | Original value (stringified) |
| `revised` | `str` | New value (stringified) |
| `reason` | `str` | Why it was changed |
| `tradeoff` | `str` | What is lost |

#### `AlternativeSuggestion(BaseModel)` — `extra="forbid"`
| Field | Type |
|-------|------|
| `revised_protocol` | `Protocol` |
| `applied_changes` | `list[SuggestionChange]` |
| `remaining_failures` | `list[str]` |
| `improved` | `bool` |
| `pre_check` | `FeasibilityCheckResult` |
| `post_check` | `FeasibilityCheckResult` |

### Type Aliases

```python
ExplanationRenderer = Callable[
    [LabManagerActionType, FeasibilityCheckResult, Optional[AlternativeSuggestion]],
    str,
]
```
