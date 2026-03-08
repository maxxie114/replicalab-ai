# AGT 11 Scientist Model Selection

## Decision

The primary V2 training base model is **Qwen3-8B**.

The reduced-scale fallback is **Qwen3-4B** when Colab, T4, or lower-memory
debugging is more important than maximum planning quality.

The same `Qwen3-8B` base is shared across two first-class model artifacts:

- **Scientist**: GRPO LoRA via Unsloth
- **Lab Manager**: SFT LoRA via Unsloth

## Why Qwen3-8B

- Stronger structured planning headroom for the Scientist GRPO target while
  still fitting comfortably on the H100 runtime the team now intends to use.
- Large enough to support both the Scientist and Lab Manager adapters on one
  shared base family without fragmenting the stack.
- Open weights with a permissive Apache 2.0 license.
- A clean fit for the current V2 architecture: keep deterministic reward and
  feasibility truth while training two role-specific adapters on one base.

## Why Not Smaller By Default

- Smaller checkpoints are cheaper, but they lose headroom on multi-step
  technical planning, strict JSON output, and richer Lab Manager narration.
- The active runtime assumption is now a Northflank H100 GPU job rather than a
  Colab-first compromise.

## Why Keep Qwen3-4B As Fallback

- The judged artifact still needs a credible notebook path even if the heavy
  run happens on Northflank.
- `Qwen3-4B` remains useful for smoke tests, lower-cost debugging, and any
  reduced-scale Colab fallback.

## Project Usage

- **Scientist primary training:** `Qwen/Qwen3-8B`
- **Lab Manager primary training:** `Qwen/Qwen3-8B` with a separate adapter
- **Fallback notebook/debug training:** `Qwen/Qwen3-4B`

## Notes

- The reward loop stays deterministic regardless of the model choice.
- The active oracle provider remains external and API-only; Anthropic is used
  for scenario enrichment and post-mortem features, not as the training reward.
- `TRN 14` should mirror this decision on the notebook side and in the
  Northflank H100 job entrypoint.
