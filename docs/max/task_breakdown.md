# Max (Person C) Task Breakdown

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current situation

- `FND 01`, `FND 02`, `FND 05`, `FND 07`, and `FND 10` are already complete
- Those tasks were executed by `Person B (Ayush)` and logged in `docs/changes.md`
- `FND 03` and `FND 12` are now complete via the validated frontend import from Kush's branch onto `ayush`
- `FND 11` is now complete and verified
- The backend path is now real-env-backed locally: `server/app.py` imports `ReplicaLabEnv`, `openenv validate` passes, and local Docker verification is complete
- `API 02`, `API 03`, `API 04`, `API 06`, `API 07`, `API 08`, `API 09`, `API 13`, and `API 15` are complete
- `API 01`, `API 14`, and `OBS 02` are the remaining partial tasks in Max's lane
- Max's remaining implementation priority is live Space deployment, replay persistence, observability, and the remaining API polish

---

## Unblocked now

1. `API 10` is now unblocked because HF metadata and deployment instructions are in place
2. `API 17` is now unblocked because `API 09` is complete
3. Replay or persistence work (`MOD 07`, `ENV 09`, `API 05`, `JDG 07`) is now the next infra-heavy backend chain

---

## Still blocked

- `FND 13` is now unblocked because `FND 03` is complete, but it remains owned by Kush (Person D)
- `API 05` still depends on `ENV 09`
- `API 16` still depends on `UI 10`
- `API 18` still depends on `API 05` and `ENV 11`
- `API 19` still depends on `API 10`

---

## Recommended execution order

1. Ship `API 10` live Space deployment verification
2. Ship `API 17` secrets and hosted-key documentation
3. Finish `API 01`, `API 14`, and `OBS 02` sign-off work
4. Move into replay persistence (`MOD 07` -> `ENV 09` -> `API 05`)
