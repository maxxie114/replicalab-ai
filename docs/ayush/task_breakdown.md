# Person B (Ayush) Task Breakdown and Execution Plan

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

All dependency references below are taken directly from the source of truth.
No assumptions from other documents are used to reclassify blocked status.

---

## 1. Blocking Status

`FND 08`, `FND 09`, `MOD 09`, `SCN 11`, and `AGT 01` are now complete.
The scenario prerequisite bundle (`SCN 01` to `SCN 10`) also exists in the
repo, so Ayush no longer waits on `SCN 09` to start prompt-layer work.

Ayush now has one fully unblocked task:

1. `AGT 03` -- highest leverage next task inside the Scientist chain

The prompt and Lab Manager workstream continues to assume a normalized scenario
pack below the stable outer contract, so Ayush-owned prompting should be
assembled from mapped scenario data rather than hard-coded to one domain.

---

## 2. Active Now

| ID | Task | Depends On | Why It Is Ready | Est |
|----|------|-----------|-----------------|-----|
| AGT 03 | Parse plus retry for malformed output | MOD 09, AGT 02 | The parser and observation formatter are now both complete | 0.75h |

**Total: 1 task, 0.75h**

---

## 3. Internal Ayush Chain After AGT 03

These are blocked only by earlier Ayush-owned work.

| ID | Task | Depends On | Blocked By | Est |
|----|------|-----------|-----------|-----|
| AGT 08 | Prompt formatting and parse tests | AGT 01 to AGT 04 | Person B: AGT 03 | 0.75h |

**Total: 1 task, 0.75h**

---

## 4. Still Blocked by Kian (Person A) or Mixed A+B Work

| ID | Task | Depends On | Remaining External Deliverable | Est |
|----|------|-----------|-------------------------------|-----|
| JDG 10 | Expose component metrics for training plots | JDG 05, JDG 07 | `JDG 05` from Kian and `JDG 07` from Max | 0.5h |

**Total: 1 task, 0.5h**

### What to ask Kian for first

1. `JDG 05` and `JDG 06` -- unlock `JDG 10` and later `AGT 10`
2. `SCN 13` -- deepens the booking-conflict layer for the Lab Manager path
3. `ENV 01` -- makes the real environment path available beyond the stub server

---

## 5. Mixed Chain After AGT 05 and Judge Work

These depend on both Ayush-owned work and remaining upstream work.

| ID | Task | Depends On | Blocked By | Est |
|----|------|-----------|-----------|-----|
| AGT 10 | Write domain-neutral prompt text files for all 3 roles | AGT 01, AGT 07, JDG 06 | Person A: JDG 06 | 0.75h |

**Total: 1 task, 0.75h**

---

## 6. Blocked by Max (Person C)

Cannot proceed until Max delivers the server and deployment pieces.

| ID | Task | Depends On | Max Deliverable | Est |
|----|------|-----------|----------------|-----|
| TRN 01 | Notebook skeleton | API 10 | Deployed HF Space | 0.5h |
| TRN 03 | Env client wrapper in notebook | API 06 | WebSocket handler against the real env | 1h |
| TRN 13 | `client.py` reusable module | API 06 | WebSocket handler against the real env | 1h |

**Total: 3 tasks, 2.5h**

### What to ask Max for first

1. `API 06` -- unblocks `TRN 03` and `TRN 13`
2. `API 10` -- unblocks `TRN 01`

---

## 7. Deep Training Chain

These execute in strict order once Person A, Person C, and earlier Ayush tasks
are done.

| Order | ID | Task | Depends On | Est |
|-------|----|------|-----------|-----|
| 1 | TRN 02 | Package install and model setup cell | TRN 01 | 0.75h |
| 2 | TRN 14 | Select and document base model (notebook side) | TRN 01 | 0.5h |
| 3 | TRN 04 | Rollout collection loop | TRN 03, AGT 01 | 1h |
| 4 | TRN 05 | Connect rollouts to GRPO trainer | TRN 04 | 1.25h |
| 5 | TRN 06 | Log episode metrics | JDG 10, TRN 04 | 0.75h |
| 6 | TRN 07 | Plot reward curves | TRN 06 | 0.5h |
| 7 | TRN 08 | Before vs after eval on fixed seeds | SCN 11, TRN 05 | 1h |
| 8 | TRN 09 | Policy loading for trained checkpoint | TRN 05 | 0.5h |
| 9 | TRN 10 | Export plots to outputs/plots | TRN 07 | 0.25h |
| 10 | TRN 15 | Agreement and invalid action rate aggregation | TRN 06, TRN 08, OBS 09 | 0.5h |
| 11 | OBS 06 | Log training run metadata | TRN 06 | 0.5h |

**Total: 11 tasks, 7.5h**

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

### Phase 2: Active now

6. `AGT 03`

### Phase 3: After AGT 03

7. `AGT 08`

### Phase 4: After judge work

8. `AGT 10`
9. `JDG 10`

### Phase 5: After Max lands `API 06` and `API 10`

10. `TRN 13`
11. `TRN 01`
12. `TRN 02`
13. `TRN 03`
14. `TRN 14`

### Phase 6: Training pipeline

15. `TRN 04`
16. `TRN 05`
17. `TRN 06`
18. `TRN 07`
19. `TRN 08`
20. `TRN 09`
21. `TRN 10`
22. `TRN 15`
23. `OBS 06`

### Phase 7: Final notebook validation

24. `TST 09`

---

## 10. Summary Table

| Category | Count | Hours |
|----------|-------|-------|
| Active now | 1 | 0.75h |
| Internal Ayush chain after AGT 03 | 1 | 0.75h |
| Blocked by Kian or mixed A+B work | 1 | 0.5h |
| Mixed chain after AGT 05 and judge work | 1 | 0.75h |
| Blocked by Max | 3 | 2.5h |
| Deep training chain | 11 | 7.5h |
| Blocked by Kush | 1 | 0.5h |
| **Total remaining** | **19** | **13.25h** |

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
