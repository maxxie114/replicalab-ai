# Max (Person C) Task Breakdown

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current situation

- `FND 01`, `FND 02`, `FND 05`, `FND 07`, and `FND 10` are already complete
- Those tasks were executed by `Person B (Ayush)` and logged in `docs/changes.md`
- Max's next implementation priority in the Person C lane is `FND 03`, followed by `FND 11`

---

## Unblocked now

1. `FND 03` — React plus Vite frontend shell
2. `FND 11` — `server/requirements.txt`

---

## Still blocked

- `FND 12` depends on `FND 03`
- `FND 13` depends on `FND 03` even though it is owned by Kush (Person D)

---

## Recommended execution order

1. Finish `FND 03`
2. Land `FND 11`
3. Land `FND 12`
4. Continue into API and deployment work once the frontend/server skeleton exists

