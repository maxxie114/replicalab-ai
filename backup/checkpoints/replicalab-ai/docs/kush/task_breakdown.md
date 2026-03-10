# Kush (Person D) Task Breakdown

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current situation

- Person D's backlog is complete in the main tracker.
- The frontend narrative has now been tightened around the actual hackathon demo:
  1. show the paper
  2. show the parsed replication task
  3. watch the Scientist and Lab Manager negotiate
  4. reveal the deterministic judge verdict
  5. connect that verdict to training
- The current frontend build is green after cleaning pre-existing strict TypeScript issues in several imported UI components.

---

## Demo-order guidance

1. Dashboard
   Show the four-step paper-to-training flow and use `Replicate a Paper`.
2. Episode page
   Keep the audience on the source paper and benchmark context first, then let the conversation and score panels do the live work.
3. Episode end state
   Use the training callout to explain why the judge output matters beyond the demo.
4. Training panel
   Reference the minimal Colab notebook and fixed-seed evaluation framing.
5. Compare page
   Position it as a seeded evaluation bench for additional cases.

---

## Remaining practical polish

- If a final live training run is ready, replace the packaged demo comparison data in `TrainingResults.tsx`.
- Capture updated screenshots or footage from the new dashboard and episode layouts.
- Keep README/demo copy aligned with the same paper-to-training sequence.
- Keep the backend health check visible on the setup card so live demos fail loudly and instructively if the API server is not running.
