# Max (Person C) Task List

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- `FND 01`, `FND 02`, `FND 03`, `FND 05`, `FND 07`, `FND 10`, `FND 11`, and `FND 12` are complete
- The server now runs against the real `ReplicaLabEnv`, not just the legacy stub fallback
- `API 02`, `API 03`, `API 04`, `API 06`, `API 07`, `API 08`, `API 09`, `API 13`, and `API 15` are complete
- `API 01`, `API 14`, and `OBS 02` remain partial
- The remaining Max work is now live deployment verification, replay or persistence work, observability, and the rest of the API or packaging path

---

## Immediate next tasks

- [ ] **API 10** | Deploy the live HF Space and verify `/health`, `/reset`, and `/step` end to end | Depends: `API 09`
- [ ] **API 17** | Document secrets and API key management for HF Space and Colab | Depends: `API 09`
- [ ] **API 01 / API 14 / OBS 02** | Finish the remaining partial server tasks and sign-offs | Depends: real-env server path already present
- [ ] **MOD 07 / ENV 09 / API 05** | Finish replay persistence and replay retrieval path | Depends: `MOD 04`, `ENV 06`

---

## Completed assigned tasks executed by another contributor

- [x] **FND 01** | Completed by Person B (Ayush)
- [x] **FND 02** | Completed by Person B (Ayush)
- [x] **FND 03** | Completed by Kush and imported onto `ayush`
- [x] **FND 05** | Completed by Person B (Ayush)
- [x] **FND 07** | Completed by Person B (Ayush)
- [x] **FND 10** | Completed by Person B (Ayush)
- [x] **FND 12** | Completed by Kush and imported onto `ayush`

## Completed in Max's lane

- [x] **FND 11** | Completed and verified in `server/requirements.txt`
- [x] **API 02** | Completed by Person B (Ayush)
- [x] **API 03** | Completed by Person B (Ayush)
- [x] **API 04** | Completed by Person B (Ayush)
- [x] **API 06** | Completed by Person B (Ayush)
- [x] **API 07** | Completed by Person B (Ayush)
- [x] **API 08** | Completed by Person B (Ayush)
- [x] **API 09** | Completed by Person B (Ayush)
- [x] **API 13** | Completed by Person B (Ayush)
- [x] **API 15** | Completed by Person B (Ayush)
- [x] **TST 07** | Completed by Person B (Ayush)

