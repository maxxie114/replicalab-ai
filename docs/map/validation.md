# Validation Map — `replicalab/utils/validation.py`

> Deterministic protocol validation against scenario constraints.
> Pure functions — no LLM calls, no side effects.
>
> **Tasks implemented:** MOD 05

## Public API

### `validate_protocol(protocol: Protocol, scenario: NormalizedScenarioPack) -> ValidationResult`
Main entry point. Never raises — always returns a `ValidationResult`.

**Checks run (in order):**
1. `_check_obvious_impossibilities` — sample_size < 1, no controls, duration < 1
2. `_check_duration_vs_time_limit` — protocol days vs lab time_limit_days
3. `_check_equipment_vocabulary` — items vs available/booked/substitutable
4. `_check_reagent_vocabulary` — items vs in-stock/out-of-stock/substitutable
5. `_check_required_element_coverage` — protocol text vs hidden_reference_spec.required_elements

**Result:** `valid=True` only if zero ERROR-level issues.

## Data Classes

### `IssueSeverity(str, Enum)`
| Value | Meaning |
|-------|---------|
| `error` | Hard failure — protocol cannot proceed |
| `warning` | Advisory — protocol is suboptimal but possible |

### `ValidationIssue(BaseModel)` — `extra="forbid"`
| Field | Type | Example |
|-------|------|---------|
| `severity` | `IssueSeverity` | `ERROR` |
| `category` | `str` | `"equipment"`, `"duration"`, `"sample_size"` |
| `message` | `str` | `"Equipment 'X' is booked and has no substitution."` |

### `ValidationResult(BaseModel)` — `extra="forbid"`
| Field | Type |
|-------|------|
| `valid` | `bool` |
| `issues` | `list[ValidationIssue]` |

**Properties:**
- `errors` → `list[ValidationIssue]` (severity=ERROR only)
- `warnings` → `list[ValidationIssue]` (severity=WARNING only)

## Check Details

### `_check_obvious_impossibilities`
| Condition | Severity | Category |
|-----------|----------|----------|
| `sample_size < 1` | ERROR | `sample_size` |
| `controls` empty | WARNING | `controls` |
| `duration_days < 1` | ERROR | `duration` |

### `_check_duration_vs_time_limit`
| Condition | Severity | Category |
|-----------|----------|----------|
| `duration_days > time_limit_days` | ERROR | `duration` |

### `_check_equipment_vocabulary`
| Condition | Severity | Category |
|-----------|----------|----------|
| Item available | — (pass) | — |
| Item booked + has substitution | WARNING | `equipment` |
| Item booked + no substitution | ERROR | `equipment` |
| Item unknown (not in inventory) | WARNING | `equipment` |

### `_check_reagent_vocabulary`
| Condition | Severity | Category |
|-----------|----------|----------|
| Item in stock | — (pass) | — |
| Item out of stock + has substitution | WARNING | `reagent` |
| Item out of stock + no substitution | ERROR | `reagent` |
| Item unknown (not in inventory) | WARNING | `reagent` |

### `_check_required_element_coverage`
Checks each `hidden_reference_spec.required_elements` against protocol text fields using token matching.

**Protocol text searched:** technique, rationale, controls, equipment, reagents (joined, lowercased).
**Token extraction:** `_element_tokens(element)` splits on spaces, keeps tokens with 3+ chars.
**Match:** any token from element found in protocol text → covered.

| Condition | Severity | Category |
|-----------|----------|----------|
| Element not addressed | WARNING | `required_element` |

## Internal Helpers

| Function | Purpose |
|----------|---------|
| `_normalize(label)` | Lowercase, strip, collapse whitespace |
| `_element_tokens(element)` | Split element string into searchable tokens (3+ chars) |
| `_substitution_alternatives(scenario)` | Set of normalized original items from `allowed_substitutions` |

## Who Consumes This

- **`lab_manager_policy.py`** — `check_feasibility()` calls `validate_protocol()` and wraps result in `protocol` DimensionCheck
- **`scoring/`** (future) — JDG 01 rigor score will reuse `_element_tokens` for required element matching
