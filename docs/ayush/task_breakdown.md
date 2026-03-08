# Person B (Ayush) Task Breakdown and Execution Plan

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

All dependency references below are taken directly from the source of truth.
No assumptions from other documents are used to reclassify blocked status.

---

## 1. Blocking Status

`FND 08`, `FND 09`, `MOD 09`, `SCN 11`, `AGT 01`, `AGT 02`, `AGT 03`,
`AGT 04`, `AGT 05`, `AGT 06`, `AGT 07`, `AGT 08`, `AGT 10`, `AGT 11`,
`TRN 13`, `TRN 03`, `TRN 04`, `TRN 01`, `TRN 02`, and `TRN 14` are now
complete.
The scenario prerequisite bundle (`SCN 01` to `SCN 10`) also exists in the
repo, so Ayush no longer waits on `SCN 09` to start prompt-layer work.

Ayush now has two fully unblocked tasks:

1. `TRN 05` -- connect collected rollouts to the trainer now that `TRN 04` is complete
2. `JDG 10` -- expose component metrics now that `JDG 07` is closed

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
| TRN 05 | Connect rollouts to GRPO trainer | TRN 04 | The reusable GRPO stack now exists, so the remaining work is validating a short real run and adapter-loading path | 1.25h |
| JDG 10 | Expose component metrics for training plots | JDG 05, JDG 07 | Reward logging is closed and the training metrics layer now exists, so notebook-facing aggregation can be finalized | 0.5h |

**Total: 2 tasks, 1.75h**

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

1. No active Kian dependency is blocking the Ayush lane right now

---

## 5. Previously Blocked by Max (Person C)

| ID | Task | Depends On | Max Deliverable | Est |
|----|------|-----------|----------------|-----|
| - | No Ayush tasks are currently blocked on Max-only deliverables | - | - | - |

**Total: 0 tasks, 0h**

### What to ask Max for first

1. `OBS 09` -- needed later for `TRN 15`
2. `API 18` -- needed later for UI and replay-facing audit consumers

---

## 7. Deep Training Chain

These execute in strict order once Person A, Person C, and earlier Ayush tasks
are done.

| Order | ID | Task | Depends On | Est |
|-------|----|------|-----------|-----|
| 1 | JDG 10 | Notebook-facing component metrics | JDG 05, JDG 07 | 0.5h |
| 2 | TRN 05 | Connect rollouts to GRPO trainer | TRN 04 | 1.25h |
| 3 | TRN 06 | Log episode metrics plus bounded tool metrics | JDG 10, TRN 04 | 0.75h |
| 4 | TRN 07 | Plot reward curves | TRN 06 | 0.5h |
| 5 | TRN 08 | Before vs after eval on fixed seeds and frozen evidence packs | SCN 11, TRN 05 | 1h |
| 6 | TRN 09 | Policy loading for trained checkpoint | TRN 05 | 0.5h |
| 7 | TRN 10 | Export plots to outputs/plots | TRN 07 | 0.25h |
| 8 | TRN 15 | Agreement, invalid action, and invalid bounded-tool rate aggregation | TRN 06, TRN 08, OBS 09 | 0.5h |
| 9 | OBS 06 | Log training run metadata | TRN 06 | 0.5h |

**Total: 9 tasks, 5.75h**

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
18. `TRN 01`
19. `TRN 02`
20. `TRN 14`

### Phase 3: Active now

21. `JDG 10`
22. `TRN 05`

### Phase 4: Training pipeline

23. `TRN 06`
24. `TRN 07`
25. `TRN 08`
26. `TRN 09`
27. `TRN 10`
28. `TRN 15`
29. `OBS 06`

### Phase 5: Final notebook validation

30. `TST 09`

---

## 10. Summary Table

| Category | Count | Hours |
|----------|-------|-------|
| Active now | 2 | 1.75h |
| Internal Ayush chain after API 06 | 1 | 0.5h |
| Blocked by Kian or mixed A+B work | 0 | 0h |
| Blocked by Max | 0 | 0h |
| Remaining downstream training chain | 6 | 3.5h |
| Blocked by Kush | 1 | 0.5h |
| **Total remaining** | **10** | **6.25h** |

---

## 11. Base Model Assumptions

### Trainable Scientist policy

Primary model: **Qwen3-8B**

| Constraint | Qwen3-8B | Qwen3-4B (fallback) |
|-----------|----------|---------------------|
| Northflank H100 training (BF16, ~3-4x inference mem) | Strong primary fit with more reasoning headroom | Also fits, but lower-capacity default |
| Colab or low-memory debug path | Heavier | Easier reduced-scale fallback |
| Structured JSON output | Better | Good |
| V2 dual-role reuse | Shared base for Scientist and Lab Manager | Debug-only fallback |

Use `Qwen3-8B` for the primary Northflank H100 runs and keep `Qwen3-4B` as the
reduced-scale fallback for notebook demos or lighter debugging.

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
- The active V2 setup now uses one shared base model (`Qwen3-8B`) with
  separate Scientist and Lab Manager adapters.

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
| `replicalab/training/*.py` | Reusable training stack and Northflank job entrypoints |
