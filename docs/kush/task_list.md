# Kush (Person D) Task List

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## Current status

- All Person D implementation and storytelling tasks are recorded complete in the source-of-truth backlog.
- The frontend now presents the demo in the intended order:
  - source paper
  - parsed replication brief
  - live negotiation
  - deterministic judge
  - training story
- The dashboard, episode page, training panel, and evaluation bench all build successfully after the latest refinement pass.

---

## Active focus

- No open Person D implementation blockers remain in the backlog.
- Remaining polish is demo execution quality:
  - keep the live script aligned with the new paper-to-training UI flow
  - swap packaged training demo data for live artifacts if a final run is ready
  - capture final screenshots or footage from the updated frontend

---

## Notes for demo prep

- Start the live walkthrough from `/episode?template=ml_benchmark&difficulty=medium`.
- Use the left panel to anchor the narrative in the source paper and parsed brief.
- Use the right-side training callout at episode end to connect the judged reward to the minimal Colab notebook.
- Use `/compare` as the seeded evaluation bench, not as the primary baseline-vs-trained story.
