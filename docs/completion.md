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
| Completed | 8 |
| Partial / active | 11 |
| Remaining | 144 |
| **Completion rate** | **5.26%** |

### Completion by Person

| Person | Assigned | Completed (own) | Completed (by others) | Remaining | Rate |
|--------|----------|----------------|----------------------|-----------|------|
| Kian (Person A) | 49 (47 solo + 2 shared with B) | 0 | 1 (FND 04 done by Person B) | 48 | 2.04% |
| Person B (Ayush) | 29 (27 solo + 2 shared with A) | 0 own-assigned | 0 | 29 | 0% |
| Max (Person C) | 41 | 1 (FND 11) | 5 (FND 01, FND 02, FND 05, FND 07, FND 10 done by Person B) | 35 | 14.63% |
| Kush (Person D) | 32 | 0 | 1 (FND 06 done by Person B) | 31 | 3.13% |
| All (shared) | 3 | 0 | 0 | 3 | 0% |

Note: Person B (Ayush) completed 7 tasks total, but all were assigned to other
people (FND 01, FND 02, FND 05, FND 07, and FND 10 assigned to Person C; FND 04
assigned to Person A; FND 06 assigned to Person D). Person B has 0 of their own
29 assigned tasks completed because the first shared contract task `FND 08`
still requires Person A sign-off and the rest remain blocked by upstream
dependencies.

---

## Active Partial Tasks

| ID | Assigned To | Current Status | Remaining Acceptance Item |
|----|-------------|----------------|---------------------------|
| FND 08 | Person A and B | Contract draft completed by Person B in `docs/fnd08_frozen_json_contract.md` | Person A review and sign-off |
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

### Person B (Ayush) — Completed on behalf of others

| ID | Epic | Assigned To | Task | File/Module | Date | What Was Done | Acceptance Criteria | Verified |
|----|------|------------|------|-------------|------|---------------|--------------------|---------|
| FND 01 | E01 | Person C | Create repo structure and base folders from agreed layout | repo root | 2026-03-07 | Created the full repo scaffold: `replicalab/` with subdirectories for `agents/`, `env/`, `prompts/`, `scenarios/`, `scoring/`, `utils/`; `server/`; `frontend/` with `src/components/` and `src/pages/`; `notebooks/`; `tests/`. All directories tracked via `.gitkeep` files. | All top level folders exist and repo clones cleanly | Yes |
| FND 02 | E01 | Person C | Add Python project config and dependencies placeholder | `pyproject.toml` | 2026-03-08 | Added a PEP 621 `pyproject.toml` with package metadata, Python 3.10+ requirement, runtime dependencies (`pydantic`, `fastapi`, `uvicorn`, `websockets`), dev extras (`pytest`, `pytest-cov`, `ruff`, `mypy`), package discovery, and pytest test-path settings. | Project installs locally without missing package errors for base modules | Yes — verified with `python -m pip install -e .`, `python -m pip install -e ".[dev]"`, and `python -c "from replicalab.models import ..."` |
| FND 04 | E01 | Person A | Add empty Pydantic models and shared type names | `replicalab/models.py` | 2026-03-08 | Created `replicalab/__init__.py` (empty, makes package importable) and `replicalab/models.py` with 8 Pydantic BaseModel stubs: `ScientistAction` (9 fields), `LabManagerAction` (11 fields), `ScientistObservation` (9 fields), `LabManagerObservation` (13 fields), `Observation` (wrapper with scientist and lab_manager branches), `StepResult` (4 fields: observation, reward, done, info), `EpisodeState` (24 fields covering seed, scenario, paper, lab, protocol, conversation, scoring), `EpisodeLog` (12 fields covering episode record, transcript, reward breakdown, judge output). All fields have type annotations and sensible defaults. No validators or business logic. | Import paths resolve for all placeholder models | Yes — verified with `python -c "from replicalab.models import ..."` |
| FND 05 | E01 | Person C | Add ignore rules for Python, Node, logs, notebooks, and build artifacts | `.gitignore`, `.dockerignore` | 2026-03-08 | Added `.dockerignore` with the required runtime-context exclusions and expanded `.gitignore` for Python caches, coverage artifacts, notebook checkpoints, frontend build files, and generated output directories while preserving tracked `.gitkeep` files. | Repo status stays clean after local run and build, and Docker build excludes non-runtime files | Yes — verified by checking the ignore files contain the required exclusions and preserve tracked output scaffolds |
| FND 06 | E01 | Person D | Add temporary project stub with title, mission, team roles, and local setup placeholder | `README.md` | 2026-03-08 | Replaced the aspirational README with a temporary foundation stub that now states the current repo status, mission, team ownership, intended system roles, verified local setup placeholder, and near-term milestones. | New contributor can understand repo purpose in under two minutes | Yes — verified by content review against the required stub elements |
| FND 07 | E01 | Person C | Define branch naming, PR template, and issue template | `.github/` and repo workflow docs | 2026-03-08 | Added `.github/pull_request_template.md` and `.github/ISSUE_TEMPLATE/task.yml`, and documented preferred branch naming patterns plus required tracking-doc updates in `docs/project_management_rules.md`. | All future PRs auto show the template and issue fields | Yes — verified by the presence of the GitHub template files and the documented branch workflow |
| FND 10 | E01 | Person C | Create output directory structure | `replicalab/outputs/` | 2026-03-07 | Created `replicalab/outputs/` with three subdirectories: `logs/`, `replays/`, `plots/`. All tracked via `.gitkeep` files. | Output directories exist and generated files are not committed to git | Yes |
| FND 11 | E01 | Person C | Create server requirements file pinning runtime dependencies | `server/requirements.txt` | 2026-03-08 | Added `server/requirements.txt` with standalone FastAPI, uvicorn, websockets, and pydantic runtime pins aligned to the repo package configuration. | Server can be installed from requirements.txt independently of pyproject.toml | Yes — verified with `python -m pip install -r server/requirements.txt` |

### Kian (Person A) — No tasks completed yet

| ID | Epic | Task | Status |
|----|------|------|--------|
| — | — | No tasks completed | 0 of 49 assigned |

### Max (Person C) — Completed own task

| ID | Epic | Task | Status |
|----|------|------|--------|
| FND 11 | E01 | Create `server/requirements.txt` pinning runtime dependencies | Completed |

### Kush (Person D) — No tasks completed yet

| ID | Epic | Task | Status |
|----|------|------|--------|
| — | — | No tasks completed | 0 of 32 assigned |

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
| FND 11 | No new formal dependencies, but server scaffold work can now install from a standalone requirements file |
| FND 10 | No downstream dependencies |

### Current Unblocked and Active Tasks

| ID | Owner | Task | Unblocked By |
|----|-------|------|-------------|
| FND 03 | Max (Person C) | Initialize React plus Vite frontend shell | FND 01 |
| FND 08 | Person A and B | Freeze JSON contract for actions and observations (draft complete, sign-off pending) | FND 04 |
| FND 09 | Kian (Person A) | Create openenv.yaml configuration | FND 04 |
| DOC 01 | Kush (Person D) | Write hook, problem statement, and one line product summary | FND 06 |

---

## Epic Progress

| Epic | Total Tasks | Completed | Rate |
|------|------------|-----------|------|
| E01. Foundations and repository setup | 13 | 8 | 61.54% |
| E02. Domain models, validation, state contracts | 12 | 0 | 0% |
| E03. Scenario engine and constraint generation | 13 | 0 | 0% |
| E04. Scientist agent and Lab Manager policy | 11 | 0 | 0% |
| E05. Judge engine and reward logic | 11 | 0 | 0% |
| E06. OpenEnv environment implementation | 11 | 0 | 0% |
| E07. API, server, Docker, deployment | 19 | 0 | 0% |
| E08. RL training pipeline and evaluation | 15 | 0 | 0% |
| E09. Frontend, UX, replay, demo views | 15 | 0 | 0% |
| E10. Logging, replay, observability | 9 | 0 | 0% |
| E11. Testing and quality gates | 12 | 0 | 0% |
| E12. README, demo video, submission packaging | 11 | 0 | 0% |
