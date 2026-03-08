# Tests Map - `tests/`

> 327 tests across 14 files. All passing.
>
> **Last verified:** 2026-03-08

## Summary

| File | Tests | What it covers |
|------|-------|----------------|
| `test_client.py` | 24 | `TRN 13` reusable client over REST and WebSocket |
| `test_config.py` | 3 | Shared constants and config consistency |
| `test_env.py` | 56 | `ENV 01-08`, `ENV 10`, `ENV 11`, `OBS 04`, `JDG 04-05`, `TST 01-03` |
| `test_judge_policy.py` | 10 | `JDG 11` structured judge audit payload |
| `test_lab_manager_policy.py` | 37 | `AGT 05-07` plus `AGT 09` determinism coverage |
| `test_models.py` | 21 | Action, observation, step, state, and log contracts |
| `test_prompts.py` | 6 | `AGT 10` prompt files and bounded-tool rendering |
| `test_reward.py` | 40 | `JDG 01-06`, `JDG 08`, and reward regression coverage |
| `test_rollout.py` | 12 | `TRN 03` rollout worker behavior |
| `test_rollout_traces.py` | 2 | `TRN 04` bounded tool trace aggregation and batched collection |
| `test_scenarios.py` | 13 | `SCN 01-13` scenario generation and determinism |
| `test_scientist_policy.py` | 46 | `MOD 09`, `AGT 01-04`, `AGT 08` |
| `test_server.py` | 37 | `API 02-04`, `API 06-08`, `API 13`, replay audit propagation |
| `test_validation.py` | 20 | `MOD 05-06` semantic validation |
| **Total** | **327** | |

## Coverage Notes

- The environment stack is covered end to end:
  - `test_env.py` validates reset, step, invalid action, termination, reward integration, deep state snapshots, close/reopen lifecycle behavior, terminal judge-audit propagation, and seeded replay determinism across all scenario families.
- The API/server stack is covered end to end:
  - `test_server.py` covers REST reset/step/scenarios, WebSocket session handling, idle timeout cleanup, CORS behavior, and replay audit propagation.
- The scientist stack is covered end to end:
  - `test_scientist_policy.py`, `test_prompts.py`, `test_rollout.py`, and `test_rollout_traces.py` together cover prompt construction, observation formatting, parse/retry, baseline policy, rollout collection, and bounded tool trace capture.
- The judge stack is covered end to end:
  - `test_reward.py` covers rubric scores and reward math, while `test_judge_policy.py` covers structured audit payload generation.

## Remaining Gaps

| Planned test work | Why it still matters |
|-------------------|----------------------|
| `TST 09` notebook smoke coverage | Fresh-runtime validation for the judged training notebook |

## Task-to-Test Mapping

| Area | Primary test files |
|------|--------------------|
| Models and contracts | `test_models.py`, `test_validation.py` |
| Scenarios | `test_scenarios.py` |
| Scientist policy | `test_scientist_policy.py`, `test_prompts.py` |
| Lab Manager policy | `test_lab_manager_policy.py` |
| Judge and reward | `test_reward.py`, `test_judge_policy.py` |
| Environment | `test_env.py` |
| API and deployment-facing server behavior | `test_server.py` |
| Client and training rollouts | `test_client.py`, `test_rollout.py`, `test_rollout_traces.py` |
