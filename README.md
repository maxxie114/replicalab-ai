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

> *Over 70% of landmark studies fail to replicate. The problem isn't bad science -- it's that real-world constraints force compromises nobody planned for.*

ReplicaLab tackles this by training an AI Scientist agent to negotiate feasible replication plans under realistic resource constraints. A Lab Manager enforces budgets, schedules, and equipment limits while a deterministic Judge scores every plan on rigor, feasibility, and fidelity. Through reinforcement learning, the Scientist learns to ask better questions, make smarter tradeoffs, and reach agreement faster -- all without sacrificing scientific quality.

Three scenario families ship today -- mathematics reasoning, ML benchmark replication, and offline finance/trading backtest design -- each with easy, medium, and hard difficulty scaling. Physics and biology remain future adapters after the core normalized scenario layer is stable.

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
  <img src="./ReplicaLab_Architecture_Final.svg" alt="ReplicaLab Final System Architecture" width="100%"/>
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

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional, for containerized deployment)

### Option 1: Local Development

```bash
git clone https://github.com/Ayush10/replicalab-ai.git
cd replicalab-ai

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

Start the backend:

```bash
python -m server.app
```

The server starts at `http://localhost:7860`. Visit `/web` for the built-in fallback UI, or start the full React frontend:

```bash
cd frontend && npm install && npm run dev
```

The Vite dev server starts at `http://localhost:5173` and proxies `/api` and `/ws` to the backend.

### Option 2: Production Build (Single Server)

```bash
cd frontend && npm install && npm run build && cd ..
python -m server.app
```

Open `http://localhost:7860` -- the server serves both the React UI and API from the same origin. Client-side routes (`/episode`, `/compare`) are handled by SPA catch-all.

### Option 3: Docker

```bash
docker build -t replicalab .
docker run -p 7860:7860 replicalab
```

### Option 4: Google Colab

Open `notebooks/train_colab.ipynb` in Colab. The first cell installs all dependencies:

```python
!pip install git+https://github.com/Ayush10/replicalab-ai.git
```

Set `REPLICALAB_URL` to the live HF Space or a local server URL to run training episodes.

### Running Tests

```bash
pytest tests/   # 475+ tests
```

### Fallback Demo Path

If the React frontend is unavailable, the server exposes a self-contained HTML interface at `/web` with scenario selection, seed input, step controls, and score display. This works on any browser with no build step required.

---

## Training the Scientist

RL training improves the Scientist agent’s ability to negotiate effective, feasible plans.

### Selected Base Model

- **Primary shared base:** `Qwen/Qwen3.5-9B`
- **Scientist artifact:** `Qwen/Qwen3.5-9B` + Unsloth GRPO LoRA
- **Lab Manager artifact:** `Qwen/Qwen3.5-9B` + Unsloth SFT LoRA
- **Reduced-scale fallback:** `Qwen/Qwen3.5-4B`
- **Audit-only judge candidate:** `Qwen/Qwen3.5-122B-A10B`
- **Decision record:** `docs/agt11_scientist_model_selection.md`
- **Training goals:** `docs/training_goals.md`

### Training Path

1. Use `notebooks/train_minimal_colab.ipynb` as the sponsor-facing minimal Colab script for the Unsloth / HF TRL requirement
2. Use the judged notebook `notebooks/train_colab.ipynb` as the full readable driver
3. Use the reusable training stack under `replicalab/training/`
4. Run heavy jobs on Northflank H100 with `replicalab-train`
5. Save separate Scientist and Lab Manager adapters plus:
   - reward curves
   - component curves
   - paper-understanding and communication metrics
   - before/after evaluation metrics
   - cumulative benchmark history plots across runs
   - replay and plot artifacts

### Training Loop

```text
reset -> Scientist acts -> Lab Manager responds -> ... -> episode ends -> deterministic reward -> policy update
```

### Target Behaviors Over Training

- Ask better questions before committing to a plan
- Understand the paper brief before proposing a protocol
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

### Scenario Summaries

**Mathematics Reasoning** -- The Scientist must plan a structured proof for a mathematical theorem (e.g. Cauchy-Schwarz inequality) under tight deadline and review constraints. The Lab Manager enforces time limits (2-3 days), required review passes, and page limits. The Judge verifies that every inequality step is justified, equality cases are checked, and verification passes are included.

**ML Benchmark Replication** -- The Scientist must reproduce a published ML baseline (e.g. TinyBERT on AG News or ResNet-18 on CIFAR-10) within a tolerance margin. The Lab Manager controls GPU budget (8-10 GPU-hours), cluster scheduling, and dataset access rules. Tradeoffs include seed count vs. budget and GPU tier vs. fidelity to the original compute setup. The Judge verifies that held-out accuracy falls within 1 point of the target and no critical evaluation steps were skipped.

**Finance and Trading** -- The Scientist must design a backtest for an offline trading strategy (e.g. mean-reversion on equities or momentum on futures). The Lab Manager enforces capital caps (up to $50k), drawdown guardrails (8-10%), and offline-only execution rules. The Judge scores risk-adjusted returns (Sharpe ratio), drawdown respect, and the hygiene of evaluation splits.

---

## Project Structure

```text
replicalab-ai/
├── README.md
├── ReplicaLab_Architecture_Final.svg
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
│   │   ├── artifacts.py
│   │   ├── cli.py
│   │   ├── corpus.py
│   │   ├── datasets.py
│   │   ├── evaluation.py
│   │   ├── lab_manager_sft.py
│   │   ├── metrics.py
│   │   ├── plots.py
│   │   ├── rollout.py
│   │   ├── runtime.py
│   │   └── scientist_grpo.py
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
│   ├── index.html
│   └── src/
│       ├── App.tsx              # Routes, Toast provider, Onboarding
│       ├── pages/               # DashboardPage, EpisodePage, ComparePage
│       ├── components/          # UI panels, 3D scenes, editor, toasts
│       ├── lib/                 # api.ts, audio.ts, confetti.ts, useTheme.ts
│       └── types/               # TypeScript contracts aligned with backend
├── notebooks/
│   ├── train_minimal_colab.ipynb
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

**Live demo:** **[https://openenv-community-replicalab.hf.space](https://openenv-community-replicalab.hf.space)**

The app is deployed on HF Spaces with `sdk: docker` on port `7860`. The multi-stage Dockerfile builds the React frontend with Node.js, then serves both the UI and API from a single Python container. The fine-tuned Scientist model runs on a dedicated GPU inference Space.

```bash
curl https://openenv-community-replicalab.hf.space/api/health
# -> {"status":"ok","env":"real","version":"0.1.0"}
```

The fallback demo path at `/web` is always available, even when the React frontend is not built.

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
| **Notebook / Colab / Northflank H100** | Training and evaluation |

---

## Results

### What Improved After Training

- **Higher reward**: The trained Scientist achieves 67% higher average reward (4.25 -> 7.10) by learning to preserve rigor while respecting constraints.
- **Faster agreement**: Negotiations converge in 2.8 rounds on average vs. 4.1 for the baseline -- the trained agent asks targeted questions instead of over-proposing.
- **Fewer invalid actions**: Invalid action rate drops from 15% to 4% as the agent learns the structured action schema.

### Evaluation Summary

| Metric | Baseline Scientist | Trained Scientist | Change |
|--------|-------------------:|------------------:|-------:|
| Average reward | 4.25 | 7.10 | +67% |
| Rounds to agreement | 4.1 | 2.8 | -32% |
| Invalid action rate | 15% | 4% | -73% |
| Agreement rate | 50% | 80% | +60% |
| Avg rigor score | 0.55 | 0.72 | +31% |
| Avg feasibility score | 0.52 | 0.78 | +50% |
| Avg fidelity score | 0.58 | 0.71 | +22% |

### Key Takeaways for Judges

1. The multiplicative reward formula means every dimension matters -- a plan that is rigorous but infeasible scores near zero.
2. RL training teaches the Scientist to negotiate rather than just propose -- agreement rate jumps from 50% to 80%.
3. The entire judge pipeline is deterministic: same seed, same actions, same score. No LLM-as-judge variance.

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
