# Three-Minute Pitch + Two-Minute Q&A Outline (DOC 10)

## Pitch Structure (3 minutes)

### 1. The Problem (30 seconds)

> "Over 70% of landmark studies fail to replicate. The gap isn't bad science -- it's that real-world constraints force compromises that nobody planned for. Budgets shrink, equipment breaks, timelines slip. The protocol that worked in Theory A fails under Constraint B."

### 2. Our Solution (30 seconds)

> "ReplicaLab is an OpenEnv environment where an AI Scientist learns to negotiate realistic replication plans. A Lab Manager enforces real constraints -- GPU budgets, scheduling conflicts, equipment limits. A deterministic Judge scores every plan. Through RL, the Scientist gets measurably better at navigating tradeoffs."

### 3. Live Demo (60 seconds)

- Show HF Space or local frontend
- Start an ML Benchmark episode (seed 42, medium difficulty)
- Point out the Scientist's proposal and Lab Manager's feasibility report
- Show the Judge scoring: rigor, feasibility, fidelity breakdown
- Toggle to training results: before vs after comparison

### 4. Technical Architecture (30 seconds)

> "Three scenario families -- math, ML, finance -- each with deterministic seed-based generation. The reward formula is multiplicative: 10 x rigor x feasibility x fidelity. Every dimension must score well. The entire judge is deterministic -- same seed, same actions, same score. No LLM-as-judge variance."

### 5. Results (20 seconds)

> "After RL training: 67% higher reward, 32% fewer negotiation rounds, invalid actions drop from 15% to 4%, agreement rate jumps from 50% to 80%."

### 6. Close (10 seconds)

> "ReplicaLab. An OpenEnv world where agents learn to negotiate science."

---

## Anticipated Q&A Topics

| Question | Talking Points |
|----------|---------------|
| Why deterministic scoring? | Noisy rewards make RL unstable. Deterministic judge = reproducible training. Optional Oracle layer adds richness without corrupting the reward signal. |
| How does difficulty scaling work? | Mechanical constraint tightening: budgets shrink, resources go out of stock, scheduling conflicts appear. Same outer contract at every difficulty. |
| What model do you train? | Qwen3-8B with GRPO via Unsloth/TRL. 4B fallback for faster iteration. |
| How many scenarios? | 3 domain families x 3 difficulties x infinite seeds. Each seed produces a unique but deterministic scenario. |
| Why not LLM-as-judge? | Variance. Two runs of the same episode would get different scores. We need a stable reward signal for RL. The optional Oracle post-mortem adds natural language analysis without replacing the score. |
| What's the Lab Manager? | Hybrid: deterministic feasibility checker (ground truth) + optional model narration. Checker output is always the source of truth. |
| Fallback if UI breaks? | `/web` endpoint serves a self-contained HTML interface with no build step. |
