# Person B (Ayush) Task Breakdown and Execution Plan

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## 1. Tasks That Can Start Immediately

These have no hard blockers. The ScientistAction schema shape is fully defined
in the blueprint (Section 9.1 and models.py spec), so code can be written now
and wired to real Pydantic models once Person A ships MOD 01.

| ID | Task | Formal Dep | Why Startable | Est |
|----|------|-----------|---------------|-----|
| AGT 11 | Select and document base model for Scientist training | AGT 01 | Pure research and decision task, no code needed from anyone | 0.5h |
| TRN 14 | Same decision, notebook side documentation | TRN 01 | Same as above, duplicate entry, do once | 0.5h |
| AGT 01 | Draft Scientist system prompt | MOD 01, SCN 11 | ScientistAction schema fully defined in blueprint | 0.75h |
| MOD 09 | Build output parser mapping model text to ScientistAction | MOD 01 | Schema shape is known, write parser, wire to real model later | 0.75h |

**Total startable now: ~2.5h of work**

---

## 2. Blocked by Other Person B Tasks Only (Internal Chain)

These unblock as you complete the tasks above. No waiting on other team members
except where noted.

| ID | Task | Depends On | Est |
|----|------|-----------|-----|
| AGT 02 | Observation to prompt formatting helper | AGT 01 (B) + MOD 03 (A) | 0.75h |
| AGT 03 | Parse plus retry for malformed output | MOD 09 (B) + AGT 02 (B) | 0.75h |
| AGT 04 | Baseline heuristic Scientist | AGT 02 (B) | 1h |
| AGT 08 | Prompt formatting and parse tests | AGT 01 to 04 (B) | 0.75h |
| AGT 10 | Write prompt text files for all 3 roles | AGT 01 (B) + AGT 07 (B) + JDG 06 (A) | 0.75h |

**Total: ~4h**

---

## 3. Blocked by Person A (Hard Dependencies)

Cannot proceed until Person A delivers these specific modules.

| ID | Task | Waiting On | Person A Task | Est |
|----|------|-----------|---------------|-----|
| FND 08 | Freeze JSON contract (shared A+B) | FND 04 | Empty Pydantic models | 0.75h |
| SCN 11 | Create golden scenarios for testing | SCN 09 | generate_scenario() | 0.75h |
| AGT 02 | Observation to prompt formatter (partial) | MOD 03 | Observation models | 0.75h |
| AGT 05 | Feasibility checker (shared A+B) | SCN 07, MOD 05 | Constraint generator + validation | 1.25h |
| AGT 06 | Alternative suggestion logic | AGT 05 | Feasibility checker | 1h |
| AGT 07 | Response templating | AGT 05 | Feasibility checker | 0.75h |
| JDG 10 | Expose component metrics for plots | JDG 05, JDG 07 | Reward breakdown + logging | 0.5h |

**Total: ~5.75h**

### What to ask Person A for first (priority order)

1. **MOD 01** (ScientistAction schema) -- unblocks MOD 09 wiring and AGT 01 finalization
2. **MOD 03** (Observation models) -- unblocks AGT 02
3. **FND 04 + FND 08** (Pydantic models + contract freeze) -- unblocks everything downstream
4. **SCN 07 + MOD 05** (constraints + validation) -- unblocks AGT 05/06/07
5. **SCN 09** (generate_scenario) -- unblocks SCN 11 golden scenarios

---

## 4. Blocked by Person C (Needs Server/API)

Cannot proceed until Person C delivers the server and deployment.

| ID | Task | Waiting On | Person C Task | Est |
|----|------|-----------|---------------|-----|
| TRN 01 | Notebook skeleton | API 10 | Deployed HF Space | 0.5h |
| TRN 03 | Env client wrapper in notebook | API 06 | WebSocket handler | 1h |
| TRN 13 | client.py reusable module | API 06 | WebSocket handler | 1h |

**Total: ~2.5h**

### What to ask Person C for first (priority order)

1. **API 06** (WebSocket handler) -- unblocks TRN 03 and TRN 13
2. **API 10** (deployed HF Space) -- unblocks TRN 01 notebook skeleton

---

## 5. Deep Training Chain (Sequential After Server Is Up)

These execute in strict order once TRN 01-03 and upstream tasks are done.

| Order | ID | Task | Depends On | Est |
|-------|----|------|-----------|-----|
| 1 | TRN 02 | Package install and model setup cell | TRN 01 | 0.75h |
| 2 | TRN 04 | Rollout collection loop | TRN 03, AGT 01 | 1h |
| 3 | TRN 05 | Connect rollouts to GRPO trainer | TRN 04 | 1.25h |
| 4 | TRN 06 | Log episode metrics | JDG 10, TRN 04 | 0.75h |
| 5 | TRN 07 | Plot reward curves | TRN 06 | 0.5h |
| 6 | TRN 08 | Before vs after eval on fixed seeds | SCN 11, TRN 05 | 1h |
| 7 | TRN 09 | Policy loading for trained checkpoint | TRN 05 | 0.5h |
| 8 | TRN 10 | Export plots to outputs/plots | TRN 07 | 0.25h |
| 9 | TRN 15 | Agreement and invalid action rate aggregation | TRN 06, TRN 08, OBS 09 | 0.5h |
| 10 | OBS 06 | Log training run metadata | TRN 06 | 0.5h |
| 11 | TST 09 | Notebook smoke test for fresh runtime | TRN 12 (Person D) | 0.5h |

**Total: ~7h**

---

## 6. Recommended Execution Order

### Phase 1: Start Now (no blockers)

1. **AGT 11 / TRN 14** -- Pick the base model. Research Qwen 2.5 7B, Phi-3 Mini,
   Llama 3.1 8B, Mistral 7B. Document choice with rationale for size, license,
   structured output capability, and Unsloth/TRL compatibility.
2. **AGT 01** -- Draft the Scientist system prompt using the schema from the blueprint.
   Define role, constraints, JSON output contract, and example actions.
3. **MOD 09** -- Build the output parser. Stub against the known ScientistAction shape.
   Handle JSON extraction, field validation, and parse error reporting.

### Phase 2: Once Person A Delivers MOD 01-03

4. Wire MOD 09 to real Pydantic models
5. **AGT 02** -- Build observation to prompt formatter
6. **AGT 03** -- Add parse plus retry logic
7. **AGT 04** -- Build baseline heuristic Scientist that can complete episodes
8. **AGT 08** -- Write tests for prompt formatting and parsing

### Phase 3: Once Person A Delivers AGT 05 (Feasibility Checker)

9. **AGT 06** -- Alternative suggestion logic for Lab Manager
10. **AGT 07** -- Human readable response templating
11. **AGT 10** -- Write all prompt text files (scientist.txt, lab_manager.txt, judge.txt)
12. **AGT 11** -- Finalize base model documentation if not done

### Phase 4: Once Person C Delivers API 06 + API 10

13. **TRN 13** -- Build client.py reusable module
14. **TRN 01** -- Create notebook skeleton
15. **TRN 02** -- Package install and model setup cell
16. **TRN 03** -- Environment client wrapper in notebook (or reuse TRN 13)

### Phase 5: Training Pipeline

17. **TRN 04** -- Rollout collection loop
18. **TRN 05** -- Connect to GRPO trainer
19. **TRN 06** -- Log episode metrics
20. **TRN 07** -- Plot reward curves
21. **TRN 08** -- Before vs after evaluation
22. **TRN 09** -- Policy loading for checkpoints
23. **TRN 10** -- Export plots
24. **TRN 15** -- Agreement and invalid action rate metrics
25. **OBS 06** -- Training run metadata logging
26. **TST 09** -- Notebook smoke test

---

## 7. Summary Table

| Category | Count | Hours |
|----------|-------|-------|
| Start NOW | 3 unique tasks | ~2h |
| Blocked by Person B internal chain | 5 | ~4h |
| Blocked by Person A | 7 | ~5.75h |
| Blocked by Person C | 3 | ~2.5h |
| Deep training chain | 11 | ~7h |
| **Total** | **28 tasks** | **~20.75h** |

---

## 8. Key Risks for Person B

| Risk | Impact | Mitigation |
|------|--------|------------|
| Person A MOD 01-03 delayed | Blocks AGT 02-04 and downstream | Start AGT 01, MOD 09 against blueprint schema now |
| Person C API delayed | Blocks entire training pipeline | Build client.py and notebook stubs against mock endpoints |
| Base model too large for Colab | Training fails or is too slow | Pick 7B or smaller, verify Colab GPU memory first |
| RL training produces flat rewards | No improvement to demo | Have baseline heuristic ready, tune reward weights with Person A |
| Scientist produces invalid JSON | Rollout loop crashes | AGT 03 parse plus retry is critical, build it robust |

---

## 9. Files Person B Owns

| File | Purpose |
|------|---------|
| `replicalab/agents/scientist_policy.py` | Trainable Scientist policy |
| `replicalab/agents/lab_manager_policy.py` | Rule-based Lab Manager (shared with A) |
| `replicalab/client.py` | Reusable environment client |
| `replicalab/prompts/scientist.txt` | Scientist system prompt |
| `replicalab/prompts/lab_manager.txt` | Lab Manager response templates |
| `replicalab/prompts/judge.txt` | Judge explanation prompt |
| `notebooks/train_colab.ipynb` | RL training notebook (judged asset) |
