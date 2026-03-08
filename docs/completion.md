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
| Completed | 13 |
| Partial / active | 10 |
| Remaining | 139 |
| **Completion rate** | **8.55%** |

### Completion by Person

| Person | Assigned | Completed (own) | Completed (by others) | Remaining | Rate |
|--------|----------|----------------|----------------------|-----------|------|
| Kian (Person A) | 49 (47 solo + 2 shared with B) | 1 shared sign-off (`FND 08`) | 5 (`FND 04`, `FND 09`, `MOD 01`, `MOD 02`, `MOD 03` done by Person B) | 43 | 12.24% |
| Person B (Ayush) | 29 (27 solo + 2 shared with A) | 1 shared task (`FND 08`) | 0 | 28 | 3.45% |
| Max (Person C) | 41 | 1 (`FND 11`) | 5 (`FND 01`, `FND 02`, `FND 05`, `FND 07`, `FND 10` done by Person B) | 35 | 14.63% |
| Kush (Person D) | 32 | 0 | 1 (`FND 06` done by Person B) | 31 | 3.13% |
| All (shared) | 3 | 1 (`FND 08`) | 0 | 2 | 33.33% |

Note: Person B (Ayush) has completed one shared task in their own lane
(`FND 08`) and has also executed eleven tasks outside their assigned ownership
(`FND 01`, `FND 02`, `FND 04`, `FND 05`, `FND 06`, `FND 07`, `FND 09`,
`FND 10`, `MOD 01`, `MOD 02`, `MOD 03`) to keep the Kian, Max, and Kush
dependency chain moving. The Ayush lane still has one direct implementation
task ready now: `MOD 09`.

---

## Active Partial Tasks

| ID | Assigned To | Current Status | Remaining Acceptance Item |
|----|-------------|----------------|---------------------------|
| API 01 | Max (Person C) | FastAPI app shell and `/health` endpoint work locally against the stub env | Real env dependency and task-owner sign-off |
| API 02 | Max (Person C) | `/reset` works locally against the stub env | Real env reset dependency and task-owner sign-off |
| API 03 | Max (Person C) | `/step` works locally against the stub env | Real env step dependency and task-owner sign-off |
| API 04 | Max (Person C) | `/scenarios` exists with a stub-backed scenario list | Real scenario source and task-owner sign-off |
| API 06 | Max (Person C) | WebSocket reset, ping, and step work locally against the stub env | Real env integration and task-owner sign-off |
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
| FND 04 | FND 08, FND 09 |
| FND 05 | No downstream dependencies |
| FND 06 | DOC 01 |
| FND 07 | No downstream dependencies |
| FND 08 | MOD 01, MOD 02, MOD 03, MOD 12, SCN 01 |
| FND 09 | OpenEnv registration layer is now present for later `/web` and deployment work |
| FND 10 | No downstream dependencies |
| FND 11 | No new formal dependencies, but server scaffold work can now install from a standalone requirements file |
| MOD 01 | MOD 05, MOD 09 |
| MOD 02 | No new formal dependencies, but the Lab Manager contract is now stable for later policy work |
| MOD 03 | MOD 04, MOD 11 |

### Current Unblocked and Active Tasks

| ID | Owner | Task | Unblocked By |
|----|-------|------|-------------|
| FND 03 | Max (Person C) | Initialize React plus Vite frontend shell | FND 01 |
| MOD 04 | Kian (Person A) | Implement `EpisodeState` and `EpisodeLog` models | MOD 03 |
| MOD 05 | Kian (Person A) | Add protocol validation for sample size, controls, duration, equipment vocab, and reagent vocab | MOD 01 |
| MOD 09 | Person B (Ayush) | Add output parser that maps model text to `ScientistAction` | MOD 01 |
| MOD 11 | Kian (Person A) | Implement `StepResult` model | MOD 03 |
| MOD 12 | Kian (Person A) | Create shared environment configuration module | FND 08 |
| SCN 01 | Kian (Person A) | Implement deterministic RNG helper | FND 08 |
| DOC 01 | Kush (Person D) | Write hook, problem statement, and one line product summary | FND 06 |

---

## Epic Progress

| Epic | Total Tasks | Completed | Rate |
|------|------------|-----------|------|
| E01. Foundations and repository setup | 13 | 10 | 76.92% |
| E02. Domain models, validation, state contracts | 12 | 3 | 25.00% |
| E03. Scenario engine and constraint generation | 13 | 0 | 0% |
| E04. Scientist agent and Lab Manager policy | 11 | 0 | 0% |
| E05. Judge engine and reward logic | 11 | 0 | 0% |
| E06. OpenEnv environment implementation | 11 | 0 | 0% |
| E07. API, server, Docker, deployment | 19 | 0 | 0% |
| E08. RL training pipeline and evaluation | 15 | 0 | 0% |
| E09. Frontend, UX, replay, demo views | 15 | 0 | 0% |
| E10. Logging, replay, and observability | 9 | 0 | 0% |
| E11. Testing and quality gates | 12 | 0 | 0% |
| E12. README, demo video, submission packaging | 11 | 0 | 0% |
