# ReplicaLab

**A multi-agent scientific replication environment built on [OpenEnv](https://github.com/openenv)**

> *How do we adapt an experiment without breaking the science?*

ReplicaLab tackles the **replication crisis** in science. Published protocols describe ideal conditions, but real labs face missing equipment, tight budgets, booking conflicts, and reagent shortages. ReplicaLab trains an AI agent to negotiate realistic experiment adaptations while preserving scientific validity.

## Current Build Status

- The repository is still in the foundation stage.
- The Python package foundation is verified through editable install plus shared-model import checks.
- Shared contracts currently live in `replicalab/models.py`, with the draft freeze in `docs/fnd08_frozen_json_contract.md`.
- Frontend shell, server wiring, and `openenv.yaml` are still in progress.

## Team Ownership

| Owner | Current focus |
|------|----------------|
| Person A | Shared schemas, validation, scenario engine, judge logic |
| Person B (Ayush) | Contract freeze, Scientist-side prompting and parsing, notebook and client path |
| Person C | Repo/runtime setup, frontend shell, server and deployment plumbing |
| Person D | README and demo docs, UI shell planning, polish and presentation assets |

---

## Architecture

<p align="center">
  <img src="./architecture.svg" alt="ReplicaLab Architecture" width="100%"/>
</p>

---

## How It Works

Each episode simulates a negotiation between two agents inside a constrained virtual lab:

| Role | Type | Responsibility |
|------|------|----------------|
| **Scientist** | Trainable LLM policy | Proposes replication protocols, preserves scientific rigor |
| **Lab Manager** | Rule-based policy | Enforces budget, equipment, staffing, and feasibility constraints |
| **Judge** | Deterministic rubric engine | Scores the final protocol on Rigor, Feasibility, and Fidelity |

### Episode Lifecycle

1. **Reset** -- `reset(seed)` generates a paper template, lab constraints, and a hidden evaluation rubric
2. **Scientist observes** -- Paper summary, experiment goal, conversation history, current protocol
3. **Lab Manager observes** -- Budget, equipment, calendar, reagents, staff, safety rules
4. **Negotiation** -- Multiple rounds of proposals, counteroffers, and questions
5. **Agreement or timeout** -- Both accept, or the round limit is reached
6. **Reward** -- Judge scores the final protocol

### Reward Formula

```
total_reward = 10 * rigor * feasibility * fidelity + efficiency_bonus + communication_bonus - penalties
```

The **multiplicative core** prevents fake wins: a scientifically perfect but impossible plan scores low, and a cheap but scientifically broken plan also scores low.

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

RL training improves the Scientist agent's ability to negotiate effective, feasible protocols.

### Quick Start (Google Colab)

1. Open `notebooks/train_colab.ipynb` in Google Colab
2. Connect to a GPU runtime
3. Run all cells -- the notebook handles environment setup, rollout, and training via TRL/Unsloth with GRPO

### Training Loop

```
Environment resets -> Scientist proposes -> Lab Manager responds -> ... -> Episode ends -> Reward computed -> Policy updated
```

**Target behaviors over training:**
- Ask better questions before committing to a protocol
- Preserve critical controls (positive/negative controls, minimum sample sizes)
- Choose realistic substitutions (e.g., WST1 instead of MTT when appropriate)
- Reach agreement in fewer rounds
- Avoid over-budget plans

---

## Scenario System

Scenarios are generated deterministically from a seed. Each template defines:

- Required equipment and valid substitutes
- Must-keep controls and minimum sample sizes
- Typical costs and likely bottlenecks
- Difficulty-scaled constraints

| Difficulty | Description |
|------------|-------------|
| **Easy** | Lab has most of what is needed |
| **Medium** | Some missing items, tighter budget and time |
| **Hard** | Major shortages, bigger tradeoffs, booking conflicts |

### Included Scenario Templates

| Template | Domain | Example Experiment |
|----------|--------|--------------------|
| `cell_biology` | Wet lab | Drug cytotoxicity assay (MTT/WST1) |
| `ml_benchmark` | Compute lab | Model evaluation with GPU/dataset constraints |
| `behavioral_psych` | Human subjects | Survey replication with participant pool limits |

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
│   │   ├── templates.py       # Base scenario template
│   │   ├── cell_biology.py    # Cell biology scenarios
│   │   ├── ml_benchmark.py    # ML benchmark scenarios
│   │   └── behavioral_psych.py
│   ├── scoring/
│   │   ├── rubric.py          # Main scoring engine
│   │   ├── rigor.py           # Scientific rigor scorer
│   │   ├── feasibility.py     # Lab feasibility scorer
│   │   └── fidelity.py        # Protocol fidelity scorer
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
docker build -t replicalab .
docker run -p 7860:7860 replicalab
```

### Hugging Face Spaces

The app is configured for HF Spaces with `sdk: docker` on port `7860`. Push the repo to your HF Space to deploy.

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
