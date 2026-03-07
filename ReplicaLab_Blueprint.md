# ReplicaLab

**A multi-agent scientific replication environment built on OpenEnv**

---

## Overview

ReplicaLab is a virtual scientific replication world. Each episode generates an original experiment and a constrained lab, then two agents negotiate a replication plan:

- A **Scientist** agent that protects scientific validity.
- A **Lab Manager** agent that protects cost, equipment, time, staffing, and feasibility.

They negotiate over multiple rounds. If they converge on a sound, feasible protocol, the episode yields a high reward. If they fail, overspend, or strip away critical scientific elements, the reward stays low.

The real-world motivation is the **replication crisis**: published protocols describe ideal conditions, but real labs face missing tools, tight budgets, booking conflicts, reagent shortages, and limited personnel. ReplicaLab trains an agent to answer a single question:

> *How do we adapt an experiment without breaking the science?*

---

## Hackathon Track Alignment

ReplicaLab touches four of the five OpenEnv Hackathon problem statements.

### Primary Tracks

| Track | Fit |
|---|---|
| **Multi-Agent Interactions** | Two roles hold different private information and must negotiate toward consensus. Strongest fit. |
| **World Modeling (Professional)** | The agent reasons inside a professional world with hidden constraints. Very strong fit. |

### Supporting Tracks

| Track | Fit |
|---|---|
| **Long-Horizon Planning** | The agent must ask, revise, recover, and converge across multiple rounds rather than solving in one step. |
| **Self-Improvement** | The same environment trains the Scientist so its behavior improves over repeated episodes. |

**Demo framing:** Lead with Multi-Agent + World Modeling. Support with Long-Horizon + Self-Improvement.

---

## Why This Is an Environment

ReplicaLab is not a prompt. It satisfies all five properties of a proper environment:

1. **State** — Current paper, lab constraints, round number, negotiation history, proposed protocol, spent budget, remaining stock, done flag.
2. **Actions** — The Scientist can propose, revise, ask questions, or accept. The Lab Manager can report feasibility, suggest substitutions, reject, or accept.
3. **Transitions** — Each action mutates the world: budget consumed, protocol updated, round counter incremented, dialogue history extended.
4. **Observations** — Each role sees a different partial view of the world (partially observable).
5. **Reward** — The environment scores the quality of the final plan.

OpenEnv provides exactly this pattern: typed `Action`, `Observation`, and `State` models with `reset()`, `step()`, and `state()` methods, wrapped in FastAPI + WebSocket serving with per-session instances.

---

## Episode Lifecycle

A single episode unfolds as follows:

1. **Reset** — `reset(seed=42)` creates one paper template, one lab constraint set, and one hidden evaluation rubric.
2. **Scientist observes** — Paper summary, experiment goal, conversation history, current proposed protocol.
3. **Lab Manager observes** — Budget, equipment, booking calendar, reagents, staff, safety rules, current proposal.
4. **Scientist acts** — Proposes, revises, asks, or accepts.
5. **Lab Manager responds** — Reports feasibility, suggests substitutions, or accepts.
6. **State updates** — Environment transitions.
7. **Repeat** for a fixed number of rounds or until both sides accept (or timeout).
8. **Reward returned** — The environment scores the final protocol.

### Key Design Decision

For the MVP, only the **Scientist is trained**.

| Role | Implementation |
|---|---|
| **Scientist** | Trainable LLM policy |
| **Lab Manager** | Deterministic rule-based policy with readable responses |
| **Judge** | Deterministic rubric engine, with optional LLM explanation layer |

This gives stable environment dynamics and clean reward signals for a hackathon setting.

---

## The Three Roles

### A. Scientist Agent

The Scientist protects scientific quality. It reasons about essential controls, safe sample-size reductions, valid substitutions, and the minimum viable version of an experiment that still tests the claim.

**Action schema:**

```json
{
  "action_type": "propose_protocol | revise_protocol | request_info | accept",
  "sample_size": 60,
  "controls": ["vehicle_control", "positive_control"],
  "technique": "WST1",
  "duration_days": 7,
  "required_equipment": ["plate_reader", "incubator"],
  "required_reagents": ["drug_A", "WST1_kit"],
  "questions": ["Do we have a plate reader free this week?"],
  "rationale": "WST1 is an acceptable substitute for MTT in this template"
}
```

### B. Lab Manager Agent

The Lab Manager protects feasibility: budget, equipment availability, machine bookings, reagent delivery timelines, and staffing. For the MVP this is a rule-based system (deterministic constraint checker, substitution suggester, cost estimator, booking checker, natural-language response template) to keep environment behavior stable and debuggable.

### C. Judge

The Judge is a **rubric-backed scorer**, not a free-form LLM.

It receives the original paper, hidden minimum-viable replication spec, final proposed protocol, actual lab constraints, and negotiation transcript. It outputs:

- Rigor score
- Feasibility score
- Fidelity score
- Final reward
- Audit notes

An optional LLM explanation layer can translate the audit into readable notes for the UI.

---

## Reward Structure

### Core Dimensions

| Dimension | What It Measures | Examples |
|---|---|---|
| **Rigor** | Did the agent preserve the important science? | Sample size, controls, method validity, statistics, duration |
| **Feasibility** | Can this lab actually run the plan? | Budget, equipment availability, stock, timeline, staffing |
| **Fidelity** | How close is the plan to the original experiment? | Same technique or valid substitute, same control logic, similar sample size, same study aim |

### Formula

```
total_reward = 10 × rigor × feasibility × fidelity
             + efficiency_bonus
             + communication_bonus
             − penalties
```

The multiplicative core prevents fake wins: a scientifically perfect but impossible plan scores low, and a cheap but scientifically broken plan also scores low.

### Penalties

Applied for timeout, exceeding budget, invalid structure, missing critical controls, and bad substitutions.

---

## Reinforcement Learning

RL improves the **Scientist policy**.

1. Environment resets.
2. Scientist generates an action.
3. Lab Manager replies.
4. Episode ends with a reward.
5. Training loop adjusts the Scientist toward higher-reward behaviors.

**Target behaviors over training:**

- Ask better questions before committing.
- Preserve critical controls.
- Choose realistic substitutions.
- Reach agreement faster.
- Avoid over-budget plans.

TRL supports OpenEnv-style training through a custom `rollout_func` for stepping through an environment with environment-computed rewards. GRPO supports custom reward functions. Unsloth provides GRPO notebooks designed for this kind of training.

---

## Self-Improvement

For the MVP, self-improvement means the Scientist gets measurably better through repeated episodes. That is sufficient for the track.

**Stretch goals (time permitting):**

- **Curriculum learning** — Easy scenarios first, then medium, then hard.
- **Self-critique** — After a failed episode, the agent reviews a short audit and retries.
- **Self-play** — Train both Scientist and Lab Manager.

---

## World Modeling and Long-Horizon Planning

### World Modeling

The agent must build an internal model of a hidden world: what the lab has, what it lacks, what is booked, what is scientifically critical, what is flexible, and how choices affect future feasibility. None of this is fully visible, so the agent infers the world through negotiation.

### Long-Horizon Planning

The best move is rarely the first move. A strong Scientist follows a chain: understand the paper goal, ask what is available, propose a first plan, revise after constraints surface, trade off cost against rigor, and reach agreement before timeout. That is multi-step planning, not a single answer.

---

## Constraint System

Constraints come from a **scenario generator**. Each scenario template defines required equipment, optional substitutes, must-keep controls, minimum sample size, minimum duration, typical costs, and likely bottlenecks. Difficulty modifies them:

| Difficulty | Description |
|---|---|
| **Easy** | Lab has most of what is needed. |
| **Medium** | Some missing items, tighter budget, tighter time. |
| **Hard** | Major shortages, bigger tradeoffs, booking conflicts. |

For the MVP, the world is **deterministic within each episode**: the initial seed defines the entire scenario, resources change only through agent choices, and there are no random surprise events. This makes debugging, replay, and demo presentations much stronger.

---

## Interface Design

### Layout

| Section | Content |
|---|---|
| **Left Panel** | Original paper summary, challenge label, seed, round counter |
| **Middle Panel** | Negotiation log (Scientist in blue, Lab Manager in green, Judge audit at end) |
| **Right Panel** | Current proposed protocol, lab inventory snapshot, budget bar, score bars for rigor/feasibility/fidelity |
| **Bottom Controls** | New episode, seed selector, scenario selector, replay slider, before-vs-after training toggle |

### Implementation

- **Demo UI:** Custom React + Vite app hitting the FastAPI + WebSocket backend.
- **Fallback UI:** OpenEnv built-in `/web` interface.

---

## Folder Structure

```
replicalab/
├── README.md
├── pyproject.toml
├── openenv.yaml
├── .dockerignore
├── replicalab/
│   ├── __init__.py
│   ├── models.py
│   ├── client.py
│   ├── prompts/
│   │   ├── scientist.txt
│   │   ├── lab_manager.txt
│   │   └── judge.txt
│   ├── scenarios/
│   │   ├── templates.py
│   │   ├── cell_biology.py
│   │   ├── ml_benchmark.py
│   │   └── behavioral_psych.py
│   ├── scoring/
│   │   ├── rubric.py
│   │   ├── rigor.py
│   │   ├── feasibility.py
│   │   └── fidelity.py
│   ├── agents/
│   │   ├── scientist_policy.py
│   │   ├── lab_manager_policy.py
│   │   └── judge_policy.py
│   ├── env/
│   │   └── replicalab_env.py
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
│       ├── App.tsx
│       ├── components/
│       └── pages/
├── notebooks/
│   └── train_colab.ipynb
└── tests/
    ├── test_env.py
    ├── test_reward.py
    ├── test_scenarios.py
    └── test_server.py
```

---

## Toolchain

| Tool | Purpose |
|---|---|
| **OpenEnv 0.2.1** | Environment class and server |
| **Hugging Face Spaces** | Public hosting (Docker SDK, port 7860) |
| **Docker** | Packaging server + frontend |
| **Google Colab** | Required training notebook |
| **TRL / Unsloth** | RL training on the Scientist |
| **FastAPI + WebSocket** | Live environment serving |
| **React + Vite** | Frontend |
| **Tailwind + shadcn/ui** | Styling |
| **Matplotlib** | Reward curves in Colab |
| **CSV / JSONL logs** | Replay and debugging |

---

## Scope

### In Scope (MVP)

1. One working OpenEnv environment
2. Three scenario templates (Cell Biology, ML Benchmark, Behavioral Psychology)
3. Trainable Scientist agent
4. Rule-based Lab Manager
5. Judge rubric engine
6. Reward logging
7. HF Space deployment
8. Colab RL notebook with reward curve
9. Public repo
10. One-minute YouTube demo
11. Clean README
12. React UI or polished `/web` fallback

### Stretch (Only If Ahead)

- LLM Lab Manager
- Live replay mode
- Side-by-side before-vs-after comparison
- More scenario families
- Judge explanation LLM
- Curriculum learning

### Out of Scope

- Proving a real paper is true or false
- Parsing arbitrary papers from the internet
- Full autonomous lab automation
- Real wet-lab execution
- Full multi-model self-play
- Enterprise workflow integrations

---

## Team Roles (4 People)

| Person | Ownership |
|---|---|
| **P1: Environment + Reward** | Scenario engine, environment state, constraint logic, reward logic, tests |
| **P2: RL + Model** | Scientist policy prompt, TRL/Unsloth notebook, rollout loop, reward curves, before/after evaluation |
| **P3: Backend + Deploy** | FastAPI, WebSocket, Docker, HF Space, logging, replay API |
| **P4: Frontend + Story** | React/Vite UI, visualization, demo flow, README, YouTube demo |

Everyone shares bug fixing, testing, and final polish.

---

## Build Sequence

1. Freeze the environment schema
2. Implement one scenario end to end
3. Add reward and logs
4. Add rule-based Lab Manager
5. Add Scientist baseline
6. Connect Colab training
7. Add React UI
8. Deploy to HF
9. Record demo
10. Write README

---

## Judging Criteria and Demo Strategy

| Criterion (Weight) | How ReplicaLab Scores |
|---|---|
| **Environment Innovation (40%)** | Partially observable, multi-role scientific negotiation world, not a toy chat task. |
| **Storytelling (30%)** | Scientist vs. Lab Manager is instantly understandable. |
| **Training Improvement (20%)** | Same seed, before training vs. after training, visible reward improvement. |
| **Pipeline Setup (10%)** | Clean reward formula, structured logs, reproducible Colab notebook. |

### Demo Flow

1. New episode with a specific seed.
2. Paper appears, Scientist proposes.
3. Lab Manager pushes back.
4. Negotiation unfolds over rounds.
5. Judge shows final scores.
6. Replay same seed with the trained model.
7. Trained model asks smarter questions, avoids bad substitutions, earns higher reward.

---

## Success Metrics

| Metric | Untrained Scientist | Trained Scientist |
|---|---|---|
| Average reward | Lower | Higher |
| Rounds to agreement | More | Fewer |
| Invalid action rate | Higher | Lower |
| Agreement rate | Lower | Higher |

---

## Sponsor Alignment

| Target | Rationale |
|---|---|
| **Halluminate** | True multi-actor environment with different beliefs and information per role. |
| **Snorkel AI** | Simulated experts in the loop; the Scientist learns by interacting with expert-style roles. |
| **Fleet AI** (alternate) | Judge as an explicit oversight layer monitoring and explaining the two agents. |

---

## Real-World Applications

**Target users:** Biotech teams, pharma R&D groups, contract research organizations, university labs, cloud lab platforms, AI labs training scientific agents.

**Potential revenue paths:** Enterprise experiment planning software, evaluation benchmark licensing, simulation API access, experiment design copilot products.

---

## The Simple Explanation

Imagine two kids want to bake a cake. One knows the **recipe**. The other knows what is in the **kitchen**. The recipe kid says they need eggs, milk, flour, and chocolate. The kitchen kid says there is no chocolate, but there is cocoa. They talk and make the best cake they can. If the cake stays tasty, uses what the kitchen has, and finishes on time, they earn a star.

ReplicaLab is that, but for science.
