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

