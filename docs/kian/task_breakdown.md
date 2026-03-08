# Kian (Person A) Task Breakdown

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 04`, `FND 08`, `FND 09`, `MOD 01` to `MOD 05`, `MOD 11`, `MOD 12` are complete
- Shared `AGT 05` is now complete, so the deterministic feasibility layer exists for both the Lab Manager path and the judge feasibility score
- `SCN 01` to `SCN 10` are complete, so the deterministic scenario layer exists in code
- `ENV 01` to `ENV 08` are all complete — the full environment lifecycle (reset, step, validate, Lab Manager response, termination, judge scoring, state snapshot, close) works end-to-end
- `JDG 01` to `JDG 06` plus `JDG 08` are complete — the deterministic reward pipeline is wired, the plain-English explanation layer exists, and the reward stack now has stronger regression coverage for ordering, substitution behavior, partial feasibility credit, and breakdown determinism
- `TST 01` to `TST 05` are complete with 36 env tests and 40 reward tests passing
- `MOD 06`, `SCN 13`, `AGT 09`, `JDG 11`, `ENV 11`, `ENV 10`, and `OBS 04` are now complete, so the remaining Kian work is the blocked schema follow-on

Bounded-tool scope note:

1. Kian-owned scenario, judge, and environment tasks now need to support
   bounded `search`, `code_check`, and `image_inspection` traces without
   changing the outer action contract.
2. Training reward must remain deterministic and must not depend on live web.
3. Frozen evidence packs are the default training-time source of tool inputs.
4. Audio remains out of scope.

---

## Recommended execution order

1. `MOD 08` -- add schema and validator unit-test expansion

---

## Why this order

- `SCN 13` is complete, so the normalized scenario layer now carries booking and scheduling conflicts as structured deterministic data.
- `AGT 09` is complete, so the grounded Lab Manager checker, suggestion, and response stack now has deterministic regression coverage.
- `JDG 11` is complete and `ENV 11` is now integrated, so terminal env outputs and replay-facing state carry the canonical audit payload end to end.
- `ENV 10` and `OBS 04` are now complete, so the environment stack has deterministic replay and broader regression coverage on top of the completed ENV 01-08 and ENV 11 lifecycle.
- `MOD 08` is the only remaining Kian-owned implementation task, and it is now fully unblocked.
