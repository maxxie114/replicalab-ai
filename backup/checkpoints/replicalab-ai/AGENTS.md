# Repo Working Rules

This repository uses file-based project management. Treat the files below as the persistent project memory for the repo:

- `ReplicaLab_Comprehensive_Task_Division.md`
- `docs/project_management_rules.md`
- `docs/completion.md`
- `docs/changes.md`
- `docs/<owner>/` folders

Current owner-folder mapping:

- `docs/ayush/` = Person B (Ayush)
- `docs/kian/` = Person A
- `docs/max/` = Person C
- `docs/kush/` = Person D

## Required start-of-work checklist

Every human contributor and every automated model agent must:

1. Read this file.
2. Read `docs/project_management_rules.md`.
3. Read `docs/completion.md`.
4. Read `docs/changes.md`.
5. Read the relevant `docs/<owner>/` folder for the task they are touching.
6. Confirm task status, dependencies, and acceptance criteria in `ReplicaLab_Comprehensive_Task_Division.md` before starting work.

## Required close-out checklist

Before ending work, every contributor must:

1. Update the code or docs for the task itself.
2. Update `ReplicaLab_Comprehensive_Task_Division.md` if task status, executor, dependency notes, or acceptance interpretation changed.
3. Update `docs/completion.md` if work became partial or complete.
4. Update the relevant `docs/<owner>/` files if next steps, blockers, or priorities changed.
5. Append an entry to `docs/changes.md` if the work deviated from the original plan in any meaningful way.
6. Leave shared tasks as `🟡 Partial` until all listed owners have signed off.

## Shared-task rule

If a task is assigned to more than one owner, drafting the work is not enough for final completion. The task stays partial until all owners have reviewed and signed off.

## Executor rule

If someone completes or partially completes a task assigned to another owner, that executor must be recorded in the backlog and related tracking docs.

