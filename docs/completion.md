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
| Completed | 38 |
| Partial / active | 10 |
| Remaining | 104 |
| **Completion rate** | **25.00%** |

### Completion by Person

| Person | Assigned | Completed (own) | Completed (by others) | Remaining | Rate |
|--------|----------|----------------|----------------------|-----------|------|
| Kian (Person A) | 49 (47 solo + 2 shared with B) | 1 shared sign-off (`FND 08`) | 20 (`FND 04`, `FND 09`, `MOD 01`, `MOD 02`, `MOD 03`, `MOD 04`, `MOD 05`, `MOD 11`, `MOD 12`, `SCN 01` to `SCN 10`, `AGT 05` done by Person B) | 28 | 42.86% |
| Person B (Ayush) | 29 (27 solo + 2 shared with A) | 10 (`FND 08`, `MOD 09`, `SCN 11`, `AGT 01`, `AGT 02`, `AGT 04`, `AGT 05`, `AGT 06`, `AGT 07`, `AGT 11`) | 0 | 19 | 34.48% |
| Max (Person C) | 41 | 1 (`FND 11`) | 7 (`FND 01`, `FND 02`, `FND 03`, `FND 05`, `FND 07`, `FND 10`, `FND 12` done by others) | 33 | 19.51% |
| Kush (Person D) | 32 | 0 | 1 (`FND 06` done by Person B) | 31 | 3.13% |
| All (shared) | 3 | 2 (`FND 08`, `AGT 05`) | 0 | 1 | 66.67% |

Note: Person B (Ayush) has completed two shared tasks in their own lane
(`FND 08`, `AGT 05`) plus eight solo tasks in their own lane (`MOD 09`,
`SCN 11`, `AGT 01`, `AGT 02`, `AGT 04`, `AGT 06`, `AGT 07`, `AGT 11`), and has also executed twenty-five tasks outside their assigned
ownership (`FND 01`, `FND 02`, `FND 04`, `FND 05`, `FND 06`, `FND 07`,
`FND 09`, `FND 10`, `MOD 01`, `MOD 02`, `MOD 03`, `MOD 04`, `MOD 05`,
`MOD 11`, `MOD 12`, `SCN 01` to `SCN 10`) to keep the Kian, Max, and Kush
dependency chain moving. Ayush now has one fully unblocked implementation
task available: `AGT 03`, with `AGT 10` reduced to a single remaining
external dependency on `JDG 06`.

---

## Active Partial Tasks

| ID | Assigned To | Current Status | Remaining Acceptance Item |
|----|-------------|----------------|---------------------------|
| API 01 | Max (Person C) | FastAPI app shell and `/health` endpoint work locally against the stub env | Real env dependency and task-owner sign-off |
| API 02 | Max (Person C) | `/reset` works locally against the stub env and now seeds normalized math / ML / finance scenarios through the shared generator | Real env reset dependency and task-owner sign-off |
| API 03 | Max (Person C) | `/step` works locally against the stub env | Real env step dependency and task-owner sign-off |
| API 04 | Max (Person C) | `/scenarios` returns the normalized scenario-family list from the shared generator | Real env exposure and task-owner sign-off |
| API 06 | Max (Person C) | WebSocket reset, ping, and step work locally against the stub env, including normalized scenario-family resets | Real env integration and task-owner sign-off |
| API 07 | Max (Person C) | Idle timeout and cleanup logic exist in the WebSocket path | Real env disconnect cleanup verification |
| API 08 | Max (Person C) | `server/Dockerfile` exists | Local Docker build and run verification |
| API 13 | Max (Person C) | CORS middleware exists for dev and hosted origins | Frontend integration verification |
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

### Person B (Ayush) - Completed own tasks

| ID | Epic | Task | File/Module | Date | What Was Done | Acceptance Criteria | Verified |
|----|------|------|-------------|------|---------------|--------------------|---------|
| MOD 09 | E02 | Add output parser that maps model text to `ScientistAction` | `replicalab/agents/scientist_policy.py`, `replicalab/agents/__init__.py`, `tests/test_scientist_policy.py` | 2026-03-08 | Added a raw-text parser that extracts JSON from plain output, fenced blocks, or prose-wrapped objects, validates it into `ScientistAction`, and raises explicit `ScientistOutputParseError` values for missing JSON, invalid JSON, or schema failures. | Parser returns structured action or explicit parse error | Yes - verified with `python -m pytest tests/test_scientist_policy.py tests/test_models.py` and a direct `parse_scientist_output(...)` smoke check |
| SCN 11 | E03 | Create hand checked golden scenarios for prompt testing | `tests/fixtures/golden_scenarios.json`, `tests/test_scenarios.py` | 2026-03-08 | Added three deterministic golden scenarios for math, ML, and finance prompt checks plus fixture-validation tests. | Three fixed scenarios are available for deterministic manual testing | Yes - verified with `python -m pytest tests/test_scenarios.py` |
| AGT 01 | E04 | Draft domain-neutral system prompt for Scientist role from normalized scenario data | `replicalab/agents/scientist_policy.py`, `tests/test_scientist_policy.py` | 2026-03-08 | Added `build_scientist_system_prompt(...)` to render role guidance, success criteria, mapped constraints, mapped resources, substitutions, and the strict JSON contract from normalized scenario data. | Prompt clearly explains role, mapped constraints, and JSON output contract | Yes - verified with `python -m pytest tests/test_scientist_policy.py` and a direct prompt-build smoke check |
| AGT 02 | E04 | Build observation to prompt formatting helper from normalized scenario-derived observations | `replicalab/agents/scientist_policy.py`, `replicalab/agents/__init__.py`, `tests/test_scientist_policy.py` | 2026-03-08 | Added `format_scientist_observation(...)` to render round status, paper context, conversation history, current protocol, and the next-action instruction in a fixed deterministic order, and exported it through the agent package. | Formatted prompt includes task info, history, and action schema consistently | Yes - verified with `python -m pytest tests/test_scientist_policy.py` |
| AGT 04 | E04 | Build baseline heuristic Scientist for non trained smoke tests | `replicalab/agents/scientist_policy.py`, `replicalab/agents/__init__.py`, `tests/test_scientist_policy.py` | 2026-03-08 | Added `build_baseline_scientist_action(...)`, a deterministic non-LLM Scientist policy that proposes a protocol on the first turn, revises only when the latest Lab Manager feedback contains an obvious blocker, and otherwise accepts the current protocol so smoke episodes can finish cleanly. | Baseline can complete episodes without crashing | Yes - verified with `python -m pytest tests/test_scientist_policy.py` including a stub-env episode smoke test |
| AGT 05 | E04 | Implement deterministic feasibility checker over normalized constraints and resources | `replicalab/agents/lab_manager_policy.py`, `replicalab/agents/__init__.py`, `tests/test_lab_manager_policy.py` | 2026-03-08 | Added a deterministic Lab Manager feasibility checker with a typed `FeasibilityCheckResult`, explicit per-dimension protocol, budget, equipment, reagents, schedule, staff, and policy checks, substitution reporting, and stable summary output. | Checker returns clear pass or fail per constraint dimension | Yes - verified with `python -m pytest tests/test_lab_manager_policy.py tests/test_validation.py tests/test_scientist_policy.py` |
| AGT 06 | E04 | Implement alternative suggestion logic from allowed substitutions and resource tradeoffs | `replicalab/agents/lab_manager_policy.py`, `replicalab/agents/__init__.py`, `tests/test_lab_manager_policy.py` | 2026-03-08 | Added deterministic alternative-suggestion logic that applies substitutions, duration clamps, and sample-size reductions in fixed order, re-runs feasibility after the revision, and returns a typed `AlternativeSuggestion` with applied changes, remaining failures, and pre or post feasibility checks. | Lab Manager can suggest at least one sensible revision when the initial plan fails | Yes - verified with `python -m pytest tests/test_lab_manager_policy.py` |
| AGT 07 | E04 | Add grounded Lab Manager response synthesis from feasibility results and suggested revisions | `replicalab/agents/lab_manager_policy.py`, `replicalab/agents/__init__.py`, `server/app.py`, `tests/test_lab_manager_policy.py` | 2026-03-08 | Added `compose_lab_manager_response(...)`, a deterministic outward-action composer that converts feasibility plus alternative-suggestion results into a typed `LabManagerAction` with stable flags, readable explanations, and optional injected explanation rendering, then wired the stub server to log those grounded responses instead of placeholder text. | Output is readable, grounded in checker results, and maps cleanly to underlying checks | Yes - verified with `python -m pytest tests/test_lab_manager_policy.py` and a stub-env step smoke check |
| AGT 11 | E04 | Select and document base model for Scientist training | `docs/agt11_scientist_model_selection.md`, `README.md` | 2026-03-08 | Recorded `Qwen3-4B` as the primary Scientist training model with `Qwen3-8B` as the H100-only stretch fallback, and surfaced the decision in the README so the training path uses one canonical model choice. | Decision is recorded and all team members know which model will be fine tuned | Yes - verified by the decision record and README update |

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

### Current Unblocked and Active Tasks

| ID | Owner | Task | Unblocked By |
|----|-------|------|-------------|
| FND 13 | Kush (Person D) | Install and configure Tailwind plus shadcn base setup, theme tokens, and global styles | FND 03 |
| UI 01 | Kush (Person D) | Create application shell with three panel layout | FND 03 |
| AGT 03 | Person B (Ayush) | Add parse plus retry strategy for malformed model output | MOD 09, AGT 02 |
| MOD 06 | Kian (Person A) | Add semantic validators for impossible plans such as zero sample size with positive controls | MOD 05 |
| MOD 07 | Max (Person C) | Add state serialization helper for replay logs | MOD 04 |
| JDG 01 | Kian (Person A) | Implement rigor or objective-validity score for plan completeness, required checks, method quality, and justification | SCN 08 |
| JDG 02 | Kian (Person A) | Implement feasibility score for budget, resources, time, staffing, compute, and bookings | SCN 07, AGT 05 |
| JDG 03 | Kian (Person A) | Implement fidelity score against hidden reference spec, required steps, and allowed substitutions | SCN 08 |
| SCN 13 | Kian (Person A) | Implement shared booking and scheduling data model for GPUs, rooms, or equipment with time slot conflicts and duration | SCN 07 |
| ENV 01 | Kian (Person A) | Create `ReplicaLabEnv` class skeleton | MOD 04, SCN 09 |
| DOC 01 | Kush (Person D) | Write hook, problem statement, and one line product summary | FND 06 |

---

## Epic Progress

| Epic | Total Tasks | Completed | Rate |
|------|------------|-----------|------|
| E01. Foundations and repository setup | 13 | 12 | 92.31% |
| E02. Domain models, validation, state contracts | 12 | 8 | 66.67% |
| E03. Scenario engine and constraint generation | 13 | 11 | 84.62% |
| E04. Scientist agent and Lab Manager policy | 11 | 7 | 63.64% |
| E05. Judge engine and reward logic | 11 | 0 | 0% |
| E06. OpenEnv environment implementation | 11 | 0 | 0% |
| E07. API, server, Docker, deployment | 19 | 0 | 0% |
| E08. RL training pipeline and evaluation | 15 | 0 | 0% |
| E09. Frontend, UX, replay, demo views | 15 | 0 | 0% |
| E10. Logging, replay, and observability | 9 | 0 | 0% |
| E11. Testing and quality gates | 12 | 0 | 0% |
| E12. README, demo video, submission packaging | 11 | 0 | 0% |
