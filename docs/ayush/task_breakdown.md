# Person B (Ayush) Task Breakdown and Execution Plan

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

All dependency references below are taken directly from the source of truth.
No assumptions from other documents are used to reclassify blocked status.

---

## 1. Blocking Status

Per the source of truth, `FND 08` is now complete and `FND 09` has landed in
`openenv.yaml` with OpenEnv-compatible runtime wiring in the repo.
`MOD 01` and `MOD 03` are now complete, so `MOD 09` is immediately unblocked
and the observation side of `AGT 02` is no longer waiting on Person A.
The next Ayush-owned tasks after `MOD 09` are still gated by Kian's remaining
scenario and validation deliverables, starting with `SCN 09` and `MOD 05`.
The prompt and Lab Manager workstream now assumes a normalized scenario pack
below the stable outer contract, so Ayush-owned prompting should be assembled
from mapped scenario data rather than hard-coded to one domain.

---

## 2. Blocked by Kian (Person A)-Led External Dependencies

These tasks are first gated by upstream deliverables, primarily from Kian (Person A).
`JDG 10` also requires Max (Person C) to ship `JDG 07`.

| ID | Task | Depends On | Person A Deliverable | Est |
|----|------|-----------|---------------------|-----|
| AGT 01 | Draft domain-neutral Scientist system prompt | MOD 01, SCN 11 | ScientistAction schema + generate_scenario | 0.75h |
| AGT 05 | Implement deterministic feasibility checker (shared A+B) | SCN 07, MOD 05 | Constraint generator + validation | 1.25h |
| SCN 11 | Create golden scenarios for prompt testing | SCN 09 | generate_scenario() | 0.75h |
| JDG 10 | Expose component metrics for training plots | JDG 05, JDG 07 | Reward breakdown (A) + logging (C) | 0.5h |

**Total: 4 tasks, 3.25h**

### What to ask Kian for first (priority order)

1. **SCN 09** (generate normalized scenario packs) -- unblocks SCN 11 and then AGT 01
2. **SCN 07 + MOD 05** (normalized constraints/resources + validation) -- unblocks AGT 05, AGT 06, AGT 07
3. **JDG 05 + JDG 06** (reward breakdown + explanation) -- unblocks AGT 10 and is only part of the path for JDG 10
4. **SCN 08** (minimum viable replication spec) -- unblocks AGT 06 after AGT 05

---

## 3. Blocked by Person A Then Person B Internal Chain

These depend on Person A deliverables AND on earlier Person B tasks. They unblock
sequentially as both streams deliver.

| ID | Task | Depends On | Blocked By | Est |
|----|------|-----------|-----------|-----|
| AGT 02 | Observation to prompt formatting helper | AGT 01 (B) + MOD 03 (A) | Person B: AGT 01 | 0.75h |
| AGT 03 | Parse plus retry for malformed output | MOD 09 (B) + AGT 02 (B) | Person B: MOD 09, AGT 02 | 0.75h |
| AGT 04 | Baseline heuristic Scientist | AGT 02 (B) | Person B: AGT 02 | 1h |
| AGT 06 | Alternative suggestion logic from allowed substitutions | AGT 05 (A+B), SCN 08 (A) | Person A: SCN 08, Person A+B: AGT 05 | 1h |
| AGT 07 | Model-backed Lab Manager response synthesis | AGT 05 (A+B) | Person A+B: AGT 05 | 0.75h |
| AGT 08 | Prompt formatting and parse tests | AGT 01 to AGT 04 (B) | Person B: AGT 01-04 | 0.75h |
| AGT 10 | Write domain-neutral prompt text files for all 3 roles | AGT 01 (B) + AGT 07 (B) + JDG 06 (A) | Person A: JDG 06, Person B: AGT 01, AGT 07 | 0.75h |
| AGT 11 | Select and document base model | AGT 01 (B) | Person B: AGT 01 | 0.5h |

**Total: 8 tasks, 6.25h**

---

## 4. Blocked by Max (Person C) (Needs Server/API)

Cannot proceed until Person C delivers the server and deployment.

| ID | Task | Depends On | Person C Deliverable | Est |
|----|------|-----------|---------------------|-----|
| TRN 01 | Notebook skeleton | API 10 | Deployed HF Space | 0.5h |
| TRN 03 | Env client wrapper in notebook | API 06 | WebSocket handler | 1h |
| TRN 13 | client.py reusable module | API 06 | WebSocket handler | 1h |

**Total: 3 tasks, 2.5h**

### What to ask Max for first (priority order)

1. **API 06** (WebSocket handler) -- unblocks TRN 03 and TRN 13
2. **API 10** (deployed HF Space) -- unblocks TRN 01 notebook skeleton

---

## 5. Deep Training Chain (Sequential After Upstream Deliverables)

These execute in strict order once Person A, Person C, and earlier Person B tasks
are done.

| Order | ID | Task | Depends On | Est |
|-------|----|------|-----------|-----|
| 1 | TRN 02 | Package install and model setup cell | TRN 01 (B) | 0.75h |
| 2 | TRN 14 | Select and document base model (notebook side) | TRN 01 (B) | 0.5h |
| 3 | TRN 04 | Rollout collection loop | TRN 03 (B), AGT 01 (B) | 1h |
| 4 | TRN 05 | Connect rollouts to GRPO trainer | TRN 04 (B) | 1.25h |
| 5 | TRN 06 | Log episode metrics | JDG 10 (B), TRN 04 (B) | 0.75h |
| 6 | TRN 07 | Plot reward curves | TRN 06 (B) | 0.5h |
| 7 | TRN 08 | Before vs after eval on fixed seeds | SCN 11 (B), TRN 05 (B) | 1h |
| 8 | TRN 09 | Policy loading for trained checkpoint | TRN 05 (B) | 0.5h |
| 9 | TRN 10 | Export plots to outputs/plots | TRN 07 (B) | 0.25h |
| 10 | TRN 15 | Agreement and invalid action rate aggregation | TRN 06 (B), TRN 08 (B), OBS 09 (C) | 0.5h |
| 11 | OBS 06 | Log training run metadata | TRN 06 (B) | 0.5h |

**Total: 11 tasks, 7.5h**

---

## 6. Blocked by Kush (Person D)

| ID | Task | Depends On | Person D Deliverable | Est |
|----|------|-----------|---------------------|-----|
| TST 09 | Notebook smoke test for fresh runtime | TRN 12 | Evaluation storytelling insights | 0.5h |

**Total: 1 task, 0.5h**

---

## 7. Recommended Execution Order

All phases are gated by the listed external dependency being delivered first.

### Phase 1: Active now

1. **FND 08** -- Completed and signed off
2. **FND 09** -- Completed in `openenv.yaml`
3. **MOD 09** -- Build output parser for ScientistAction

### Phase 2: After Kian delivers SCN 09

4. **SCN 11** -- Create golden scenarios for prompt testing
5. **AGT 01** -- Draft domain-neutral Scientist system prompt
6. **AGT 11** -- Select and document base model

### Phase 3: After AGT 01

7. **AGT 02** -- Build observation to prompt formatter
8. **AGT 03** -- Add parse plus retry logic
9. **AGT 04** -- Build baseline heuristic Scientist
10. **AGT 08** -- Write tests for prompt formatting and parsing

### Phase 4: After Kian delivers SCN 07 + MOD 05 + SCN 08 + JDG 05 + JDG 06, and Max delivers JDG 07

11. **AGT 05** -- Deterministic feasibility checker (shared with Person A)
12. **AGT 06** -- Alternative suggestion logic from allowed substitutions
13. **AGT 07** -- Model-backed Lab Manager response synthesis
14. **AGT 10** -- Write all domain-neutral prompt text files
15. **JDG 10** -- Expose component metrics for training plots

### Phase 5: After Max delivers API 06 + API 10

16. **TRN 13** -- Build client.py reusable module
17. **TRN 01** -- Create notebook skeleton
18. **TRN 02** -- Package install and model setup cell
19. **TRN 03** -- Environment client wrapper in notebook
20. **TRN 14** -- Document base model choice (notebook side)

### Phase 6: Training Pipeline (internal chain)

21. **TRN 04** -- Rollout collection loop
22. **TRN 05** -- Connect to GRPO trainer
23. **TRN 06** -- Log episode metrics
24. **TRN 07** -- Plot reward curves
25. **TRN 08** -- Before vs after evaluation
26. **TRN 09** -- Policy loading for checkpoints
27. **TRN 10** -- Export plots
28. **TRN 15** -- Agreement and invalid action rate metrics
29. **OBS 06** -- Training run metadata logging

### Phase 7: After Kush delivers TRN 12

30. **TST 09** -- Notebook smoke test

---

## 8. Summary Table

| Category | Count | Hours |
|----------|-------|-------|
| Active now | 1 | 0.75h |
| Blocked by Person A (first-order) | 4 | 3.25h |
| Blocked by Person A then Person B chain | 8 | 6.25h |
| Blocked by Person C | 3 | 2.5h |
| Deep training chain (internal) | 11 | 7.5h |
| Blocked by Person D | 1 | 0.5h |
| **Total** | **29** | **21.5h** |

---

## 9. Base Model Assumptions

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

The MVP Lab Manager path is now hybrid:
- A deterministic feasibility checker remains the source of truth for
  `feasible`, constraint flags, and any final structured `LabManagerAction`.
- Model-backed response generation is used for negotiation language and
  alternative suggestions, but it does not own truth or reward.
- The reward formula does not change. The deterministic rubric scores the final
  plan against the hidden reference spec regardless of how the Lab Manager
  generates its language.
- Reward does not split into separate Scientist vs Lab Manager objectives.
  Both roles share the same cooperative reward signal.
- If the team later shares one base model across both roles, the pragmatic
  default is one base model (Qwen3-4B) with separate role-specific adapters.

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

## 10. Key Risks for Person B

| Risk | Impact | Mitigation |
|------|--------|------------|
| Person A SCN 09 or MOD 05 delayed | Blocks AGT 01 via SCN 11 and delays AGT 05-07 plus downstream work | Communicate priority order to Person A early |
| Person C API delayed | Blocks entire training pipeline (TRN 01-15) | Coordinate with Person C on API 06 timeline |
| Qwen3-4B underperforms on structured output | Scientist produces low quality protocols | Fall back to Qwen3-8B on H100, use reduced-scale Colab fallback |
| RL training produces flat rewards | No improvement to demo | Have baseline heuristic ready, tune reward weights with Person A |
| Scientist produces invalid JSON | Rollout loop crashes | AGT 03 parse plus retry is critical, build it robust |
| Hybrid Lab Manager increases variance if generation settings are too loose | Slower RL convergence | Keep checker as source of truth, use low-variance generation or frozen manager weights during Scientist training |

---

## 11. Files Person B Owns

| File | Purpose |
|------|---------|
| `replicalab/agents/scientist_policy.py` | Trainable Scientist policy |
| `replicalab/agents/lab_manager_policy.py` | Hybrid Lab Manager grounded by deterministic feasibility checks (shared with A) |
| `replicalab/client.py` | Reusable environment client |
| `replicalab/prompts/scientist.txt` | Scientist system prompt |
| `replicalab/prompts/lab_manager.txt` | Lab Manager response templates |
| `replicalab/prompts/judge.txt` | Judge explanation prompt |
| `notebooks/train_colab.ipynb` | RL training notebook (judged asset) |
