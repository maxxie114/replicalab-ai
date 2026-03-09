# Training Goals

## Immediate Goal

Improve the two trainable role models without destabilizing the deterministic
reward loop.

The current near-term training target is not "make the models sound better."
It is:

1. stronger paper understanding
2. stronger constraint grounding
3. cleaner Scientist-Lab Manager communication
4. fewer invalid or hallucinated actions
5. more reliable agreement on feasible plans

## Role Definitions

### Scientist

The Scientist should:

1. understand the paper hypothesis, method, key finding, and experiment goal
2. propose or revise protocols that stay grounded in the visible brief
3. ask blocking questions only when needed
4. avoid hallucinating tools, resources, or hidden facts
5. converge toward a feasible plan under lab constraints

### Lab Manager / Lab Research Assistant

The Lab Manager should:

1. enforce budget, time, staffing, equipment, and reagent constraints
2. explain feasibility failures clearly
3. suggest grounded revisions rather than generic rejections
4. keep the collaboration moving toward an executable plan

### Judge

The deterministic judge remains the reward source.

Optional large-model judges may be used only for:

1. audit text
2. post-run error analysis
3. qualitative review of failure patterns

They must not replace the deterministic rubric as the training reward.

## Core Metrics To Track Every Run

1. average reward
2. agreement rate
3. invalid action rate
4. rigor
5. feasibility
6. fidelity
7. paper understanding
8. communication quality

## Data Expansion Direction

The Scientist dataset should keep growing along three prompt goals:

1. `paper_understanding`
2. `constraint_grounding`
3. `negotiation_quality`

This expands coverage without changing the outer environment contract.

## Current Model Mapping

1. Scientist: `Qwen/Qwen3.5-9B`
2. Lab Manager: `Qwen/Qwen3.5-9B`
3. Fallback: `Qwen/Qwen3.5-4B`
4. Audit-only judge candidate: `Qwen/Qwen3.5-122B-A10B`

## Architecture Note: Execution Environment

The current environment mainly judges collaborative planning quality.

The proposed next phase is larger:

1. the Lab Manager allocates and configures experimental resources
2. the Scientist performs bounded experimental steps inside the environment
3. the judge scores not only negotiation quality but experimental execution
   quality and error recovery
4. paper replication is judged by reproducing the logic and outcome of the
   experiment, not by line-by-line paraphrase of the source paper

This is an environment redesign and should be implemented as a separate phase,
not mixed into training-metric changes silently.

## Guardrails

1. no hallucinated resources, tools, measurements, or outcomes
2. no hidden ground-truth leakage into model prompts
3. no live-web reward dependence
4. deterministic reward remains the training source of truth
5. before/after graphs must stay comparable across runs
