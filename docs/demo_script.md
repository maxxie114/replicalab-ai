# ReplicaLab -- One-Minute Demo Script

Total duration: **60 seconds**

---

## Scene 1: Hook (0:00 -- 0:08)

**Visual**: Dashboard landing page with 3D molecule background and three animated characters.

**Narration / Caption**:
> "Most ML papers can't be reproduced. ReplicaLab trains an AI agent to negotiate realistic replication plans -- under real constraints."

---

## Scene 2: The Cast (0:08 -- 0:16)

**Visual**: Scroll down to "Meet the Cast" section. Hover over each tilt card to show the 3D effect.

**Narration / Caption**:
> "Three roles: Dr. Elara proposes plans. Takuma enforces GPU budgets, schedules, and resource limits. Aldric judges the result."

---

## Scene 3: Start an Episode (0:16 -- 0:24)

**Visual**: Click "Run Episode". Select ML Benchmark, Medium difficulty. Click "Start Episode".

**Narration / Caption**:
> "Each episode generates a seeded scenario. Here: replicate a ViT fine-tuning result with a limited GPU budget."

---

## Scene 4: Negotiation (0:24 -- 0:38)

**Visual**: Show the CharacterStage with Scientist and Lab Manager animated. Scroll through the negotiation log showing the proposal, feasibility report, and revised protocol.

**Narration / Caption**:
> "The Scientist proposes 5 seeds on A100s. The Lab Manager flags the budget overshoot. The Scientist revises down to 3 seeds -- staying within budget while keeping A100 for compute fidelity."

---

## Scene 5: Judge Verdict (0:38 -- 0:48)

**Visual**: Click "Step". Show the Judge appearing center-stage with gavel sound. Score card reveals total reward 8.12 with R/F/D breakdown.

**Narration / Caption**:
> "Judge Aldric scores the plan: 85% rigor, 93% feasibility, 80% fidelity. Total reward: 8.12 out of 10. The multiplicative formula means every dimension matters."

---

## Scene 6: Training Results (0:48 -- 0:56)

**Visual**: Show the Training Results panel with the before/after toggle. Click the toggle to show baseline vs. trained curves.

**Narration / Caption**:
> "After RL training with GRPO, the Scientist improves: 67% higher reward, 32% fewer rounds, and the invalid action rate drops from 15% to 4%."

---

## Scene 7: Close (0:56 -- 1:00)

**Visual**: Return to dashboard hero with all three characters. Show the HF Space URL.

**Narration / Caption**:
> "ReplicaLab. An OpenEnv world where agents learn to negotiate science."

---

## Backup Notes

- **Pre-tested seed**: Use seed `42` with `ml_benchmark` / `medium` for a reliable demo.
- **Fallback**: If the custom UI fails, navigate to `/web` on the HF Space for the OpenEnv built-in interface.
- **Audio**: The app has built-in sound effects. Keep speakers on for a richer demo, or mute if presenting in a noisy venue.
