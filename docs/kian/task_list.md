# Kian (Person A) Task List

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 04`, `FND 08`, and `FND 09` are complete
- `MOD 01`, `MOD 02`, `MOD 03`, `MOD 04`, `MOD 05`, `MOD 11`, and `MOD 12` are complete
- Shared `AGT 05` is now complete through Ayush's implementation of the deterministic feasibility checker
- `SCN 01` to `SCN 10` are now complete in the repo
- The normalized scenario pack, seeded generation, difficulty scaling, and three initial domain families are already present
- The next Kian-lane tasks are now `MOD 06`, `SCN 13`, `JDG 01`, `JDG 02`, `JDG 03`, and `ENV 01`
- `MOD 05` and shared `AGT 05` now exist, so the judge and environment path can build on real scenario-grounded checks instead of placeholder rules

---

## Immediate next tasks

- [ ] **MOD 06** | Add semantic validators for impossible plans such as zero sample size with positive controls | 0.75h | Depends: MOD 05
- [ ] **SCN 13** | Implement shared booking and scheduling data model for GPUs, rooms, or equipment with time-slot conflicts and duration | 1h | Depends: SCN 07
- [ ] **JDG 01** | Implement rigor or objective-validity score for plan completeness, required checks, method quality, and justification | 1.25h | Depends: SCN 08
- [ ] **JDG 02** | Implement feasibility score for budget, resources, time, staffing, compute, and bookings | 1.25h | Depends: SCN 07, AGT 05
- [ ] **JDG 03** | Implement fidelity score against hidden reference spec, required steps, and allowed substitutions | 1h | Depends: SCN 08
- [ ] **ENV 01** | Create `ReplicaLabEnv` class skeleton | 0.5h | Depends: MOD 04, SCN 09

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
