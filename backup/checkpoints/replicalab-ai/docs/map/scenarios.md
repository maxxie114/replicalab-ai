# Scenarios Map — `replicalab/scenarios/`

> Normalized scenario generation across 3 domains with seeded determinism.
>
> **Tasks implemented:** SCN 01-12

## Entry Point

### `generate_scenario(seed, template, difficulty) -> NormalizedScenarioPack`
Located in `templates.py`. The main public API.

**Flow:**
1. `seed_rng(seed)` → deterministic `random.Random` instance
2. `load_template(template)` → picks the template builder function
3. `builder(rng)` → raw draft dict (randomly selects one of 2 cases per domain)
4. `apply_difficulty(draft, difficulty, rng)` → scales budget, time, staff, resources
5. `_build_pack(seed, template, draft)` → constructs `NormalizedScenarioPack`

### `available_scenario_families() -> list[dict]`
Returns `[{"family": name, "difficulties": ["easy", "medium", "hard"]}]` for each template.

## Core Data Classes (all in `templates.py`)

### `NormalizedScenarioPack(BaseModel)` — `extra="forbid"`
The complete scenario definition. Every downstream consumer uses this.

| Field | Type | Source |
|-------|------|--------|
| `scenario_id` | `str` | `"{template}_{seed}"` |
| `template` | `TemplateName` | input param |
| `domain_id` | `str` | from template case |
| `difficulty` | `Difficulty` | input param |
| `seed` | `int` | input param |
| `task_summary` | `str` | from template case |
| `success_criteria` | `list[str]` | from template case |
| `constraints` | `list[ScenarioConstraint]` | from template + difficulty scaling |
| `resources` | `list[ScenarioResource]` | from template + difficulty scaling |
| `allowed_substitutions` | `list[AllowedSubstitution]` | from template case |
| `hidden_reference_spec` | `HiddenReferenceSpec` | from template case |
| `scientist_observation` | `ScientistObservation` | built from case fields |
| `lab_manager_observation` | `LabManagerObservation` | built from case fields |

### `ScenarioConstraint(BaseModel)`
| Field | Type | Example |
|-------|------|---------|
| `key` | `str` | `"gpu_hours"` |
| `label` | `str` | `"Maximum GPU budget"` |
| `quantity` | `float \| int \| None` | `8` |
| `unit` | `str \| None` | `"gpu_hours"` |
| `comparator` | `Literal["<=", ">=", "="]` | `"<="` |
| `hard` | `bool` | `True` |
| `details` | `str` | `"The full run must fit within eight GPU-hours."` |

### `ScenarioResource(BaseModel)`
| Field | Type | Example |
|-------|------|---------|
| `key` | `str` | `"gpu_node"` |
| `label` | `str` | `"A100 GPU node"` |
| `quantity` | `float \| int \| None` | `1` |
| `unit` | `str \| None` | `"node"` |
| `available` | `bool` | `True` |
| `category` | `str` | `"compute"` |
| `details` | `str` | `"Reserved for one benchmark run at a time."` |

### `AllowedSubstitution(BaseModel)`
| Field | Type | Example |
|-------|------|---------|
| `original` | `str` | `"A100 GPU node"` |
| `alternative` | `str` | `"V100 GPU node"` |
| `condition` | `str` | `"Use if A100 is booked."` |
| `tradeoff` | `str` | `"V100 is slower; extend training by ~30%."` |

### `HiddenReferenceSpec(BaseModel)`
Ground truth the judge uses to score fidelity. The scientist never sees this.

| Field | Type | Example |
|-------|------|---------|
| `summary` | `str` | `"A valid plan keeps the published split..."` |
| `required_elements` | `list[str]` | `["published data split", "held-out accuracy evaluation"]` |
| `flexible_elements` | `list[str]` | `["batch size", "learning-rate schedule"]` |
| `target_metric` | `str` | `"held_out_accuracy"` |
| `target_value` | `str` | `"within one point of the reported baseline"` |

## Template Builders

Each returns a raw `dict[str, Any]` with one randomly selected case.

### `build_math_reasoning_template(rng)` — `math_reasoning.py`
- **Domain:** `mathematics`
- **Case A:** Cauchy-Schwarz inequality — structured proof verification
- **Case B:** Jensen's inequality — convexity-based proof
- **Equipment:** Structured proof notebook, Automated proof checker
- **Reagents:** Graduate reviewer, Reference textbook
- **Substitutions:** Graduate reviewer → self-check rubric

### `build_ml_benchmark_template(rng)` — `ml_benchmark.py`
- **Domain:** `machine_learning`
- **Case A:** AG News TinyBERT — text classification replication
- **Case B:** CIFAR-10 ResNet-18 — image classification replication
- **Equipment:** A100 GPU node, Dataset mirror, Experiment tracker
- **Reagents:** Pre-trained checkpoint, Evaluation harness
- **Substitutions:** A100 → V100 (slower), full dataset → stratified sample

### `build_finance_trading_template(rng)` — `finance_trading.py`
- **Domain:** `finance_trading`
- **Case A:** SPY/QQQ mean-reversion — pairs trading backtest
- **Case B:** Momentum futures — trend-following strategy
- **Equipment:** Backtest engine, Historical daily bar dataset
- **Reagents:** Risk reviewer, Compliance packet
- **Substitutions:** Daily bars → weekly bars, risk reviewer → automated risk check
- **Safety restrictions:** offline-only execution policy

## Difficulty Scaling — `apply_difficulty(draft, difficulty, rng)`

| Parameter | Easy | Medium | Hard |
|-----------|------|--------|------|
| `budget_total` | ×1.15 | ×0.95 | ×0.80 |
| `time_limit_days` | unchanged | −1 day | −1 day |
| `staff_count` | unchanged | unchanged | −1 person |
| Resources tightened | 0 | 1 | 2 |
| Conflict constraint | no | yes (1) | yes (1) |

**`_tighten_one_resource`**: picks a random resource, sets `available=False`.
**`_append_conflict_constraint`**: adds a soft constraint noting resource conflict.

## Utility — `replicalab/utils/seed.py`

| Function | Purpose |
|----------|---------|
| `get_deterministic_seed(seed, namespace)` | SHA256-based child seed derivation |
| `seed_rng(seed, namespace)` | Returns `random.Random(derived_seed)` |

## Type Aliases

```python
Difficulty = Literal["easy", "medium", "hard"]
TemplateName = Literal["math_reasoning", "ml_benchmark", "finance_trading"]
TemplateBuilder = Callable[[Any], dict[str, Any]]
```

## Constants

```python
GOLDEN_SCENARIO_SPECS_PATH = Path("tests/fixtures/golden_scenarios.json")
```

## Who Consumes This

- **`validation.py`** — reads constraints, resources, substitutions, hidden_reference_spec
- **`lab_manager_policy.py`** — reads lab_manager_observation, substitutions, constraints
- **`scientist_policy.py`** — reads scenario pack for system prompt generation
- **`server/app.py`** — calls `generate_scenario()` on reset, stores pack for lab manager
- **`scoring/`** (future) — will read hidden_reference_spec for fidelity scoring
