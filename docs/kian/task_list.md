# Kian (Person A) Task List

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 04` is complete in `replicalab/models.py`
- `FND 08` is complete in `docs/fnd08_frozen_json_contract.md`
- `FND 09` is complete in `openenv.yaml`
- `MOD 01` is now complete in `replicalab/models.py`
- `MOD 02` is now complete in `replicalab/models.py`
- `MOD 03` is now complete in `replicalab/models.py`
- The next Kian-lane tasks are `MOD 12`, `SCN 01`, `MOD 05`, `MOD 04`, `SCN 02`, and `MOD 11`
- `SCN 02` now needs to formalize the normalized scenario pack below the stable outer contract

---

## Immediate next tasks

- [ ] **MOD 12** | Create environment configuration module with shared constants | 0.5h | Depends: FND 08
- [ ] **SCN 01** | Implement deterministic RNG helper `seed_rng()` | 0.5h | Depends: FND 08
- [ ] **MOD 05** | Add protocol validation for sample size, controls, duration, and vocab checks | 1h | Depends: MOD 01
- [ ] **MOD 04** | Implement `EpisodeState` and `EpisodeLog` models | 0.75h | Depends: MOD 03
- [ ] **SCN 02** | Define normalized scenario schema with hidden reference spec and mapper-ready inputs | 0.75h | Depends: MOD 04
- [ ] **MOD 11** | Implement `StepResult` model | 0.5h | Depends: MOD 03

---

## Foundation tasks already landed

- [x] **FND 04** | Completed by Person B (Ayush)
- [x] **FND 08** | Completed with shared sign-off
- [x] **FND 09** | Completed by Person B (Ayush)
- [x] **MOD 01** | Completed by Person B (Ayush)
- [x] **MOD 02** | Completed by Person B (Ayush)
- [x] **MOD 03** | Completed by Person B (Ayush)

