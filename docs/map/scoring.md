# Scoring Map — `replicalab/scoring/`

> Judge scoring engine for protocol evaluation.
> Pure deterministic functions — no model calls, no side effects.
>
> **Tasks implemented:** JDG 01, JDG 02, JDG 03, JDG 04, JDG 05, JDG 06, JDG 08
> **Tasks remaining:** JDG 07

## Oracle Hybrid Note

The repo now includes an additive Oracle layer for richer scenario generation,
optional Lab Manager narration, optional event injection, and post-mortem
analysis. None of that replaces the files in `replicalab/scoring/`.

For RL training, this folder remains the canonical reward source:
- deterministic
- reproducible
- testable
- used by the environment for the actual scalar reward signal

## Architecture

```
replicalab/scoring/
    __init__.py          # exports: score_rigor, score_feasibility, score_fidelity,
                         #          build_reward_breakdown, compute_total_reward
    rigor.py             # JDG 01 — protocol structural quality
    feasibility.py       # JDG 02 — resource feasibility (wraps AGT 05)
    fidelity.py          # JDG 03 — adherence to hidden reference spec
    rubric.py            # JDG 04-05 — total reward formula and breakdown builder
    explain.py           # JDG 06 — deterministic plain-English explanation
```

## Current Reward Structure

The training signal now has two layers:

- **Terminal reward** from `replicalab/scoring/rubric.py`
  - `10 * rigor * feasibility * fidelity * parsimony`
  - plus bonuses
  - minus named penalties
- **Step shaping reward** from `replicalab/env/replicalab_env.py`
  - information-gain bonus for novel questions
  - protocol-delta and momentum bonuses for productive revisions
  - contradiction, hallucination, stalling, regression, invalid-action,
    timeout, and no-agreement penalties

The judge remains deterministic. The terminal audit still explains the final
`RewardBreakdown`, while cumulative episode reward now includes the per-step
shaping applied inside the environment.

## Shared Utilities

Token matching extracted into `replicalab/utils/text.py`:
- `normalize_label(label) -> str` — lowercase, strip, collapse whitespace
- `element_tokens(element) -> list[str]` — split into searchable tokens (3+ chars)

Used by: `validation.py`, `rigor.py`, `fidelity.py`

---

## JDG 01 — `score_rigor(protocol, scenario) -> float`

**File:** `rigor.py`
**Range:** [0.0, 1.0]
**Measures:** structural completeness and alignment to scenario requirements.

### Weight Breakdown

| Component | Weight | Method |
|-----------|--------|--------|
| Structural completeness | 0.30 | Field population checks |
| Success criteria coverage | 0.40 | Token match vs `scenario.success_criteria` |
| Required element coverage | 0.30 | Token match vs `hidden_reference_spec.required_elements` |

### Structural Completeness (0.30)

Each check contributes equally (0.05 each, total 0.35, then normalized):

| Check | Condition |
|-------|-----------|
| Sample size present | `sample_size >= 1` |
| Sample size meaningful | `sample_size >= 4` |
| Has control | `len(controls) >= 1` |
| Has second control | `len(controls) >= 2` |
| Technique specified | `technique` non-empty |
| Duration allocated | `duration_days >= 1` |
| Substantive rationale | `len(rationale) > 20` |

### Internal Functions

| Function | Purpose |
|----------|---------|
| `_structural_completeness(protocol)` | Field population score |
| `_success_criteria_coverage(protocol, scenario)` | Fraction of criteria matched |
| `_required_element_coverage(protocol, scenario)` | Fraction of elements matched |
| `_protocol_text_blob(protocol)` | Join all text fields for matching |
| `_text_matches(element, blob)` | Token overlap check |

---

## JDG 02 — `score_feasibility(protocol, scenario, check=None) -> float`

**File:** `feasibility.py`
**Range:** [0.0, 1.0]
**Measures:** whether the lab can execute this protocol.

### Key Design: No Rescoring

Does NOT recompute feasibility from scratch. Derives score from `FeasibilityCheckResult`
produced by AGT 05's `check_feasibility()`. If no pre-computed check is passed, calls
`check_feasibility()` internally. This prevents drift between Lab Manager grounding
and Judge scoring.

### Weight Breakdown

7 dimensions, each worth 1/7:

| Dimension | Type | Partial Credit Formula |
|-----------|------|----------------------|
| Protocol | Binary | 1.0 if ok, else 0.0 |
| Budget | Continuous | `min(1.0, budget_remaining / estimated_cost)` |
| Equipment | Continuous | fraction of required items that are available |
| Reagents | Continuous | fraction of required items that are in stock |
| Schedule | Binary | 1.0 if ok, else 0.0 |
| Staff | Continuous | `min(1.0, staff_count / required_staff)` |
| Policy | Binary | 1.0 if ok, else 0.0 (hard constraint) |

### Internal Functions

| Function | Purpose |
|----------|---------|
| `_budget_score(check, budget_remaining)` | Continuous budget ratio |
| `_staff_score(check, staff_count)` | Continuous staff ratio |
| `_fraction_score(required, available)` | Generic item-availability fraction |

---

## JDG 03 — `score_fidelity(protocol, scenario) -> float`

**File:** `fidelity.py`
**Range:** [0.0, 1.0]
**Measures:** adherence to `hidden_reference_spec` (which the scientist never sees).

### Weight Breakdown

| Component | Weight | Method |
|-----------|--------|--------|
| Required element coverage | 0.50 | Substitution-aware token match |
| Flexible element alignment | 0.20 | Bonus only, no penalty |
| Target metric alignment | 0.20 | Token match vs metric + value |
| Technique appropriateness | 0.10 | Token match vs spec summary |

### Substitution-Aware Scoring

For required elements:
- **Direct match** (token in protocol text): 1.0 credit
- **Substitution match** (allowed alternative present): 0.7 credit
- **Miss**: 0.0 credit

This is the key difference from JDG 01's element check.

### Internal Functions

| Function | Purpose |
|----------|---------|
| `_required_element_score(elements, text, sub_index)` | Substitution-aware coverage |
| `_flexible_element_score(elements, text)` | Bonus-only coverage |
| `_target_metric_score(metric, value, text)` | Metric + value matching |
| `_technique_score(summary, text)` | Summary alignment |
| `_protocol_text_blob(protocol)` | Join text fields |
| `_text_matches(element, blob)` | Token overlap |
| `_substitution_matches(element, text, sub_index)` | Check alternatives |
| `_build_substitution_index(scenario)` | Map originals → alternatives |

---

---

## JDG 04 — `compute_total_reward(breakdown) -> float`

**File:** `rubric.py`
**Formula:** `10 × rigor × feasibility × fidelity + efficiency_bonus + communication_bonus − sum(penalties)`

Returns a scalar reward from a `RewardBreakdown` object.

## JDG 05 — `build_reward_breakdown(protocol, scenario, rounds_used, max_rounds, *, check=None) -> RewardBreakdown`

**File:** `rubric.py`
**Composes:** rigor (JDG 01) + feasibility (JDG 02) + fidelity (JDG 03) + efficiency bonus.

### Efficiency Bonus
- Max bonus: 1.0 (configurable via `_MAX_EFFICIENCY_BONUS`)
- Formula: `bonus × (max_rounds - rounds_used) / (max_rounds - 1)`
- Finishing in round 1 of 6 → maximum bonus; using all rounds → 0

### Internal Functions

| Function | Purpose |
|----------|---------|
| `compute_total_reward(breakdown)` | Apply the reward formula |
| `build_reward_breakdown(...)` | Compose all sub-scores into a breakdown |
| `_efficiency_bonus(rounds_used, max_rounds)` | Compute efficiency bonus |

---

## Not Yet Implemented

### Bonuses & Penalties — JDG 07
- `communication_bonus`: reward for clear negotiation (reserved)
- `penalties`: policy violations, hallucinated resources, etc.

## Data Consumed

| Source | Used by | For what |
|--------|---------|----------|
| `Protocol` (models.py) | All 3 scorers | The final agreed protocol |
| `NormalizedScenarioPack` (scenarios) | All 3 scorers | Constraints, resources, criteria |
| `HiddenReferenceSpec` (scenarios) | JDG 01, JDG 03 | Required/flexible elements, target metric |
| `FeasibilityCheckResult` (agents) | JDG 02 | 7 dimension checks with partial credit |
| `AllowedSubstitution` (scenarios) | JDG 03 | Partial credit for substitutions |
| `element_tokens` (utils/text.py) | JDG 01, JDG 03 | Shared token extraction |

## Test Coverage — `tests/test_reward.py`

| Test | What it verifies |
|------|-----------------|
| `test_rigor_good_protocol_scores_higher_than_bad` | Quality ordering |
| `test_rigor_is_deterministic` | Same inputs → same output |
| `test_rigor_empty_controls_reduces_score` | Controls matter |
| `test_rigor_short_rationale_reduces_score` | Rationale length matters |
| `test_rigor_all_domains_return_valid_range` | [0,1] across all 9 combinations |
| `test_feasibility_viable_protocol_scores_high` | Good protocol > 0.7 |
| `test_feasibility_infeasible_protocol_scores_lower` | Bad < good |
| `test_feasibility_accepts_precomputed_check` | Pre-computed = computed |
| `test_feasibility_is_deterministic` | Same inputs → same output |
| `test_feasibility_partial_credit_for_near_budget` | Slightly over > far over |
| `test_feasibility_all_domains_return_valid_range` | [0,1] across all 9 combinations |
| `test_fidelity_aligned_protocol_scores_higher` | Aligned > misaligned |
| `test_fidelity_is_deterministic` | Same inputs → same output |
| `test_fidelity_substitution_gets_partial_credit` | Sub > miss |
| `test_fidelity_mentioning_target_metric_improves_score` | Metric mention helps |
| `test_fidelity_all_domains_return_valid_range` | [0,1] across all 9 combinations |
| `test_all_scores_between_zero_and_one_for_bad_protocol` | Bounds check |
| `test_good_protocol_dominates_bad_on_rigor_and_fidelity` | Cross-scorer consistency |
| `test_good_protocol_beats_awful_protocol_on_all_scores_and_total_reward` | Good protocol beats a clearly infeasible protocol across all judge axes |
| `test_rigor_explicit_success_criteria_mentions_improve_score` | Success-criteria mentions improve rigor coverage |
| `test_feasibility_partial_equipment_credit_sits_between_full_and_total_miss` | Partial equipment availability yields intermediate feasibility credit |
| `test_fidelity_direct_match_beats_substitution_and_miss` | Fidelity prefers direct match over allowed substitution over a miss |
| `test_breakdown_matches_with_and_without_precomputed_feasibility_check` | Reward breakdown stays identical with or without an injected feasibility check |
