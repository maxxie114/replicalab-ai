# Kian (Person A) Task List

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 04`, `FND 08`, and `FND 09` are complete
- `MOD 01`, `MOD 02`, `MOD 03`, `MOD 04`, `MOD 05`, `MOD 11`, and `MOD 12` are complete
- Shared `AGT 05` is now complete through Ayush's implementation of the deterministic feasibility checker
- `SCN 01` to `SCN 10` are now complete in the repo
- The normalized scenario pack, seeded generation, difficulty scaling, and three initial domain families are already present
- `ENV 01` to `ENV 08` are now complete, so the full environment lifecycle (reset, step, validate, Lab Manager response, termination, judge scoring, state snapshot, close) works end-to-end
- `JDG 01` to `JDG 05` are now complete, so the deterministic reward pipeline (rigor, feasibility, fidelity, total reward formula, breakdown builder) is fully wired
- `TST 01` to `TST 05` are now complete, with 36 env tests and 26 reward tests passing
- The next Kian-lane tasks are `MOD 06`, `SCN 13`, `JDG 06`, `JDG 08`, `ENV 10`

---

## Immediate next tasks

- [ ] **MOD 06** | Add semantic validators for impossible plans such as zero sample size with positive controls | 0.75h | Depends: MOD 05
- [ ] **SCN 13** | Implement shared booking and scheduling data model for GPUs, rooms, or equipment with time-slot conflicts and duration | 1h | Depends: SCN 07
- [ ] **JDG 06** | Add optional plain English explanation function from reward breakdown | 0.75h | Depends: JDG 05
- [ ] **JDG 08** | Add score determinism tests and edge case tests | 1h | Depends: JDG 01 to JDG 05
- [ ] **ENV 10** | Add reset, step, invalid action, timeout, and deterministic replay tests | 1.25h | Depends: ENV 02 to ENV 09

---

## Foundation and scenario tasks already landed

- [x] **FND 04** | Completed by Person B (Ayush)
- [x] **FND 08** | Completed with shared sign-off
- [x] **FND 09** | Completed by Person B (Ayush)
- [x] **MOD 01** | Completed by Person B (Ayush)
- [x] **MOD 02** | Completed by Person B (Ayush)
- [x] **MOD 03** | Completed by Person B (Ayush)
- [x] **MOD 04** | Completed by Person B (Ayush)
- [x] **MOD 05** | Completed by Person B (Ayush)
- [x] **MOD 11** | Completed by Person B (Ayush)
- [x] **MOD 12** | Completed by Person B (Ayush)
- [x] **AGT 05** | Completed by Person B (Ayush)
- [x] **SCN 01** | Completed by Person B (Ayush)
- [x] **SCN 02** | Completed by Person B (Ayush)
- [x] **SCN 03** | Completed by Person B (Ayush)
- [x] **SCN 04** | Completed by Person B (Ayush)
- [x] **SCN 05** | Completed by Person B (Ayush)
- [x] **SCN 06** | Completed by Person B (Ayush)
- [x] **SCN 07** | Completed by Person B (Ayush)
- [x] **SCN 08** | Completed by Person B (Ayush)
- [x] **SCN 09** | Completed by Person B (Ayush)
- [x] **SCN 10** | Completed by Person B (Ayush)
- [x] **ENV 01** | Completed by Person B (Ayush)
- [x] **ENV 02** | Completed by Person B (Ayush)
- [x] **ENV 03** | Completed by Person B (Ayush)
- [x] **ENV 04** | Completed by Person B (Ayush)
- [x] **ENV 05** | Completed by Person B (Ayush)
- [x] **ENV 06** | Completed by Person B (Ayush)
- [x] **ENV 07** | Completed by Person B (Ayush)
- [x] **ENV 08** | Completed by Person B (Ayush)
- [x] **JDG 01** | Completed by Person B (Ayush)
- [x] **JDG 02** | Completed by Person B (Ayush)
- [x] **JDG 03** | Completed by Person B (Ayush)
- [x] **JDG 04** | Completed by Person B (Ayush)
- [x] **JDG 05** | Completed by Person B (Ayush)
- [x] **TST 01** | Completed by Person B (Ayush)
- [x] **TST 02** | Completed by Person B (Ayush)
- [x] **TST 03** | Completed by Person B (Ayush)
- [x] **TST 04** | Completed by Person B (Ayush)
- [x] **TST 05** | Completed by Person B (Ayush)
