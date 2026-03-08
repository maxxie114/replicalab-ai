# Change Log

This file records deviations from the original project plan.

Rules:

- Append new entries; do not rewrite history unless a prior entry is factually wrong.
- Record the contributor, the task or area, the deviation, and the reason.
- Update this file in the same branch or PR as the deviation whenever possible.

| Date | Contributor | Task or Area | Deviation | Reason | Impact | Follow-up |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-03-07 | Person B (Ayush) | FND 01 | Executed the task even though it was assigned to Person C | The repo scaffold was missing and needed immediately to unblock foundation work | Repo structure was created and tracking docs were updated to reflect the actual executor | None |
| 2026-03-08 | Person B (Ayush) | FND 02 | Executed the task even though it was assigned to Person C | The Python package config was needed to verify editable installs and unblock `FND 11` | `pyproject.toml` was added, install verification was run, and tracking docs were updated | `FND 11` is now unblocked |
| 2026-03-07 | Person B (Ayush) | FND 10 | Executed the task even though it was assigned to Person C | The output directories were still missing after the initial scaffold and needed for backlog compliance | `replicalab/outputs/` and subdirectories were added and tracking docs were updated | None |
| 2026-03-08 | Person B (Ayush) | FND 04 | Executed the task even though it was assigned to Person A | The shared contract stubs were needed to unblock `FND 08` and downstream schema work | `replicalab/models.py` was created and tracking docs were updated | None |
| 2026-03-08 | Person B (Ayush) | FND 05 | Executed the task even though it was assigned to Person C | Ignore rules were incomplete and needed to keep generated artifacts out of git and Docker context | `.gitignore` and `.dockerignore` were updated and tracking docs were aligned | None |
| 2026-03-08 | Person B (Ayush) | FND 06 | Executed the task even though it was assigned to Person D | The existing README described a future state and needed to become an honest temporary stub for new contributors | `README.md` now reflects the current foundation stage and verified setup placeholder | `DOC 01` is now unblocked |
| 2026-03-08 | Person B (Ayush) | FND 07 | Executed the task even though it was assigned to Person C | GitHub templates and explicit repo workflow artifacts were needed to reduce coordination overhead | PR and task templates were added and the project-management rules were tightened | Future PRs and task issues should use the new templates |
| 2026-03-08 | Person B (Ayush) | Project management | Added governance docs and a deviation log outside the original backlog | Coordination overhead and tracking drift had become a project-management risk | New repo rules now govern future task tracking, docs updates, and deviation logging | Keep these docs in sync with future work |

