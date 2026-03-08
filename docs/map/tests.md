# Tests Map — `tests/`

> 231 tests across 10 files. All passing.
>
> **Last verified:** 2026-03-08

## Summary

| File | Tests | What it covers |
|------|-------|---------------|
| `test_config.py` | 3 | Shared constants consistency |
| `test_models.py` | 15 | All Pydantic model contracts |
| `test_scenarios.py` | 8 | Scenario generation and determinism |
| `test_validation.py` | 13 | Protocol validation checks |
| `test_scientist_policy.py` | 18+ | Parser, retry, formatter, baseline, bounded tools |
| `test_lab_manager_policy.py` | 13 | Feasibility, suggestion, response |
| `test_reward.py` | 26 | JDG 01-05 scoring functions |
| `test_env.py` | 36 | ENV 01-08, JDG 04-05, TST 01-03 |
| `test_server.py` | 34 | API endpoint integration (API 02-04, 06-07, 13) |
| `test_client.py` | 24 | TRN 13 client module (REST + WS transports) |
| **Total** | **231** | |

## Missing Coverage (not yet implemented)

| File (planned) | Would cover |
|---------------|-------------|
| `test_env.py` (expand) | ENV 10 full reset/step/replay tests |

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

## `test_reward.py` (18 tests)

| Test | What it verifies |
|------|-----------------|
| `test_rigor_good_protocol_scores_higher_than_bad` | Quality ordering |
| `test_rigor_is_deterministic` | Same inputs → same output |
| `test_rigor_empty_controls_reduces_score` | Controls matter |
| `test_rigor_short_rationale_reduces_score` | Rationale length matters |
| `test_rigor_all_domains_return_valid_range` | [0,1] across all 9 combinations |
| `test_feasibility_viable_protocol_scores_high` | Good protocol > 0.7 |
| `test_feasibility_infeasible_protocol_scores_lower` | Bad < good |
| `test_feasibility_accepts_precomputed_check` | Pre-computed = computed |
| `test_feasibility_is_deterministic` | Same inputs → same output |
| `test_feasibility_partial_credit_for_near_budget` | Slightly over > far over |
| `test_feasibility_all_domains_return_valid_range` | [0,1] across all 9 combinations |
| `test_fidelity_aligned_protocol_scores_higher` | Aligned > misaligned |
| `test_fidelity_is_deterministic` | Same inputs → same output |
| `test_fidelity_substitution_gets_partial_credit` | Sub > miss |
| `test_fidelity_mentioning_target_metric_improves_score` | Metric mention helps |
| `test_fidelity_all_domains_return_valid_range` | [0,1] across all 9 combinations |
| `test_all_scores_between_zero_and_one_for_bad_protocol` | Bounds check |
| `test_good_protocol_dominates_bad_on_rigor_and_fidelity` | Cross-scorer consistency |

## `test_env.py` (32 tests)

### TST 01 — Reset (8 tests)
| Test | What it verifies |
|------|-----------------|
| `test_reset_returns_observation_with_both_roles` | Both scientist + lab_manager present |
| `test_reset_scientist_fields_populated` | Paper title, hypothesis, goal, round 0 |
| `test_reset_lab_manager_fields_populated` | Budget, staff, time limit populated |
| `test_reset_preserves_booked_and_out_of_stock` | ENV 02 scenario-pack data preserved |
| `test_reset_state_round_zero` | State starts at round 0, not done |
| `test_reset_generates_episode_id` | UUID episode ID generated |
| `test_reset_clears_previous_episode` | Second reset clears first episode |
| `test_reset_all_templates_and_difficulties` | All 9 template/difficulty combos work |

### TST 03 — Invalid Action (4 tests)
| Test | What it verifies |
|------|-----------------|
| `test_invalid_duration_returns_error_string` | Validation error returned |
| `test_env_survives_after_invalid_action` | Env still accepts valid actions after error |
| `test_invalid_action_does_not_advance_round` | Round stays at 0 |
| `test_request_info_always_passes_validation` | Non-proposal actions skip validation |

### TST 02 — Step and Terminal Path (8 tests)
| Test | What it verifies |
|------|-----------------|
| `test_step_advances_round_number` | Round increments |
| `test_step_returns_observations` | Both roles in step result |
| `test_step_records_conversation_history` | Scientist + LM entries logged |
| `test_accept_with_protocol_terminates` | Accept → done=True |
| `test_accept_terminal_step_has_real_reward` | ENV 06 real scores, not stub 0.8 |
| `test_max_rounds_terminates` | Max rounds → done, no agreement |
| `test_step_info_has_round_and_episode_id` | Metadata populated |
| `test_full_episode_propose_then_accept` | Full 2-step episode |

### ENV 07 — State Snapshot (2 tests)
| Test | What it verifies |
|------|-----------------|
| `test_state_is_deep_copy` | Mutating snapshot doesn't affect env |
| `test_state_history_is_independent` | History list is independent copy |

### ENV 08 — Close/Reopen (3 tests)
| Test | What it verifies |
|------|-----------------|
| `test_close_is_idempotent` | Double close doesn't throw |
| `test_step_after_close_raises` | RuntimeError on step after close |
| `test_reset_reopens_closed_env` | Reset clears closed state |

### JDG 04-05 — Rubric (7 tests)
| Test | What it verifies |
|------|-----------------|
| `test_compute_total_reward_formula` | 10×r×f×fi + bonuses = expected |
| `test_compute_total_reward_with_penalties` | Penalties subtracted correctly |
| `test_compute_total_reward_zero_scores` | Zero dimension → zero reward |
| `test_build_reward_breakdown_returns_valid_scores` | All sub-scores in [0,1] |
| `test_build_reward_breakdown_efficiency_bonus` | Fewer rounds → higher bonus |
| `test_build_reward_breakdown_is_deterministic` | Same inputs → same output |
| `test_total_reward_matches_manual_calculation` | Cross-check formula |

## `test_server.py` (34 tests)

### GET /scenarios — API 04 (5 tests)
| Test | What it verifies |
|------|-----------------|
| `test_returns_200` | Endpoint returns 200 |
| `test_response_has_scenarios_key` | Response has `scenarios` list |
| `test_all_families_present` | All 3 families present |
| `test_each_family_has_difficulties` | Each has easy/medium/hard |
| `test_no_extra_keys` | Only `family` and `difficulties` keys |

### CORS — API 13 (3 tests)
| Test | What it verifies |
|------|-----------------|
| `test_preflight_allows_localhost_vite_origin` | localhost:5173 allowed |
| `test_preflight_allows_hf_space_origin` | HF Spaces origin allowed |
| `test_preflight_rejects_unconfigured_origin` | Unknown origin → 400 |

### POST /reset — API 02 (7 tests)
| Test | What it verifies |
|------|-----------------|
| `test_reset_returns_200_with_expected_keys` | 200 with session_id, episode_id, observation |
| `test_reset_observation_has_both_roles` | Scientist + lab_manager present |
| `test_reset_with_explicit_session_id_reuses_slot` | Same session_id reused |
| `test_reset_reuse_closes_prior_env` | New episode on reuse |
| `test_reset_default_params` | Defaults work without error |
| `test_reset_custom_scenario_and_difficulty` | All 9 combos succeed |
| `test_reset_deterministic_with_same_seed` | Same seed → same observation |

### POST /step — API 03 (5 tests)
| Test | What it verifies |
|------|-----------------|
| `test_reset_then_step_happy_path` | Reset → step returns 200 with StepResult |
| `test_step_invalid_session_returns_404` | Non-existent session → 404 |
| `test_terminal_step_returns_real_reward_breakdown` | Accept has real scores, not stub 0.8 |
| `test_semantic_invalid_action_returns_200_with_error` | Invalid duration → 200 with info.error |
| `test_replay_uses_real_judge_data` | Replay has real judge_notes, not stub |

### WebSocket — API 06 (12 tests)
| Test | What it verifies |
|------|-----------------|
| `test_ws_ping_pong` | Ping → pong |
| `test_ws_reset_returns_observation` | Reset returns episode_id + observation |
| `test_ws_step_returns_result` | Step returns step_ok with result |
| `test_ws_full_episode_real_reward` | Propose → accept returns real scores |
| `test_ws_invalid_json` | Bad JSON → error |
| `test_ws_missing_action_field` | Missing action → error |
| `test_ws_invalid_action_payload` | Invalid action schema → error |
| `test_ws_unknown_message_type` | Unknown type → error |
| `test_ws_session_isolation` | Two connections have independent env state |
| `test_ws_semantic_invalid_action_returns_step_ok_with_info_error` | Invalid duration → step_ok with info.error |
| `test_ws_timeout_verdict` | Max rounds → done, timeout verdict |
| `test_ws_terminal_episode_persists_real_replay_log` | WS episode → /replay has real data |

### WebSocket Idle Timeout — API 07 (2 tests)
| Test | What it verifies |
|------|-----------------|
| `test_ws_idle_timeout_closes_connection` | No messages → server closes with code 1000 |
| `test_ws_env_closes_on_disconnect` | env.close() called in finally block on disconnect |

## `test_client.py` (24 tests)

### REST Transport (10 tests)
| Test | What it verifies |
|------|-----------------|
| `test_connect_succeeds` | REST connect hits /health |
| `test_connect_bad_url_raises` | Bad URL raises |
| `test_reset_returns_observation` | reset() returns typed Observation |
| `test_reset_sets_session_and_episode_id` | IDs set after reset |
| `test_reset_reuses_session` | Same session_id on re-reset |
| `test_step_returns_step_result` | step() returns typed StepResult |
| `test_step_before_reset_raises` | step() without reset raises |
| `test_full_episode_propose_accept` | Full episode with reward > 0 |
| `test_replay_after_episode` | replay() returns typed EpisodeLog |
| `test_context_manager_closes` | `with` block sets connected=False |

### WebSocket Transport (11 tests)
| Test | What it verifies |
|------|-----------------|
| `test_connect_succeeds` | WS connect opens connection |
| `test_connect_bad_url_raises` | Bad URL raises |
| `test_reset_returns_observation` | reset() returns typed Observation |
| `test_reset_sets_episode_id` | episode_id set after reset |
| `test_ws_session_id_is_none` | WS has no session_id |
| `test_step_returns_step_result` | step() returns typed StepResult |
| `test_full_episode_propose_accept` | Full episode with reward > 0 |
| `test_semantic_invalid_action_step_ok_with_error` | Invalid action → info.error |
| `test_context_manager_closes` | `with` block sets connected=False |
| `test_state_not_supported` | state() raises NotImplementedError |
| `test_replay_not_supported` | replay() raises NotImplementedError |

### Constructor (3 tests)
| Test | What it verifies |
|------|-----------------|
| `test_unknown_transport_raises` | "grpc" → ValueError |
| `test_not_connected_raises_on_reset` | reset() without connect raises |
| `test_default_transport_is_websocket` | Default is _WsTransport |

## Test Helpers

### Shared fixtures in test files
| Helper | File | Purpose |
|--------|------|---------|
| `_scenario(template, difficulty)` | test_lab_manager_policy | Generate scenario with seed=123 |
| `_protocol_for_scenario(scenario, **overrides)` | test_lab_manager_policy | Build viable protocol from scenario |
| `_base_observation(**overrides)` | test_scientist_policy | Build ScientistObservation with defaults |
| `_make_system_prompt()` | test_scientist_policy | Build prompt from math_reasoning scenario |
| `_VALID_REQUEST_INFO_JSON` | test_scientist_policy | Valid request_info JSON string |
| `_scenario(template, difficulty)` | test_env | Generate scenario with seed=42 |
| `_good_action(scenario)` | test_env | Build valid propose_protocol action |
| `_accept_action()` | test_env | Build valid accept action |
| `_good_protocol(scenario)` | test_env | Build well-formed protocol |
| `_reset(client, **kwargs)` | test_server | Reset and return response JSON |
| `_good_action_payload(client)` | test_server | Build valid propose_protocol payload |
| `_accept_action_payload()` | test_server | Build valid accept payload |
| `_propose_action(obs)` | test_client | Build valid propose_protocol ScientistAction |
| `_accept_action()` | test_client | Build valid accept ScientistAction |
| `live_server` | test_client | Module-scoped uvicorn server fixture |
