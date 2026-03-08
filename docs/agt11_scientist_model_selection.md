# AGT 11 Scientist Model Selection

## Decision

The primary Scientist training model is **Qwen3-4B**.

The stretch fallback is **Qwen3-8B** if H100-only training is acceptable and
the 4B model underperforms on structured planning quality.

## Why Qwen3-4B

- Strong enough for structured JSON action output without moving to a much
  slower large-model loop.
- Small enough for fast RL iteration on H100 and practical 4-bit Colab use.
- Open weights with a permissive Apache 2.0 license.
- A clean fit for the current architecture: train the Scientist first while the
  reward and Lab Manager grounding remain deterministic.

## Why Not Smaller

- Smaller checkpoints are cheaper, but they are more likely to underperform on
  multi-step technical planning and strict output schemas.
- The project needs enough reasoning quality to negotiate across mathematics,
  machine learning, and finance-trading scenarios.

## Why Not Larger By Default

- Larger checkpoints slow rollout collection and raise memory pressure.
- The judged artifact still needs a credible Colab path, not only an H100-only
  path.
- Faster iteration matters more than squeezing out a marginal quality gain at
  this stage.

## Project Usage

- **Scientist MVP training:** `Qwen3-4B`
- **Stretch Scientist training:** `Qwen3-8B`
- **Lab Manager future path:** reuse the same base family with a separate
  role-specific adapter if the team later trains both roles

## Notes

- The reward loop stays deterministic regardless of the model choice.
- `TRN 14` should mirror this decision on the notebook side once the Colab
  skeleton exists.
