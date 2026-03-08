# Person B (Ayush) Task Breakdown and Execution Plan

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

All dependency references below are taken directly from the source of truth.
No assumptions from other documents are used to reclassify blocked status.

---

## 1. Blocking Status

Per the source of truth, every Person B task has at least one explicit dependency.
There are zero unblocked Person B tasks at project start.

---

## 2. Blocked by Person A-Led External Dependencies

These tasks are first gated by upstream deliverables, primarily from Person A.
`JDG 10` also requires Person C to ship `JDG 07`.

| ID | Task | Depends On | Person A Deliverable | Est |
|----|------|-----------|---------------------|-----|
| FND 08 | Freeze JSON contract (shared A+B) | FND 04 | Empty Pydantic models | 0.75h |
| MOD 09 | Build output parser for ScientistAction | MOD 01 | ScientistAction schema | 0.75h |
| AGT 01 | Draft Scientist system prompt | MOD 01, SCN 11 | ScientistAction schema + generate_scenario | 0.75h |
| AGT 05 | Implement feasibility checker (shared A+B) | SCN 07, MOD 05 | Constraint generator + validation | 1.25h |
| SCN 11 | Create golden scenarios for prompt testing | SCN 09 | generate_scenario() | 0.75h |
| JDG 10 | Expose component metrics for training plots | JDG 05, JDG 07 | Reward breakdown (A) + logging (C) | 0.5h |

**Total: 6 tasks, 4.75h**

### What to ask Person A for first (priority order)

1. **FND 04** (empty Pydantic models) -- unblocks FND 08 contract freeze
2. **MOD 01** (ScientistAction schema) -- unblocks MOD 09 and, after SCN 11, AGT 01
3. **MOD 03** (Observation models) -- unblocks AGT 02
4. **SCN 09** (generate_scenario) -- unblocks SCN 11 golden scenarios
5. **SCN 07 + MOD 05** (constraints + validation) -- unblocks AGT 05, AGT 06, AGT 07
6. **JDG 05 + JDG 06** (reward breakdown + explanation) -- unblocks AGT 10 and is only part of the path for JDG 10
7. **SCN 08** (minimum viable replication spec) -- unblocks AGT 06 after AGT 05

---

## 3. Blocked by Person A Then Person B Internal Chain

These depend on Person A deliverables AND on earlier Person B tasks. They unblock
sequentially as both streams deliver.

| ID | Task | Depends On | Blocked By | Est |
|----|------|-----------|-----------|-----|
| AGT 02 | Observation to prompt formatting helper | AGT 01 (B) + MOD 03 (A) | Person A: MOD 03, Person B: AGT 01 | 0.75h |
| AGT 03 | Parse plus retry for malformed output | MOD 09 (B) + AGT 02 (B) | Person B: MOD 09, AGT 02 | 0.75h |
| AGT 04 | Baseline heuristic Scientist | AGT 02 (B) | Person B: AGT 02 | 1h |
| AGT 06 | Alternative suggestion logic | AGT 05 (A+B), SCN 08 (A) | Person A: SCN 08, Person A+B: AGT 05 | 1h |
| AGT 07 | Human readable response templating | AGT 05 (A+B) | Person A+B: AGT 05 | 0.75h |
| AGT 08 | Prompt formatting and parse tests | AGT 01 to AGT 04 (B) | Person B: AGT 01-04 | 0.75h |
| AGT 10 | Write prompt text files for all 3 roles | AGT 01 (B) + AGT 07 (B) + JDG 06 (A) | Person A: JDG 06, Person B: AGT 01, AGT 07 | 0.75h |
| AGT 11 | Select and document base model | AGT 01 (B) | Person B: AGT 01 | 0.5h |

**Total: 8 tasks, 6.25h**

---

## 4. Blocked by Person C (Needs Server/API)

Cannot proceed until Person C delivers the server and deployment.

| ID | Task | Depends On | Person C Deliverable | Est |
|----|------|-----------|---------------------|-----|
| TRN 01 | Notebook skeleton | API 10 | Deployed HF Space | 0.5h |
| TRN 03 | Env client wrapper in notebook | API 06 | WebSocket handler | 1h |
| TRN 13 | client.py reusable module | API 06 | WebSocket handler | 1h |

**Total: 3 tasks, 2.5h**

### What to ask Person C for first (priority order)

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

## 6. Blocked by Person D

| ID | Task | Depends On | Person D Deliverable | Est |
|----|------|-----------|---------------------|-----|
| TST 09 | Notebook smoke test for fresh runtime | TRN 12 | Evaluation storytelling insights | 0.5h |

**Total: 1 task, 0.5h**

---

## 7. Recommended Execution Order

All phases are gated by the listed external dependency being delivered first.

### Phase 1: After Person A delivers FND 04

1. **FND 08** -- Freeze JSON contract (shared with Person A, needs FND 04)

### Phase 2: After Person A and B complete FND 08, and Person A delivers MOD 01 + SCN 09

2. **SCN 11** -- Create golden scenarios for prompt testing
3. **MOD 09** -- Build output parser for ScientistAction
4. **AGT 01** -- Draft Scientist system prompt
5. **AGT 11** -- Select and document base model

### Phase 3: After Person A delivers MOD 03

6. **AGT 02** -- Build observation to prompt formatter
7. **AGT 03** -- Add parse plus retry logic
8. **AGT 04** -- Build baseline heuristic Scientist
9. **AGT 08** -- Write tests for prompt formatting and parsing

### Phase 4: After Person A delivers SCN 07 + MOD 05 + SCN 08 + JDG 05 + JDG 06, and Person C delivers JDG 07

10. **AGT 05** -- Feasibility checker (shared with Person A)
11. **AGT 06** -- Alternative suggestion logic
12. **AGT 07** -- Response templating
13. **AGT 10** -- Write all prompt text files
14. **JDG 10** -- Expose component metrics for training plots

### Phase 5: After Person C delivers API 06 + API 10

15. **TRN 13** -- Build client.py reusable module
16. **TRN 01** -- Create notebook skeleton
17. **TRN 02** -- Package install and model setup cell
18. **TRN 03** -- Environment client wrapper in notebook
19. **TRN 14** -- Document base model choice (notebook side)

### Phase 6: Training Pipeline (internal chain)

20. **TRN 04** -- Rollout collection loop
21. **TRN 05** -- Connect to GRPO trainer
22. **TRN 06** -- Log episode metrics
23. **TRN 07** -- Plot reward curves
24. **TRN 08** -- Before vs after evaluation
25. **TRN 09** -- Policy loading for checkpoints
26. **TRN 10** -- Export plots
27. **TRN 15** -- Agreement and invalid action rate metrics
28. **OBS 06** -- Training run metadata logging

### Phase 7: After Person D delivers TRN 12

29. **TST 09** -- Notebook smoke test

---

## 8. Summary Table

| Category | Count | Hours |
|----------|-------|-------|
| Blocked by Person A (first-order) | 6 | 4.75h |
| Blocked by Person A then Person B chain | 8 | 6.25h |
| Blocked by Person C | 3 | 2.5h |
| Deep training chain (internal) | 11 | 7.5h |
| Blocked by Person D | 1 | 0.5h |
| **Total** | **29** | **21.5h** |

---

## 9. Key Risks for Person B

| Risk | Impact | Mitigation |
|------|--------|------------|
| Person A MOD 01-03 delayed | Blocks AGT 01, MOD 09, AGT 02-04 and all downstream | Communicate priority order to Person A early |
| Person C API delayed | Blocks entire training pipeline (TRN 01-15) | Coordinate with Person C on API 06 timeline |
| Base model too large for Colab | Training fails or is too slow | Pick 7B or smaller, verify Colab GPU memory first |
| RL training produces flat rewards | No improvement to demo | Have baseline heuristic ready, tune reward weights with Person A |
| Scientist produces invalid JSON | Rollout loop crashes | AGT 03 parse plus retry is critical, build it robust |

---

## 10. Files Person B Owns

| File | Purpose |
|------|---------|
| `replicalab/agents/scientist_policy.py` | Trainable Scientist policy |
| `replicalab/agents/lab_manager_policy.py` | Rule-based Lab Manager (shared with A) |
| `replicalab/client.py` | Reusable environment client |
| `replicalab/prompts/scientist.txt` | Scientist system prompt |
| `replicalab/prompts/lab_manager.txt` | Lab Manager response templates |
| `replicalab/prompts/judge.txt` | Judge explanation prompt |
| `notebooks/train_colab.ipynb` | RL training notebook (judged asset) |
