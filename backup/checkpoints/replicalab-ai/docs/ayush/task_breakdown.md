# Person B (Ayush) Task Breakdown and Execution Plan

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

---

## 1. Status

Ayush's implementation lane is complete.

Completed tasks in this lane now cover:

1. Scientist prompting and parsing
2. Baseline Scientist policy
3. Shared deterministic Lab Manager grounding contributions
4. Notebook and reusable training stack
5. ART/OpenEnv rollout-to-trainer integration
6. Metrics, plotting, evaluation, trained-policy loading, and metadata export
7. Fresh-runtime notebook smoke validation

The remaining training risk is no longer missing backlog work in Ayush's lane.
It is model quality:

1. The ART/OpenEnv Scientist runtime is live and reproducible.
2. The latest live checkpoint still underperforms the deterministic baseline on held-out comparison.
3. The next useful work is experiment iteration, not infrastructure completion.

---

## 2. Final Verification State

The following validation steps are now complete:

1. `scientist-preview` smoke run
2. `lab-manager-preview` smoke run
3. live `art-scientist-train` smoke run against the hosted ReplicaLab environment
4. `scientist-compare-eval` smoke run against the trained checkpoint
5. focused training-policy tests and CLI tests

Smoke artifacts now exist under:

1. `replicalab/outputs/training/scientist-preview-smoke-20260308/`
2. `replicalab/outputs/training/lab-manager-preview-smoke-20260308/`
3. `replicalab/outputs/art-training/art-scientist-smoke-20260308/`
4. `replicalab/outputs/art-training/art-scientist-compare-smoke-20260308/`

---

## 3. Remaining External Work

No Ayush-owned backlog items remain.

Open work outside this lane that still matters to the final story:

1. `TRN 12` owned by Person D: turn evaluation outputs into judge-facing result bullets
2. UI and README result presentation tasks
3. demo-storytelling tasks

These are not blockers for the training runtime itself.

---

## 4. Next Technical Focus

If work continues in this lane, it should target model improvement rather than missing task closure:

1. Increase Scientist training coverage beyond the current smoke scenario set
2. Inspect failure episodes from `art-scientist-compare-20260308-step5` and `art-scientist-compare-smoke-20260308`
3. Add stronger warm-start or curriculum before more RL updates
4. Execute the Lab Manager SFT path live and evaluate its effect separately
5. Keep baseline-vs-trained comparisons on fixed seeds and frozen evidence packs

---

## 5. Base Model Assumptions

Primary shared base: **Qwen3-8B**

1. Scientist uses the shared base with a GRPO-style trainable adapter.
2. Lab Manager uses the same shared base with a separate SFT adapter.
3. Anthropic remains an additive oracle and explanation layer only.
4. The deterministic rubric remains the only training reward source.

---

## 6. Summary Table

| Category | Count | Status |
|----------|-------|--------|
| Ayush-owned tasks remaining | 0 | Closed |
| Technical blockers in Ayush lane | 0 | Closed |
| Live runtime path | 1 | Validated |
| Main remaining risk | 1 | Model quality, not infrastructure |
