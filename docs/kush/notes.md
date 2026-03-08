# Person D Notes

Use this file for working notes and short-term reminders.

Durable deviations belong in `docs/changes.md`.

---

## 2026-03-08 demo-flow refinement

- Dashboard now frames the product as `paper -> brief -> negotiate -> judge -> train`.
- Episode page now foregrounds the source paper and explicitly connects the terminal judge result to the training loop.
- Controls now read as replication setup instead of generic episode controls.
- Compare page is positioned as a seeded evaluation bench rather than the primary training-results story.
- The frontend default step action is now scenario-aware, so the live episode path produces valid judged runs instead of immediate invalid-action penalties on ML cases.
- The negotiation panel now shows an explicit `Advance First Round` CTA so a newly reset episode no longer looks frozen at `0 messages`.
- The dashboard `Replicate a Paper` CTA now launches a seeded live demo automatically: reset, first proposal, autoplay, and judged completion all happen without extra clicks.
- The replication setup card now performs a backend health check up front and surfaces a concrete startup command instead of the opaque browser-level `Failed to fetch` message when the API server is down.

## 2026-03-08 three-outcome live demo

- The live demo now has three seeded story modes on the dashboard: `fast-agreement`, `learning-opportunity`, and `no-agreement`.
- Each mode runs against the real backend with deterministic episode data and renders a post-episode results report instead of stopping at a generic terminal state.
- The results report now shows executed rounds, disagreement count, replicability score, paper reliability quality, reward and score charts, training interpretation, and next-tool suggestions.
- Verified backend-driven outputs for the current seeded ML demo cases:
  - `fast-agreement` -> round `2`, verdict `accept`, cumulative reward `2.906845`
  - `learning-opportunity` -> round `6`, verdict `accept`, cumulative reward `4.537097`
  - `no-agreement` -> round `6`, verdict `timeout`, cumulative reward `0.366529`

## 2026-03-08 training page with real artifacts

- Added a dedicated `/training` page instead of relying on the old packaged dashboard card.
- The new page is backed by real artifact values from the existing outputs:
  - local deterministic baseline summary
  - live ART/OpenEnv scientist checkpoints
  - seeded hold-out compare summary
  - scientist and lab-manager preview summaries
- The training story is now explicit and honest:
  - the training pipeline works
  - live reward moved positive by later checkpoints
  - hold-out compare still shows the trained Scientist underperforming baseline
  - more training and parser/invalid-action cleanup are still needed
- Header nav now includes `Training`, dashboard training CTA points there, and the dashboard training teaser uses the same artifact-backed data.

## 2026-03-08 automated demo video build

- Added `scripts/build_demo_video.py` to synthesize an ElevenLabs voiceover from `.env`, capture clean frontend screenshots, generate captioned slides, and build the final mp4 with `ffmpeg`.
- Added `docs/demo_video_script_60s.md` as the canonical one-minute narration and shot list.
- Generated the current outputs under `replicalab/outputs/demo_video/`:
  - `audio/voiceover.mp3`
  - `replicalab_demo_60s.mp4`
  - `text/voiceover.txt`
  - `text/voiceover.srt`

## 2026-03-08 Hugging Face Space redeploy

- Investigated the public Space after it showed only the backend landing page instead of the React app.
- Confirmed the repo already had the correct multi-stage Dockerfile and SPA-serving `server/app.py`, but the runtime SHA was still pinned to an older backend-only container.
- Synced the current app files to `ayushozha/replicalab` through the Hugging Face API, restarted the Space, and waited for the runtime SHA to advance to the new repo revision.
- Reverified:
  - `https://ayushozha-replicalab.hf.space/` now serves the React frontend
  - `https://ayushozha-replicalab.hf.space/episode?...` returns `200`
  - `https://ayushozha-replicalab.hf.space/health` still reports `{\"status\":\"ok\",\"env\":\"real\",\"version\":\"0.1.0\"}`

## 2026-03-08 policy-results clarification page

- Added a dedicated `/policies` frontend route for the question: baseline vs trained vs oracle.
- The new page makes the current runtime explicit:
  - `/compare` is still the seeded deterministic benchmark bench
  - the public app is not currently mounting the trained Scientist adapter
  - the public app is not currently mounting the Anthropic oracle path
  - the Judge remains deterministic
- Updated `/compare` with a callout so it no longer implies that it is already comparing live mounted model policies.

## 2026-03-08 localhost model-backed Scientist mode

- Added live runtime detection to the episode flow through `/runtime`.
- Non-demo localhost episodes now prefer the backend `/agent-step` route instead of the frontend default action builder when a model runtime is available.
- The episode page now surfaces the current Scientist runtime directly in the UI so it is clear whether localhost is using baseline or a model-backed path.
- Current live localhost mode is `ollama` with `glm-5:cloud`.
- Anthropic-backed Scientist mode exists in code, but the current Anthropic account cannot run live due to insufficient API credits, so localhost falls back to the Ollama runtime for real model-driven stepping.

## 2026-03-08 dynamic live-run and judge-caveat cleanup

- The main dashboard CTA no longer launches the same fixed seeded flow every time.
- `Replicate a Random Paper` now generates a fresh seeded route with a random scenario family, difficulty, and seed, then autostarts the live episode path.
- The three fixed cards remain available, but are now labeled as scripted outcomes rather than the default live experience.
- Accepted verdicts that still carry weak-component reasons are now shown as `Accept with caveats` in the judge-facing UI instead of `Accept` plus a contradictory `Failure Reasons` block.
- The results page now reports those cases as conditional replication candidates rather than clean wins.
- The stage animation and completion toast now treat accepted-with-caveats runs as partial wins instead of full celebratory successes.
- Live reset verification confirmed the random path can surface distinct paper briefs across scenario families, including CIFAR-10 replication and offline mean-reversion backtest cases.

