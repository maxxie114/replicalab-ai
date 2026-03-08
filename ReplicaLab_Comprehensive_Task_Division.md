
# ReplicaLab Comprehensive Task Division and Delivery Backlog

## 1. Document purpose

This document is the working blueprint for building **ReplicaLab** in a hackathon setting with a **4 person team**. It is written like a lightweight real world delivery plan with:

1. Product scope  
2. Team ownership  
3. Module and function ownership  
4. Epics  
5. User stories  
6. Lowest level tasks  
7. Dependencies  
8. Acceptance criteria  
9. Delivery workflow  
10. Definition of done  

The goal is to let any team member pick up work immediately without confusion.

---

## 2. Product summary

**ReplicaLab** is an OpenEnv environment where a **Scientist agent** and a **Lab Manager agent** negotiate how to solve a constrained technical task under real world limits such as budget, tools, compute, schedule, stock, and staffing.

The environment is used to **train the Scientist agent with reinforcement learning** so it learns to ask better questions, preserve objective quality, use bounded evidence tools correctly, and produce more feasible plans under domain-specific constraints.

The first domain focus is:

1. Mathematics
2. Machine learning
3. Finance and trading design in offline or backtest form

Physics and biology remain follow-on adapters once the normalized scenario layer is stable.

### The judged MVP outcome

By judging time, the project should demonstrate:

1. A working OpenEnv environment deployed on Hugging Face Spaces on port `7860`
2. At least one full scenario family working end to end, with a target of three
3. A Scientist agent that can interact with the environment through structured actions and bounded evidence tools
4. A hybrid model-backed Lab Manager with deterministic feasibility grounding and bounded validation tools
5. A deterministic judge and reward engine
6. A Colab training notebook using Unsloth or HF TRL
7. A reward curve showing improvement
8. A public GitHub repository
9. A one minute YouTube demo
10. A README with architecture, setup, and results

---

## 3. Scope control

## 3.1 In scope for the hackathon MVP

1. OpenEnv environment implementation
2. FastAPI and WebSocket serving
3. Hugging Face Docker Space deployment
4. Scientist agent with structured JSON action output plus bounded search, code-check, and image-inspection capability
5. Hybrid model-backed Lab Manager grounded by deterministic feasibility checks plus bounded validation tools
6. Judge rubric engine with deterministic scoring
7. Three scenario families for MVP
   1. Mathematics reasoning and proof planning
   2. ML benchmark replication
   3. Finance or trading backtest planning
8. Frozen evidence packs for deterministic training plus limited live validation during demo or eval
9. Reward logging
10. Replay logs
11. Colab RL notebook
12. Reward curve image
13. Thin React plus Vite frontend or OpenEnv `/web` fallback
14. README, demo video, submission package

## 3.2 Out of scope for the hackathon MVP

1. Proving whether a real research paper is globally true or false
2. Unrestricted parsing of arbitrary live internet content inside the training loop
3. Real wet lab execution
4. Live trading or production finance execution
5. Real time collaboration features
6. Training both Scientist and Lab Manager in self play
7. Open-ended autonomous coding outside a bounded verification or analysis sandbox
8. Image generation or audio capabilities in the agent policy loop
9. Complex third party enterprise integrations
10. Full multi-domain rollout unless time remains
11. Manager-led subagent orchestration unless the MVP is already stable

---

## 4. Team structure and role ownership

| Role | Owner focus | Primary responsibilities | Secondary responsibilities |
| --- | --- | --- | --- |
| Person A | Environment and Scoring Lead | scenario engine, constraint logic, reward logic, state transitions, tests | supports judge audit text |
| Person B | RL and Agent Lead | Scientist prompting, action schemas, training loop, rollouts, evaluation, reward curves | supports lab manager templating |
| Person C | Backend and Infra Lead | FastAPI server, WebSocket handling, Docker, HF Space deploy, logs, replay endpoints | supports local dev scripts |
| Person D | Frontend and Storytelling Lead | React plus Vite UI, live negotiation display, replay viewer, README, demo flow, video assets | supports final integration testing |

### Shared responsibilities

| Shared area | Expectation |
| --- | --- |
| Git hygiene | every feature goes through branch plus PR |
| Integration | merge to main only after quick smoke test |
| Testing | each owner writes tests for their workstream |
| Storytelling | everyone contributes screenshots, gifs, examples |
| Submission readiness | all four review final demo, notebook, README, repo visibility |

## 4.1 Training compute and model selection

1. The team has access to an H100 GPU for heavier Scientist training and evaluation runs.
2. Person B is the primary owner of that compute for RL tasks, especially `TRN 04` to `TRN 10`, `TRN 13` to `TRN 15`, `OBS 06`, and `TST 09`.
3. The judged artifact remains the Colab notebook, so any H100 run must still have a documented notebook path or reduced scale fallback that can be shown in Colab.
4. Person C supports any environment URL, secret, or infra setup needed so the H100 training run can connect to the same backend contract as the notebook.

### Trainable model

The primary trainable model for the Scientist policy is **Qwen3-4B**.

| Model | Role | Rationale |
| --- | --- | --- |
| Qwen3-4B | Primary Scientist policy | BF16 fits H100 (~14GB weights, ~42-56GB training). 4-bit fits Colab T4 (5.5GB). Strong structured output for JSON action schemas. Fast RL iteration speed. |
| Qwen3-8B | H100-only stretch | Better reasoning quality but 4-bit barely fits Colab T4 (6.5GB). Use only if Qwen3-4B quality is insufficient and Colab demo uses reduced-scale fallback. |

### Evaluator layer

The training reward is always the **deterministic rubric engine** defined in E05. A hosted frontier evaluator may optionally be used for post-episode explanation and demo audit only. The frontier evaluator is never part of the training reward loop.

### MVP role implementations

| Role | MVP implementation | Future stretch |
| --- | --- | --- |
| Scientist | Trainable policy (Qwen3-4B) | Qwen3-8B if quality insufficient |
| Lab Manager | Hybrid model-backed negotiation plus deterministic feasibility checker | Manager orchestrator with specialist subagents and role-specific adapters |
| Judge (training reward) | Deterministic rubric engine | Unchanged |
| Judge (explanation layer) | Optional hosted frontier evaluator | Extended explanation panel in UI |

## 4.2 Domain roadmap and normalized scenario layer

The frozen outer action and observation contract from `FND 08`, `MOD 01`, `MOD 02`, and `MOD 03` remains stable. Domain expansion happens below that contract through a normalized scenario layer.

The internal data flow is:

`scenario adapter -> normalized scenario pack -> observation mapper -> ScientistObservation or LabManagerObservation`

Every scenario family must emit the same normalized scenario pack with, at minimum:

1. `domain_id`
2. `task_summary`
3. `success_criteria`
4. `constraints`
5. `resources`
6. `allowed_substitutions`
7. `hidden_reference_spec`
8. `scenario_id`
9. `seed`

Rules for the normalized scenario layer:

1. Domain-specific logic belongs in thin adapters, not in prompts or reward code.
2. Prompts must be assembled from the normalized scenario pack, not hard-coded to one domain.
3. Difficulty and curriculum changes should mechanically alter constraints, resources, or conflicts rather than fork separate prompt logic.
4. The deterministic scorer compares the final agreed plan against `hidden_reference_spec`; model-backed roles never own truth.

For the bounded-tool MVP, pending scenario and environment work will extend the
existing normalized scenario pack with additive evidence fields. This is an
extension below the frozen outer contract, not a reopening of `FND 08`,
`MOD 01`, `MOD 02`, or `MOD 03`.

Tool-capable scenario extensions:

1. `evidence_pack`
2. `artifact_refs`
3. `allowed_tools`
4. `tool_budget`
5. `validation_policy`

## 4.3 Bounded tool capability policy

The richer-capability MVP keeps the final outward action contract stable while
adding bounded tools below it.

### Scientist allowed capabilities

1. `search_evidence`
   - retrieve supporting facts, benchmark rules, paper details, or official references
   - not a reward source
2. `run_code_check`
   - bounded code or config analysis, metric checks, value generation, runtime or cost estimation
3. `inspect_image`
   - read tables, plots, figures, screenshots, and charts for evidence extraction

### Lab Manager allowed capabilities

1. `search_resources`
   - retrieve resource, policy, benchmark, or documentation constraints
2. `run_code_check`
   - validate cost, runtime, config, reproducibility, or execution assumptions
3. `inspect_image`
   - inspect figures, charts, and screenshots relevant to feasibility or policy review

### Judge capability rules

1. The judge reward remains deterministic and must not depend on live web search.
2. Tool traces and evidence references may inform deterministic penalties, bonuses, or audit text.
3. The judge may use bounded evidence verification for demo or audit text, but never as the training reward source.

### Training and demo rules

1. Training uses frozen evidence packs and deterministic tool traces whenever possible.
2. Live web search is limited to demo-time or eval-time validation, not the core training reward loop.
3. Image generation and audio are excluded from the policy loop for the hackathon MVP.
4. Coding capability must stay sandboxed and task-scoped rather than open-ended.

---

## 5. Module and function ownership map

| Module or file | Key functions or classes | Owner | Notes |
| --- | --- | --- | --- |
| `replicalab/models.py` | `ScientistAction`, `LabManagerAction`, `Observation`, `StepResult`, `EpisodeState`, `EpisodeLog` | Person A with Person B | shared contract file |
| `replicalab/scenarios/templates.py` | `generate_scenario()`, `load_template()`, `apply_difficulty()`, `seed_rng()` | Person A | central normalized scenario factory and mapper inputs |
| `replicalab/scenarios/math_reasoning.py` | `build_math_reasoning_template()` | Person A | first structured reasoning scenario |
| `replicalab/scenarios/ml_benchmark.py` | `build_ml_benchmark_template()` | Person A | first reproducible compute scenario |
| `replicalab/scenarios/finance_trading.py` | `build_finance_trading_template()` | Person A | offline strategy and backtest planning only |
| `replicalab/agents/scientist_policy.py` | `build_scientist_prompt()`, `parse_scientist_output()` | Person B | trainable role |
| `replicalab/agents/lab_manager_policy.py` | `generate_lab_manager_response()`, `check_feasibility()` | Person B with Person A | model-backed negotiation grounded by deterministic checker |
| `replicalab/agents/judge_policy.py` | `explain_judgement()` optional only | Person A | explanation layer only |
| `replicalab/tools/search.py` | `search_evidence()`, `search_resources()` | Person B with Person C | bounded retrieval and validation only |
| `replicalab/tools/code_tools.py` | `run_code_check()` | Person B | bounded code analysis, config checks, and derived-value generation |
| `replicalab/tools/image_tools.py` | `inspect_image()` | Person B with Person D | bounded table, chart, figure, and screenshot inspection |
| `replicalab/scoring/rigor.py` | `score_rigor()` | Person A | deterministic |
| `replicalab/scoring/feasibility.py` | `score_feasibility()` | Person A | deterministic |
| `replicalab/scoring/fidelity.py` | `score_fidelity()` | Person A | deterministic |
| `replicalab/scoring/rubric.py` | `compute_total_reward()`, `build_reward_breakdown()` | Person A | core reward |
| `replicalab/utils/validation.py` | `validate_protocol()`, `validate_vocab()` | Person A | schema and semantic checks |
| `replicalab/utils/logging.py` | `write_episode_log()`, `write_reward_csv()` | Person C | logging helpers |
| `replicalab/env/replicalab_env.py` | `ReplicaLabEnv.reset()`, `step()`, `state()`, `close()` | Person A | OpenEnv environment |
| `server/app.py` | `create_app()`, REST routes, WebSocket handler | Person C | runtime entrypoint |
| `server/Dockerfile` | build and run app | Person C | deployment |
| `frontend/src/App.tsx` | app shell | Person D | UI root |
| `frontend/src/components/*` | paper panel, log panel, score panel, controls, replay, judge audit | Person D | UI components |
| `frontend/vite.config.ts` | dev proxy and build output config | Person C with Person D | frontend and backend integration |
| `frontend/tailwind.config.ts` and `frontend/postcss.config.js` | theme tokens and CSS pipeline | Person D | matches declared styling stack |
| `notebooks/train_colab.ipynb` | setup, connect, rollout, train, plot | Person B | judged asset |
| `tests/*` | unit and integration tests | all | each owner covers own modules |
| `openenv.yaml` | environment registration and server config | Person A | required for OpenEnv discovery |
| `replicalab/config.py` | `MAX_ROUNDS`, `DEFAULT_DIFFICULTY`, `TIMEOUT_SECONDS`, `MAX_BUDGET` | Person A | single source of truth for constants |
| `replicalab/client.py` | `ReplicaLabClient.connect()`, `reset()`, `step()`, `close()` | Person B | reusable by notebook and external consumers |
| `replicalab/utils/seed.py` | `seed_rng()`, `get_deterministic_seed()` | Person A | shared by scenarios and env |
| `replicalab/prompts/*.txt` | role prompt templates | Person B | loadable domain-neutral text files assembled from normalized scenario data |
| `replicalab/outputs/` | `logs/`, `replays/`, `plots/` | Person C | gitignored output directories |
| `server/requirements.txt` | pinned runtime dependencies | Person C | standalone server install |
| `README.md` | project story, setup, results | Person D with all | judged asset |

---

## 6. Delivery phases

| Phase | Goal | Exit condition |
| --- | --- | --- |
| Phase 0 | contracts and scaffolding | repo, schema, branch rules, basic app skeleton |
| Phase 1 | one working scenario end to end | reset, step, reward, logs work locally |
| Phase 2 | deployable environment | FastAPI, Docker, HF Space live |
| Phase 3 | trainable loop | Colab notebook connects and shows non flat rewards |
| Phase 4 | compelling demo | UI, replay, reward breakdown, README, video |
| Phase 5 | hardening | smoke tests, bug fixes, final submission review |

---

## 7. Operating workflow

## 7.1 Branching model

| Branch type | Example | Rule |
| --- | --- | --- |
| main | `main` | always demo safe |
| feature | `feature/env-reset-loop` | one feature per branch |
| hotfix | `hotfix/ws-timeout-fix` | used only for urgent breaks |

## 7.2 PR checklist

Every PR must include:

1. linked task ID
2. summary of change
3. screenshots or logs if UI or environment behavior changed
4. quick test result
5. note on any schema or API changes

## 7.3 Integration cadence

1. Sync at start of day
2. Merge every 2 to 3 hours if stable
3. End of block smoke test on:
   1. local reset
   2. one full episode
   3. frontend load
   4. notebook connection if applicable

---

## 8. Epic backlog

### Status legend

- `✅ Completed`
- `❌ Failed`
- `🟡 Partial`
- `⬜ Not started`
- `Completed by`: fill this only when the finisher is different from the assigned owner; otherwise use `—`

---

## Epic E01. Foundations and repository setup

### Epic goal
Create a stable shared codebase, contracts, and development workflow so all workstreams can proceed in parallel.

### Current status

- `FND 01` status: completed on 2026-03-07
- `FND 01` completed by: `Person B (Ayush)` while the assigned owner remains `Person C`
- `FND 02` status: completed on 2026-03-08
- `FND 02` completed by: `Person B (Ayush)` while the assigned owner remains `Person C`
- `FND 04` status: completed on 2026-03-08
- `FND 04` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `FND 05` status: completed on 2026-03-08
- `FND 05` completed by: `Person B (Ayush)` while the assigned owner remains `Person C`
- `FND 06` status: completed on 2026-03-08
- `FND 06` completed by: `Person B (Ayush)` while the assigned owner remains `Person D`
- `FND 07` status: completed on 2026-03-08
- `FND 07` completed by: `Person B (Ayush)` while the assigned owner remains `Person C`
- `FND 08` status: completed on 2026-03-08
- `FND 08` completed by: `Person A (Kian)` and `Person B (Ayush)` with shared sign-off recorded in `docs/fnd08_frozen_json_contract.md`
- `FND 09` status: completed on 2026-03-08
- `FND 09` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `FND 11` status: completed on 2026-03-08
- `FND 11` completed by: `Max (Person C)`; the branch import and standards validation were handled by `Person B (Ayush)`
- `FND 10` status: completed on 2026-03-07
- `FND 10` completed by: `Person B (Ayush)` while the assigned owner remains `Person C`
- Completed scope for `FND 01`: created the agreed repo scaffold for `replicalab/`, `server/`, `frontend/`, `notebooks/`, and `tests/`, including the initial `replicalab/*` and `frontend/src/*` subfolders from the planned layout
- Completed scope for `FND 02`: added `pyproject.toml` with package metadata, Python version floor, runtime dependencies, dev extras, and basic pytest discovery settings; verified editable install and shared-model imports
- Completed scope for `FND 04`: added importable empty Pydantic model stubs in `replicalab/models.py` for the shared action, observation, step, state, and log contracts
- Completed scope for `FND 05`: created `.dockerignore` and expanded `.gitignore` to cover Python, Node, notebook, coverage, cache, and generated output artifacts while preserving tracked `.gitkeep` scaffold files
- Completed scope for `FND 06`: replaced the aspirational README with a temporary foundation stub that reflects the actual repo state, mission, team ownership, and current local setup placeholder
- Completed scope for `FND 07`: added GitHub PR and task-issue templates and tightened the repo workflow rules for branch naming and required tracking-doc updates
- Completed scope for `FND 08`: added `docs/fnd08_frozen_json_contract.md` with field semantics, enums, nested object schemas, null-vs-empty rules, canonical JSON examples for all 8 shared models, and final shared sign-off
- Completed scope for `FND 09`: added `openenv.yaml` with OpenEnv manifest metadata plus the minimal repo wiring required for local OpenEnv validation (`openenv-core` dependency, `server` script entry point, `uv.lock`, and `server.app.main()`)
- Completed scope for `FND 10`: created `replicalab/outputs/` with tracked `logs/`, `replays/`, and `plots/` subdirectories
- Completed scope for `FND 11`: added `server/requirements.txt` with standalone runtime dependency pins and verified installation from that file
- Completed scope for `FND 03`: imported the full React plus Vite frontend tree from Kush's branch onto `ayush`, including the app shell, pages, shared components, assets, and TypeScript config, and validated it with `npm --prefix frontend install` plus `npm --prefix frontend run build`
- Completed scope for `FND 12`: imported `frontend/vite.config.ts` with local `/api` and `/ws` proxy support plus stable Vite build settings and validated the build on `ayush`
- Backend and deployment scope imported from Max's PR has now been normalized onto the current standards, validated against the real env, Docker-verified locally, and extended with HF Spaces metadata plus deployment instructions
- Newly unblocked by `FND 08`: `MOD 01`, `MOD 02`, `MOD 03`, `MOD 12`, `SCN 01`
- Newly unblocked by `FND 06`: `DOC 01`
- Newly unblocked by `FND 03`: `FND 13`, `UI 01`
- Remaining Epic E01 work still gated by follow-on dependencies: `FND 13`
- Remaining completion items for the backend and deployment path: live HF Space bring-up (`API 10`), secrets documentation (`API 17`), replay persistence, and the remaining partial API polish tasks
- Completed scope for `SCN 01` to `SCN 10`: added deterministic seed utilities, normalized scenario-pack models, math / ML / finance template builders, difficulty scaling, hidden reference specs, allowed substitutions, and seeded scenario tests
- Completed scope for `SCN 11`: added three fixed golden scenarios for deterministic prompt and manual checks under `tests/fixtures/golden_scenarios.json`
- Completed scope for `AGT 01`: added a domain-neutral Scientist system prompt builder that renders role instructions, success criteria, mapped constraints, mapped resources, substitutions, and the strict JSON output contract from normalized scenario data
- Newly unblocked by `SCN 11` and `AGT 01`: `AGT 02`, `AGT 11`, `TRN 04`, `TRN 08`
- Remaining Epic E03 work after the scenario bundle: `SCN 12`

### User stories

**US E01.1**  
As a developer, I want a clean repo and file layout so I can build without stepping on other people’s work.

**US E01.2**  
As a team, we want agreed schemas and coding rules so integration risk stays low.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FND 01 | E01.1 | Person C | repo root | Create repo structure and base folders from agreed layout | none | 0.5h | all top level folders exist and repo clones cleanly | ✅ Completed | Person B (Ayush) |
| FND 02 | E01.1 | Person C | `pyproject.toml` | Add Python project config and dependencies placeholder | FND 01 | 0.5h | project installs locally without missing package errors for base modules | ✅ Completed | Person B (Ayush) |
| FND 03 | E01.1 | Person C | `frontend/package.json` | Initialize React plus Vite frontend shell | FND 01 | 0.5h | `npm install` and dev server run successfully | ✅ Completed | Kush |
| FND 04 | E01.2 | Person A | `replicalab/models.py` | Add empty Pydantic models and shared type names | FND 01 | 0.5h | import paths resolve for all placeholder models | ✅ Completed | Person B (Ayush) |
| FND 05 | E01.2 | Person C | `.gitignore` and `.dockerignore` | Add ignore rules for Python, Node, logs, notebooks, and build artifacts. `.dockerignore` must explicitly exclude `.git`, `node_modules`, `notebooks/`, `tests/`, `__pycache__`, `.venv`, and output files to keep the Docker image lean | FND 01 | 0.25h | repo status stays clean after local run and build, and Docker build excludes non-runtime files | ✅ Completed | Person B (Ayush) |
| FND 06 | E01.2 | Person D | `README.md` | Add temporary project stub with title, mission, team roles, and local setup placeholder | FND 01 | 0.5h | new contributor can understand repo purpose in under two minutes | ✅ Completed | Person B (Ayush) |
| FND 07 | E01.2 | Person C | repo settings | Define branch naming, PR template, and issue template | FND 01 | 0.5h | all future PRs auto show the template and issue fields | ✅ Completed | Person B (Ayush) |
| FND 08 | E01.2 | Person A and B | docs or backlog file | Freeze JSON contract for actions and observations | FND 04 | 0.75h | all owners sign off and no blocking contract ambiguity remains | ✅ Completed | Person A (Kian) and Person B (Ayush) |
| FND 09 | E01.2 | Person A | `openenv.yaml` | Create OpenEnv configuration file specifying environment class, action and observation types, and server settings | FND 04 | 0.5h | OpenEnv can discover and serve the environment using this config file | ✅ Completed | Person B (Ayush) |
| FND 10 | E01.1 | Person C | `replicalab/outputs/` | Create output directory structure with `logs/`, `replays/`, and `plots/` subdirectories and add to gitignore | FND 01 | 0.25h | output directories exist and generated files are not committed to git | ✅ Completed | Person B (Ayush) |
| FND 11 | E01.1 | Person C | `server/requirements.txt` | Create server requirements file pinning FastAPI, uvicorn, websockets, and other runtime dependencies | FND 02 | 0.25h | server can be installed from requirements.txt independently of pyproject.toml | ✅ Completed | Max (Person C) |
| FND 12 | E01.1 | Person C | `frontend/vite.config.ts` | Create Vite config with API and WebSocket proxy support for local development plus stable build output settings | FND 03 | 0.5h | frontend dev server can reach backend without manual URL edits and build output is predictable for Docker packaging | ✅ Completed | Kush |
| FND 13 | E01.1 | Person D | `frontend/tailwind.config.ts` and `frontend/postcss.config.js` | Install and configure Tailwind plus shadcn base setup, theme tokens, and global styles | FND 03 | 0.75h | frontend can use Tailwind utilities and shared shadcn compatible theme tokens without CSS pipeline errors | ⬜ Not started | — |

---

## Epic E02. Domain models, validation, and state contracts

### Epic goal
Define the environment contracts cleanly so state, actions, and observations are deterministic and easy to train against.

### Current status

- `MOD 01` status: completed on 2026-03-08
- `MOD 01` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `MOD 02` status: completed on 2026-03-08
- `MOD 02` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `MOD 03` status: completed on 2026-03-08
- `MOD 03` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `MOD 04` status: completed on 2026-03-08
- `MOD 04` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `MOD 05` status: completed on 2026-03-08
- `MOD 05` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `MOD 11` status: completed on 2026-03-08
- `MOD 11` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `MOD 12` status: completed on 2026-03-08
- `MOD 12` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `MOD 09` status: completed on 2026-03-08
- Completed scope for `MOD 01`: replaced the placeholder `ScientistAction` with a strict enum-backed schema, required all frozen-contract fields, forbade unknown keys, rejected mixed-mode payloads, added conditional validation for proposal, revision, request-info, and accept modes, added focused schema tests, and patched the stub server so `accept` no longer overwrites the current protocol with default values
- Completed scope for `MOD 02`: replaced the placeholder `LabManagerAction` with a strict enum-backed schema, required all frozen-contract fields, forbade unknown keys, enforced feasible-flag consistency across budget, equipment, reagent, schedule, and staff checks, rejected suggestion fields outside `suggest_alternative`, and added focused validation tests
- Completed scope for `MOD 03`: introduced typed `ConversationEntry` and `Protocol` models, upgraded both observation branches to use typed nested structures with non-negative numeric constraints and stable keys, and verified dict-to-model coercion through the current stub server and focused tests
- Completed scope for `MOD 04`: replaced the remaining loose `dict` state and replay fields with typed `Protocol`, `ConversationEntry`, and `RewardBreakdown` models, updated the stub runtime to construct those nested models explicitly, and added round-trip coverage for serialized state and logs
- Completed scope for `MOD 05`: added deterministic semantic protocol validation in `replicalab/utils/validation.py` with `ValidationResult` and `validate_protocol(...)` checks for resource vocabulary, allowed substitutions, duration limits, required-element coverage, and obvious impossibilities against the normalized scenario pack
- Completed scope for `MOD 11`: introduced typed `RewardBreakdown` and `StepInfo` models, upgraded `StepResult.info` to the reserved-key contract while still allowing debug metadata, and updated the stub runtime to build typed reward and step-info payloads explicitly
- Completed scope for `MOD 12`: added `replicalab/config.py` as the shared constants module for default scenario, difficulty, round cap, budget cap, timeout values, stub reward, and API host or port defaults; updated the server and scenario builders to import those constants instead of repeating magic numbers
- Completed scope for `MOD 09`: added `replicalab/agents/scientist_policy.py` with a raw-text parser that extracts JSON from plain text or fenced blocks, validates it into `ScientistAction`, and raises an explicit `ScientistOutputParseError` for missing JSON, invalid JSON, or schema failures; added focused parser tests and package exports
- Newly unblocked by `MOD 01`: `MOD 05`, `MOD 09`
- Newly unblocked by `MOD 03`: `MOD 04`, `MOD 11`
- Newly unblocked by `MOD 04`: `MOD 07`, `ENV 01`
- Newly unblocked by `MOD 05`: `MOD 06`, `AGT 05`
- `MOD 11` does not introduce a new formal dependency edge by itself, but it stabilizes `StepResult` metadata for environment, API, replay, and training consumers
- `MOD 09` does not fully unblock a new task by itself, but it removes one half of the blocker on `AGT 03`; `AGT 03` now only waits on `AGT 02`

### User stories

**US E02.1**  
As the environment, I need typed actions and observations so invalid messages can be rejected early.

**US E02.2**  
As the training loop, I need deterministic state serialization so episodes can be replayed and compared.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MOD 01 | E02.1 | Person A | `replicalab/models.py` | Implement `ScientistAction` schema | FND 08 | 0.5h | valid scientist actions parse and invalid fields raise validation errors | ✅ Completed | Person B (Ayush) |
| MOD 02 | E02.1 | Person A | `replicalab/models.py` | Implement `LabManagerAction` schema | FND 08 | 0.5h | valid lab manager actions parse and invalid fields raise validation errors | ✅ Completed | Person B (Ayush) |
| MOD 03 | E02.1 | Person A | `replicalab/models.py` | Implement role specific `Observation` models | FND 08 | 0.75h | scientist and lab observations serialize to JSON with stable keys | ✅ Completed | Person B (Ayush) |
| MOD 04 | E02.2 | Person A | `replicalab/models.py` | Implement `EpisodeState` and `EpisodeLog` models | MOD 03 | 0.75h | full state round trip serialize plus deserialize works | ✅ Completed | Person B (Ayush) |
| MOD 05 | E02.1 | Person A | `replicalab/utils/validation.py` | Add protocol validation for sample size, controls, duration, equipment vocab, reagent vocab | MOD 01 | 1h | invalid protocol examples are rejected with readable reasons | ✅ Completed | Person B (Ayush) |
| MOD 06 | E02.1 | Person A | `replicalab/utils/validation.py` | Add semantic validators for impossible plans such as zero sample size with positive controls | MOD 05 | 0.75h | semantic validator catches at least five invalid edge cases | ✅ Completed | Person B (Ayush) |
| MOD 07 | E02.2 | Person C | `replicalab/utils/logging.py` | Add state serialization helper for replay logs | MOD 04 | 0.5h | state logs can be written and loaded without loss | ✅ Completed | Person B (Ayush) |
| MOD 08 | E02.2 | Person A | tests | Write unit tests for schemas and validators | MOD 01 to MOD 07 | 1h | tests cover valid parse, invalid parse, and replay serialization | ⬜ Not started | — |
| MOD 09 | E02.2 | Person B | `replicalab/agents/scientist_policy.py` | Add output parser that maps model text to `ScientistAction` | MOD 01 | 0.75h | parser returns structured action or explicit parse error | ✅ Completed | — |
| MOD 10 | E02.2 | Person C | API docs | Publish schema examples for frontend and notebook clients | MOD 01 to MOD 04 | 0.5h | frontend and notebook can mock against shared sample payloads | ✅ Completed | Person B (Ayush) |
| MOD 11 | E02.1 | Person A | `replicalab/models.py` | Implement `StepResult` model with observation, reward, done flag, and info dict | MOD 03 | 0.5h | step result serializes cleanly and all consumers agree on its shape | ✅ Completed | Person B (Ayush) |
| MOD 12 | E02.2 | Person A | `replicalab/config.py` | Create environment configuration module with constants for max rounds, default difficulty, timeout duration, max budget, and round time limit | FND 08 | 0.5h | all modules import config from one place and no magic numbers remain in env or scoring code | ✅ Completed | Person B (Ayush) |

---

## Epic E03. Scenario engine and constraint generation

### Epic goal
Generate deterministic, varied, and internally consistent technical scenarios through a normalized scenario layer.

### User stories

**US E03.1**  
As a user, I want seeded scenarios so I can replay identical tasks.

**US E03.2**  
As a judge, I want normalized constraints and resources so the environment tests real tradeoffs across domains without changing the outer contract.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCN 01 | E03.1 | Person A | `replicalab/utils/seed.py` | Implement deterministic RNG helper `seed_rng()` in dedicated seed utility module | FND 08 | 0.5h | same seed always yields the same random choices and seed module is importable from scenarios and env | ✅ Completed | Person B (Ayush) |
| SCN 02 | E03.1 | Person A | `replicalab/scenarios/templates.py` | Define normalized scenario schema with task summary, success criteria, constraints, resources, allowed substitutions, and hidden reference spec | MOD 04 | 0.75h | all scenario builders return the same normalized top level structure and mapper-ready inputs | ✅ Completed | Person B (Ayush) |
| SCN 03 | E03.2 | Person A | `replicalab/scenarios/math_reasoning.py` | Implement mathematics template with theorem, proof-goal, tool, time, and review constraints | SCN 02 | 1h | generated scenario passes structure and internal consistency tests | ✅ Completed | Person B (Ayush) |
| SCN 04 | E03.2 | Person A | `replicalab/scenarios/ml_benchmark.py` | Implement ML benchmark template with dataset, compute, time, and evaluation constraints | SCN 02 | 1h | generated scenario passes structure and internal consistency tests | ✅ Completed | Person B (Ayush) |
| SCN 05 | E03.2 | Person A | `replicalab/scenarios/finance_trading.py` | Implement finance and trading planning template with risk, capital, slippage, and backtest constraints | SCN 02 | 1h | generated scenario passes structure and internal consistency tests | ✅ Completed | Person B (Ayush) |
| SCN 06 | E03.1 | Person A | `replicalab/scenarios/templates.py` | Implement difficulty application for easy, medium, hard by mechanically altering constraints, resources, and conflicts | SCN 03 to SCN 05 | 1h | difficulty visibly changes the normalized scenario pack in a meaningful way | ✅ Completed | Person B (Ayush) |
| SCN 07 | E03.2 | Person A | `replicalab/scenarios/templates.py` | Implement normalized constraint and resource generator for budget, time, compute, personnel, stock, and bookings | SCN 02 | 1.25h | no generated scenario contains contradictory constraints or resources | ✅ Completed | Person B (Ayush) |
| SCN 08 | E03.2 | Person A | `replicalab/scenarios/templates.py` | Implement hidden reference spec and allowed substitutions per template | SCN 03 to SCN 05 | 1h | hidden reference clearly marks what is fixed versus flexible for deterministic scoring | ✅ Completed | Person B (Ayush) |
| SCN 09 | E03.1 | Person A | `replicalab/scenarios/templates.py` | Implement `generate_scenario(seed, template, difficulty)` | SCN 01 to SCN 08 | 0.75h | function returns a full scenario with deterministic content | ✅ Completed | Person B (Ayush) |
| SCN 10 | E03.1 | Person A | tests | Add seeded generation tests and consistency tests | SCN 09 | 1h | same seed plus template returns same scenario and different seeds vary | ✅ Completed | Person B (Ayush) |
| SCN 11 | E03.2 | Person B | fixtures | Create hand checked golden scenarios for prompt testing | SCN 09 | 0.75h | three fixed scenarios are available for deterministic manual testing | ✅ Completed | — |
| SCN 12 | E03.2 | Person D | docs | Write plain language scenario summaries for UI examples and README | SCN 03 to SCN 05 | 0.5h | each template has a clean one paragraph explanation for judges | ⬜ Not started | — |
| SCN 13 | E03.2 | Person A | `replicalab/scenarios/templates.py` | Implement shared booking and scheduling data model for GPUs, rooms, or equipment with time slot conflicts and duration | SCN 07 | 1h | constraint generator can produce realistic booking conflicts across domains and the Lab Manager can check availability | ✅ Completed | Person B (Ayush) |

---

## Epic E04. Scientist agent and Lab Manager policy

### Epic goal
Create the interactive roles that operate inside the environment while keeping truth in deterministic checkers and reward logic.

### User stories

**US E04.1**  
As the Scientist agent, I want a structured action space so I can learn consistent policy behavior.

**US E04.2**  
As the Lab Manager, I want grounded negotiation plus deterministic feasibility checks so the environment remains stable and fair.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AGT 01 | E04.1 | Person B | `replicalab/agents/scientist_policy.py` | Draft domain-neutral system prompt for Scientist role from normalized scenario data | MOD 01, SCN 11 | 0.75h | prompt clearly explains role, mapped constraints, and JSON output contract | ✅ Completed | — |
| AGT 02 | E04.1 | Person B | `replicalab/agents/scientist_policy.py` | Build observation to prompt formatting helper from normalized scenario-derived observations | AGT 01, MOD 03 | 0.75h | formatted prompt includes task info, history, and action schema consistently | ✅ Completed | — |
| AGT 03 | E04.1 | Person B | `replicalab/agents/scientist_policy.py` | Add parse plus retry strategy for malformed model output | MOD 09, AGT 02 | 0.75h | malformed output triggers at least one controlled retry or explicit failure | ✅ Completed | — |
| AGT 04 | E04.1 | Person B | `replicalab/agents/scientist_policy.py` | Build baseline heuristic Scientist for non trained smoke tests | AGT 02 | 1h | baseline can complete episodes without crashing | ✅ Completed | — |
| AGT 05 | E04.2 | Person A and B | `replicalab/agents/lab_manager_policy.py` | Implement deterministic feasibility checker against normalized constraints, resources, schedule, and policy rules | SCN 07, MOD 05 | 1.25h | checker returns clear pass or fail per constraint dimension | ✅ Completed | Person B (Ayush) |
| AGT 06 | E04.2 | Person B | `replicalab/agents/lab_manager_policy.py` | Implement alternative suggestion logic from allowed substitutions and resource tradeoffs | AGT 05, SCN 08 | 1h | lab manager can suggest at least one sensible revision when initial plan fails | ✅ Completed | — |
| AGT 07 | E04.2 | Person B | `replicalab/agents/lab_manager_policy.py` | Add model-backed response synthesis from feasibility results and suggested revisions | AGT 05 | 0.75h | output is readable, grounded in checker results, and maps cleanly to underlying checks | ✅ Completed | — |
| AGT 08 | E04.1 | Person B | tests | Add prompt formatting, parse, and bounded-tool policy tests for Scientist policy | AGT 01 to AGT 04 | 0.75h | tests cover happy path, malformed output handling, and stable tool-policy reminders | ✅ Completed | — |
| AGT 09 | E04.2 | Person A | tests | Add deterministic feasibility checker tests for Lab Manager grounding | AGT 05 to AGT 07 | 0.75h | same proposal plus same normalized scenario returns the same checker results every time | ✅ Completed | Person B (Ayush) |
| AGT 10 | E04.1 | Person B | `replicalab/prompts/` | Write prompt text files for all three roles: `scientist.txt`, `lab_manager.txt`, `judge.txt`, including bounded rules for search, code checks, and image inspection | AGT 01, AGT 07, JDG 06 | 0.75h | prompt files exist, are loadable, encode bounded tool rules clearly, and assemble correctly from normalized scenario data and agreed role behavior | ✅ Completed | — |
| AGT 11 | E04.1 | Person B | docs | Select and document base model for Scientist training with rationale for model size, license, and structured output capability | AGT 01 | 0.5h | decision is recorded and all team members know which model will be fine tuned | ✅ Completed | — |

---

## Epic E05. Judge engine and reward logic

### Epic goal
Score the final plan fairly, explainably, and deterministically against the hidden reference spec.

### User stories

**US E05.1**  
As the training system, I need a stable reward so the model can improve.

**US E05.2**  
As a judge, I need a readable score breakdown so I can understand why the environment rewarded or penalized the agent.

### Executor notes

- `JDG 01` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `JDG 02` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`
- `JDG 03` completed by: `Person B (Ayush)` while the assigned owner remains `Person A`

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| JDG 01 | E05.1 | Person A | `replicalab/scoring/rigor.py` | Implement rigor or objective-validity score for plan completeness, required checks, method quality, justification, and correct bounded evidence use when present | SCN 08 | 1.25h | score is between 0 and 1, matches rubric examples, and rewards correct evidence-backed planning without depending on live web results | ✅ Completed | Person B (Ayush) |
| JDG 02 | E05.1 | Person A | `replicalab/scoring/feasibility.py` | Implement feasibility score for budget, resources, time, staffing, compute, bookings, and deterministic tool-backed validation results | SCN 07, AGT 05 | 1.25h | score is between 0 and 1 and matches normalized constraint logic plus deterministic tool outcomes | ✅ Completed | Person B (Ayush) |
| JDG 03 | E05.1 | Person A | `replicalab/scoring/fidelity.py` | Implement fidelity score against hidden reference spec, required steps, allowed substitutions, and supported evidence claims when present | SCN 08 | 1h | score is between 0 and 1 and matches rubric examples for plan and evidence alignment | ✅ Completed | Person B (Ayush) |
| JDG 04 | E05.1 | Person A | `replicalab/scoring/rubric.py` | Implement total reward formula with bonuses and penalties, including deterministic penalties for invalid tool use or unsupported evidence claims | JDG 01 to JDG 03 | 0.75h | total reward formula matches agreed math and returns consistent output for plan quality and bounded tool behavior | ✅ Completed | Person B (Ayush) |
| JDG 05 | E05.2 | Person A | `replicalab/scoring/rubric.py` | Build reward breakdown object with component scores, penalties, and tool-use diagnostics | JDG 04 | 0.5h | breakdown includes rigor, feasibility, fidelity, bonuses, penalties, and bounded tool diagnostics | ✅ Completed | Person B (Ayush) |
| JDG 06 | E05.2 | Person A | `replicalab/scoring/explain.py` | Add optional plain English explanation function from reward breakdown | JDG 05 | 0.75h | explanation mirrors rubric, may reference bounded evidence or tool outcomes, and introduces no new hidden logic | ✅ Completed | Person B (Ayush) |
| JDG 07 | E05.1 | Person C | `replicalab/utils/logging.py` | Log reward breakdown to CSV or JSONL per episode | JDG 05, MOD 07 | 0.5h | reward file contains seed, scenario, score components, total reward, rounds, agreement, and bounded tool metrics | ⬜ Not started | — |
| JDG 08 | E05.1 | Person A | tests | Add score determinism tests and edge case tests | JDG 01 to JDG 05 | 1h | perfect and broken protocols produce expected relative ordering | ✅ Completed | Person B (Ayush) |
| JDG 09 | E05.2 | Person D | UI mocks | Create mock score cards and language for frontend | JDG 05 | 0.5h | UI can display score breakdown from mock data | ⬜ Not started | — |
| JDG 10 | E05.1 | Person B | notebook support | Expose component metrics for training plots | JDG 05, JDG 07 | 0.5h | notebook can read average rigor, feasibility, fidelity, and bounded tool metrics over time | ⬜ Not started | — |
| JDG 11 | E05.2 | Person A | `replicalab/scoring/rubric.py` and `replicalab/agents/judge_policy.py` | Add structured final audit payload with `judge_notes`, `verdict`, and top failure reasons derived from the rubric | JDG 05, JDG 06 | 0.75h | final judgement output is deterministic, human readable, and consumable by env, API, logs, and UI | ✅ Completed | Person B (Ayush) |

---

## Epic E06. OpenEnv environment implementation

### Epic goal
Turn the scenario, roles, and reward logic into a real OpenEnv environment.

### User stories

**US E06.1**  
As a client, I want `reset()` to start a clean, seeded episode.

**US E06.2**  
As a client, I want `step()` to advance one turn and return observation, reward, and done.

**US E06.3**  
As a judge, I want deterministic replay and cleanup.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENV 01 | E06.1 | Person A | `replicalab/env/replicalab_env.py` | Create `ReplicaLabEnv` class skeleton | MOD 04, SCN 09 | 0.5h | environment class imports and instantiates without runtime errors | ✅ Completed | Person B (Ayush) |
| ENV 02 | E06.1 | Person A | `replicalab/env/replicalab_env.py` | Implement `reset(seed, template, difficulty)` | ENV 01, SCN 09 | 1h | reset returns initial observations and a fresh episode state | ✅ Completed | Person B (Ayush) |
| ENV 03 | E06.2 | Person A | `replicalab/env/replicalab_env.py` | Implement internal Scientist turn application and bounded tool mediation | ENV 02, AGT 05 | 1h | valid Scientist action plus any allowed tool traces update state and history correctly | ✅ Completed | Person B (Ayush) |
| ENV 04 | E06.2 | Person A | `replicalab/env/replicalab_env.py` | Implement internal Lab Manager response step with bounded validation tools | ENV 03, AGT 07 | 1h | lab manager response plus any supporting bounded tool traces are appended and returned in the next observation | ✅ Completed | Person B (Ayush) |
| ENV 05 | E06.2 | Person A | `replicalab/env/replicalab_env.py` | Implement accept, timeout, and max round logic | ENV 03, ENV 04 | 0.75h | episode terminates correctly on agreement or round limit | ✅ Completed | Person B (Ayush) |
| ENV 06 | E06.2 | Person A | `replicalab/env/replicalab_env.py` | Integrate reward computation at finalization and optional intermediate score previews | ENV 05, JDG 05 | 1h | final step returns total reward, breakdown info, and deterministic penalties or bonuses for bounded tool behavior | ✅ Completed | Person B (Ayush) |
| ENV 07 | E06.3 | Person A | `replicalab/env/replicalab_env.py` | Implement `state()` | ENV 02 to ENV 06 | 0.5h | current environment state can be retrieved for debugging and replay | ✅ Completed | Person B (Ayush) |
| ENV 08 | E06.3 | Person A | `replicalab/env/replicalab_env.py` | Implement `close()` cleanup | ENV 01 | 0.25h | close frees any transient resources and does not throw | ✅ Completed | Person B (Ayush) |
| ENV 09 | E06.3 | Person C | `replicalab/utils/logging.py` | Write episode logs on completion | ENV 06, JDG 07 | 0.5h | completed episodes generate replayable logs automatically | ⬜ Not started | — |
| ENV 10 | E06.1 to E06.3 | Person A | tests | Add reset, step, invalid action, timeout, and deterministic replay tests | ENV 02 to ENV 09 | 1.25h | tests pass for seeded reset, valid step, invalid step, and replay consistency | ✅ Completed | Person B (Ayush) |
| ENV 11 | E06.2 | Person A | `replicalab/env/replicalab_env.py` | Attach judge audit payload to final `StepResult`, terminal observations, and replay state | ENV 06, JDG 11 | 0.5h | completed episodes expose audit notes alongside reward breakdown in a stable schema | ✅ Completed | Person B (Ayush) |

---

## Epic E07. API, server, Docker, and deployment

### Epic goal
Serve the environment reliably for frontend users and training clients, then deploy it to Hugging Face Spaces.

### User stories

**US E07.1**  
As a client, I want to connect over WebSocket or REST to interact with the environment remotely.

**US E07.2**  
As the team, we want one click reproducible deployment to HF Spaces.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| API 01 | E07.1 | Person C | `server/app.py` | Create FastAPI app shell and health endpoint | ENV 01 | 0.5h | `GET /health` returns 200 with simple payload | 🟡 Partial | — |
| API 02 | E07.1 | Person C | `server/app.py` | Add `POST /reset` endpoint | ENV 02 | 0.75h | reset endpoint starts a new episode and returns initial observation | ✅ Completed | Person B (Ayush) |
| API 03 | E07.1 | Person C | `server/app.py` | Add `POST /step` endpoint | ENV 06 | 0.75h | step endpoint accepts valid action and returns step result | ✅ Completed | Person B (Ayush) |
| API 04 | E07.1 | Person C | `server/app.py` | Add `GET /scenarios` endpoint | SCN 03 to SCN 05 | 0.5h | endpoint lists available scenario families and difficulties | ✅ Completed | Person B (Ayush) |
| API 05 | E07.1 | Person C | `server/app.py` | Add `GET /replay/{episode_id}` endpoint | ENV 09 | 0.75h | endpoint returns completed log for valid episode id | ⬜ Not started | — |
| API 06 | E07.1 | Person C | `server/app.py` | Add WebSocket session handler | ENV 06 | 1.25h | each connection gets isolated environment state and can reset plus step | ✅ Completed | Person B (Ayush) |
| API 07 | E07.1 | Person C | `server/app.py` | Add idle timeout and graceful disconnect cleanup | API 06, ENV 08 | 0.75h | stale connections close cleanly and environment closes without leak | ✅ Completed | Person B (Ayush) |
| API 08 | E07.2 | Person C | `server/Dockerfile` | Build Dockerfile with Python app startup on port 7860 | API 01 to API 07 | 0.75h | local Docker run serves app on port 7860 | ✅ Completed | Person B (Ayush) |
| API 09 | E07.2 | Person C | HF config files | Add Hugging Face Space metadata and deploy instructions | API 08 | 0.5h | Space config is valid for Docker app deployment | ✅ Completed | Person B (Ayush) |
| API 10 | E07.2 | Person C | deployment docs | Deploy live Space and verify health, reset, and step | API 09 | 1h | live Space responds successfully to health and one end to end episode | ⬜ Not started | — |
| API 11 | E07.1 | Person C | tests | Add server endpoint tests and WebSocket smoke test | API 01 to API 07 | 1h | local server tests pass for health, reset, step, invalid payload, and ws connect | ⬜ Not started | — |
| API 12 | E07.2 | Person D | docs | Capture deployment screenshots and public link for README | API 10 | 0.25h | README ready screenshots and live link are available | ⬜ Not started | — |
| API 13 | E07.1 | Person C | `server/app.py` | Add CORS middleware configuration for frontend origins in dev and production | API 01 | 0.25h | frontend on localhost:5173 and HF Space origin can reach the API without CORS errors | ✅ Completed | Person B (Ayush) |
| API 14 | E07.1 | Person C | `server/app.py` | Add REST session management so each user gets isolated environment state | API 02, API 03 | 0.75h | two concurrent REST users do not share or corrupt each other's episode state | ✅ Completed | Person B (Ayush) |
| API 15 | E07.2 | Person C | HF Space repo | Create HF Space README.md with YAML frontmatter specifying `sdk: docker`, `app_port: 7860`, title, and emoji | API 08 | 0.25h | HF Space config is valid and Space launches correctly from the metadata | ✅ Completed | Person B (Ayush) |
| API 16 | E07.2 | Person C | `server/Dockerfile` | Configure Docker to build frontend and serve static assets from FastAPI in a single container | API 08, UI 10 | 0.75h | single Docker container serves both API and frontend on port 7860 | ⬜ Not started | — |
| API 17 | E07.2 | Person C | deployment docs | Document secrets and API key management for hosted Scientist model access in deployment and notebook | API 09 | 0.5h | team knows how to set API keys in HF Space secrets, local env, and Colab secrets | ⬜ Not started | — |
| API 18 | E07.1 | Person C | `server/app.py` | Include judge audit payload plus bounded tool-trace summaries in REST, replay, and WebSocket responses for terminal episodes | API 03, API 05, API 06, ENV 11 | 0.5h | clients receive `judge_notes`, verdict fields, and bounded tool audit data without separate log file access | ⬜ Not started | — |
| API 19 | E07.2 | Person C | `openenv.yaml` and deployment docs | Expose and verify OpenEnv built in `/web` fallback route locally and on HF Space | FND 09, API 08, API 10 | 0.5h | `/web` is documented, reachable, and able to run a seeded episode when the custom UI is unavailable | ⬜ Not started | — |

---

## Epic E08. RL training pipeline and evaluation

### Epic goal
Train the Scientist agent and show observable reward improvement.

### User stories

**US E08.1**  
As a judge, I want a Colab notebook that clearly trains the agent and shows improvement.

**US E08.2**  
As the team, we want a repeatable evaluation workflow for before versus after comparison.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TRN 01 | E08.1 | Person B | `notebooks/train_colab.ipynb` | Create notebook skeleton with setup, connect, train, bounded-tool policy, and plot sections | API 10 | 0.5h | notebook has clear runnable sections in the right order and documents the bounded-tool policy | ⬜ Not started | — |
| TRN 02 | E08.1 | Person B | notebook | Add package install and model setup cell for Unsloth or HF TRL | TRN 01 | 0.75h | notebook installs dependencies without manual edits beyond secrets | ⬜ Not started | — |
| TRN 03 | E08.1 | Person B | notebook or `client.py` | Implement environment client wrapper for reset plus step over WebSocket or REST | API 06 | 1h | notebook can start and finish an episode against local or hosted env and can read tool-aware step payloads | ✅ Completed | — |
| TRN 04 | E08.1 | Person B | notebook | Implement rollout collection loop for Scientist episodes | TRN 03, AGT 01 | 1h | loop collects trajectories, rewards, done signals, and bounded tool traces from frozen evidence packs | ✅ Completed | — |
| TRN 05 | E08.1 | Person B | notebook | Connect rollouts to GRPO or equivalent trainer | TRN 04 | 1.25h | at least one short training run completes without runtime errors while preserving deterministic reward and frozen evidence inputs | ⬜ Not started | — |
| TRN 06 | E08.1 | Person B | notebook | Log episode reward, rigor, feasibility, fidelity, rounds used, and bounded tool metrics | JDG 10, TRN 04 | 0.75h | notebook stores a metrics frame across training episodes including bounded tool metrics | ⬜ Not started | — |
| TRN 07 | E08.2 | Person B | notebook | Plot reward curve and component curves with matplotlib | TRN 06 | 0.5h | plotted image shows visible metrics and can be saved to file | ⬜ Not started | — |
| TRN 08 | E08.2 | Person B | notebook | Add before versus after evaluation on fixed seeds and frozen evidence packs | SCN 11, TRN 05 | 1h | notebook compares baseline and trained policy on the same scenarios and evidence packs | ⬜ Not started | — |
| TRN 09 | E08.2 | Person B | `replicalab/agents/scientist_policy.py` | Add policy loading path for trained adapter or checkpoint | TRN 05 | 0.5h | evaluation can switch between baseline and trained model cleanly | ⬜ Not started | — |
| TRN 10 | E08.2 | Person B | docs | Export plot image and sample logs to `outputs/plots` | TRN 07 | 0.25h | plots are saved and versioned for README use | ⬜ Not started | — |
| TRN 11 | E08.1 | Person C | infra notes | Document environment URL, secrets, and connection troubleshooting | TRN 03 | 0.25h | any team member can run the notebook using the notes | ✅ Completed | Person B (Ayush) |
| TRN 12 | E08.2 | Person D | storytelling | Convert evaluation results into two or three clear bullet insights for judges | TRN 08 | 0.5h | README and demo can state what improved in plain English | ⬜ Not started | — |
| TRN 13 | E08.1 | Person B | `replicalab/client.py` | Create reusable environment client module with `connect()`, `reset()`, `step()`, `close()` over REST and WebSocket | API 06 | 1h | client module can be imported by notebook and other consumers without duplicating connection logic | ✅ Done | 2026-03-08 |
| TRN 14 | E08.1 | Person B | notebook or docs | Select and document base model for Scientist fine tuning with rationale for size, license, and structured output capability | TRN 01 | 0.5h | base model choice is documented and all team members know which model is being trained | ⬜ Not started | — |
| TRN 15 | E08.2 | Person B | notebook | Add agreement rate, invalid action rate, and invalid bounded-tool rate aggregation to evaluation outputs and before versus after comparison | TRN 06, TRN 08, OBS 09 | 0.5h | notebook reports reward, rounds, agreement rate, invalid action rate, and invalid bounded-tool rate for baseline and trained runs | ⬜ Not started | — |

---

## Epic E09. Frontend, UX, replay, and demo views

### Epic goal
Create a judge friendly interface that makes the environment behavior obvious in seconds.

### User stories

**US E09.1**  
As a judge, I want to immediately see the paper, the negotiation, and the score.

**US E09.2**  
As a team, we want a replayable UI for debugging and recording the demo.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UI 01 | E09.1 | Person D | `frontend/src/App.tsx` | Create application shell with three panel layout | FND 03 | 0.75h | app renders layout for paper, conversation, and scoring panels | ⬜ Not started | — |
| UI 02 | E09.1 | Person D | `frontend/src/components/PaperPanel.tsx` | Build original paper summary panel | SCN 12 | 0.75h | panel displays title, hypothesis, method, key finding, and seed | ⬜ Not started | — |
| UI 03 | E09.1 | Person D | `frontend/src/components/ProtocolPanel.tsx` | Build current protocol and diff panel | JDG 09 | 1h | panel highlights current plan fields and updates after each round | ⬜ Not started | — |
| UI 04 | E09.1 | Person D | `frontend/src/components/NegotiationLog.tsx` | Build chat style negotiation log | API 03 or API 06 | 1h | scientist and lab manager messages show in correct order with role styling | ⬜ Not started | — |
| UI 05 | E09.1 | Person D | `frontend/src/components/ScorePanel.tsx` | Build rigor, feasibility, fidelity, and total score cards | JDG 09 | 0.75h | score cards render component values and penalties clearly | ⬜ Not started | — |
| UI 06 | E09.2 | Person D | `frontend/src/components/Controls.tsx` | Build new episode, seed input, scenario selector, and start controls | API 02, API 04 | 0.75h | user can start a chosen scenario with chosen seed from UI | ⬜ Not started | — |
| UI 07 | E09.2 | Person D | `frontend/src/lib/api.ts` | Add REST plus WebSocket client helpers | API 02 to API 06 | 0.75h | UI can connect locally and to the hosted Space | ⬜ Not started | — |
| UI 08 | E09.2 | Person D | `frontend/src/components/ReplayViewer.tsx` | Build replay viewer from completed episode logs | API 05 | 1h | user can load a past episode and step through rounds | ⬜ Not started | — |
| UI 09 | E09.1 | Person D | `frontend/src/components/TrainingResults.tsx` | Add before versus after panel or static result card | TRN 10 | 0.75h | UI can show reward curve image and summary metrics | ⬜ Not started | — |
| UI 10 | E09.1 | Person D | frontend styling | Add clean visual styling with Tailwind plus shadcn compatible primitives and responsive spacing | UI 01 to UI 09, FND 13 | 0.75h | UI is presentable on demo screen without layout breaks and styling stack matches the declared toolchain | ⬜ Not started | — |
| UI 11 | E09.2 | Person C | integration | Serve frontend with backend or configure proxy during dev | UI 07, API 01 | 0.5h | one command local dev works and deployed app serves UI path | ⬜ Not started | — |
| UI 12 | E09.2 | Person D | tests and smoke | Add smoke test checklist for core UI flow | UI 01 to UI 11 | 0.5h | checklist confirms new episode, step, score update, and replay all work | ⬜ Not started | — |
| UI 13 | E09.1 | Person D | `frontend/src/components/JudgeAuditPanel.tsx` or `NegotiationLog.tsx` | Render final Judge audit text and verdict at episode end | JDG 11, API 18 | 0.75h | UI shows a clear end of episode audit without hiding the deterministic score breakdown | ⬜ Not started | — |
| UI 14 | E09.2 | Person D | `frontend/src/components/ReplayViewer.tsx` | Add replay slider or scrubber so judges can move across rounds quickly | UI 08 | 0.5h | user can scrub to any round without replaying the full episode sequentially | ⬜ Not started | — |
| UI 15 | E09.1 | Person D | `frontend/src/components/TrainingResults.tsx` and `Controls.tsx` | Add before versus after training toggle for baseline versus trained views in the demo UI | UI 06, UI 09, TRN 15 | 0.5h | judges can switch between baseline and trained result summaries from the UI | ⬜ Not started | — |

---

## Epic E10. Logging, replay, and observability

### Epic goal
Make behavior inspectable for debugging, judging, and storytelling.

### User stories

**US E10.1**  
As a developer, I want clear logs so I can diagnose why an episode failed.

**US E10.2**  
As a judge, I want the same seeded scenario to be replayable.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OBS 01 | E10.1 | Person C | `replicalab/utils/logging.py` | Standardize episode log schema for transcript, state snapshots, and scores | ENV 09 | 0.5h | every completed episode log contains the same required fields | ⬜ Not started | — |
| OBS 02 | E10.1 | Person C | logging config | Add local log levels and readable console formatting | API 01 | 0.5h | debug logs can be toggled without code edits | 🟡 Partial | — |
| OBS 03 | E10.1 | Person C | replay utilities | Add episode id generation and file naming conventions | OBS 01 | 0.25h | logs never overwrite and are easy to locate | ⬜ Not started | — |
| OBS 04 | E10.2 | Person A | tests | Add deterministic replay test using seed and action sequence | ENV 10 | 0.75h | replay of same seed and actions matches prior state sequence | ✅ Completed | Person B (Ayush) |
| OBS 05 | E10.2 | Person D | UI | Surface episode id and replay link in UI | API 05, UI 08 | 0.5h | user can easily capture or revisit a past episode | ⬜ Not started | — |
| OBS 06 | E10.1 | Person B | notebook | Log training run metadata including model, seed, scenario set, steps, evidence-pack version, and bounded-tool policy | TRN 06 | 0.5h | notebook exports metadata with each run for reproducibility including evidence-pack version and bounded-tool policy | ⬜ Not started | — |
| OBS 07 | E10.1 | Person C | scripts | Add simple local script to run one episode and dump logs | ENV 06, OBS 01 | 0.5h | one command produces a complete local sample log | ⬜ Not started | — |
| OBS 08 | E10.2 | Person D | storytelling | Create static replay screenshots or gifs for README and video | UI 08 | 0.5h | at least two crisp visual assets are ready for docs and demo | ⬜ Not started | — |
| OBS 09 | E10.1 | Person C | `replicalab/utils/logging.py` | Extend episode summary schema with `judge_notes`, `agreement`, `invalid_action_count`, and `invalid_action_rate` for replay and evaluation consumers | OBS 01, JDG 11, ENV 11 | 0.5h | every completed episode log contains the audit payload plus demo and evaluation metrics needed by notebook, UI, and README | ⬜ Not started | — |

---

## Epic E11. Testing and quality gates

### Epic goal
Reduce demo day breakage and keep the environment stable.

### User stories

**US E11.1**  
As the team, we want automated tests around core behavior so merges do not silently break the demo.

**US E11.2**  
As a judge, I want the system to work reliably when clicked live.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TST 01 | E11.1 | Person A | `tests/test_env.py` | Add reset returns valid observations test | ENV 02 | 0.5h | test confirms both roles receive valid structured observations | ✅ Completed | Person B (Ayush) |
| TST 02 | E11.1 | Person A | `tests/test_env.py` | Add valid action step test | ENV 03 to ENV 06 | 0.5h | valid action advances round and returns correct shape | ✅ Completed | Person B (Ayush) |
| TST 03 | E11.1 | Person A | `tests/test_env.py` | Add invalid action handling test | MOD 05, ENV 03 | 0.5h | invalid action yields structured error and environment survives | ✅ Completed | Person B (Ayush) |
| TST 04 | E11.1 | Person A | `tests/test_reward.py` | Add perfect protocol high reward test | JDG 04 | 0.5h | perfect protocol scores higher than baseline and broken protocol | ✅ Completed | Person B (Ayush) |
| TST 05 | E11.1 | Person A | `tests/test_reward.py` | Add zero dimension or penalty behavior test | JDG 04 | 0.5h | zero feasibility or timeout lowers reward as expected | ✅ Completed | Person B (Ayush) |
| TST 06 | E11.1 | Person C | `tests/test_server.py` | Add health plus reset plus step endpoint tests | API 01 to API 03 | 0.75h | API tests pass locally | ⬜ Not started | — |
| TST 07 | E11.1 | Person C | `tests/test_server.py` | Add WebSocket connection and invalid payload tests | API 06 | 0.75h | WebSocket errors are graceful and session stays isolated | ✅ Completed | Person B (Ayush) |
| TST 08 | E11.2 | Person D | manual checklist | Create demo smoke checklist for local and hosted builds | UI 12, API 10 | 0.5h | team can verify full demo in under five minutes | ⬜ Not started | — |
| TST 09 | E11.2 | Person B | notebook checklist | Create notebook smoke test for fresh runtime | TRN 12 | 0.5h | training notebook runs from top with minimal edits and the bounded-tool path works against frozen evidence packs | ⬜ Not started | — |
| TST 10 | E11.2 | all | full run | Execute one integrated test pass before freeze | all prior TST tasks | 1h | environment, UI, Space, and notebook all pass their smoke tests the same day | ⬜ Not started | — |
| TST 11 | E11.1 | Person C | `tests/test_server.py` and `tests/test_env.py` | Add contract tests for judge audit payloads and invalid action metrics in terminal responses and replay logs | API 18, OBS 09 | 0.75h | tests confirm terminal payloads and replay files expose audit notes, agreement, and invalid action metrics | ⬜ Not started | — |
| TST 12 | E11.2 | Person D | manual checklist | Add fallback `/web` smoke step plus replay slider and before versus after toggle checks to demo checklist | API 19, UI 14, UI 15 | 0.5h | checklist verifies custom UI path and fallback UI path are both demo ready | ⬜ Not started | — |

---

## Epic E12. README, demo video, submission packaging

### Epic goal
Turn the technical build into a memorable submission judges can understand quickly.

### User stories

**US E12.1**  
As a judge, I want to understand the environment, reward, and improvement within one minute.

**US E12.2**  
As the team, we want all submission requirements complete and polished.

### Tasks

| ID | Story | Owner | Module or file | Task | Depends on | Estimate | Acceptance criteria | Status | Completed by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DOC 01 | E12.1 | Person D | `README.md` | Write hook, problem statement, and one line product summary | FND 06 | 0.75h | README opening clearly explains the replication crisis and ReplicaLab solution | ⬜ Not started | — |
| DOC 02 | E12.1 | Person D | `README.md` | Add architecture diagram and environment loop explanation | ENV 06, API 10 | 1h | diagram matches actual code and can be understood in under ten seconds | ⬜ Not started | — |
| DOC 03 | E12.1 | Person D | `README.md` | Add setup instructions for local run, Docker, HF Space, and Colab | API 10, TRN 11 | 0.75h | new user can follow setup without asking the team for hidden steps | ⬜ Not started | — |
| DOC 04 | E12.1 | Person D | `README.md` | Add results section with reward curve and before versus after comparison | TRN 10, TRN 12 | 0.75h | README includes at least one figure and one concrete improvement statement | ⬜ Not started | — |
| DOC 05 | E12.2 | Person D | demo script | Write one minute demo script with time coded scenes | UI 10, TRN 12 | 0.5h | demo script fits within one minute and covers problem, environment, and result | ⬜ Not started | — |
| DOC 06 | E12.2 | Person D | demo assets | Capture screen recording clips and narration or captions | DOC 05 | 1h | raw footage covers all key scenes and is visually clear | ⬜ Not started | — |
| DOC 07 | E12.2 | Person D | final video | Edit and upload final one minute YouTube demo | DOC 06 | 1h | video is public or unlisted, shareable, and under the time limit | ⬜ Not started | — |
| DOC 08 | E12.2 | Person C | repo hygiene | Verify repo is public and all required files are committed | API 10, UI 10, TRN 10 | 0.25h | public repo contains code, notebook, docs, and no secret leakage | ⬜ Not started | — |
| DOC 09 | E12.2 | all | submission form prep | Prepare final submission links and partner track selections | DOC 07, DOC 08 | 0.5h | all submission fields have final links and verified accessibility | ⬜ Not started | — |
| DOC 10 | E12.2 | all | dry run | Run final three minute pitch plus two minute Q and A rehearsal | DOC 09 | 0.75h | team can explain tracks, reward, architecture, and results confidently | ⬜ Not started | — |
| DOC 11 | E12.1 | Person D | `README.md` | Add evaluation summary table for average reward, rounds to agreement, invalid action rate, agreement rate, and note the `/web` fallback route as backup demo path | DOC 03, DOC 04, TRN 15, API 19 | 0.5h | README results and setup sections reflect all promised metrics and clearly document the fallback demo route | ⬜ Not started | — |

---

## 9. Critical path

These tasks form the core chain that must not slip:

1. FND 08, FND 09
2. MOD 01 to MOD 05, MOD 11, MOD 12
3. SCN 01 to SCN 09, SCN 13
4. AGT 05 to AGT 07, AGT 11
5. JDG 01 to JDG 05
6. ENV 01 to ENV 06
7. API 01 to API 10, API 13, API 14, API 16
8. TRN 01 to TRN 08, TRN 13, TRN 14
9. DOC 05 to DOC 09  

If any of these are blocked, the team should swarm and unblock immediately.

---

## 10. Suggested work allocation by time block

## Block 1. Foundation and contracts
**Duration target:** first 2 to 3 hours

| Person | Highest priority tasks |
| --- | --- |
| Person A | FND 04, FND 08, FND 09, MOD 01 to MOD 05, MOD 11, MOD 12 |
| Person B | MOD 09, AGT 01, AGT 02, AGT 11 |
| Person C | FND 01 to FND 03, FND 05, FND 07, FND 10, FND 11, FND 12 |
| Person D | FND 06, FND 13, initial UI shell planning, doc stub |

## Block 2. One end to end scenario
**Duration target:** next 3 to 4 hours

| Person | Highest priority tasks |
| --- | --- |
| Person A | SCN 01 to SCN 04, SCN 13, JDG 01 to JDG 04, ENV 01 to ENV 03 |
| Person B | AGT 03 to AGT 07, AGT 10 |
| Person C | API 01 to API 03, API 13, API 14 |
| Person D | UI 01 to UI 05 |

## Block 3. Full environment plus deploy
**Duration target:** next 3 to 4 hours

| Person | Highest priority tasks |
| --- | --- |
| Person A | SCN 05 to SCN 10, JDG 11, ENV 04 to ENV 11 |
| Person B | AGT 08, AGT 09, TRN 01 to TRN 04, TRN 13, TRN 14 |
| Person C | API 04 to API 10, API 15 to API 19 |
| Person D | UI 06 to UI 10, UI 13 |

## Block 4. Training, docs, and polish
**Duration target:** next 3 to 5 hours

| Person | Highest priority tasks |
| --- | --- |
| Person A | TST 01 to TST 05, edge case fixes |
| Person B | TRN 05 to TRN 15, TST 09 |
| Person C | TST 06, TST 07, TST 11, OBS tasks, deployment fixes |
| Person D | UI 11, UI 12, UI 14, UI 15, DOC 01 to DOC 07, DOC 11 |

## Block 5. Final freeze
**Duration target:** final 2 hours

| Person | Highest priority tasks |
| --- | --- |
| All | TST 10 to TST 12, DOC 08 to DOC 11, final bug fixes only |

---

## 11. Acceptance criteria for the whole MVP

The MVP is complete when all of the following are true:

1. `ReplicaLabEnv` supports `reset()`, `step()`, `state()`, and `close()`
2. At least one scenario family runs end to end, with a target of three
3. The Scientist and Lab Manager can complete a multi round negotiation
4. The Judge returns rigor, feasibility, fidelity, total reward, and deterministic audit notes
5. Reward logs are persisted for completed episodes
6. The server exposes health, reset, step, scenarios, and replay endpoints
7. WebSocket sessions work without cross talk
8. The environment is live on a public HF Space on port `7860`
9. The Colab notebook can connect to the environment and complete training
10. The notebook produces at least one reward curve
11. The frontend can demonstrate one episode clearly, and the documented `/web` fallback works if the custom UI fails
12. README explains setup, architecture, and results
13. The repo is public
14. The demo video is uploaded
15. The team can explain which tracks and sponsor fits are being targeted
16. Final terminal responses and replay logs include Judge audit notes and verdict
17. Evaluation outputs report average reward, rounds to agreement, invalid action rate, and agreement rate

---

## 12. Nice to have backlog, only after MVP is green

| Priority order | Task | Why it matters |
| --- | --- | --- |
| 1 | add side by side before versus after comparison in UI | strongest demo improvement visual |
| 2 | add judge plain English explanation panel | better judge readability |
| 3 | add second and third difficulty levels to all templates | stronger world modeling story |
| 4 | add curriculum training path | stronger self improvement story |
| 5 | add Lab Manager orchestrator with specialist subagents for compute, scheduling, budget, or risk review | stronger multi agent depth while preserving the same outer contract |
| 6 | add third agent such as ethics reviewer | potential partner fit extension |
| 7 | add post episode self critique before retry | stronger self improvement story from Blueprint Section 14.2 |
| 8 | add automatic scenario difficulty scaling | adaptive curriculum from Blueprint Section 14.2 |

---

## 13. Risk register and mitigation

| Risk | Likely impact | Mitigation owner | Mitigation plan |
| --- | --- | --- | --- |
| schema churn breaks integration | high | Person A | freeze contracts early and review all changes in PR |
| RL training is unstable | high | Person B | keep the reward deterministic, train Scientist first, and keep the model-backed Lab Manager grounded by the deterministic checker with low-variance settings or frozen weights during Scientist training |
| HF Space deployment issues | high | Person C | test local Docker first and keep `/health` simple |
| frontend polish consumes too much time | medium | Person D | keep fallback to OpenEnv `/web` or a very thin React view |
| reward too noisy or subjective | high | Person A | keep judge deterministic and rubric based |
| final demo breaks live | high | all | keep replay logs and a pre tested demo seed ready |
| too many scenarios | medium | Person A | ship one excellent scenario, then add more only if stable |
| scenario adapters become mini business-logic engines | medium | Person A | keep adapters thin, emit normalized packs only, and push scoring or validation rules back into shared checker modules |
| hybrid Lab Manager drifts from checker truth | medium | Person B | treat checker output as source of truth, derive final action fields from validated checker results, and use model-backed text only for negotiation language and alternatives |

---

## 14. Handoff contracts between workstreams

### Environment to frontend contract
The backend must expose:

1. initial observation
2. current round
3. conversation log
4. current proposed protocol
5. score breakdown
6. episode id
7. replay payload
8. CORS headers allowing frontend origin in dev and production

### Environment to training contract
The environment client must expose:

1. `reset(seed, template, difficulty)`
2. `step(action)`
3. reward
4. done
5. final info including component scores
6. API key or secret configuration for hosted-model access in both hosted and notebook environments

### Scenario to judge contract
Every scenario must provide:

1. normalized scenario pack
2. success criteria
3. allowed substitutions
4. constraints and resources
5. hidden reference spec
6. scenario id and seed

---

## 15. Team meeting rhythm

| Meeting | Duration | Purpose |
| --- | --- | --- |
| kickoff sync | 15 min | confirm scope, owners, blockers |
| integration sync | 10 min every 2 to 3 hours | merge timing and interface checks |
| pre demo sync | 15 min | decide the exact demo path and backup path |
| freeze sync | 10 min | only high severity fixes after this point |

---

## 16. Final recommendation on staffing focus

If the team gets overloaded, protect this order:

1. environment core
2. reward engine
3. server and deployment
4. training notebook
5. minimal UI
6. README
7. demo video
8. extra scenarios
9. extra polish

The project wins on **clarity and working proof**, not on the largest number of features.

---

## 17. One sentence team mission

**Build a deterministic OpenEnv world where a Scientist learns, through RL, to negotiate high quality technical plans with a constraint-aware Lab Manager across seeded domains, starting with mathematics and machine learning.**
