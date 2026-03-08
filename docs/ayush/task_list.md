# Person B (Ayush) Task List

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 04` is complete in `replicalab/models.py`
- `FND 08` is now the next unblocked Ayush task

---

## Epic E02. Domain Models

- [ ] **MOD 09** | Add output parser that maps model text to `ScientistAction` | 0.75h | Depends: MOD 01

---

## Epic E03. Scenario Engine

- [ ] **SCN 11** | Create hand checked golden scenarios for prompt testing | 0.75h | Depends: SCN 09

---

## Epic E04. Scientist Agent and Lab Manager Policy

- [ ] **AGT 01** | Draft system prompt for Scientist role | 0.75h | Depends: MOD 01, SCN 11
- [ ] **AGT 02** | Build observation to prompt formatting helper | 0.75h | Depends: AGT 01, MOD 03
- [ ] **AGT 03** | Add parse plus retry strategy for malformed model output | 0.75h | Depends: MOD 09, AGT 02
- [ ] **AGT 04** | Build baseline heuristic Scientist for non trained smoke tests | 1h | Depends: AGT 02
- [ ] **AGT 05** | Implement feasibility checker (shared with Person A) | 1.25h | Depends: SCN 07, MOD 05
- [ ] **AGT 06** | Implement alternative suggestion logic | 1h | Depends: AGT 05, SCN 08
- [ ] **AGT 07** | Add human readable response templating | 0.75h | Depends: AGT 05
- [ ] **AGT 08** | Add prompt formatting and parse tests | 0.75h | Depends: AGT 01 to AGT 04
- [ ] **AGT 10** | Write prompt text files for all three roles | 0.75h | Depends: AGT 01, AGT 07, JDG 06
- [ ] **AGT 11** | Select and document base model for Scientist training | 0.5h | Depends: AGT 01

---

## Epic E05. Judge Engine and Reward

- [ ] **JDG 10** | Expose component metrics for training plots | 0.5h | Depends: JDG 05, JDG 07

---

## Epic E08. RL Training Pipeline

- [ ] **TRN 01** | Create notebook skeleton | 0.5h | Depends: API 10
- [ ] **TRN 02** | Add package install and model setup cell | 0.75h | Depends: TRN 01
- [ ] **TRN 03** | Implement environment client wrapper | 1h | Depends: API 06
- [ ] **TRN 04** | Implement rollout collection loop | 1h | Depends: TRN 03, AGT 01
- [ ] **TRN 05** | Connect rollouts to GRPO or equivalent trainer | 1.25h | Depends: TRN 04
- [ ] **TRN 06** | Log episode reward, rigor, feasibility, fidelity, rounds | 0.75h | Depends: JDG 10, TRN 04
- [ ] **TRN 07** | Plot reward curve and component curves | 0.5h | Depends: TRN 06
- [ ] **TRN 08** | Add before versus after evaluation on fixed seeds | 1h | Depends: SCN 11, TRN 05
- [ ] **TRN 09** | Add policy loading path for trained adapter | 0.5h | Depends: TRN 05
- [ ] **TRN 10** | Export plot image and sample logs to outputs/plots | 0.25h | Depends: TRN 07
- [ ] **TRN 13** | Create reusable environment client module (client.py) | 1h | Depends: API 06
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

- [ ] **FND 08** | Freeze JSON contract for actions and observations (with Person A) | 0.75h | Depends: FND 04 (done) | Status: ready now

---

## Totals

| Metric | Value |
|--------|-------|
| Total tasks | 29 |
| Total estimated hours | 21.5h |
