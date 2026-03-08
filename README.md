---
title: ReplicaLab
emoji: 🧪
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# ReplicaLab

**A multi-agent constraint-aware planning environment built on [OpenEnv](https://github.com/openenv)**

> *How do we adapt a plan without breaking the objective?*

ReplicaLab trains an agent to negotiate high-quality plans under real constraints. The initial domain focus is mathematics and machine learning, with finance and trading design in offline or backtest form as the third scenario family. Physics and biology remain later adapters once the core normalized scenario layer is stable.

## Current Build Status

- The repository is now past the foundation stage and has a working real environment plus deterministic judge pipeline.
- The Python package foundation is verified through editable install plus full test-suite checks.
- Shared contracts currently live in `replicalab/models.py`, with the signed-off freeze in `docs/fnd08_frozen_json_contract.md`.
- `server/app.py` now serves the real `ReplicaLabEnv` by default, with the legacy stub retained only as a fallback safety path.
- `openenv.yaml` exists and passes local OpenEnv validation.
- Local Docker validation has been completed for the server image on port `7860`.
- Hugging Face Spaces deployment is live at `https://ayushozha-replicalab.hf.space` with all endpoints verified.
- The frozen outer contract remains stable while the internal scenario engine moves toward a normalized scenario pack.
- The planned Lab Manager path is hybrid: model-backed negotiation language plus deterministic feasibility grounding.

## Team Ownership

| Owner | Current focus |
|------|----------------|
| Kian (Person A) | Shared schemas, validation, normalized scenario engine, judge logic |
| Person B (Ayush) | Contract freeze, domain-neutral Scientist prompting and parsing, notebook and client path |
| Max (Person C) | Repo/runtime setup, frontend shell, server and deployment plumbing |
| Kush (Person D) | README and demo docs, UI shell planning, polish and presentation assets |

---

## Architecture

<p align="center">
  <img src="./architecture.svg" alt="ReplicaLab Architecture" width="100%"/>
</p>

---

## How It Works

Each episode simulates a negotiation between two agents inside a constrained technical scenario:

| Role | Type | Responsibility |
|------|------|----------------|
| **Scientist** | Trainable model policy | Proposes plans, asks questions, and preserves objective quality |
| **Lab Manager** | Hybrid model-backed policy with deterministic grounding | Negotiates revisions while the checker enforces feasibility and constraint truth |
| **Judge** | Deterministic rubric engine | Scores the final plan on Rigor, Feasibility, and Fidelity |

### Episode Lifecycle

1. **Reset** -- `reset(seed)` generates a normalized scenario pack, mapped role observations, and a hidden reference spec
2. **Scientist observes** -- Task summary, experiment or benchmark goal, conversation history, current plan
3. **Lab Manager observes** -- Resource, scheduling, staffing, and policy constraints mapped from the same normalized pack
4. **Negotiation** -- Multiple rounds of proposals, counteroffers, and questions
5. **Agreement or timeout** -- Both accept, or the round limit is reached
6. **Reward** -- Judge scores the final plan against the hidden reference spec

### Reward Formula

```
total_reward = 10 * rigor * feasibility * fidelity + efficiency_bonus + communication_bonus - penalties
```

The **multiplicative core** prevents fake wins: a theoretically strong but impossible plan scores low, and a cheap but invalid plan also scores low.

### Internal normalization rule

The outer action and observation models stay stable. Domain-specific content is converted into a normalized scenario pack first, then mapped into the current `ScientistObservation` and `LabManagerObservation` contracts. Prompts are assembled from that normalized data rather than hard-coded per domain.

---

## Getting Started

This section mixes verified foundation commands with planned end-to-end commands. As of 2026-03-08, the verified local path is the editable Python install plus the shared-model import smoke test.

### Prerequisites

- Python 3.10+
- Node.js 18+ (for the frontend)
- Docker (for deployment)
- A Google Colab account (for RL training)

### Installation

```bash
# Clone the repository
git clone https://github.com/Ayush10/replicalab-ai.git
cd replicalab-ai

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -e ".[dev]"
```

### Verified Foundation Smoke Test

```bash
python -c "from replicalab.models import ScientistAction, LabManagerAction; print('imports_ok')"
```

### Running the Environment Server

```bash
# Planned command once server wiring lands
python -m server.app
```

The server is intended to start at `http://localhost:7860` once the server task chain is complete.

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

The React UI is intended to start at `http://localhost:5173` once the frontend shell and Vite config are in place.

### Running Tests

```bash
pytest tests/
```

---

## Training the Scientist

RL training improves the Scientist agent's ability to negotiate effective, feasible plans.

### Selected base model

- **Primary Scientist model:** `Qwen3-4B`
- **Stretch fallback:** `Qwen3-8B`
- **Decision record:** `docs/agt11_scientist_model_selection.md`

### Quick Start (Google Colab)

1. Open `notebooks/train_colab.ipynb` in Google Colab
2. Connect to a GPU runtime
3. Run all cells -- the notebook handles environment setup, rollout, and training via TRL/Unsloth with GRPO

### Training Loop

```
Environment resets -> Scientist proposes -> Lab Manager responds -> ... -> Episode ends -> Reward computed -> Policy updated
```

**Target behaviors over training:**
- Ask better questions before committing to a plan
- Preserve critical checks, assumptions, and required steps
- Choose realistic substitutions when a preferred method or resource is unavailable
- Reach agreement in fewer rounds
- Avoid impossible or over-budget plans

---

## Scenario System

Scenarios are generated deterministically from a seed. Each template first emits a normalized scenario pack with:

- `task_summary`
- `success_criteria`
- `constraints`
- `resources`
- `allowed_substitutions`
- `hidden_reference_spec`

Difficulty scaling should then mechanically tighten constraints, remove resources, or add conflicts instead of changing the outer contract or prompt structure.

| Difficulty | Description |
|------------|-------------|
| **Easy** | Most required resources are present and tradeoffs are light |
| **Medium** | Some missing items, tighter budgets or time, and at least one meaningful conflict |
| **Hard** | Multiple shortages, sharper tradeoffs, and serious scheduling or resource conflicts |

### Included Scenario Templates

| Template | Domain | Example Task |
|----------|--------|--------------------|
| `math_reasoning` | Mathematics | Proof planning under tool, review, and time constraints |
| `ml_benchmark` | Machine learning | Model evaluation with dataset, compute, and time constraints |
| `finance_trading` | Finance and trading | Offline strategy and backtest planning under risk and capital limits |

---

## Project Structure

```
replicalab-ai/
├── README.md
├── architecture.svg
├── pyproject.toml
├── openenv.yaml
├── replicalab/
│   ├── __init__.py
│   ├── models.py              # Action, Observation, State schemas
│   ├── client.py              # OpenEnv client wrapper
│   ├── prompts/
│   │   ├── scientist.txt      # Scientist system prompt
│   │   ├── lab_manager.txt    # Lab Manager response templates
│   │   └── judge.txt          # Judge rubric prompt
│   ├── scenarios/
│   │   ├── templates.py       # Normalized scenario template layer
│   │   ├── math_reasoning.py  # Mathematics scenarios
│   │   ├── ml_benchmark.py    # ML benchmark scenarios
│   │   └── finance_trading.py
│   ├── scoring/
│   │   ├── rubric.py          # Main scoring engine
│   │   ├── rigor.py           # Objective-validity scorer
│   │   ├── feasibility.py     # Constraint feasibility scorer
│   │   └── fidelity.py        # Hidden-reference fidelity scorer
│   ├── agents/
│   │   ├── scientist_policy.py
│   │   ├── lab_manager_policy.py
│   │   └── judge_policy.py
│   ├── env/
│   │   └── replicalab_env.py  # OpenEnv environment implementation
│   └── utils/
│       ├── seed.py
│       ├── validation.py
│       └── logging.py
├── server/
│   ├── app.py                 # FastAPI + WebSocket server
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── components/
│       └── pages/
├── notebooks/
│   └── train_colab.ipynb      # RL training notebook
└── tests/
    ├── test_env.py
    ├── test_reward.py
    ├── test_scenarios.py
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

**Live deployment:** https://ayushozha-replicalab.hf.space

The app is deployed on HF Spaces with `sdk: docker` on port `7860`.

```bash
# Verify the live Space
curl https://ayushozha-replicalab.hf.space/health
# → {"status":"ok","env":"real"}
```

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
| **Google Colab** | Training notebook |

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
