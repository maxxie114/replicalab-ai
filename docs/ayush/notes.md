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
- `notebooks/train_minimal_colab.ipynb` is now the explicit sponsor-facing minimal Colab script using Unsloth + HF TRL.
- `notebooks/train_colab.ipynb` is the judged notebook driver, but heavy runs
  are expected to use the `replicalab-train` entrypoint on Northflank H100.
- The primary shared base is `Qwen/Qwen3-8B` with separate Scientist GRPO and
  Lab Manager SFT adapters.
- The deterministic rubric remains the only training reward source even when
  Anthropic-backed oracle features are enabled for V2 overlays.

Current ART/OpenEnv runtime note:

- The active live Scientist RL path is now `art-scientist-train` in
  `replicalab/training/cli.py`.
- Fresh-runtime smoke validation completed on 2026-03-08 for:
  - `scientist-preview-smoke-20260308b`
  - `lab-manager-preview-smoke-20260308b`
  - `art-scientist-smoke-20260308b`
  - `art-scientist-compare-smoke-20260308b`
- The live ART Scientist checkpoint reached `step7`, but the current trained
  checkpoint still underperforms the deterministic baseline on held-out
  comparison.
- The main remaining work is experiment quality iteration, not missing training
  infrastructure.

Current localhost model-runtime note:

- `server/app.py` now exposes `/runtime` and `/agent-step` so the local app can run a backend-selected Scientist policy instead of the frontend stub.
- Anthropic-backed Scientist inference was wired, but the current Anthropic account cannot be used live because the API billing balance is too low.
- Localhost therefore currently runs in `ollama` mode with `glm-5:cloud` as the working model-backed Scientist path.
- The server applies a small deterministic safety adapter to model outputs before env stepping:
  - trims controls to fit sample size
  - aligns equipment and reagent requests to the available inventory
  - clamps duration to the current lab time limit
- If the local model stalls or errors, `/agent-step` falls back to the deterministic baseline Scientist and records that in the step metadata as `scientist_runtime=ollama_fallback`.

