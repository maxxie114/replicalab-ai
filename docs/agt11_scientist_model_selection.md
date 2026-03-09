# AGT 11 Scientist Model Selection

## Decision

The primary Northflank and local training base for both role adapters is now
**Qwen/Qwen3.5-9B**.

The reduced-scale fallback is **Qwen/Qwen3.5-4B** for lower-memory smoke runs,
faster iteration, and notebook fallback paths.

The optional audit-only judge model candidate is
**Qwen/Qwen3.5-122B-A10B**. It is not part of the deterministic reward loop.

## Role Mapping

- **Scientist**: `Qwen/Qwen3.5-9B` + Unsloth GRPO LoRA
- **Lab Manager / Lab Research Assistant**: `Qwen/Qwen3.5-9B` + Unsloth SFT LoRA
- **Fallback Scientist or Lab Manager**: `Qwen/Qwen3.5-4B`
- **Audit-only judge candidate**: `Qwen/Qwen3.5-122B-A10B`

## Why Qwen3.5-9B For The Two Trainable Roles

- It is a cleaner fit for the current Northflank H100 path than the older
  `Qwen3-8B` baseline and keeps both trainable roles on one family.
- It preserves enough planning headroom for strict JSON action output,
  paper-grounded reasoning, and negotiation under constraints.
- It still leaves a realistic fallback to the 4B variant when the team wants
  faster notebook iteration.

## Why Keep The Judge Deterministic

- The reward source must stay reproducible across runs.
- A large model judge is useful for audits, narrative analysis, and post-run
  error review, but not for the scalar training reward.
- This keeps benchmark history and before/after graphs comparable across runs.

## Current Training Priorities

1. Measure paper understanding explicitly on every evaluation run.
2. Expand Scientist prompt coverage around paper understanding, constraint
   grounding, and negotiation quality.
3. Keep cumulative benchmark graphs updating across runs instead of only
   saving one-off plots.
4. Treat the execution-style lab environment as the next architecture phase,
   not as an untracked reward change.
