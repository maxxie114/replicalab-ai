# ReplicaLab Project Map

> Living reference of every module, class, function, and relationship.
> Updated after each implementation session.
>
> **Last updated:** 2026-03-07

## Module Index

| File | What it covers |
|------|---------------|
| [models.md](models.md) | Data contracts — actions, observations, protocol, reward, episode state |
| [scenarios.md](scenarios.md) | Scenario generation — templates, constraints, resources, hidden specs |
| [agents.md](agents.md) | Agent policies — scientist prompt/parse/retry, lab manager feasibility/suggest/compose |
| [validation.md](validation.md) | Protocol validation — deterministic checks against scenario constraints |
| [scoring.md](scoring.md) | Judge scoring — rigor, feasibility, fidelity (NOT YET IMPLEMENTED) |
| [server.md](server.md) | FastAPI server — REST + WebSocket endpoints, stub environment |
| [frontend.md](frontend.md) | React UI — dashboard, episode viewer, components |
| [config.md](config.md) | Shared constants — rounds, budget, timeouts |
| [tests.md](tests.md) | Test coverage — 87 tests across 6 files |

## Dependency Graph

```
server/app.py
 ├── replicalab.config
 ├── replicalab.models
 ├── replicalab.scenarios (generate_scenario, available_scenario_families)
 └── replicalab.agents (check_feasibility, suggest_alternative, compose_lab_manager_response)

replicalab/agents/scientist_policy.py
 ├── replicalab.models (ScientistAction, ScientistObservation, Protocol, ConversationEntry)
 └── replicalab.scenarios (NormalizedScenarioPack)

replicalab/agents/lab_manager_policy.py
 ├── replicalab.models (LabManagerAction, LabManagerActionType, Protocol)
 ├── replicalab.scenarios (NormalizedScenarioPack)
 └── replicalab.utils.validation (ValidationResult, validate_protocol)

replicalab/scenarios/templates.py
 ├── replicalab.config (MAX_BUDGET, MAX_ROUNDS)
 ├── replicalab.models (ScientistObservation, LabManagerObservation)
 ├── replicalab.scenarios.{math_reasoning, ml_benchmark, finance_trading}
 └── replicalab.utils.seed (seed_rng)

replicalab/utils/validation.py
 ├── replicalab.models (Protocol)
 └── replicalab.scenarios.templates (NormalizedScenarioPack)

replicalab/scoring/           <-- NOT YET IMPLEMENTED
 ├── replicalab.models (Protocol, RewardBreakdown)
 ├── replicalab.scenarios (NormalizedScenarioPack, HiddenReferenceSpec)
 └── replicalab.agents.lab_manager_policy (check_feasibility, FeasibilityCheckResult)
```

## File Tree (implemented only)

```
replicalab/
 ├── __init__.py              (empty)
 ├── config.py                (shared constants)
 ├── models.py                (25 classes — all data contracts)
 ├── agents/
 │   ├── __init__.py          (re-exports from submodules)
 │   ├── scientist_policy.py  (AGT 01-04: prompt, formatter, parser, retry, baseline)
 │   └── lab_manager_policy.py(AGT 05-07: feasibility, suggest, compose)
 ├── scenarios/
 │   ├── __init__.py          (re-exports from templates)
 │   ├── templates.py         (NormalizedScenarioPack, generate_scenario, apply_difficulty)
 │   ├── math_reasoning.py    (2 cases: Cauchy-Schwarz, Jensen's inequality)
 │   ├── ml_benchmark.py      (2 cases: AG News TinyBERT, CIFAR-10 ResNet-18)
 │   └── finance_trading.py   (2 cases: SPY/QQQ mean-reversion, momentum futures)
 ├── scoring/                 <-- EMPTY (JDG 01-03 not yet built)
 │   └── .gitkeep
 └── utils/
     ├── seed.py              (deterministic RNG from SHA256)
     └── validation.py        (MOD 05: protocol validation, 5 checks)

server/
 └── app.py                   (FastAPI + WebSocket + _StubEnv)

frontend/
 ├── package.json             (React 19, Three.js, Framer Motion, Recharts, Tailwind)
 ├── src/
 │   ├── App.tsx              (router: /, /episode, /episode/:id)
 │   ├── types/index.ts       (TypeScript interfaces mirroring Python models)
 │   ├── lib/
 │   │   ├── api.ts           (REST + WebSocket client + mock data generators)
 │   │   ├── audio.ts         (audio utilities)
 │   │   └── utils.ts         (shared helpers)
 │   ├── components/          (15 React components)
 │   └── pages/               (DashboardPage, EpisodePage)
 └── vite.config.ts

tests/
 ├── test_config.py           (3 tests)
 ├── test_models.py           (15 tests)
 ├── test_scenarios.py        (8 tests)
 ├── test_validation.py       (13 tests)
 ├── test_scientist_policy.py (18 tests)
 └── test_lab_manager_policy.py(13 tests)
```

## Task Completion Status

| Area | Done | Remaining | Key gaps |
|------|------|-----------|----------|
| Models (MOD) | MOD 01-05, 09, 11-12 | MOD 06 | Semantic validators for impossible plans |
| Scenarios (SCN) | SCN 01-12 | SCN 13 | Booking/scheduling data model |
| Agents (AGT) | AGT 01-07, 11 | AGT 08-10 | LLM-backed scientist, model selection |
| Judge (JDG) | — | JDG 01-08 | Entire scoring engine |
| Environment (ENV) | — | ENV 01-11 | Entire real environment |
| Server (API) | API 01-04, 06 (partial) | API 05, 07-10 | Replay, auth, rate limiting |
| Frontend (FND) | FND 01-10 | — | Complete |
| Training (TRN) | — | TRN 01-18 | Entire RL pipeline |
