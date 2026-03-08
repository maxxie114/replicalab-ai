# Person B (Ayush) Task List

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 08` is complete in `docs/fnd08_frozen_json_contract.md`
- `MOD 09` is complete in `replicalab/agents/scientist_policy.py`
- `SCN 11` is complete in `tests/fixtures/golden_scenarios.json`
- `AGT 01` is complete in `replicalab/agents/scientist_policy.py`
- `AGT 02` is complete in `replicalab/agents/scientist_policy.py`
- `AGT 03` is complete in `replicalab/agents/scientist_policy.py`
- `AGT 04` is complete in `replicalab/agents/scientist_policy.py`
- `AGT 05` is complete in `replicalab/agents/lab_manager_policy.py`
- `AGT 06` is complete in `replicalab/agents/lab_manager_policy.py`
- `AGT 07` is complete in `replicalab/agents/lab_manager_policy.py`
- `AGT 08` is complete in `replicalab/agents/scientist_policy.py`
- `AGT 11` is complete in `docs/agt11_scientist_model_selection.md`
- The scenario prerequisite bundle (`SCN 01` to `SCN 10`) is now present in the repo, so Ayush prompt work is backed by real normalized scenario packs instead of placeholders
- `API 06` is now complete, so `TRN 03` and `TRN 13` were fully unblocked
- `TRN 13` is now complete in `replicalab/client.py`
- `TRN 03` is now complete in `replicalab/training/rollout.py`
- `AGT 10` is now complete in `replicalab/prompts/`
- `TRN 04` is now complete in `replicalab/training/rollout.py`
- The next fully unblocked Ayush task is `TRN 05`

---

## Epic E02. Domain Models

- [x] **MOD 09** | Add output parser that maps model text to `ScientistAction` | 0.75h | Depends: MOD 01 | Status: completed on 2026-03-08

---

## Epic E03. Scenario Engine

- [x] **SCN 11** | Create hand checked golden scenarios for prompt testing | 0.75h | Depends: SCN 09 | Status: completed on 2026-03-08

---

## Epic E04. Scientist Agent and Lab Manager Policy

- [x] **AGT 01** | Draft domain-neutral system prompt for Scientist role from normalized scenario data | 0.75h | Depends: MOD 01, SCN 11 | Status: completed on 2026-03-08
- [x] **AGT 02** | Build observation to prompt formatting helper from normalized scenario-derived observations | 0.75h | Depends: AGT 01, MOD 03 | Status: completed on 2026-03-08
- [x] **AGT 04** | Build baseline heuristic Scientist for non trained smoke tests | 1h | Depends: AGT 02 | Status: completed on 2026-03-08
- [x] **AGT 05** | Implement deterministic feasibility checker over normalized constraints and resources (shared with Person A) | 1.25h | Depends: SCN 07, MOD 05 | Status: completed on 2026-03-08
- [x] **AGT 06** | Implement alternative suggestion logic from allowed substitutions and tradeoffs | 1h | Depends: AGT 05, SCN 08 | Status: completed on 2026-03-08
- [x] **AGT 07** | Add model-backed Lab Manager response synthesis from checker output | 0.75h | Depends: AGT 05 | Status: completed on 2026-03-08
- [x] **AGT 03** | Add parse plus retry strategy for malformed model output | 0.75h | Depends: MOD 09, AGT 02 | Status: completed on 2026-03-07
- [x] **AGT 08** | Add prompt formatting and parse tests | 0.75h | Depends: AGT 01 to AGT 04 | Status: completed on 2026-03-07
- [x] **AGT 11** | Select and document base model for Scientist training | 0.5h | Depends: AGT 01 | Status: completed on 2026-03-08
- [x] **AGT 10** | Write domain-neutral prompt text files for all three roles | 0.75h | Depends: AGT 01, AGT 07, JDG 06 | Status: completed on 2026-03-08

---

## Epic E05. Judge Engine and Reward

- [ ] **JDG 10** | Expose component metrics for training plots | 0.5h | Depends: JDG 05, JDG 07

---

## Epic E08. RL Training Pipeline

- [ ] **TRN 01** | Create notebook skeleton | 0.5h | Depends: API 10
- [ ] **TRN 02** | Add package install and model setup cell | 0.75h | Depends: TRN 01
- [x] **TRN 03** | Implement environment client wrapper | 1h | Depends: API 06 | Status: completed on 2026-03-08
- [x] **TRN 04** | Implement rollout collection loop | 1h | Depends: TRN 03, AGT 01 | Status: completed on 2026-03-08
- [ ] **TRN 05** | Connect rollouts to GRPO or equivalent trainer | 1.25h | Depends: TRN 04
- [ ] **TRN 06** | Log episode reward, rigor, feasibility, fidelity, rounds | 0.75h | Depends: JDG 10, TRN 04
- [ ] **TRN 07** | Plot reward curve and component curves | 0.5h | Depends: TRN 06
- [ ] **TRN 08** | Add before versus after evaluation on fixed seeds | 1h | Depends: SCN 11, TRN 05
- [ ] **TRN 09** | Add policy loading path for trained adapter | 0.5h | Depends: TRN 05
- [ ] **TRN 10** | Export plot image and sample logs to outputs/plots | 0.25h | Depends: TRN 07
- [x] **TRN 13** | Create reusable environment client module (client.py) | 1h | Depends: API 06 | Status: completed on 2026-03-08
- [ ] **TRN 14** | Select and document base model (notebook side) | 0.5h | Depends: TRN 01 | Assumption: Qwen3-4B primary, Qwen3-8B H100-only stretch
- [ ] **TRN 15** | Add agreement rate and invalid action rate aggregation | 0.5h | Depends: TRN 06, TRN 08, OBS 09

---

## Epic E10. Logging and Observability

- [ ] **OBS 06** | Log training run metadata | 0.5h | Depends: TRN 06

---

## Epic E11. Testing

- [ ] **TST 09** | Create notebook smoke test for fresh runtime | 0.5h | Depends: TRN 12

---

## Shared Tasks

- [x] **FND 08** | Freeze JSON contract for actions and observations (with Person A) | 0.75h | Depends: FND 04 | Status: completed and signed off

---

## Totals

| Metric | Value |
|--------|-------|
| Total tasks | 29 |
| Completed | 16 |
| Remaining | 13 |
| Total estimated hours | 8h |
