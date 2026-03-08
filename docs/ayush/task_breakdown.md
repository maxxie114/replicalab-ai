# Person B (Ayush) Task Breakdown and Execution Plan

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

All dependency references below are taken directly from the source of truth.
No assumptions from other documents are used to reclassify blocked status.

---

## 1. Blocking Status

`FND 08`, `FND 09`, `MOD 09`, `SCN 11`, `AGT 01`, `AGT 02`, `AGT 03`,
`AGT 04`, `AGT 05`, `AGT 06`, `AGT 07`, `AGT 08`, `AGT 10`, `AGT 11`,
`TRN 13`, `TRN 03`, and `TRN 04` are now complete.
The scenario prerequisite bundle (`SCN 01` to `SCN 10`) also exists in the
repo, so Ayush no longer waits on `SCN 09` to start prompt-layer work.

Ayush now has one fully unblocked task:

1. `TRN 05` -- connect collected rollouts to the trainer now that `TRN 04` is complete

The prompt and Lab Manager workstream continues to assume a normalized scenario
pack below the stable outer contract, so Ayush-owned prompting should be
assembled from mapped scenario data rather than hard-coded to one domain.

Bounded-tool scope note:

1. Ayush-owned prompt, training, and client tasks now assume bounded `search`,
   `code_check`, and `image_inspection` capabilities.
2. Training must still use frozen evidence packs and deterministic reward.
3. Live web search is for validation or demo-time evidence only, not the core
   reward loop.
4. Audio remains out of scope.

---

## 2. Active Now

| ID | Task | Depends On | Why It Is Ready | Est |
|----|------|-----------|-----------------|-----|
| TRN 05 | Connect rollouts to GRPO trainer | TRN 04 | The rollout worker is complete, so the next step is wiring those trajectories into the trainer loop | 1.25h |

**Total: 1 task, 1.25h**

---

## 3. Internal Ayush Chain After API 06

These are blocked only by earlier Ayush-owned work.

| ID | Task | Depends On | Blocked By | Est |
|----|------|-----------|-----------|-----|
| TRN 09 | Policy loading for trained checkpoint | TRN 05 | Person B: TRN 05 | 0.5h |

**Total: 1 task, 0.5h**

---

## 4. Still Blocked by Kian (Person A) or Mixed A+B Work

| ID | Task | Depends On | Remaining External Deliverable | Est |
|----|------|-----------|-------------------------------|-----|
| - | No Ayush tasks are currently blocked on Kian-only deliverables | - | - | - |

**Total: 0 tasks, 0h**

### What to ask Kian for first

1. `SCN 13` -- deepens the booking-conflict layer for the Lab Manager path
2. `ENV 10` -- strengthens environment regression coverage before training ramps
3. `JDG 11` -- structured final audit payload for env, API, logs, and UI

---

## 5. Blocked by Max (Person C)

Cannot proceed until Max delivers the remaining server and deployment pieces.

| ID | Task | Depends On | Max Deliverable | Est |
|----|------|-----------|----------------|-----|
| JDG 10 | Expose component metrics for training plots | JDG 05, JDG 07 | `JDG 07` from Max | 0.5h |
| TRN 01 | Notebook skeleton | API 10 | Deployed HF Space or stable hosted env URL | 0.5h |

**Total: 2 tasks, 1h**

### What to ask Max for first

1. `API 10` -- unlocks `TRN 01`
2. `JDG 07` -- unlocks `JDG 10`

---

## 7. Deep Training Chain

These execute in strict order once Person A, Person C, and earlier Ayush tasks
are done.

| Order | ID | Task | Depends On | Est |
|-------|----|------|-----------|-----|
| 1 | TRN 01 | Notebook skeleton | API 10 | 0.5h |
| 2 | TRN 02 | Package install and model setup cell | TRN 01 | 0.75h |
| 3 | TRN 14 | Select and document base model (notebook side) | TRN 01 | 0.5h |
| 4 | TRN 04 | Rollout collection loop with frozen evidence packs and bounded tool traces | TRN 03, AGT 01 | 1h |
| 5 | TRN 05 | Connect rollouts to GRPO trainer | TRN 04 | 1.25h |
| 6 | TRN 06 | Log episode metrics plus bounded tool metrics | JDG 10, TRN 04 | 0.75h |
| 7 | TRN 07 | Plot reward curves | TRN 06 | 0.5h |
| 8 | TRN 08 | Before vs after eval on fixed seeds and frozen evidence packs | SCN 11, TRN 05 | 1h |
| 9 | TRN 09 | Policy loading for trained checkpoint | TRN 05 | 0.5h |
| 10 | TRN 10 | Export plots to outputs/plots | TRN 07 | 0.25h |
| 11 | TRN 15 | Agreement, invalid action, and invalid bounded-tool rate aggregation | TRN 06, TRN 08, OBS 09 | 0.5h |
| 12 | OBS 06 | Log training run metadata | TRN 06 | 0.5h |

**Total: 12 tasks, 8h**

---

## 8. Blocked by Kush (Person D)

| ID | Task | Depends On | Kush Deliverable | Est |
|----|------|-----------|-----------------|-----|
| TST 09 | Notebook smoke test for fresh runtime | TRN 12 | Evaluation storytelling and final notebook flow | 0.5h |

**Total: 1 task, 0.5h**

---

## 9. Recommended Execution Order

### Phase 1: Completed

1. `FND 08`
2. `FND 09`
3. `MOD 09`
4. `SCN 11`
5. `AGT 01`
6. `AGT 02`
7. `AGT 03`
8. `AGT 04`
9. `AGT 05`
10. `AGT 06`
11. `AGT 07`
12. `AGT 08`
13. `AGT 11`
14. `TRN 13`
15. `TRN 03`

### Phase 2: Recently completed

16. `AGT 10`
17. `TRN 04`

### Phase 3: Active now

18. `TRN 05`

### Phase 4: After `API 10`

19. `TRN 01`
20. `TRN 02`
21. `TRN 14`

### Phase 5: After judge work

22. `JDG 10`

### Phase 6: Training pipeline

23. `TRN 06`
24. `TRN 07`
25. `TRN 08`
26. `TRN 09`
27. `TRN 10`
28. `TRN 15`
29. `OBS 06`

### Phase 7: Final notebook validation

30. `TST 09`

---

## 10. Summary Table

| Category | Count | Hours |
|----------|-------|-------|
| Active now | 1 | 1.25h |
| Internal Ayush chain after API 06 | 1 | 0.5h |
| Blocked by Kian or mixed A+B work | 0 | 0h |
| Blocked by Max | 2 | 1h |
| Remaining downstream training chain | 8 | 4.75h |
| Blocked by Kush | 1 | 0.5h |
| **Total remaining** | **13** | **8h** |

---

## 11. Base Model Assumptions

### Trainable Scientist policy

Primary model: **Qwen3-4B**

| Constraint | Qwen3-4B | Qwen3-8B (stretch) |
|-----------|----------|-------------------|
| H100 training (BF16, ~3-4x inference mem) | ~14GB weights, ~42-56GB total. Fits 80GB easily | ~19GB weights, ~57-76GB total. Tight |
| Colab T4 (16GB, 4-bit QLoRA) | 5.5GB. Fits comfortably | 6.5GB. Fits but less headroom |
| Structured JSON output | Good | Better |
| RL iteration speed | Fast | Slower |

Qwen3-8B is H100-only stretch. Use only if Qwen3-4B quality is insufficient and
Colab demo uses a reduced-scale fallback.

### Reward

The training reward is always the **deterministic rubric engine** (E05 in the
source of truth). A hosted frontier evaluator may optionally be used for
post-episode explanation and demo audit. The frontier evaluator is never part
of the training reward loop.

### Hybrid Lab Manager

The MVP Lab Manager path is hybrid:

- A deterministic feasibility checker remains the source of truth for
  `feasible`, constraint flags, and any final structured `LabManagerAction`.
- Model-backed response generation is used for negotiation language and
  alternative suggestions, but it does not own truth or reward.
- The reward formula does not change. The deterministic rubric scores the final
  plan against the hidden reference spec regardless of how the Lab Manager
  generates its language.
- Reward does not split into separate Scientist versus Lab Manager objectives.
  Both roles share the same cooperative reward signal.
- If the team later shares one base model across both roles, the pragmatic
  default is one base model (`Qwen3-4B`) with separate role-specific adapters.

### Prompt assembly

Ayush-owned prompts should be assembled from normalized scenario data:

- `task_summary`
- `success_criteria`
- `constraints`
- `resources`
- `allowed_substitutions`

This keeps `AGT 01`, `AGT 02`, and `AGT 10` domain-neutral even when the
scenario families expand from mathematics and machine learning into finance,
physics, or biology.

---

## 12. Files Person B Owns

| File | Purpose |
|------|---------|
| `replicalab/agents/scientist_policy.py` | Trainable Scientist policy |
| `replicalab/agents/lab_manager_policy.py` | Hybrid Lab Manager grounded by deterministic feasibility checks (shared with A) |
| `replicalab/client.py` | Reusable environment client |
| `replicalab/prompts/scientist.txt` | Scientist system prompt |
| `replicalab/prompts/lab_manager.txt` | Lab Manager response templates |
| `replicalab/prompts/judge.txt` | Judge explanation prompt |
| `notebooks/train_colab.ipynb` | RL training notebook (judged asset) |
