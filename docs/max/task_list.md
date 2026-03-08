# Max (Person C) Task List

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 01`, `FND 02`, `FND 05`, `FND 07`, and `FND 10` are complete
- All five were executed by `Person B (Ayush)` and recorded as executor deviations
- `FND 11` is complete
- A stub-backed backend server scaffold now exists in `server/app.py`
- `API 01`, `API 02`, `API 03`, `API 04`, `API 06`, `API 07`, `API 08`, `API 13`, `API 14`, and `OBS 02` are partial pending real-env and Docker-level verification
- The next unblocked untouched Max task is `FND 03`

---

## Immediate next tasks

- [ ] **FND 03** | Initialize React plus Vite frontend shell | Depends: `FND 01` | Status: unblocked
- [ ] **FND 12** | Create `frontend/vite.config.ts` with proxy settings | Depends: `FND 03` | Status: blocked
- [ ] **API 01 / API 02 / API 03 / API 06** | Convert the stub-backed server scaffold into real-env-backed endpoints | Depends: `ENV 01`, `ENV 02`, `ENV 06` | Status: partial
- [ ] **API 08** | Validate Docker locally for the server image | Depends: `API 01` to `API 07` | Status: partial
- [ ] **OBS 02** | Confirm logging behavior against the integrated environment path | Depends: `API 01` | Status: partial

---

## Completed assigned tasks executed by another contributor

- [x] **FND 01** | Completed by Person B (Ayush)
- [x] **FND 02** | Completed by Person B (Ayush)
- [x] **FND 05** | Completed by Person B (Ayush)
- [x] **FND 07** | Completed by Person B (Ayush)
- [x] **FND 10** | Completed by Person B (Ayush)

## Completed in Max's lane

- [x] **FND 11** | Completed and verified in `server/requirements.txt`

