# Tests Map — `tests/`

> 87 tests across 6 files. All passing.
>
> **Last verified:** 2026-03-07

## Summary

| File | Tests | What it covers |
|------|-------|---------------|
| `test_config.py` | 3 | Shared constants consistency |
| `test_models.py` | 15 | All Pydantic model contracts |
| `test_scenarios.py` | 8 | Scenario generation and determinism |
| `test_validation.py` | 13 | Protocol validation checks |
| `test_scientist_policy.py` | 18 | Parser, retry, formatter, baseline |
| `test_lab_manager_policy.py` | 13 | Feasibility, suggestion, response |
| **Total** | **87** | |

## Missing Coverage (not yet implemented)

| File (planned) | Would cover |
|---------------|-------------|
| `test_reward.py` | JDG 01-03 scoring functions |
| `test_env.py` | ENV 01-11 real environment |
| `test_server.py` | API endpoint integration tests |

---

## `test_config.py` (3 tests)

| Test | What it verifies |
|------|-----------------|
| `test_reset_request_defaults_match_shared_config` | ResetRequest defaults match config constants |
| `test_generated_scenarios_respect_shared_round_and_budget_caps` | Scenarios use MAX_ROUNDS and MAX_BUDGET |
| `test_timeout_exports_share_the_same_default_value` | SESSION_TTL, WS_IDLE, ROUND_TIME all equal TIMEOUT |

## `test_models.py` (15 tests)

### ScientistAction (6 tests)
| Test | What it verifies |
|------|-----------------|
| `test_scientist_action_accepts_valid_protocol_payload` | propose_protocol with full fields passes |
| `test_scientist_action_rejects_unknown_action_type` | Invalid enum value rejected |
| `test_scientist_action_rejects_request_info_without_questions` | questions must be non-empty for request_info |
| `test_scientist_action_rejects_protocol_payload_for_request_info` | No protocol fields with request_info |
| `test_scientist_action_rejects_protocol_with_zero_sample_size` | sample_size >= 1 for protocol actions |
| `test_scientist_action_rejects_extra_fields` | extra="forbid" enforcement |

### LabManagerAction (4 tests)
| Test | What it verifies |
|------|-----------------|
| `test_lab_manager_action_accepts_valid_suggestion_payload` | suggest_alternative with all fields passes |
| `test_lab_manager_action_rejects_feasible_flag_mismatch` | feasible must match constraint flags AND |
| `test_lab_manager_action_rejects_missing_suggestion_fields` | suggest_alternative needs suggestion fields |
| `test_lab_manager_action_rejects_suggestions_for_report_feasibility` | Suggestion fields forbidden for non-suggest |

### Observation (2 tests)
| Test | What it verifies |
|------|-----------------|
| `test_observation_coerces_nested_dicts_to_typed_models` | Dict coercion to ConversationEntry/Protocol |
| `test_observation_rejects_invalid_conversation_role` | Only scientist/lab_manager/system |
| `test_observation_rejects_negative_budget` | budget_total ge=0 |

### Episode Models — MOD 04 (3 tests)
| Test | What it verifies |
|------|-----------------|
| `test_episode_state_accepts_typed_protocol_and_history` | Protocol + ConversationEntry fields |
| `test_episode_state_accepts_none_protocol` | Optional[Protocol] = None |
| `test_episode_state_json_round_trip` | model_dump_json → model_validate_json |
| `test_episode_log_accepts_typed_fields` | Typed transcript + reward_breakdown |
| `test_episode_log_none_reward_breakdown` | Optional[RewardBreakdown] = None |
| `test_episode_log_json_round_trip` | Serialization round-trip |
| `test_episode_log_nested_state_preserves_typed_fields` | final_state nesting |
| `test_step_result_with_typed_info` | StepInfo with RewardBreakdown |

## `test_scenarios.py` (8 tests)

| Test | What it verifies |
|------|-----------------|
| `test_generate_scenario_is_deterministic_for_same_seed` | Same seed → same output |
| `test_generate_scenario_varies_across_seeded_cases` | Different seeds → different output |
| `test_available_scenario_families_exposes_three_domain_families` | 3 families, each with 3 difficulties |
| `test_hard_finance_scenario_exposes_unavailable_resource_and_safety_rules` | Hard mode tightens resources |
| `test_difficulty_levels_mechanically_change_budget_and_constraints` | Easy > medium > hard budget |
| `test_generated_scenarios_keep_unique_constraint_and_resource_keys` | No duplicate keys |
| `test_golden_scenario_specs_exist_for_manual_prompt_checks` | Golden file exists |
| `test_golden_scenarios_match_expected_title_and_domain` | Golden content matches |

## `test_validation.py` (13 tests)

| Test | What it verifies |
|------|-----------------|
| `test_valid_protocol_passes` | Well-formed protocol → valid=True |
| `test_zero_sample_size_is_error` | sample_size < 1 → ERROR |
| `test_zero_duration_is_error` | duration_days < 1 → ERROR |
| `test_duration_exceeding_time_limit_is_error` | Over limit → ERROR |
| `test_duration_within_limit_passes` | Under limit → pass |
| `test_unknown_equipment_is_warning` | Unknown item → WARNING |
| `test_booked_equipment_without_substitution_is_error` | Booked + no sub → ERROR |
| `test_out_of_stock_reagent_without_substitution_is_error` | Out + no sub → ERROR |
| `test_unknown_reagent_is_warning` | Unknown reagent → WARNING |
| `test_required_element_warning_when_not_addressed` | Missing element → WARNING |
| `test_no_controls_is_warning` | Empty controls → WARNING |
| `test_validation_result_never_raises` | Always returns, never throws |
| `test_validation_result_json_round_trip` | Serialization round-trip |

## `test_scientist_policy.py` (18 tests)

### Parser — MOD 09 (5 tests)
| Test | What it verifies |
|------|-----------------|
| `test_parse_scientist_output_accepts_plain_json` | Plain JSON parsing |
| `test_parse_scientist_output_accepts_fenced_json_with_prose` | Fenced block extraction |
| `test_parse_scientist_output_raises_explicit_error_when_json_is_missing` | no_json error code |
| `test_parse_scientist_output_raises_explicit_error_when_json_is_invalid` | invalid_json error code |
| `test_parse_scientist_output_raises_explicit_error_when_schema_is_invalid` | invalid_action error code |

### System Prompt — AGT 01 (1 test)
| Test | What it verifies |
|------|-----------------|
| `test_build_scientist_system_prompt_uses_normalized_scenario_data` | Contains role, task, criteria, action types |

### Observation Formatter — AGT 02 (5 tests)
| Test | What it verifies |
|------|-----------------|
| `test_format_observation_empty_history_no_protocol` | Empty state formatting |
| `test_format_observation_with_history_and_protocol` | Populated state formatting |
| `test_format_observation_stable_section_order` | Section order is deterministic |
| `test_format_observation_history_entry_without_action_type` | Null action_type handled |
| `test_format_observation_from_generated_scenario` | Works with real scenario data |

### Retry Loop — AGT 03 (7 tests)
| Test | What it verifies |
|------|-----------------|
| `test_retry_success_on_first_try` | No retry needed |
| `test_retry_malformed_json_then_valid` | Recovers from bad JSON |
| `test_retry_invalid_action_then_valid` | Recovers from schema error |
| `test_retry_exhausted_raises_last_error` | Raises after max retries |
| `test_retry_correction_message_includes_parser_error` | Correction prompt has error detail |
| `test_retry_correction_for_invalid_action_includes_validation_detail` | Schema error in correction |
| `test_retry_metadata_serializable` | RetryMetadata JSON round-trip |

### Baseline Action — AGT 04 (4 tests — user-added)
| Test | What it verifies |
|------|-----------------|
| `test_baseline_scientist_proposes_protocol_for_fresh_observation` | No protocol → propose |
| `test_baseline_scientist_accepts_existing_protocol_without_blocker` | Accepted → accept |
| `test_baseline_scientist_revises_when_latest_feedback_has_blocker` | Blocker → revise |
| `test_baseline_scientist_finishes_stub_episode_without_crashing` | Full 2-round stub episode |

## `test_lab_manager_policy.py` (13 tests)

### Feasibility — AGT 05 (7 tests — user-added)
| Test | What it verifies |
|------|-----------------|
| `test_check_feasibility_passes_for_viable_protocol` | All 7 dimensions pass |
| `test_check_feasibility_flags_budget_overrun` | Over-budget detected |
| `test_check_feasibility_flags_unavailable_resource_and_lists_substitution` | Out-of-stock + substitution |
| `test_check_feasibility_flags_schedule_overrun` | Duration over limit |
| `test_check_feasibility_flags_staff_overload` | Staff insufficient |
| `test_check_feasibility_flags_policy_violation` | Policy violation detected |
| `test_check_feasibility_is_deterministic` | Same inputs → same output |

### Suggestion — AGT 06 (8 tests)
| Test | What it verifies |
|------|-----------------|
| `test_suggest_alternative_returns_none_for_feasible_protocol` | Feasible → None |
| `test_suggest_alternative_substitutes_equipment` | Equipment swap applied |
| `test_suggest_alternative_substitutes_reagent` | Reagent swap applied |
| `test_suggest_alternative_clamps_duration` | Duration reduced to limit |
| `test_suggest_alternative_reduces_sample_size_for_budget` | Sample size halved for budget |
| `test_suggest_alternative_is_deterministic` | Same inputs → same output |
| `test_suggest_alternative_post_check_is_not_worse` | Post-fix has <= pre-fix failures |
| `test_suggest_alternative_reports_remaining_failures` | Unfixable failures listed |

### Response Composition — AGT 07 (5 tests — user-added)
| Test | What it verifies |
|------|-----------------|
| `test_compose_lab_manager_response_accepts_feasible_protocol` | Feasible → ACCEPT |
| `test_compose_lab_manager_response_suggests_alternative_when_revision_exists` | Has suggestion → SUGGEST |
| `test_compose_lab_manager_response_rejects_when_no_revision_exists` | No fix → REJECT |
| `test_compose_lab_manager_response_reports_non_lab_issues` | Policy-only → REPORT |
| `test_compose_lab_manager_response_uses_custom_renderer_without_changing_verdict` | Custom renderer works |

## Test Helpers

### Shared fixtures in test files
| Helper | File | Purpose |
|--------|------|---------|
| `_scenario(template, difficulty)` | test_lab_manager_policy | Generate scenario with seed=123 |
| `_protocol_for_scenario(scenario, **overrides)` | test_lab_manager_policy | Build viable protocol from scenario |
| `_base_observation(**overrides)` | test_scientist_policy | Build ScientistObservation with defaults |
| `_make_system_prompt()` | test_scientist_policy | Build prompt from math_reasoning scenario |
| `_VALID_REQUEST_INFO_JSON` | test_scientist_policy | Valid request_info JSON string |
