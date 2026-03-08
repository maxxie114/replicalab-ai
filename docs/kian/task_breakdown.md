# Kian (Person A) Task Breakdown

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 04`, `FND 08`, `FND 09`, `MOD 01`, `MOD 02`, `MOD 03`, `MOD 04`, `MOD 05`, `MOD 11`, and `MOD 12` are complete
- Shared `AGT 05` is now complete, so the deterministic feasibility layer exists for both the Lab Manager path and the later judge feasibility score
- `SCN 01` to `SCN 10` are also complete, so the deterministic scenario layer now exists in code
- The Kian lane no longer needs to start with scenario seeding or template scaffolding
- The remaining high-leverage work is semantic edge-case validation, booking conflicts, judge logic, and the real environment

---

## Recommended execution order

1. `MOD 06` -- extend the new semantic validation layer to catch impossible edge cases early
2. `SCN 13` -- deepen the normalized scenario layer with booking and scheduling conflicts
3. `JDG 01`, `JDG 02`, and `JDG 03` -- start the deterministic reward components that are now unblocked
4. `JDG 04` and `JDG 05` -- complete the reward pipeline once the component scorers exist
5. `ENV 01` and `ENV 02` -- once typed state and core scoring pieces are in place, start the real OpenEnv environment path

---

## Why this order

- `MOD 06` is the smallest remaining contract-hardening task and builds directly on the completed `MOD 05` validator.
- `SCN 13` is the remaining scenario-layer depth task; it builds naturally on the completed normalized resource model.
- `JDG 01` and `JDG 03` can start immediately because their only formal prerequisite, `SCN 08`, is already complete.
- `JDG 02` is now also unblocked because the deterministic feasibility checker from `AGT 05` exists.
- The environment path can now start from typed state and step-result contracts instead of loose dict-based placeholders.
