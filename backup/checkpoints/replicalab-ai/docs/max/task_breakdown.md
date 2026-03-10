# Max (Person C) Task Breakdown

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current situation

- `FND 01`, `FND 02`, `FND 05`, `FND 07`, and `FND 10` are already complete
- Those tasks were executed by `Person B (Ayush)` and logged in `docs/changes.md`
- `FND 03` and `FND 12` are now complete via the validated frontend import from Kush's branch onto `ayush`
- `FND 11` is now complete and verified
- The backend path is now real-env-backed locally: `server/app.py` imports `ReplicaLabEnv`, `openenv validate` passes, and local Docker verification is complete
- `API 02`, `API 03`, `API 04`, `API 06`, `API 07`, `API 08`, `API 09`, `API 10`, `API 13`, `API 14`, `API 15`, and `API 17` are complete
- `MOD 07` and `MOD 10` are complete and verified
- `TRN 11` is now complete via `docs/max/training_connection.md`, so notebook users already have a stable environment URL, transport, and troubleshooting guide
- `API 01` and `OBS 02` are the remaining partial tasks in Max's lane
- Max's remaining implementation priority is reward logging, replay persistence, observability, and the remaining API polish

---

## Unblocked now

1. `JDG 07` is now the next clean backend task because `MOD 07` is complete and replay-aware reward logging is the next missing piece
2. `TRN 11` is complete, so notebook connection and troubleshooting notes already exist for local and hosted environment usage
3. Replay or persistence work (`JDG 07`, `ENV 09`, `API 05`) is now the next infra-heavy backend chain

---

## Still blocked

- `FND 13` is now unblocked because `FND 03` is complete, but it remains owned by Kush (Person D)
- `API 05` still depends on `ENV 09`
- `API 16` still depends on `UI 10`
- `API 18` still depends on `API 05` and `ENV 11`
- `API 19` still depends on `API 10`

---

## Recommended execution order

1. Finish `API 01` and `OBS 02` sign-off work
2. Move into reward/replay persistence (`JDG 07` -> `ENV 09` -> `API 05`)
3. Then finish `API 11`, `API 18`, and `API 19`
