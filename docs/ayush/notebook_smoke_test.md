# Notebook Smoke Test

Purpose: verify that the training notebook and CLI-backed training flow run from a fresh runtime with frozen evidence packs and the bounded-tool policy enabled.

Last verified on `2026-03-08` with:

- `scientist-preview-smoke-20260308b`
- `lab-manager-preview-smoke-20260308b`
- `art-scientist-smoke-20260308b`
- `art-scientist-compare-smoke-20260308b`

## Fresh Runtime Setup

1. Create a fresh Python environment or notebook runtime.
2. Install the training dependencies:
   - `pip install -e .`
   - `pip install openpipe-art weave python-dotenv`
   - `pip install unsloth trl datasets matplotlib openai`
3. Confirm the local corpus exists:
   - `data/papers/manifest.json`
   - `data/papers/<field>/<paper-name>/paper.pdf`

## Environment Variables

Set these before running training or comparison:

- `WANDB_API_KEY`
- `ANTHROPIC_API_KEY` if Oracle features are being exercised
- `HF_TOKEN` for local Unsloth model downloads
- Optional: `REPLICALAB_PERSIST_ROOT`

## Smoke Commands

Run these in order:

1. Scientist dataset preview
```bash
python -m replicalab.training.cli scientist-preview --persist-root replicalab/outputs/training --run-name scientist-preview-smoke --seed-count 2 --max-steps 12
```

2. Lab Manager dataset preview
```bash
python -m replicalab.training.cli lab-manager-preview --persist-root replicalab/outputs/training --run-name lab-manager-preview-smoke --seed-count 2
```

3. ART/OpenEnv Scientist RL smoke
```bash
python -m replicalab.training.cli art-scientist-train --persist-root replicalab/outputs/art-training --run-name art-scientist-smoke --project replicalab-ai --model-name replicalab-scientist-art-live --base-model OpenPipe/Qwen3-14B-Instruct --base-url https://ayushozha-replicalab.hf.space --train-steps 1 --rollouts-per-group 2 --max-turns 4 --max-completion-tokens 450 --max-parse-retries 2 --scenario-spec 0:ml_benchmark:easy 1:ml_benchmark:medium
```

4. Before vs after comparison smoke
```bash
python -m replicalab.training.cli scientist-compare-eval --persist-root replicalab/outputs/art-training --run-name art-scientist-compare-smoke --base-url https://ayushozha-replicalab.hf.space --transport rest --eval-seeds 101 --scenarios ml_benchmark --difficulties easy --project replicalab-ai --model-name replicalab-scientist-art-live --base-model OpenPipe/Qwen3-14B-Instruct
```

## What Must Exist After Success

- `reports/summary.json`
- `reports/metrics.jsonl`
- `reports/run_metadata.json`
- `manifests/evidence_packs.json`
- `plots/*.png`

## Bounded-Tool Assertions

Check that:

1. The Scientist prompt still includes `search_evidence`, `run_code_check`, and `inspect_image`.
2. The run metadata records the bounded-tool policy.
3. Metrics export includes invalid bounded-tool rate fields even when the value is `0.0`.

## Failure Triage

- If rollout collection fails before training starts, check the ReplicaLab server URL and `/health`.
- If ART training fails after rollouts, inspect `reports/art_training_process.md` and the W&B run page.
- If comparison eval collapses while baseline succeeds, inspect whether the trained checkpoint is undertrained rather than the environment contract being broken.
