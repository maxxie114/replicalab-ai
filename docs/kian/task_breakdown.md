# Kian (Person A) Task Breakdown

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 04`, `FND 08`, `FND 09`, `MOD 01` to `MOD 05`, `MOD 11`, `MOD 12` are complete
- Shared `AGT 05` is now complete, so the deterministic feasibility layer exists for both the Lab Manager path and the judge feasibility score
- `SCN 01` to `SCN 10` are complete, so the deterministic scenario layer exists in code
- `ENV 01` to `ENV 08` are all complete — the full environment lifecycle (reset, step, validate, Lab Manager response, termination, judge scoring, state snapshot, close) works end-to-end
- `JDG 01` to `JDG 05` are complete — the full deterministic reward pipeline (rigor, feasibility, fidelity, total reward formula with floor clamp, breakdown builder with named penalty extension point) is wired and tested
- `TST 01` to `TST 05` are complete with 36 env tests and 26 reward tests passing
- The remaining high-leverage work is semantic edge-case validation, booking conflicts, judge explanation output, and environment test suite expansion

Bounded-tool scope note:

1. Kian-owned scenario, judge, and environment tasks now need to support
   bounded `search`, `code_check`, and `image_inspection` traces without
   changing the outer action contract.
2. Training reward must remain deterministic and must not depend on live web.
3. Frozen evidence packs are the default training-time source of tool inputs.
4. Audio remains out of scope.

---

## Recommended execution order

1. `MOD 06` -- extend the semantic validation layer to catch impossible edge cases early
2. `SCN 13` -- deepen the normalized scenario layer with booking, scheduling, and evidence-pack support
3. `JDG 06` -- add plain English explanation function from reward breakdown (unblocks AGT 10 for Ayush)
4. `JDG 08` -- add score determinism tests and edge case tests
5. `ENV 10` -- add comprehensive env tests (reset, step, invalid action, timeout, deterministic replay)

---

## Why this order

- `MOD 06` is the smallest remaining contract-hardening task and builds directly on the completed `MOD 05` validator.
- `SCN 13` is the remaining scenario-layer depth task; it now also needs to carry booking-conflict and evidence-pack data in a deterministic way.
- `JDG 06` is the highest-leverage remaining judge task because it directly unblocks `AGT 10` (Ayush's prompt text files) and `JDG 11` (structured audit payload).
- `JDG 08` builds on the now-complete JDG 01-05 pipeline to add regression coverage for score ordering and edge cases.
- `ENV 10` builds on the complete ENV 01-08 lifecycle to add comprehensive environment test coverage.
