# Max (Person C) Task Breakdown

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current situation

- `FND 01`, `FND 02`, `FND 05`, `FND 07`, and `FND 10` are already complete
- Those tasks were executed by `Person B (Ayush)` and logged in `docs/changes.md`
- `FND 03` and `FND 12` are now complete via the validated frontend import from Kush's branch onto `ayush`
- `FND 11` is now complete and verified
- A normalized backend import from Max's PR is on `ayush`: `server/app.py`, `server/Dockerfile`, and `docs/max/deployment.md`
- That backend import is intentionally tracked as partial because it still runs on the stub env and Docker has not yet been validated locally
- Max's remaining implementation priority is the real-env-backed API and deployment path

---

## Unblocked now

1. Convert the stub-backed API tasks to real-env-backed implementations once Kian lands the environment work
2. Validate Docker locally once the real env path is in place

---

## Still blocked

- `FND 13` is now unblocked because `FND 03` is complete, but it remains owned by Kush (Person D)
- Real completion of `API 01`, `API 02`, `API 03`, `API 06`, and `API 07` depends on Kian's environment tasks
- Real completion of `API 08` depends on local Docker build and run validation

---

## Recommended execution order

1. Re-validate the imported server scaffold against Kian's environment implementation
2. Validate `server/Dockerfile` locally
3. Continue into deployment and replay work once the real env path is stable
