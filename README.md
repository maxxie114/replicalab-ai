---
title: ReplicaLab
emoji: "🧪"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# ReplicaLab

**A multi-agent constraint-aware planning environment built on [OpenEnv](https://github.com/openenv)**

> *How do we adapt a plan without breaking the objective?*

ReplicaLab trains a Scientist policy to negotiate better plans under real constraints. The initial domain focus is mathematics and machine learning, with offline finance and trading design as the third scenario family. Physics and biology remain future adapters after the core normalized scenario layer is stable.

## Current Build Status

- The repository is past the foundation stage and has a working real environment plus deterministic judge pipeline.
- The Python package foundation is verified through editable install plus the full test suite.
- Shared contracts live in `replicalab/models.py`, with the signed-off freeze in `docs/fnd08_frozen_json_contract.md`.
- `server/app.py` serves the real `ReplicaLabEnv` by default, with the legacy stub retained only as a fallback path.
- `openenv.yaml` exists and passes local OpenEnv validation.
- Local Docker validation has been completed for the server image on port `7860`.
- Hugging Face Spaces deployment is live at `https://ayushozha-replicalab.hf.space` for the deterministic environment path.
- The frozen outer contract remains stable while the internal scenario engine uses a normalized scenario pack.
- The Lab Manager path is hybrid: deterministic feasibility truth with optional model-backed narrative responses.
- An additive Oracle hybrid layer now exists for optional frontier-model world generation, event injection, Lab Manager narration, and post-mortem analysis while deterministic scoring remains the canonical RL reward path.

## Team Ownership

| Owner | Current focus |
|------|----------------|
| Kian (Person A) | Shared schemas, validation, scenario engine, judge logic |
| Person B (Ayush) | Scientist prompting and parsing, notebook and client path |
| Max (Person C) | Server, deployment, and runtime plumbing |
| Kush (Person D) | Frontend, UI polish, docs, and demo assets |

---

## Architecture

<p align="center">
  <img src="./ReplicaLab_Architecture_v2.svg" alt="ReplicaLab Hybrid Architecture" width="100%"/>
</p>

ReplicaLab uses a **hybrid Oracle architecture**:

- The **Oracle layer** is optional and powers world-building and narrative intelligence:
  - richer scenario generation
  - optional event injection
  - optional model-backed Lab Manager narration
  - optional post-mortem analysis
- The **deterministic core** remains canonical for RL:
  - environment transitions
  - validation
  - grounded Lab Manager feasibility
  - judge scoring and reward math

This satisfies the sponsor-facing “model-driven environment intelligence” direction without making reward noisy or irreproducible.

---

## How It Works

Each episode simulates a negotiation between two agents inside a constrained technical scenario:

| Role | Type | Responsibility |
|------|------|----------------|
| **Scientist** | Trainable model policy | Proposes plans, asks questions, and preserves objective quality |
| **Lab Manager** | Hybrid model-backed policy with deterministic grounding | Negotiates revisions while the checker enforces feasibility and constraint truth |
| **Judge** | Deterministic rubric engine | Scores the final plan on rigor, feasibility, fidelity, and parsimony |
| **Oracle (optional)** | Frontier-model intelligence layer | Generates richer worlds, optional events, optional live LM narration, and post-mortem analysis |

### Episode Lifecycle

1. **Reset**: `reset(seed)` builds a normalized scenario pack and hidden reference spec.
2. **Scientist observes**: task summary, goal, history, and current plan.
3. **Lab Manager observes**: resource, scheduling, staffing, and policy constraints from the same normalized pack.
4. **Negotiation**: multiple rounds of proposals, counteroffers, and questions.
5. **Agreement or timeout**: both accept, or the round limit is reached.
6. **Reward**: the deterministic judge scores the final plan.
7. **Optional Oracle overlays**: event injection, round commentary, and post-mortem may be layered on top without replacing deterministic reward.

### Reward Formula

```text
total_reward = 10 * rigor * feasibility * fidelity * parsimony
             + efficiency_bonus
             + communication_bonus
             - penalties
```

The multiplicative core prevents fake wins: a theoretically strong but impossible plan scores low, and a cheap but invalid plan also scores low. Even when the Oracle layer is enabled, this deterministic path remains canonical for RL training and before/after evaluation.

### Internal Normalization Rule

The outer action and observation models stay stable. Domain-specific content is converted into a normalized scenario pack first, then mapped into the current `ScientistObservation` and `LabManagerObservation` contracts. Prompts are assembled from that normalized data rather than hard-coded per domain.

---

## Getting Started

This section mixes verified foundation commands with planned end-to-end commands.

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker
- A notebook runtime such as Google Colab or the H100-backed Jupyter environment

### Installation

```bash
git clone https://github.com/Ayush10/replicalab-ai.git
cd replicalab-ai

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

### Verified Foundation Smoke Test

```bash
python -c "from replicalab.models import ScientistAction, LabManagerAction; print('imports_ok')"
```

### Running the Environment Server

```bash
python -m server.app
```

The server is intended to start at `http://localhost:7860`.

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
pytest tests/
```

---

## Training the Scientist

RL training improves the Scientist agent’s ability to negotiate effective, feasible plans.

### Selected Base Model

- **Primary Scientist model:** `Qwen3-4B`
- **Stretch fallback:** `Qwen3-8B`
- **Decision record:** `docs/agt11_scientist_model_selection.md`

### Planned Training Path

1. Connect the notebook to the environment via `replicalab/client.py`
2. Collect rollouts with `replicalab/training/rollout.py`
3. Train with **Unsloth or HF TRL**
4. Save:
   - reward curves
   - component curves
   - before/after evaluation metrics
   - replay and plot artifacts

### Training Loop

```text
reset -> Scientist acts -> Lab Manager responds -> ... -> episode ends -> deterministic reward -> policy update
```

### Target Behaviors Over Training

- Ask better questions before committing to a plan
- Preserve critical checks, assumptions, and required steps
- Choose realistic substitutions when preferred resources are unavailable
- Reach agreement in fewer rounds
- Avoid impossible or over-budget plans

---

## Scenario System

Scenarios are generated deterministically from a seed. Each template emits a normalized scenario pack with:

- `task_summary`
- `success_criteria`
- `constraints`
- `resources`
- `allowed_substitutions`
- `hidden_reference_spec`

Difficulty scaling should mechanically tighten constraints, remove resources, or add conflicts instead of changing the outer contract or prompt structure.

| Difficulty | Description |
|------------|-------------|
| **Easy** | Most required resources are present and tradeoffs are light |
| **Medium** | Some missing items, tighter budgets or time, and at least one meaningful conflict |
| **Hard** | Multiple shortages, sharper tradeoffs, and serious scheduling or resource conflicts |

### Included Scenario Templates

| Template | Domain | Example Task |
|----------|--------|--------------|
| `math_reasoning` | Mathematics | Proof planning under tool, review, and time constraints |
| `ml_benchmark` | Machine learning | Model evaluation with dataset, compute, and time constraints |
| `finance_trading` | Finance and trading | Offline strategy and backtest planning under risk and capital limits |

---

## Project Structure

```text
replicalab-ai/
├── README.md
├── ReplicaLab_Architecture_v2.svg
├── pyproject.toml
├── openenv.yaml
├── replicalab/
│   ├── __init__.py
│   ├── models.py                # Action, Observation, State schemas
│   ├── client.py                # OpenEnv client wrapper
│   ├── oracle.py                # Optional frontier-model Oracle wrapper
│   ├── oracle_models.py         # Oracle scenario and post-mortem schemas
│   ├── cache.py                 # Cached Oracle scenario generation
│   ├── prompts/
│   │   ├── scientist.txt
│   │   ├── lab_manager.txt
│   │   ├── judge.txt
│   │   ├── oracle_world_architect.txt
│   │   ├── oracle_adjudicator.txt
│   │   ├── oracle_event_injector.txt
│   │   ├── oracle_post_mortem.txt
│   │   └── oracle_lab_manager.txt
│   ├── scenarios/
│   │   ├── templates.py         # Normalized scenario pack + Oracle adapter
│   │   ├── math_reasoning.py
│   │   ├── ml_benchmark.py
│   │   └── finance_trading.py
│   ├── scoring/
│   │   ├── rubric.py            # Canonical deterministic reward math
│   │   ├── rigor.py
│   │   ├── feasibility.py
│   │   ├── fidelity.py
│   │   └── explain.py
│   ├── agents/
│   │   ├── scientist_policy.py
│   │   ├── lab_manager_policy.py
│   │   ├── lab_manager_agent.py # Optional model-backed Lab Manager wrapper
│   │   └── judge_policy.py
│   ├── env/
│   │   └── replicalab_env.py    # Real env with optional Oracle hooks
│   ├── training/
│   │   └── rollout.py
│   └── utils/
│       ├── seed.py
│       ├── validation.py
│       └── logging.py
├── server/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
├── notebooks/
│   └── train_colab.ipynb
└── tests/
    ├── test_env.py
    ├── test_reward.py
    ├── test_scenarios.py
    ├── test_oracle.py
    ├── test_cache.py
    └── test_server.py
```

---

## Deployment

### Docker

```bash
docker build -f server/Dockerfile -t replicalab .
docker run -p 7860:7860 replicalab
```

### Hugging Face Spaces

**Live deployment:** `https://ayushozha-replicalab.hf.space`

The app is deployed on HF Spaces with `sdk: docker` on port `7860`.

```bash
curl https://ayushozha-replicalab.hf.space/health
# -> {"status":"ok","env":"real"}
```

Current Space deployment is complete for the deterministic environment path. If live Oracle mode is enabled later, the Space will additionally need:

- provider SDK dependencies
- model API-key secrets
- runtime feature flags
- cold-start and latency handling

The deterministic deployment itself does not need to be redesigned.

---

## Toolchain

| Tool | Purpose |
|------|---------|
| **OpenEnv 0.2.1** | Environment class and server |
| **FastAPI + WebSocket** | Live environment serving |
| **TRL / Unsloth** | RL training (GRPO) |
| **React + Vite** | Frontend |
| **Tailwind + shadcn/ui** | Styling |
| **Docker** | Packaging |
| **Hugging Face Spaces** | Public hosting |
| **Notebook / Colab / H100** | Training and evaluation |

---

## Success Metrics

| Metric | Untrained Scientist | Trained Scientist |
|--------|--------------------:|------------------:|
| Average reward | Lower | Higher |
| Rounds to agreement | More | Fewer |
| Invalid action rate | Higher | Lower |
| Agreement rate | Lower | Higher |

---

## Hackathon Track Alignment

| Track | Fit |
|-------|-----|
| **Multi-Agent Interactions** | Two roles with private information negotiate toward consensus |
| **World Modeling (Professional)** | Agent reasons inside a professional world with hidden constraints |
| **Long-Horizon Planning** | Multi-round ask-revise-recover-converge cycle |
| **Self-Improvement** | Scientist measurably improves over repeated episodes |

---

## License

MIT
