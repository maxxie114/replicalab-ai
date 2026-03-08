# Ayush Notes

Use this file for short-lived working notes, reminders, and handoff details.

Do not use this file for durable deviations from the original plan. Put those in `docs/changes.md`.

Current local training-data note:

- A 50-paper experiment-design corpus now exists under `data/papers/`.
- Use `data/papers/manifest.json` for the full scenario-to-paper mapping.
- Most entries are marked `alternative` because many scenario titles in
  `ReplicaLab_50_Scenarios_Training_Plan.md` are synthetic summaries rather
  than directly downloadable published paper titles.

Current V2 training architecture note:

- The reusable training stack now lives under `replicalab/training/`.
- `notebooks/train_colab.ipynb` is the judged notebook driver, but heavy runs
  are expected to use the `replicalab-train` entrypoint on Northflank H100.
- The primary shared base is `Qwen/Qwen3-8B` with separate Scientist GRPO and
  Lab Manager SFT adapters.
- The deterministic rubric remains the only training reward source even when
  Anthropic-backed oracle features are enabled for V2 overlays.

