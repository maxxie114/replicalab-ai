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
- The primary shared base is now `Qwen/Qwen3.5-9B` with separate Scientist
  GRPO and Lab Manager SFT adapters.
- The reduced-scale fallback is `Qwen/Qwen3.5-4B`.
- The audit-only judge candidate is `Qwen/Qwen3.5-122B-A10B`.
- The deterministic rubric remains the only training reward source even when
  Anthropic-backed oracle features are enabled for V2 overlays.
- `docs/training_goals.md` now defines the current model goals and the
  separation between metric improvements and the larger execution-env redesign.
- A March 9 operational check found that the current Hugging Face token is
  valid for Hub auth but belongs to a non-billable personal account
  (`canPay=false`, no orgs), so it is not currently enough to provision paid
  large-model hosting on Hugging Face.
- The current Northflank manual job `replicalab-train` still has runtime env
  values, but `northflank start job run` returns `409 No deployment
  configured`, so the job cannot launch until a runnable image/deployment is
  attached.
- The live Northflank service on the same `nf-gpu-hack-16-64` plan does not
  currently expose `nvidia-smi` or `/dev/nvidia*` inside the container, so GPU
  availability should be treated as unverified until the runtime is fixed and a
  direct hardware probe succeeds.

Current Northflank notebook note:

- The dedicated notebook service now lives in project `notebook-openport` as
  service `jupyter-pytorch`.
- The pasted notebook hostname `app--jupyter-pytorch--h74j66w224jx.code.run`
  is stale; the live public notebook endpoint on 2026-03-09 is
  `app--jupyter-pytorch--9y6g97v7czb9.code.run`.
- The notebook runtime does expose a real `NVIDIA H100 80GB HBM3` GPU.
- `/home/jovyan/replicalab-ai` and `/home/jovyan/replicalab-qwen3.5-grpo`
  already exist in that notebook, with saved adapter checkpoints through
  `checkpoint-200`.
- The saved `grpo_training.log` shows the notebook ran on H100 but did not
  complete cleanly: baseline eval emitted `string indices must be integers, not
  'str'`, and the final inference cell failed in
  `tokenizer.apply_chat_template(...)` with the same content-structure issue.

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
- Evaluation summaries now track `paper_understanding` and
  `communication_quality`, and the shared benchmark-history plots live under
  `replicalab/outputs/training/history/`.

Current localhost model-runtime note:

- `server/app.py` now exposes `/runtime` and `/agent-step` so the local app can run a backend-selected Scientist policy instead of the frontend stub.
- Anthropic-backed Scientist inference was wired, but the current Anthropic account cannot be used live because the API billing balance is too low.
- Localhost therefore currently runs in `ollama` mode with `glm-5:cloud` as the working model-backed Scientist path.
- The server applies a small deterministic safety adapter to model outputs before env stepping:
  - trims controls to fit sample size
  - aligns equipment and reagent requests to the available inventory
  - clamps duration to the current lab time limit
- If the local model stalls or errors, `/agent-step` falls back to the deterministic baseline Scientist and records that in the step metadata as `scientist_runtime=ollama_fallback`.

