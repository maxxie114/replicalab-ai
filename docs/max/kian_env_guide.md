# What We Are Actually Building — For Kian
**From: Max**

---

## The Most Important Thing to Understand

Read the judging criteria:

| Criteria | Weight |
|---|---|
| **Environment Innovation** | **40%** |
| **Storytelling** | **30%** |
| Training showing improvement | 20% |
| Reward and pipeline setup | 10% |

**70% of our score is the environment design and how well we explain it.**

The training is not the product. The model is not the product. **The environment is the product.** The training script exists only to prove the environment works — a curve going up is all we need from it.

This means your job, Kian, is the most important job on the team. Not because the implementation is complex, but because the design has to be genuinely interesting. A clever environment with a mediocre training run beats a mediocre environment with a perfect training run every time.

---

## The Architecture — Same as Before, Different Domain

We are keeping the two-agent structure. That does not change. What changes is the domain: instead of replicating a wet lab experiment, we are replicating and verifying **mathematical results from real papers**.

| Role | Type | What it does |
|---|---|---|
| **Prover** (was: Scientist) | Trainable RL agent | Proposes proof steps and strategies to replicate or verify a mathematical result |
| **Math Consultant** (was: Lab Manager) | Fixed, rule-based, not trained | Simulated expert. Evaluates proof steps, enforces constraints, has preferences that change per episode |

The Prover is the only agent we fine-tune. The Consultant is part of the environment — it acts as a consultant of sorts, giving the Prover feedback, not as a co-learner.

The negotiation loop stays identical:
1. Prover sees the theorem/result and the current proof state
2. Prover proposes a proof step or strategy
3. Consultant evaluates it — is it valid? Does it meet the current constraints and preferences?
4. If yes: state advances, Prover continues
5. If no: Consultant explains why, Prover tries again
6. Episode ends when proof is complete or steps are exhausted

---

## Why This Domain

**Mathematical results from real papers.** Not arbitrary math. Specific, published results — theorems, proofs, derivations — taken from real papers, with known ground truth. The environment asks: can the Prover rediscover and verify this result, under the constraints the Consultant enforces?

This is better than a generic math solver for one reason: **a calculator can solve equations. Nothing but reasoning can construct a proof.** The untrained model is genuinely bad at this. The trained model gets measurably better. The reward signal is real.

It also connects directly to what is happening at the frontier right now. DeepSeek-R1, AlphaProof, OpenAI o3 — reasoning and proof-finding through RL is the most active area in the entire field. Judges from Meta, HuggingFace, and Berkeley will immediately recognize what this environment is pointing at. That recognition is the storytelling.

---

## How This Hits Both Sponsor Tracks

We are targeting two $10,000 partner prizes. The environment is designed to qualify for both.

**Snorkel AI — Simulated Experts-in-the-Loop**
> *"Environment that simulates interactions with real subject-matter experts, with changing requirements and preferences."*

The Math Consultant is the simulated expert. Its requirements change every episode — seeded at reset. One episode the Consultant requires a direct proof and penalises contradiction-based arguments. Another episode it requires minimal steps. Another it restricts which lemmas are permitted. Another it demands a specific level of formal rigour.

The Prover cannot memorise one strategy and apply it every time. It has to read the Consultant's current preferences and adapt. That is exactly what Snorkel AI is asking for.

**Halluminate — Multi-Actor Environments**
> *"Build a realistic environment where an agent interacts with and manages multiple actors to discover and achieve the task."*

Two actors, one task: prove the result. The Prover manages its interaction with the Consultant — deciding when to push a step, when to ask for clarification, when to pivot strategy — in order to discover a valid proof. The collaboration between the two actors is what makes the proof possible. Neither one alone solves it.

---

## What the Environment Needs to Be

The environment presents a mathematical result from a real paper. The Prover attempts to verify or reconstruct it. The Consultant enforces constraints and preferences.

The design decisions that make this environment **innovative** — the 40% — are:

**1. What results do we use?**
Pick 8 to 12 published mathematical results that are formally verifiable. Algebraic identities, number theory results, combinatorial proofs. The key requirement: the ground truth is checkable in code, and there is a space of valid proof strategies, not just one.

**2. What is a proof step / action?**
The Prover does not write free-form text. It selects structured actions — apply a transformation, invoke a lemma, substitute a value, invoke a known identity. The action space is bounded and discrete. This is what makes RL tractable and what makes verification honest.

**3. What does the Consultant enforce?**
Each episode, the Consultant's constraints are seeded. Examples:
- *Lemma budget*: only lemmas from a specific approved list may be used
- *Step budget*: proof must complete within N steps
- *Style preference*: direct proof required, no proof by contradiction
- *Rigour level*: every step must be explicitly justified, no skipping

The Prover sees a description of the current Consultant preferences at the start of each episode. It has to factor them into its proof strategy.

**4. What is the reward?**
- Valid proof step that meets Consultant constraints: small positive
- Invalid step or violated constraint: small negative, plus Consultant feedback
- Complete correct proof within constraints: large positive
- Timeout without a complete proof: zero

The reward is coherent, explainable, and directly tied to the environment's purpose.

**5. What does the Prover observe?**
- The theorem or result to prove
- The Consultant's current preferences and constraints for this episode
- The proof steps taken so far
- The current proof state (what has been established)
- Steps remaining
- The Consultant's feedback on the last step

A human playing this sees exactly the same thing. That is the test of a well-designed environment.

---

## The Three-Stage Demo

**Stage 1 — A human plays it.**
A person sits at the interface, sees a theorem and the Consultant's current constraints, and tries to construct a proof step by step. They get immediate feedback. This validates the environment before any AI touches it and gives us a live interactive demo the judges can try themselves.

**Stage 2 — Replace the human with an untrained LLM.**
The model reads the same inputs, outputs structured proof steps in the same format, gets the same feedback. Record the success rate on 10 fixed problems. This is the baseline.

**Stage 3 — Train with RL and show improvement.**
GRPO on the H100, Llama 3.2 3B or Qwen 2.5 3B, Unsloth. Run the same 10 problems after training. Show the reward curve. Show the improved success rate. The delta is the result.

---

## What the Training Proves

Ayush runs this. The deliverable is simple: a reward curve going up and a before/after success rate comparison on a fixed held-out set of problems. That is the 20%. Nothing more is required.

---

## Stretch Goal — Beat a Paper

If the environment is well-designed and the training signal is clean, this might happen naturally. Published baselines for small models on math reasoning benchmarks exist. If the trained model exceeds one of those numbers, even slightly, that is a concrete result against a peer-reviewed baseline.

Don't build toward it. Just run the evaluation against known benchmarks after training and see what the numbers say.

If it happens, mention it in the demo almost as an aside — let the judges react to it. If it doesn't happen, nothing is lost. The environment is still innovative, the improvement curve is still real, the story is still strong.

Beating a paper is a plus. It is not the plan.

---

## What Kian Needs to Build

Three things, in order:

1. **A set of results.** 10 to 12 mathematical results from real papers, with known proofs, formally verifiable in code. Start simple. Build up.

2. **The Consultant logic.** A seeded rule engine that generates constraints and preferences per episode, evaluates proof steps against them, and returns structured feedback. No LLM required here — deterministic rules are better because they are reproducible and fast.

3. **The episode loop.** Reset picks a result and seeds the Consultant. Step takes a proof action, runs Consultant evaluation, returns reward and new state. Done when proof is complete or steps exhausted.

The implementation details — proof representation, action schema, which symbolic libraries to use — are entirely Kian's call. This document is the why. Kian owns the how.
