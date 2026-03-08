# ReplicaLab Task Completion Tracker

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Working Governance Files

| File | Role |
|------|------|
| `AGENTS.md` | Required startup and close-out rules for contributors and automated model agents |
| `docs/project_management_rules.md` | Detailed project-management workflow |
| `docs/changes.md` | Append-only deviation log |
| `docs/<owner>/` | Owner-local task and planning docs |

---

## Overall Completion

| Metric | Value |
|--------|-------|
| Total tasks | 152 |
| Completed | 67 |
| Partial / active | 3 |
| Remaining | 82 |
| **Completion rate** | **44.08%** |

### Completion by Person

| Person | Assigned | Completed (own) | Completed (by others) | Remaining | Rate |
|--------|----------|----------------|----------------------|-----------|------|
| Kian (Person A) | 49 (47 solo + 2 shared with B) | 1 shared sign-off (`FND 08`) | 38 (`FND 04`, `FND 09`, `MOD 01`, `MOD 02`, `MOD 03`, `MOD 04`, `MOD 05`, `MOD 11`, `MOD 12`, `SCN 01` to `SCN 10`, `AGT 05`, `ENV 01` to `ENV 08`, `JDG 01` to `JDG 05`, `TST 01` to `TST 05` done by Person B) | 10 | 79.59% |
| Person B (Ayush) | 29 (27 solo + 2 shared with A) | 13 (`FND 08`, `MOD 09`, `SCN 11`, `AGT 01`, `AGT 02`, `AGT 03`, `AGT 04`, `AGT 05`, `AGT 06`, `AGT 07`, `AGT 08`, `AGT 11`, `TRN 13`) | 0 | 16 | 44.83% |
| Max (Person C) | 41 | 1 (`FND 11`) | 17 (`FND 01`, `FND 02`, `FND 03`, `FND 05`, `FND 07`, `FND 10`, `FND 12` done by others, `API 02`, `API 03`, `API 04`, `API 06`, `API 07`, `API 08`, `API 09`, `API 13`, `API 15`, `TST 07` done by Person B) | 23 | 43.90% |
| Kush (Person D) | 32 | 0 | 1 (`FND 06` done by Person B) | 31 | 3.13% |
| All (shared) | 3 | 2 (`FND 08`, `AGT 05`) | 0 | 1 | 66.67% |

Note: Person B (Ayush) has completed two shared tasks in their own lane
(`FND 08`, `AGT 05`) plus eleven solo tasks in their own lane (`MOD 09`,
`SCN 11`, `AGT 01`, `AGT 02`, `AGT 03`, `AGT 04`, `AGT 06`, `AGT 07`,
`AGT 08`, `AGT 11`, `TRN 13`), and has also executed a large cross-owner
bundle (`FND 01`, `FND 02`, `FND 04`, `FND 05`, `FND 06`, `FND 07`,
`FND 09`, `FND 10`, `MOD 01`, `MOD 02`, `MOD 03`, `MOD 04`, `MOD 05`,
`MOD 11`, `MOD 12`, `SCN 01` to `SCN 10`, `ENV 01` to `ENV 08`, `JDG 01`
 to `JDG 05`, `TST 01` to `TST 05`, `API 02`, `API 03`, `API 04`, `API 06`,
`API 07`, `API 08`, `API 09`, `API 13`, `API 15`, `TST 07`) to keep the
Kian, Max, and Kush dependency chain moving.
`TRN 13` is complete; `TRN 03` is the next unblocked task for Person B.

---

## Active Partial Tasks

| ID | Assigned To | Current Status | Remaining Acceptance Item |
|----|-------------|----------------|---------------------------|
| API 01 | Max (Person C) | FastAPI app shell and `/health` endpoint work locally against the real env | Task-owner sign-off and final deployment-path polish |
| API 14 | Max (Person C) | REST session isolation exists in the server stub path | Concurrent-session verification against the real env |
| OBS 02 | Max (Person C) | Structured local logging exists in `server/app.py` | Logging behavior needs real-env usage confirmation |

---

## Completed Tasks

### Person B (Ayush) - Completed on behalf of others

| ID | Epic | Assigned To | Task | File/Module | Date | What Was Done | Acceptance Criteria | Verified |
|----|------|------------|------|-------------|------|---------------|--------------------|---------|
| FND 01 | E01 | Person C | Create repo structure and base folders from agreed layout | repo root | 2026-03-07 | Created the full repo scaffold: `replicalab/` with subdirectories for `agents/`, `env/`, `prompts/`, `scenarios/`, `scoring/`, `utils/`; `server/`; `frontend/` with `src/components/` and `src/pages/`; `notebooks/`; `tests/`. All directories tracked via `.gitkeep` files. | All top level folders exist and repo clones cleanly | Yes |
| FND 02 | E01 | Person C | Add Python project config and dependencies placeholder | `pyproject.toml` | 2026-03-08 | Added a PEP 621 `pyproject.toml` with package metadata, Python 3.10+ requirement, runtime dependencies (`pydantic`, `fastapi`, `uvicorn`, `websockets`), dev extras (`pytest`, `pytest-cov`, `ruff`, `mypy`), package discovery, and pytest test-path settings. | Project installs locally without missing package errors for base modules | Yes - verified with `python -m pip install -e .`, `python -m pip install -e ".[dev]"`, and `python -c "from replicalab.models import ..."` |
| FND 04 | E01 | Person A | Add empty Pydantic models and shared type names | `replicalab/models.py` | 2026-03-08 | Created `replicalab/__init__.py` and `replicalab/models.py` with the shared action, observation, step, state, and log stubs. | Import paths resolve for all placeholder models | Yes - verified with `python -c "from replicalab.models import ..."` |
| FND 05 | E01 | Person C | Add ignore rules for Python, Node, logs, notebooks, and build artifacts | `.gitignore`, `.dockerignore` | 2026-03-08 | Added `.dockerignore` and expanded `.gitignore` for caches, coverage artifacts, notebook checkpoints, frontend build files, and generated outputs while preserving tracked `.gitkeep` files. | Repo status stays clean after local run and build, and Docker build excludes non-runtime files | Yes |
| FND 06 | E01 | Person D | Add temporary project stub with title, mission, team roles, and local setup placeholder | `README.md` | 2026-03-08 | Replaced the aspirational README with a temporary foundation stub that reflects the current repo state, mission, ownership, and verified setup placeholder. | New contributor can understand repo purpose in under two minutes | Yes |
| FND 07 | E01 | Person C | Define branch naming, PR template, and issue template | `.github/` and repo workflow docs | 2026-03-08 | Added `.github/pull_request_template.md` and `.github/ISSUE_TEMPLATE/task.yml`, and documented preferred branch naming patterns plus required tracking-doc updates in `docs/project_management_rules.md`. | All future PRs auto show the template and issue fields | Yes |
| FND 09 | E01 | Person A | Create OpenEnv configuration file specifying environment class, action and observation types, and server settings | `openenv.yaml`, `pyproject.toml`, `server/app.py`, `uv.lock` | 2026-03-08 | Added `openenv.yaml`, recorded the environment and contract metadata for OpenEnv, added `openenv-core` plus a `server` script entry point to `pyproject.toml`, added `main()` to `server/app.py`, and generated `uv.lock` so the repo passes local OpenEnv validation. | OpenEnv can discover and serve the environment using this config file | Yes - verified with `uv lock` and `openenv validate` |
| FND 10 | E01 | Person C | Create output directory structure | `replicalab/outputs/` | 2026-03-07 | Created `replicalab/outputs/` with three subdirectories: `logs/`, `replays/`, and `plots/`, all tracked via `.gitkeep` files. | Output directories exist and generated files are not committed to git | Yes |
| MOD 01 | E02 | Person A | Implement `ScientistAction` schema | `replicalab/models.py`, `tests/test_models.py`, `server/app.py` | 2026-03-08 | Replaced the `ScientistAction` stub with a strict enum-backed schema, required all frozen-contract fields, forbade unknown keys, rejected mixed-mode payloads, added conditional validation for proposal, revision, request-info, and accept modes, and patched the stub server so `accept` preserves the current protocol. | Valid scientist actions parse and invalid fields raise validation errors | Yes - verified with `python -m pytest tests/test_models.py` and a stub-env `ScientistAction.model_validate(...)` smoke step |
| MOD 02 | E02 | Person A | Implement `LabManagerAction` schema | `replicalab/models.py`, `tests/test_models.py` | 2026-03-08 | Replaced the `LabManagerAction` stub with a strict enum-backed schema, required all frozen-contract fields, forbade unknown keys, enforced feasible-flag consistency, rejected suggestion fields outside `suggest_alternative`, and added focused validation tests. | Valid lab manager actions parse and invalid fields raise validation errors | Yes - verified with `python -m pytest tests/test_models.py` |
| MOD 03 | E02 | Person A | Implement role specific observation models | `replicalab/models.py`, `tests/test_models.py`, `server/app.py` | 2026-03-08 | Added typed `ConversationEntry` and `Protocol` models, upgraded both observation branches to use typed nested structures with non-negative numeric constraints and stable keys, and verified dict-to-model coercion through the stub server. | Scientist and lab observations serialize to JSON with stable keys | Yes - verified with `python -m pytest tests/test_models.py` and a stub `reset()` / `step()` JSON smoke test |
| MOD 04 | E02 | Person A | Implement `EpisodeState` and `EpisodeLog` models | `replicalab/models.py`, `server/app.py`, `tests/test_models.py` | 2026-03-08 | Replaced the remaining loose `dict` state and replay fields with typed `Protocol`, `ConversationEntry`, and `RewardBreakdown` models, updated the stub runtime to construct those nested models explicitly, and added round-trip coverage for serialized state and logs. | Full state round trip serialize plus deserialize works | Yes - verified with `python -m pytest tests/test_models.py` |
| MOD 05 | E02 | Person A | Add protocol validation for sample size, controls, duration, equipment vocab, and reagent vocab | `replicalab/utils/validation.py`, `tests/test_models.py`, `tests/test_scenarios.py` | 2026-03-08 | Added deterministic semantic protocol validation with `ValidationResult` and `validate_protocol(...)` checks for resource vocabulary, allowed substitutions, duration limits, required-element coverage, and obvious impossibilities against the normalized scenario pack. | Invalid protocol examples are rejected with readable reasons | Yes - verified with `python -m pytest tests/test_models.py tests/test_scenarios.py` |
| MOD 11 | E02 | Person A | Implement `StepResult` model | `replicalab/models.py`, `server/app.py`, `tests/test_models.py` | 2026-03-08 | Added typed `RewardBreakdown` and `StepInfo` models, upgraded `StepResult.info` to the reserved-key contract while still allowing debug metadata, and updated the stub runtime to build typed reward and step-info payloads explicitly. | Step result serializes cleanly and all consumers agree on its shape | Yes - verified with `python -m pytest tests/test_models.py` |
| MOD 12 | E02 | Person A | Create environment configuration module with shared constants | `replicalab/config.py`, `server/app.py`, `replicalab/scenarios/*.py`, `tests/test_config.py` | 2026-03-08 | Added a shared configuration module for default scenario and difficulty, round cap, budget cap, timeout values, stub reward, and API host or port defaults, then updated the server and scenario builders to import those constants instead of repeating literals. | All modules import config from one place and no magic numbers remain in env or scoring code | Yes - verified with `python -m pytest tests/test_config.py tests/test_scenarios.py` |
| SCN 01 | E03 | Person A | Implement deterministic RNG helper `seed_rng()` | `replicalab/utils/seed.py`, `replicalab/scenarios/templates.py` | 2026-03-08 | Added deterministic seed helpers that derive reproducible RNG namespaces for scenario generation. | Same seed always yields the same random choices and the seed utility is importable from scenarios and env | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| SCN 02 | E03 | Person A | Define normalized scenario schema with task summary, success criteria, constraints, resources, allowed substitutions, and hidden reference spec | `replicalab/scenarios/templates.py` | 2026-03-08 | Added `NormalizedScenarioPack` plus strict `ScenarioConstraint`, `ScenarioResource`, `AllowedSubstitution`, and `HiddenReferenceSpec` models to standardize all scenario families. | All scenario builders return the same normalized top-level structure and mapper-ready inputs | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| SCN 03 | E03 | Person A | Implement mathematics template | `replicalab/scenarios/math_reasoning.py` | 2026-03-08 | Added deterministic mathematics planning templates covering theorem, proof-goal, review, and time constraints. | Generated scenario passes structure and internal consistency tests | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| SCN 04 | E03 | Person A | Implement ML benchmark template | `replicalab/scenarios/ml_benchmark.py` | 2026-03-08 | Added deterministic ML benchmark templates covering dataset, compute, time, and evaluation constraints. | Generated scenario passes structure and internal consistency tests | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| SCN 05 | E03 | Person A | Implement finance and trading planning template | `replicalab/scenarios/finance_trading.py` | 2026-03-08 | Added deterministic offline finance and trading planning templates covering capital, drawdown, slippage, and backtest rules. | Generated scenario passes structure and internal consistency tests | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| SCN 06 | E03 | Person A | Implement difficulty application for easy, medium, hard | `replicalab/scenarios/templates.py`, `tests/test_scenarios.py` | 2026-03-08 | Added mechanical difficulty scaling that adjusts budgets, time, staff, resource availability, and injected conflict constraints across easy, medium, and hard. | Difficulty visibly changes the normalized scenario pack in a meaningful way | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| SCN 07 | E03 | Person A | Implement normalized constraint and resource generator | `replicalab/scenarios/templates.py`, `tests/test_scenarios.py` | 2026-03-08 | Added normalized constraint and resource mapping into role-specific observations with consistency checks for unique keys and non-contradictory generated packs. | No generated scenario contains contradictory constraints or resources | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| SCN 08 | E03 | Person A | Implement hidden reference spec and allowed substitutions per template | `replicalab/scenarios/templates.py`, `tests/test_scenarios.py` | 2026-03-08 | Added per-template hidden reference specs and allowed substitutions so scoring and negotiation can distinguish fixed versus flexible elements deterministically. | Hidden reference clearly marks what is fixed versus flexible for deterministic scoring | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| SCN 09 | E03 | Person A | Implement `generate_scenario(seed, template, difficulty)` | `replicalab/scenarios/templates.py`, `server/app.py`, `tests/test_scenarios.py` | 2026-03-08 | Added deterministic full-scenario generation and wired the stub server to use the normalized scenario families instead of the earlier hard-coded lab-only placeholder list. | Function returns a full scenario with deterministic content | Yes - verified with `python -m pytest tests/test_scenarios.py` and a `_StubEnv.reset(...)` smoke test |
| SCN 10 | E03 | Person A | Add seeded generation tests and consistency tests | `tests/test_scenarios.py` | 2026-03-08 | Added seeded determinism, variation, difficulty, consistency, and family-list tests for the normalized scenario engine. | Same seed plus template returns the same scenario and different seeds vary | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| ENV 01 | E06 | Person A | Create `ReplicaLabEnv` class skeleton | `replicalab/env/replicalab_env.py`, `replicalab/env/__init__.py` | 2026-03-08 | Added a real `ReplicaLabEnv` module as a drop-in replacement for the former in-server stub, ported the working stub behavior into the environment package, wired scenario-pack-backed reset or step or state or close methods with follow-on `TODO(ENV XX)` markers, and removed the old stub-only marker from `StepInfo` payloads. | Environment class imports and instantiates without runtime errors | Yes - verified with a direct `ReplicaLabEnv.reset(...) -> step(...) -> state() -> close()` smoke run and `python -m pytest` (`111 passed`) |
| JDG 01 | E05 | Person A | Implement rigor or objective-validity score | `replicalab/scoring/rigor.py`, `replicalab/utils/text.py`, `tests/test_reward.py` | 2026-03-08 | Added `score_rigor(protocol, scenario)` with weighted sub-scores for structural completeness (0.30), success criteria coverage (0.40), and required element coverage (0.30). Uses shared `element_tokens` from `replicalab/utils/text.py`. Five focused tests in `test_reward.py` cover quality ordering, determinism, controls impact, rationale length, and all-domain range validation. | Score is between 0 and 1, matches rubric examples, and rewards correct evidence-backed planning | Yes - verified with `python -m pytest tests/test_reward.py` (18 tests pass) |
| JDG 02 | E05 | Person A | Implement feasibility score | `replicalab/scoring/feasibility.py`, `tests/test_reward.py` | 2026-03-08 | Added `score_feasibility(protocol, scenario, check=None)` that derives a continuous [0,1] signal from `FeasibilityCheckResult` (AGT 05). Seven dimensions weighted equally (1/7) with partial credit for budget, equipment, reagents, and staff. Accepts optional pre-computed check to avoid redundant work. Six focused tests cover viable protocol, infeasible ordering, pre-computed check equivalence, determinism, partial credit, and all-domain range. | Score is between 0 and 1 and matches normalized constraint logic | Yes - verified with `python -m pytest tests/test_reward.py` (18 tests pass) |
| JDG 03 | E05 | Person A | Implement fidelity score | `replicalab/scoring/fidelity.py`, `tests/test_reward.py` | 2026-03-08 | Added `score_fidelity(protocol, scenario)` with substitution-aware scoring: required element coverage (0.50, direct match=1.0, substitution=0.7), flexible element alignment (0.20, bonus only), target metric alignment (0.20), and technique appropriateness (0.10). Five focused tests cover aligned vs misaligned ordering, determinism, substitution partial credit, target metric impact, and all-domain range. | Score is between 0 and 1 and matches rubric examples for plan and evidence alignment | Yes - verified with `python -m pytest tests/test_reward.py` (18 tests pass) |
| JDG 04 | E05 | Person A | Implement total reward formula | `replicalab/scoring/rubric.py`, `tests/test_reward.py` | 2026-03-07 | `compute_total_reward(breakdown)` implements `10 × rigor × feasibility × fidelity + bonuses − penalties` with `max(0.0, ...)` floor clamp. Eight new tests in `test_reward.py` verify perfect-vs-broken ordering, zero-feasibility behavior, efficiency bonus ordering, exact penalty subtraction, zero-clamp floor, determinism, external penalties injection, and default-empty penalties. Seven existing rubric tests in `test_env.py` also cover the formula. | Total reward formula matches agreed math, clamps at zero, and returns consistent output for plan quality and bounded tool behavior | Yes - verified with `python -m pytest tests/test_reward.py` (26 tests pass) and `python -m pytest tests/test_env.py` (36 tests pass) |
| JDG 05 | E05 | Person A | Build reward breakdown object | `replicalab/scoring/rubric.py`, `replicalab/scoring/__init__.py`, `tests/test_reward.py` | 2026-03-07 | `build_reward_breakdown(...)` accepts an optional `penalties: dict[str, float]` parameter for named penalty keys (e.g. `invalid_tool_use`, `unsupported_claim`) from bounded-tool diagnostics without reopening the model contract. Returns a typed `RewardBreakdown` with rigor, feasibility, fidelity, efficiency_bonus, communication_bonus, and penalties dict. Exported through `replicalab.scoring`. | Breakdown includes rigor, feasibility, fidelity, bonuses, penalties, and bounded tool diagnostics extension point | Yes - verified with `python -m pytest tests/test_reward.py` (26 tests pass) and `python -m pytest tests/test_env.py` (36 tests pass) |
| ENV 02 | E06 | Person A | Implement real reset wiring | `replicalab/env/replicalab_env.py` | 2026-03-08 | `_make_observation()` now uses the scenario pack as source of truth for booked/out-of-stock/safety data instead of empty placeholders. Eight reset tests verify both roles populated, booked/out-of-stock preserved, all templates and difficulties. | Reset returns initial observations with full scenario data | Yes - verified with `python -m pytest tests/test_env.py` (32 tests pass) |
| ENV 03 | E06 | Person A | Implement Scientist turn with validation | `replicalab/env/replicalab_env.py` | 2026-03-08 | Added `_validate_scientist_action()` that runs `validate_protocol()` on proposals and returns structured error strings without crashing the env. Invalid actions don't advance the round. | Valid action updates state, invalid action returns structured error | Yes - verified with `python -m pytest tests/test_env.py` (32 tests pass) |
| ENV 04 | E06 | Person A | Implement Lab Manager response step | `replicalab/env/replicalab_env.py` | 2026-03-08 | `_lab_manager_action()` uses the full grounded pipeline: `check_feasibility()` → `suggest_alternative()` → `compose_lab_manager_response()`. | Lab Manager response is grounded in feasibility check results | Yes - verified with `python -m pytest tests/test_env.py` (32 tests pass) |
| ENV 05 | E06 | Person A | Centralize termination logic | `replicalab/env/replicalab_env.py` | 2026-03-08 | Added `_check_termination()`: Scientist accept with existing protocol OR max_rounds. Lab Manager accept does NOT auto-terminate. | Episode terminates on agreement or round limit | Yes - verified with `python -m pytest tests/test_env.py` (32 tests pass) |
| ENV 06 | E06 | Person A | Wire real judge scoring | `replicalab/env/replicalab_env.py`, `tests/test_env.py` | 2026-03-07 | Terminal accept steps call `build_reward_breakdown()` and `compute_total_reward()` with real rigor/feasibility/fidelity scores stored in `EpisodeState`. Terminal-without-agreement path now distinguishes `timeout` (max rounds) from `no_agreement` verdict. Four new tests in `TestEnvReward` verify agreement-terminal breakdown/notes/verdict, no-agreement determinism, timeout verdict, and state-stored component scores. | Final step returns total reward, breakdown info, and deterministic penalties or bonuses; verdict distinguishes timeout from no_agreement | Yes - verified with `python -m pytest tests/test_env.py` (36 tests pass) and `python -m pytest` (178 tests pass) |
| ENV 07 | E06 | Person A | Implement state() deep snapshot | `replicalab/env/replicalab_env.py` | 2026-03-08 | `state()` now returns `self._state.model_copy(deep=True)` so callers get an independent snapshot. Two tests verify mutation isolation. | State snapshot is independent of env internals | Yes - verified with `python -m pytest tests/test_env.py` (32 tests pass) |
| ENV 08 | E06 | Person A | Implement close() with lifecycle guard | `replicalab/env/replicalab_env.py` | 2026-03-08 | Added `_closed` flag, idempotent `close()`, `_ensure_open()` guard on `step()`, and `reset()` reopens a closed env. Three tests verify idempotency, step-after-close raises, and reset-reopens. | Close frees resources and does not throw; step after close raises | Yes - verified with `python -m pytest tests/test_env.py` (32 tests pass) |
| TST 01 | E11 | Person A | Add reset returns valid observations test | `tests/test_env.py` | 2026-03-08 | Eight tests in `TestReset` class covering both roles populated, scientist fields, lab manager fields, booked/out-of-stock preservation, state round zero, episode ID, clearing previous episode, and all templates/difficulties. | Test confirms both roles receive valid structured observations | Yes - verified with `python -m pytest tests/test_env.py` (32 tests pass) |
| TST 02 | E11 | Person A | Add valid action step test | `tests/test_env.py` | 2026-03-08 | Eight tests in `TestStep` class covering round advancement, observation shape, conversation history, accept termination, real reward scores, max round termination, step info fields, and full propose-then-accept episode. | Valid action advances round and returns correct shape | Yes - verified with `python -m pytest tests/test_env.py` (32 tests pass) |
| TST 03 | E11 | Person A | Add invalid action handling test | `tests/test_env.py` | 2026-03-08 | Four tests in `TestInvalidAction` class covering error string on invalid duration, env survival after error, no round advancement on invalid action, and request_info always passes. | Invalid action yields structured error and env survives | Yes - verified with `python -m pytest tests/test_env.py` (32 tests pass) |
| TST 04 | E11 | Person A | Add perfect protocol high reward test | `tests/test_reward.py` | 2026-03-08 | Added reward-regression coverage proving a fully aligned protocol scores higher than a broken baseline and stays ordered consistently across reruns. | Perfect protocol scores higher than baseline and broken protocol | Yes - verified with `python -m pytest tests/test_reward.py` (26 tests pass) |
| TST 05 | E11 | Person A | Add zero dimension or penalty behavior test | `tests/test_reward.py` | 2026-03-08 | Added reward-regression coverage for zero-feasibility collapse, exact penalty subtraction, and zero-floor clamp behavior so timeout and penalty paths lower reward deterministically. | Zero feasibility or timeout lowers reward as expected | Yes - verified with `python -m pytest tests/test_reward.py` (26 tests pass) |
| API 03 | E07 | Person C | Add `POST /step` endpoint | `server/app.py`, `tests/test_server.py` | 2026-03-07 | Fixed `_build_episode_log()` to take the real `StepResult` instead of rebuilding reward data from state with stale stub values. Both REST `/step` and WebSocket step handler now pass the terminal `StepResult` to the updated helper so replay logs use real `reward_breakdown`, `judge_notes`, and `verdict` (including `timeout` vs `no_agreement`). Added five endpoint tests covering reset-then-step happy path, invalid session ID 404, terminal step with real reward breakdown, semantic invalid action returning 200 with `info.error`, and replay with real judge data. | Step endpoint accepts valid action and returns step result | Yes - verified with `python -m pytest tests/test_server.py` (10 tests pass) and `python -m pytest` (183 tests pass) |
| API 06 | E07 | Person C | Add WebSocket session handler with isolated env per connection | `server/app.py`, `tests/test_server.py` | 2026-03-07 | WebSocket handler at `/ws` supports `reset`, `step`, and `ping` message types with per-connection env isolation, idle timeout, and replay storage on terminal episodes. Twelve WebSocket tests cover ping-pong, reset observation, step result, full episode real reward, invalid JSON, missing action field, invalid action payload, unknown message type, session isolation, semantic invalid action returning `step_ok` with `info.error`, timeout verdict proving real-env integration, and terminal episode replay persistence via `GET /replay/{episode_id}`. | WebSocket session handler supports reset, step, ping with isolated env per connection and correct replay storage | Yes - verified with `python -m pytest tests/test_server.py` (22 tests pass) and `python -m pytest` (195 tests pass) |
| TST 07 | E11 | Person C | Add WebSocket session handler tests | `tests/test_server.py` | 2026-03-07 | Twelve focused WebSocket tests covering connectivity, message handling, error paths, session isolation, semantic-vs-transport error distinction, timeout verdict, and replay log persistence with real judge data. Tests verify that structurally valid but semantically invalid actions return `step_ok` with `info.error` (not WS error frames), matching the env contract. | WebSocket tests cover happy path, error handling, session isolation, and real-env integration | Yes - verified with `python -m pytest tests/test_server.py` (22 tests pass) |
| API 02 | E07 | Person C | Add `POST /reset` endpoint | `server/app.py`, `tests/test_server.py` | 2026-03-08 | `/reset` endpoint creates a new env (or closes the prior one when reusing `session_id`), calls `env.reset(...)`, persists env, `last_active`, and `episode_id` in the in-memory REST session store, and returns `session_id`, `episode_id`, `observation`. Seven dedicated tests cover response shape, both-role observation, explicit session_id reuse, prior-env close on reuse, default params, all scenario/difficulty combos, and seed determinism. | Reset endpoint starts a new episode and returns initial observation | Yes - verified with `python -m pytest tests/test_server.py` (29 tests pass) and `python -m pytest` (202 tests pass) |
| API 04 | E07 | Person C | Add `GET /scenarios` endpoint | `server/app.py`, `tests/test_server.py` | 2026-03-08 | `GET /scenarios` returns the `available_scenario_families()` output through the typed `ScenariosResponse` model. Five focused tests cover status code, response shape, all three scenario families, the expected `easy`, `medium`, and `hard` difficulties, and the absence of extra keys. | Endpoint lists available scenario families and difficulties | Yes - verified with `python -m pytest tests/test_server.py -v` (34 tests pass) |
| API 07 | E07 | Person C | Add idle timeout and graceful disconnect cleanup | `server/app.py`, `tests/test_server.py` | 2026-03-08 | Verified the existing WebSocket idle-timeout and disconnect cleanup path with two focused tests: one monkeypatches the idle timeout to 0.5s and confirms the server closes with code 1000 when no message arrives, and one wraps `_make_env()` to confirm `env.close()` is called exactly once from the `finally` block on disconnect. | Stale connections close cleanly and the environment closes without leak | Yes - verified with `python -m pytest tests/test_server.py -v` (34 tests pass) |
| API 13 | E07 | Person C | Add CORS middleware configuration for frontend origins in dev and production | `server/app.py`, `tests/test_server.py` | 2026-03-08 | Confirmed the existing FastAPI CORS middleware allows the local Vite frontend origin plus `https://*.hf.space`, and added three explicit preflight tests covering localhost allowance, HF Space allowance, and disallowed-origin rejection. | Frontend on localhost:5173 and HF Space origin can reach the API without CORS errors | Yes - verified with `python -m pytest tests/test_server.py -v` (34 tests pass) |
| API 08 | E07 | Person C | Build Dockerfile with Python app startup on port 7860 | `server/Dockerfile`, `Dockerfile`, `server/requirements.txt`, `docs/max/deployment.md` | 2026-03-08 | Fixed editable install (`-e .` → `. --no-deps`) in both `server/Dockerfile` and root `Dockerfile`, added `httpx` and `websocket-client` to `server/requirements.txt` (required by `replicalab.client`), rebuilt without cache. Verified Docker container starts with the **real env** (`"env":"real"`), and all four endpoints work: `GET /health`, `GET /scenarios`, `POST /reset`, `POST /step`. Added verified endpoint commands to `docs/max/deployment.md`. | Local Docker run serves app on port 7860 | Yes - verified with `docker build -f server/Dockerfile -t replicalab . && docker run -p 7860:7860 replicalab` and curl against all four endpoints |
| API 09 | E07 | Person C | Add Hugging Face Space metadata and deploy instructions | `README.md`, `Dockerfile`, `docs/max/deployment.md` | 2026-03-08 | Added the Hugging Face Spaces YAML frontmatter to the root README, created the root-level `Dockerfile` required by the Docker SDK, and documented Space creation, git remote setup, push, logs, and secret management in `docs/max/deployment.md`. | Space config is valid for Docker app deployment | Yes - verified against HF Spaces Docker deployment requirements |
| API 15 | E07 | Person C | Create HF Space README.md with YAML frontmatter | `README.md` | 2026-03-08 | Added the required Spaces frontmatter fields (`sdk: docker`, `app_port: 7860`, title, emoji, colors, pinned) to the root README so Hugging Face parses the Space metadata correctly on push. | HF Space config is valid and Space launches correctly from the metadata | Yes - verified against the HF Spaces frontmatter schema |

### Person B (Ayush) - Completed own tasks

| ID | Epic | Task | File/Module | Date | What Was Done | Acceptance Criteria | Verified |
|----|------|------|-------------|------|---------------|--------------------|---------|
| MOD 09 | E02 | Add output parser that maps model text to `ScientistAction` | `replicalab/agents/scientist_policy.py`, `replicalab/agents/__init__.py`, `tests/test_scientist_policy.py` | 2026-03-08 | Added a raw-text parser that extracts JSON from plain output, fenced blocks, or prose-wrapped objects, validates it into `ScientistAction`, and raises explicit `ScientistOutputParseError` values for missing JSON, invalid JSON, or schema failures. | Parser returns structured action or explicit parse error | Yes - verified with `python -m pytest tests/test_scientist_policy.py tests/test_models.py` and a direct `parse_scientist_output(...)` smoke check |
| SCN 11 | E03 | Create hand checked golden scenarios for prompt testing | `tests/fixtures/golden_scenarios.json`, `tests/test_scenarios.py` | 2026-03-08 | Added three deterministic golden scenarios for math, ML, and finance prompt checks plus fixture-validation tests. | Three fixed scenarios are available for deterministic manual testing | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| AGT 01 | E04 | Draft domain-neutral system prompt for Scientist role from normalized scenario data | `replicalab/agents/scientist_policy.py`, `tests/test_scientist_policy.py` | 2026-03-08 | Added `build_scientist_system_prompt(...)` to render role guidance, success criteria, mapped constraints, mapped resources, substitutions, and the strict JSON contract from normalized scenario data. | Prompt clearly explains role, mapped constraints, and JSON output contract | Yes - verified with `python -m pytest tests/test_scientist_policy.py` and a direct prompt-build smoke check |
| AGT 02 | E04 | Build observation to prompt formatting helper from normalized scenario-derived observations | `replicalab/agents/scientist_policy.py`, `replicalab/agents/__init__.py`, `tests/test_scientist_policy.py` | 2026-03-08 | Added `format_scientist_observation(...)` to render round status, paper context, conversation history, current protocol, and the next-action instruction in a fixed deterministic order, and exported it through the agent package. | Formatted prompt includes task info, history, and action schema consistently | Yes - verified with `python -m pytest tests/test_scientist_policy.py` |
| AGT 04 | E04 | Build baseline heuristic Scientist for non trained smoke tests | `replicalab/agents/scientist_policy.py`, `replicalab/agents/__init__.py`, `tests/test_scientist_policy.py` | 2026-03-08 | Added `build_baseline_scientist_action(...)`, a deterministic baseline Scientist policy that proposes a protocol on the first turn, revises only when the latest Lab Manager feedback contains an obvious blocker, and otherwise accepts the current protocol so smoke episodes can finish cleanly. | Baseline can complete episodes without crashing | Yes - verified with `python -m pytest tests/test_scientist_policy.py` including a stub-env episode smoke test |
| AGT 05 | E04 | Implement deterministic feasibility checker over normalized constraints and resources | `replicalab/agents/lab_manager_policy.py`, `replicalab/agents/__init__.py`, `tests/test_lab_manager_policy.py` | 2026-03-08 | Added a deterministic Lab Manager feasibility checker with a typed `FeasibilityCheckResult`, explicit per-dimension protocol, budget, equipment, reagents, schedule, staff, and policy checks, substitution reporting, and stable summary output. | Checker returns clear pass or fail per constraint dimension | Yes - verified with `python -m pytest tests/test_lab_manager_policy.py tests/test_validation.py tests/test_scientist_policy.py` |
| AGT 06 | E04 | Implement alternative suggestion logic from allowed substitutions and resource tradeoffs | `replicalab/agents/lab_manager_policy.py`, `replicalab/agents/__init__.py`, `tests/test_lab_manager_policy.py` | 2026-03-08 | Added deterministic alternative-suggestion logic that applies substitutions, duration clamps, and sample-size reductions in fixed order, re-runs feasibility after the revision, and returns a typed `AlternativeSuggestion` with applied changes, remaining failures, and pre or post feasibility checks. | Lab Manager can suggest at least one sensible revision when the initial plan fails | Yes - verified with `python -m pytest tests/test_lab_manager_policy.py` |
| AGT 07 | E04 | Add grounded Lab Manager response synthesis from feasibility results and suggested revisions | `replicalab/agents/lab_manager_policy.py`, `replicalab/agents/__init__.py`, `server/app.py`, `tests/test_lab_manager_policy.py` | 2026-03-08 | Added `compose_lab_manager_response(...)`, a deterministic outward-action composer that converts feasibility plus alternative-suggestion results into a typed `LabManagerAction` with stable flags, readable explanations, and optional injected explanation rendering, then wired the stub server to log those grounded responses instead of placeholder text. | Output is readable, grounded in checker results, and maps cleanly to underlying checks | Yes - verified with `python -m pytest tests/test_lab_manager_policy.py` and a stub-env step smoke check |
| AGT 11 | E04 | Select and document base model for Scientist training | `docs/agt11_scientist_model_selection.md`, `README.md` | 2026-03-08 | Recorded `Qwen3-4B` as the primary Scientist training model with `Qwen3-8B` as the H100-only stretch fallback, and surfaced the decision in the README so the training path uses one canonical model choice. | Decision is recorded and all team members know which model will be fine tuned | Yes - verified by the decision record and README update |
| AGT 03 | E04 | Add parse plus retry strategy for malformed model output | `replicalab/agents/scientist_policy.py`, `tests/test_scientist_policy.py` | 2026-03-07 | Added `call_scientist_with_retry(...)` with error-specific correction prompts, bounded retry loop, and exposed `RetryMetadata` telemetry. Seven focused tests cover first-try success, malformed-then-valid, invalid-then-valid, exhaustion, correction message content, and metadata serialization. | Malformed output triggers at least one controlled retry or explicit failure | Yes - verified with `python -m pytest tests/test_scientist_policy.py` (7 retry tests pass) |
| AGT 08 | E04 | Add prompt formatting, parse, and bounded-tool policy tests for Scientist policy | `replicalab/agents/scientist_policy.py`, `tests/test_scientist_policy.py` | 2026-03-07 | Added bounded-tool policy block to `build_scientist_system_prompt(...)` naming `search_evidence`, `run_code_check`, and `inspect_image` with explicit rules. Added 24 new tests covering parser happy paths (propose, accept, prose-wrapped), parser edge cases (empty, whitespace, list, extra keys, `to_dict()`), system prompt across all 3 domains plus dict coercion, bounded-tool policy assertions across all domains, role-boundary and output-contract assertions, formatter edge cases (final round, empty-list protocol), and baseline domain inference and forced-accept behavior. | Tests cover happy path, malformed output handling, and stable tool-policy reminders | Yes - verified with `python -m pytest tests/test_scientist_policy.py` (46 tests pass) and `python -m pytest tests/` (111 tests pass) |
| TRN 13 | E08 | Create reusable environment client module | `replicalab/client.py`, `tests/test_client.py` | 2026-03-08 | Added `ReplicaLabClient` with dual transport support (REST via `httpx`, WebSocket via `websocket-client`), unified sync interface (`connect`, `reset`, `step`, `state`, `close`), context manager support, internal session ID tracking, typed returns mapped to Pydantic models, and constructor-level transport selection. Twenty-four tests cover both transports: connect, reset, step, full episode, replay, context manager, error paths, semantic invalid action handling, and constructor validation. | Client module can be imported by notebook and other consumers without duplicating connection logic | Yes - verified with `python -m pytest tests/test_client.py` (24 tests pass) and `python -m pytest` (231 tests pass) |

### Kush (Person D) - Completed on behalf of others

| ID | Epic | Assigned To | Task | File/Module | Date | What Was Done | Acceptance Criteria | Verified |
|----|------|------------|------|-------------|------|---------------|--------------------|---------|
| FND 03 | E01 | Max (Person C) | Initialize React plus Vite frontend shell | `frontend/package.json`, `frontend/src/`, `frontend/public/` | 2026-03-08 | Imported the full React plus Vite frontend tree from Kush's branch onto `ayush`, including the app shell, pages, component library, assets, and TypeScript config. | `npm install` and dev server run successfully | Yes - verified with `npm --prefix frontend install` and `npm --prefix frontend run build` |
| FND 12 | E01 | Max (Person C) | Create Vite config with API and WebSocket proxy support plus stable build output settings | `frontend/vite.config.ts` | 2026-03-08 | Imported Kush's Vite configuration with `@` alias plus `/api` and `/ws` proxy rules, then verified the frontend builds successfully against that config on `ayush`. | Frontend dev server can reach backend without manual URL edits and build output is predictable for Docker packaging | Yes - verified with `npm --prefix frontend run build` |

### Shared Tasks - Completed

| ID | Epic | Owners | Task | Status |
|----|------|--------|------|--------|
| FND 08 | E01 | Person A and B | Freeze JSON contract for actions and observations | Completed |

### Max (Person C) - Completed own task

| ID | Epic | Task | Status |
|----|------|------|--------|
| FND 11 | E01 | Create `server/requirements.txt` pinning runtime dependencies | Completed |

### Kush (Person D) - No tasks completed yet

| ID | Epic | Task | Status |
|----|------|------|--------|
| - | - | No tasks completed | 0 of 32 assigned |

---

## What Completing These Tasks Unblocked

| Completed Task | Directly Unblocked |
|---------------|-------------------|
| FND 01 | FND 02, FND 03, FND 04, FND 05, FND 06, FND 07, FND 10 |
| FND 02 | FND 11 |
| FND 03 | FND 12, FND 13, UI 01 |
| FND 04 | FND 08, FND 09 |
| FND 05 | No downstream dependencies |
| FND 06 | DOC 01 |
| FND 07 | No downstream dependencies |
| FND 08 | MOD 01, MOD 02, MOD 03, MOD 12, SCN 01 |
| FND 09 | OpenEnv registration layer is now present for later `/web` and deployment work |
| FND 10 | No downstream dependencies |
| FND 11 | No new formal dependencies, but server scaffold work can now install from a standalone requirements file |
| FND 12 | Frontend dev proxying is now configured for local API and WebSocket work |
| MOD 01 | MOD 05, MOD 09 |
| MOD 02 | No new formal dependencies, but the Lab Manager contract is now stable for later policy work |
| MOD 03 | MOD 04, MOD 11 |
| MOD 04 | MOD 07, ENV 01 |
| MOD 05 | MOD 06, AGT 05 |
| MOD 11 | No new formal dependency edge by itself, but `StepResult` metadata is now stable for environment, API, replay, and training consumers |
| MOD 12 | Shared defaults now come from `replicalab/config.py`, reducing config drift before environment and scoring work expands |
| SCN 01 | SCN 09 now has a deterministic seed utility to build on |
| SCN 02 | SCN 03, SCN 04, SCN 05, SCN 07 |
| SCN 03 | SCN 06, SCN 08 |
| SCN 04 | SCN 06, SCN 08 |
| SCN 05 | SCN 06, SCN 08 |
| SCN 06 | Harder scenario variants and curriculum-ready difficulty scaling now exist |
| SCN 07 | `AGT 05` is complete; `AGT 06`, `AGT 07`, `JDG 02`, and `SCN 13` are now unblocked from the normalized resource layer |
| SCN 08 | `AGT 06` is now unblocked; `JDG 01` and `JDG 03` are also unblocked |
| SCN 09 | SCN 10, SCN 11, ENV 01, ENV 02 |
| SCN 10 | Scenario determinism and consistency now have regression coverage |
| SCN 11 | AGT 01, TRN 08 |
| MOD 09 | Together with completed `AGT 02`, `AGT 03` is now unblocked |
| AGT 01 | AGT 02, AGT 11, TRN 04 |
| AGT 02 | AGT 03, AGT 04 |
| AGT 04 | Removes the last baseline-policy blocker; `AGT 08` now only waits on `AGT 03` |
| AGT 05 | AGT 06, AGT 07, JDG 02 |
| AGT 06 | No new formal dependency edge by itself, but `AGT 07` now has deterministic revision content to narrate and compare against |
| AGT 07 | `AGT 10` now only waits on `JDG 06`, and the stub server now emits grounded Lab Manager responses instead of placeholder review text |
| AGT 11 | No new formal dependency edge by itself, but the Scientist training model choice is now fixed across repo docs |
| ENV 01 | ENV 02, ENV 08, and the real-environment import path that partial server tasks now depend on |
| JDG 01 | Together with JDG 02 and JDG 03, unblocks JDG 04 (total reward formula) |
| JDG 02 | Together with JDG 01 and JDG 03, unblocks JDG 04 (total reward formula) |
| JDG 03 | Together with JDG 01 and JDG 02, unblocks JDG 04 (total reward formula) |
| JDG 04 | JDG 05, JDG 08, TST 04, TST 05 |
| JDG 05 | JDG 06, JDG 07, JDG 09, JDG 10, JDG 11, ENV 06 |
| ENV 02 | ENV 03, ENV 07, ENV 10, TST 01, API 02 (partial → full) |
| ENV 03 | ENV 04, ENV 05, TST 02, TST 03 |
| ENV 04 | ENV 05, TST 02 |
| ENV 05 | ENV 06, TST 02 |
| ENV 06 | ENV 07, ENV 09, ENV 11, API 03 (partial → full), API 06 (partial → full), OBS 07 |
| API 06 | TRN 03, TRN 13 |
| API 09 | API 10, API 17 |
| TST 07 | No new dependencies |
| ENV 07 | ENV 10 (partial unblock) |
| ENV 08 | API 07 (partial → full) |
| TST 01 | No new dependencies |
| TST 02 | No new dependencies |
| TST 03 | No new dependencies |
| API 02 | API 14 (partial → closer to full), UI 06 |
| TRN 13 | TRN 03 now has both its dependencies met (API 06 + TRN 13) |
| API 08 | API 09, API 16, API 19 |

### Current Unblocked and Active Tasks

| ID | Owner | Task | Unblocked By |
|----|-------|------|-------------|
| FND 13 | Kush (Person D) | Install and configure Tailwind plus shadcn base setup, theme tokens, and global styles | FND 03 |
| UI 01 | Kush (Person D) | Create application shell with three panel layout | FND 03 |
| AGT 09 | Kian (Person A) | Add deterministic feasibility checker tests for Lab Manager grounding | AGT 05 to AGT 07 |
| MOD 06 | Kian (Person A) | Add semantic validators for impossible plans such as zero sample size with positive controls | MOD 05 |
| MOD 07 | Max (Person C) | Add state serialization helper for replay logs | MOD 04 |
| SCN 13 | Kian (Person A) | Implement shared booking and scheduling data model for GPUs, rooms, or equipment with time slot conflicts and duration | SCN 07 |
| DOC 01 | Kush (Person D) | Write hook, problem statement, and one line product summary | FND 06 |
| JDG 06 | Kian (Person A) | Add optional plain English explanation function from reward breakdown | JDG 05 |
| JDG 08 | Kian (Person A) | Add score determinism tests and edge case tests | JDG 01 to JDG 05 |
| ENV 10 | Kian (Person A) | Add reset, step, invalid action, timeout, and deterministic replay tests | ENV 02 to ENV 09 |
| JDG 09 | Kush (Person D) | Create mock score cards and language for frontend | JDG 05 |
| API 10 | Max (Person C) | Deploy live Space and verify health, reset, and step | API 09 |
| API 17 | Max (Person C) | Document secrets and API key management for hosted deployment and Colab | API 09 |
| TRN 03 | Person B (Ayush) | Implement env client wrapper for training rollouts | API 06, TRN 13 |

Note: Person B (Ayush) has `TRN 03` as the next unblocked task (`TRN 13` is now complete). `AGT 10` still waits on `JDG 06` (Person A). The remaining TRN chain waits on `API 10` (Person C) and judge tasks (Person A).

---

## Epic Progress

| Epic | Total Tasks | Completed | Rate |
|------|------------|-----------|------|
| E01. Foundations and repository setup | 13 | 12 | 92.31% |
| E02. Domain models, validation, state contracts | 12 | 8 | 66.67% |
| E03. Scenario engine and constraint generation | 13 | 11 | 84.62% |
| E04. Scientist agent and Lab Manager policy | 11 | 9 | 81.82% |
| E05. Judge engine and reward logic | 11 | 5 | 45.45% |
| E06. OpenEnv environment implementation | 11 | 8 | 72.73% |
| E07. API, server, Docker, deployment | 19 | 9 | 47.37% |
| E08. RL training pipeline and evaluation | 15 | 1 | 6.67% |
| E09. Frontend, UX, replay, demo views | 15 | 0 | 0% |
| E10. Logging, replay, and observability | 9 | 0 | 0% |
| E11. Testing and quality gates | 12 | 6 | 50.00% |
| E12. README, demo video, submission packaging | 11 | 0 | 0% |
