# Project Management Rules

This document defines the required project-management workflow for all contributors in the repository.

## File hierarchy

Use the following order of authority when project-management files disagree:

1. `ReplicaLab_Comprehensive_Task_Division.md`
2. `AGENTS.md`
3. `docs/project_management_rules.md`
4. `docs/completion.md`
5. `docs/changes.md`
6. `docs/<owner>/` folders

## Purpose of each file

| File | Purpose |
| --- | --- |
| `ReplicaLab_Comprehensive_Task_Division.md` | Source of truth for scope, ownership, dependencies, acceptance criteria, and task status |
| `docs/completion.md` | Rollup of completed tasks and active partial tasks |
| `docs/changes.md` | Append-only log of deviations from the original plan |
| `docs/<owner>/task_list.md` | Owner-local task list and short status summary |
| `docs/<owner>/task_breakdown.md` | Owner-local blockers, dependency chain, and execution order |
| `docs/<owner>/notes.md` | Working notes, handoff notes, and reminders that are not deviations |
| `docs/<owner>/README.md` | Explains the role of the owner folder |

## Docs folder structure

- Each contributor keeps a folder under `docs/`.
- Use the actual person name when known.
- If the real name is not yet known, use a role placeholder such as `person_a`.
- Current owner-folder mapping for this repo:
  - `docs/ayush/` = Person B (Ayush)
  - `docs/kian/` = Person A
  - `docs/max/` = Person C
  - `docs/kush/` = Person D
- The minimum expected files per contributor folder are:
  - `README.md`
  - `task_list.md`
  - `task_breakdown.md`
  - `notes.md`

## Start-of-task workflow

Before starting a task:

1. Confirm the task is unblocked in `ReplicaLab_Comprehensive_Task_Division.md`.
2. Check `docs/completion.md` for current completed and active partial work.
3. Check `docs/changes.md` for recent deviations that may affect the task.
4. Check the relevant owner folder in `docs/`.
5. If the task is shared, identify the remaining sign-off requirement before making changes.

## Branch and PR rules

- One task or one tightly related task bundle per branch.
- Use the task id in the branch name when practical.
- Preferred branch name patterns:
  - `feature/<task-id>-<short-slug>`
  - `fix/<task-id>-<short-slug>`
  - `docs/<task-id>-<short-slug>`
  - `chore/<task-id>-<short-slug>`
- Do not mix unrelated tasks in the same branch or PR.
- Use `.github/pull_request_template.md` for every PR and `.github/ISSUE_TEMPLATE/task.yml` for task issues.
- Every PR should include:
  - task id or task ids
  - summary of what changed
  - verification performed
  - docs updated
  - deviations recorded, if any
- If the work is partial, say what remains and who owns the remaining sign-off or implementation.

## Task status rules

- Use `⬜ Not started` when no meaningful work for the task has landed.
- Use `🟡 Partial` when draft work is done but acceptance is not fully met.
- Use `✅ Completed` only when the task acceptance criteria are fully satisfied.
- Use `❌ Failed` only when the task path is explicitly abandoned or invalidated.

## Shared-task sign-off rules

- Shared tasks require all listed owners to sign off before completion.
- The drafting owner must document:
  - what is already done
  - what acceptance item remains
  - who must sign off
- Shared tasks remain `🟡 Partial` until that sign-off is recorded.

## Executor tracking rules

- If a contributor works on a task assigned to someone else, record that in:
  - `ReplicaLab_Comprehensive_Task_Division.md`
  - `docs/completion.md`
  - `docs/changes.md`
- Assignment does not change automatically just because another person executed the work.
- If ownership should change permanently, that must be logged as a deviation in `docs/changes.md`.

## Deviation logging rules

Append an entry to `docs/changes.md` whenever any of the following happens:

- a task is executed by someone other than the assigned owner
- a task order changes for dependency or urgency reasons
- a task is re-scoped
- a new process or governance artifact is introduced outside the original plan
- architecture or implementation direction changes from the original source of truth
- a task is marked partial because of a sign-off or dependency issue

`docs/changes.md` is append-only. Do not rewrite or delete historical entries unless they are factually wrong.

## Which file to update when

| Situation | Required updates |
| --- | --- |
| Task status changes | `ReplicaLab_Comprehensive_Task_Division.md`, `docs/completion.md`, owner folder |
| Task executor differs from assignee | `ReplicaLab_Comprehensive_Task_Division.md`, `docs/completion.md`, `docs/changes.md` |
| Blocker or next-step change | owner `task_breakdown.md`, optionally `task_list.md` |
| New durable deviation from original plan | `docs/changes.md`, and any affected source-of-truth file |
| Contract or interface freeze | source artifact plus backlog and completion tracker |

## Project memory rule for automated model agents

For automated model agents, the files listed in `AGENTS.md` are the persistent project memory for the repository.

- Load them into working context at task start.
- Preserve their constraints while working.
- Write back any relevant status, deviation, or planning change before ending work.
- If context is tight, summarize them into working notes, but do not skip them.

## Minimal close-out checklist

- The task artifact itself is updated.
- Verification was run or explicitly skipped with reason.
- Tracking docs reflect the current state.
- Deviations are logged if the work changed the original plan.

