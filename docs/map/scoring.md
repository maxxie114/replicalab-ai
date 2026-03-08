# Scoring Map — `replicalab/scoring/`

> Judge scoring engine for protocol evaluation.
>
> **Status:** NOT YET IMPLEMENTED
> **Tasks remaining:** JDG 01-08

## Planned Architecture

```
replicalab/scoring/
    __init__.py          # exports: score_rigor, score_feasibility, score_fidelity, compute_reward
    rigor.py             # JDG 01 — protocol structural quality
    feasibility.py       # JDG 02 — resource feasibility (wraps AGT 05)
    fidelity.py          # JDG 03 — adherence to hidden reference spec
```

## Planned Functions

### `score_rigor(protocol, scenario) -> float` — JDG 01
Score range: [0.0, 1.0]
Measures: structural completeness, success criteria coverage, required element coverage.

### `score_feasibility(protocol, scenario, check_result=None) -> float` — JDG 02
Score range: [0.0, 1.0]
Measures: whether the lab can execute the protocol (budget, equipment, reagents, schedule, staff, policy).
Reuses `check_feasibility()` from AGT 05. Adds partial credit (continuous signal vs binary pass/fail).

### `score_fidelity(protocol, scenario) -> float` — JDG 03
Score range: [0.0, 1.0]
Measures: how closely the protocol matches `hidden_reference_spec`.
Substitution-aware — allowed substitutions get partial credit.

### `compute_reward(protocol, scenario, check_result=None) -> RewardBreakdown` — JDG 04/05
Combines rigor + feasibility + fidelity into `RewardBreakdown`.
Applies efficiency bonus, communication bonus, and penalties.

## Data Consumed

| Source | Used by | For what |
|--------|---------|----------|
| `Protocol` (models.py) | All scorers | The final agreed protocol |
| `NormalizedScenarioPack` (scenarios) | All scorers | Constraints, resources, success criteria |
| `HiddenReferenceSpec` (scenarios) | JDG 01, JDG 03 | Required/flexible elements, target metric |
| `FeasibilityCheckResult` (agents) | JDG 02 | 7 dimension checks |
| `AllowedSubstitution` (scenarios) | JDG 03 | Partial credit for substitutions |
| `RewardBreakdown` (models.py) | JDG 04/05 | Output container |

## Data Produced

`RewardBreakdown` populates:
- `rigor: float` — from JDG 01
- `feasibility: float` — from JDG 02
- `fidelity: float` — from JDG 03
- `efficiency_bonus: float` — from JDG 04 (rounds used / max rounds)
- `communication_bonus: float` — from JDG 05 (negotiation quality)
- `penalties: dict[str, float]` — from JDG 06-08 (policy violations, etc.)
