# Future Improvements

Source of truth: `ReplicaLab_Comprehensive_Task_Division.md`

This document tracks post-MVP architectural improvements. Work here begins
only after the core logic is complete and the hackathon deliverables are
stable.

---

## 1. Domain-Agnostic Normalized Scenario Layer

### Priority: highest future feature

### Problem

The current models in `replicalab/models.py` use domain-biased field names:

- `paper_title`, `paper_hypothesis`, `paper_method`, `paper_key_finding`
- `equipment_available`, `reagents_in_stock`, `staff_count`
- `sample_size`, `controls`, `technique`

These work for the three MVP scenario families (cell biology, ML benchmark,
behavioral psychology) because all three map onto a lab-style replication
frame. But if the environment needs to support domains outside scientific
replication (e.g., engineering design, clinical trial planning, supply chain
optimization), the field names stop making sense.

The turn protocol itself (`propose`, `revise`, `request_info`, `accept`) is
already generic. The gap is in the observation and protocol content layer.

### Solution: normalized scenario representation

Introduce a structured internal representation that any domain adapter can
emit:

```python
class NormalizedScenarioPack(BaseModel):
    domain_id: str                          # "cell_biology", "ml_benchmark", etc.
    task_summary: str                       # what the agent is trying to achieve
    success_criteria: list[str]             # measurable conditions for success
    constraints: list[Constraint]           # budget, time, equipment, policy, etc.
    resources: list[Resource]               # what is available to work with
    allowed_substitutions: list[Substitution]  # valid swaps the agent can propose
    hidden_reference_spec: dict             # ground truth the judge scores against
    difficulty: str                         # "easy", "medium", "hard"
    metadata: dict                          # domain-specific extras
```

Where:

```python
class Constraint(BaseModel):
    dimension: str          # "budget", "time", "equipment", "personnel", "safety"
    label: str              # human-readable name
    value: Any              # the constraint value (numeric, list, etc.)
    hard: bool = True       # hard constraint vs soft preference

class Resource(BaseModel):
    category: str           # "equipment", "reagent", "compute", "personnel"
    name: str               # resource identifier
    available: bool         # currently available
    quantity: Optional[int] # count if applicable
    notes: str = ""         # booking conflicts, expiry, etc.

class Substitution(BaseModel):
    original: str           # what the reference spec uses
    replacement: str        # what the agent can use instead
    quality_impact: float   # 0.0 to 1.0, how much fidelity is lost
    cost_delta: float       # cost difference
```

### Architecture principle

```
Domain template
    -> Scenario adapter (thin mapper, <50 lines per domain)
        -> NormalizedScenarioPack
            -> Observation mapper (fills ScientistObservation / LabManagerObservation)
            -> Prompt assembler (data-driven, not hard-coded)
            -> Validator (checks action against constraints)
            -> Scorer (compares final protocol against hidden_reference_spec)
```

The external contract (`ScientistAction`, `LabManagerAction`,
`ScientistObservation`, `LabManagerObservation`, `StepResult`) stays
unchanged. The normalization lives below those models as an internal
implementation layer.

LLMs reason and negotiate. They never own truth. Truth lives in the
normalized scenario pack and the deterministic scorer.

### How this affects the future core logic

| Current component | Impact | Severity |
|---|---|---|
| `replicalab/models.py` | External contract unchanged. Add `NormalizedScenarioPack` and helper models as new classes | Low |
| `replicalab/scenarios/templates.py` (SCN 02) | Must define the normalized schema. `generate_scenario()` returns a pack instead of raw dicts | High |
| `replicalab/scenarios/*.py` (SCN 03-05) | Each domain file becomes a thin scenario adapter that emits a normalized pack | Medium |
| `replicalab/scenarios/templates.py` (SCN 06) | Difficulty scaling becomes mechanical: add/remove constraints, tighten resource limits | Medium, but simpler |
| `replicalab/scenarios/templates.py` (SCN 07) | Constraint generator emits `Constraint` objects instead of ad hoc lab fields | High |
| `replicalab/scenarios/templates.py` (SCN 08) | `hidden_reference_spec` is part of the pack, not a separate hidden structure | Medium |
| `replicalab/utils/validation.py` (MOD 05-06) | Validators read `constraints[]` and `resources[]` from the pack instead of checking lab-specific fields | High |
| `replicalab/scoring/*.py` (JDG 01-04) | Scorers compare the final protocol against `hidden_reference_spec` on normalized dimensions | High |
| `replicalab/env/replicalab_env.py` (ENV 01-07) | `EpisodeState` gains a `scenario_pack` field. Reset populates it from the adapter | Medium |
| `replicalab/agents/scientist_policy.py` (AGT 01-02) | Prompts assembled from scenario pack data, not hard-coded domain text | Medium |
| `replicalab/agents/lab_manager_policy.py` (AGT 05-07) | Feasibility checker reads normalized constraints instead of lab-specific fields | Medium |
| `frontend/` (UI 01+) | Render "constraint cards" and "resource cards" instead of lab-specific panels | Low (future) |

### What stays the same

- The turn protocol (`propose`, `revise`, `request_info`, `accept`)
- The reward formula (`10 * rigor * feasibility * fidelity + bonuses - penalties`)
- The external API contract (REST + WebSocket payloads)
- The training loop and RL pipeline
- The deterministic reward principle

---

## 2. Planned work items for the normalized scenario layer

### Item 1: Define the normalized scenario schema

**What:** Add `NormalizedScenarioPack`, `Constraint`, `Resource`, and
`Substitution` as Pydantic models in a new file
`replicalab/scenarios/schema.py`.

**Why:** This is the foundation. Every other item depends on having a stable
schema that all adapters, validators, and scorers agree on.

**Depends on:** Core MVP scenario work (SCN 02-09) being complete so we know
what fields the adapters actually need.

**Scope:** ~80 lines of model definitions, no business logic.

---

### Item 2: Convert existing scenario templates into adapters

**What:** Refactor `cell_biology.py`, `ml_benchmark.py`, and
`behavioral_psych.py` so each one returns a `NormalizedScenarioPack` instead
of raw domain-specific dicts.

**Why:** Proves the schema works for all three MVP domains. If a field cannot
be cleanly mapped, the schema needs revision before adding new domains.

**Depends on:** Item 1 (schema exists), SCN 03-05 (domain templates exist).

**Scope:** ~50 lines per adapter. Should be thin mappers. If an adapter
exceeds 50 lines, the schema is wrong.

**Constraint:** The existing observation fields (`paper_title`,
`equipment_available`, etc.) must still be populated. The adapter fills
both the normalized pack and the legacy observation slots until the
observation models are generalized.

---

### Item 3: Build data-driven prompt assembly

**What:** Replace hard-coded prompt text with a template that assembles from
the scenario pack:

```
You are a {role} working on: {task_summary}

Success criteria:
{success_criteria[]}

You must work within these constraints:
{constraints[].label}: {constraints[].value}

Available resources:
{resources[].name} ({resources[].category}): {available/unavailable}
```

**Why:** Makes AGT 01 (Scientist prompt) and AGT 07 (Lab Manager templates)
domain-neutral. Adding a new domain requires only a new adapter, not new
prompts.

**Depends on:** Item 2 (adapters produce normalized packs), AGT 01 and
AGT 07 existing in their MVP form.

**Scope:** One prompt template function per role. ~40 lines each.

---

### Item 4: Hybrid LLM Lab Manager with deterministic post-checking

**What:** Replace the rule-based Lab Manager with a hybrid architecture:

1. LLM receives the `LabManagerObservation` and generates negotiation text
   plus alternative suggestions in natural language
2. Deterministic constraint checker computes the real feasibility flags by
   reading the normalized scenario pack's `constraints[]` and `resources[]`
3. A composer merges the LLM output with the checker output into a valid
   `LabManagerAction`
4. The `model_validator` on `LabManagerAction` catches any inconsistency

**Why:** Gives the Lab Manager realistic negotiation language and creative
suggestions (the LLM's strength) while keeping feasibility flags truthful
(the checker's strength). Training reward stays deterministic because the
reward engine only reads the validated action, not the LLM's raw text.

**Depends on:** Item 2 (checker needs normalized constraints), AGT 05
(feasibility checker exists), MOD 02 (LabManagerAction validators exist).

**Scope:** ~120 lines. The LLM call, the checker, the composer. Uses the
same base model as the Scientist (Qwen3-4B) with a separate role adapter.

**Risk:** Episode variance increases because the same seed may produce
different negotiation paths. Mitigate by keeping the deterministic checker as
the authority on all boolean flags. The LLM only controls `explanation` text
and suggestion ideas, never the truth flags.

---

### Item 5: Normalized scoring against hidden reference spec

**What:** Refactor the scoring engine so `score_rigor()`,
`score_feasibility()`, and `score_fidelity()` compare the final protocol
against `hidden_reference_spec` from the normalized scenario pack instead of
using domain-specific scoring logic.

Scoring dimensions become:

- **Rigor:** Does the protocol preserve the success criteria? Compare
  `protocol.controls` against `hidden_reference_spec.required_controls`,
  check sample size ratio, verify statistical validity markers.
- **Feasibility:** Does the protocol satisfy all hard constraints? Walk
  `constraints[]` and check each one against the protocol.
- **Fidelity:** How close is the protocol to the reference spec? Compare
  technique, duration, equipment, reagents against
  `hidden_reference_spec` and compute a similarity score using
  `allowed_substitutions[]` quality impact.

**Why:** Makes scoring work for any domain without per-domain scorer code.
The domain-specific knowledge lives in the scenario adapter (which defines
what the reference spec and constraints are), not in the scoring engine.

**Depends on:** Item 1 (schema with `hidden_reference_spec`), Item 2
(adapters populate it), JDG 01-04 (MVP scorers exist to refactor from).

**Scope:** Refactor of existing scorer files. ~150 lines total across
`rigor.py`, `feasibility.py`, `fidelity.py`.

---

### Item 6: Lab Manager orchestrator with specialist subagents

**What:** Decompose the hybrid Lab Manager into a coordinator that delegates
to specialist subagents:

| Subagent | Responsibility |
|---|---|
| Budget agent | Checks cost against remaining budget |
| Scheduling agent | Checks timeline and booking conflicts |
| Equipment agent | Checks equipment availability and substitutions |
| Safety agent | Checks policy and compliance constraints |
| Coordinator | Aggregates subagent outputs into one `LabManagerAction` |

Externally, the contract is unchanged: one `LabManagerAction` per turn. The
orchestration is internal.

**Why:** Stronger multi-agent story for the hackathon track alignment.
Demonstrates that the Lab Manager is not a monolithic policy but a team of
constraint specialists. Each subagent can be individually tested, improved,
or replaced.

**Depends on:** Item 4 (hybrid Lab Manager works first), Item 2 (normalized
constraints are available for each subagent to read).

**Scope:** Orchestration layer ~200 lines. Each subagent ~40 lines. Total
~400 lines.

**Risk:** Adds latency (multiple LLM calls or multiple checker passes per
turn), orchestration failure handling, and logging complexity. Only pursue
after the single hybrid Lab Manager is stable and training is producing
results.

**Phasing:** This is the lowest priority item. Build it only if the MVP is
complete, training shows improvement, and there is time remaining before
submission.

---

## 3. Recommended order

| Order | Item | Gate |
|---|---|---|
| 1 | Define normalized scenario schema | After SCN 02-09 complete |
| 2 | Convert templates to adapters | After Item 1 |
| 3 | Data-driven prompt assembly | After Item 2 + AGT 01/07 |
| 4 | Hybrid LLM Lab Manager | After Item 2 + AGT 05 |
| 5 | Normalized scoring | After Item 2 + JDG 01-04 |
| 6 | Lab Manager orchestrator with subagents | After Item 4 stable |

---

## 4. Key principle

The external contract stays stable. Internal policy can evolve. LLMs reason
and negotiate. They never own truth. Truth lives in the normalized scenario
pack and the deterministic scorer.
