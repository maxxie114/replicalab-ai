# Kian (Person A) Task Breakdown

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 04` complete
- `FND 08` complete
- `FND 09` complete
- `MOD 01` complete
- `MOD 02` complete
- `MOD 03` complete
- The Kian lane should now move to config, scenario seeding, validation, the remaining state-model pass, and the normalized scenario layer

---

## Recommended execution order

1. `MOD 12` -- creates one shared config module before env and scoring files branch out
2. `SCN 01` -- starts the deterministic scenario utility chain
3. `MOD 05` -- converts the frozen action contract into reusable protocol validation
4. `MOD 04` -- upgrades state and replay models to match the typed observation path
5. `SCN 02` -- defines the normalized scenario pack below the stable outer contract
6. `MOD 11` -- finalizes `StepResult` now that the observation wrapper is typed

---

## Why this order

- `MOD 12` and `SCN 01` are the cleanest foundational follow-ons and reduce future magic numbers and seed drift.
- `MOD 05` is already unblocked and should land before higher-level environment logic starts trusting protocol payloads.
- `MOD 04` should land before `SCN 02` so the normalized scenario pack can be threaded into `EpisodeState` cleanly rather than retrofitted later.
- `SCN 02` is now the key architecture task because it formalizes the normalized pack that mathematics, machine learning, and finance scenarios all have to emit while keeping the outer contract unchanged.
- `MOD 11` now follows naturally from the typed observation work in `MOD 03`.

