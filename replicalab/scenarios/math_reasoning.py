"""Mathematics scenario templates."""

from __future__ import annotations

import random
from typing import Any

from replicalab.config import MAX_ROUNDS


def build_math_reasoning_template(rng: random.Random) -> dict[str, Any]:
    cases = [
        {
            "domain_id": "mathematics",
            "paper_title": "Planning a proof of the Cauchy-Schwarz inequality",
            "paper_hypothesis": "A square-expansion argument gives the cleanest proof path.",
            "paper_method": "Outline the proof using one algebraic identity, one equality-case check, and reviewer notes.",
            "paper_key_finding": "The proof is accepted only if every inequality step and equality case is justified.",
            "task_summary": "Produce a proof-planning workflow for the Cauchy-Schwarz inequality for an undergraduate seminar handout.",
            "success_criteria": [
                "Every inequality step is justified in plain language.",
                "The equality case is checked explicitly.",
                "The final plan fits within the review and deadline constraints.",
            ],
            "reference_summary": "A valid plan uses a square-expansion route, checks equality, and includes one verification pass.",
            "required_elements": [
                "explicit target inequality",
                "square-expansion or inner-product setup",
                "equality-case check",
                "final verification pass",
            ],
            "flexible_elements": [
                "notation style",
                "ordering of supporting lemmas",
                "proof-sketch granularity",
            ],
            "target_metric": "proof_validity",
            "target_value": "all required justification steps are present",
            "constraints": [
                {
                    "key": "deadline_days",
                    "label": "Proof planning deadline",
                    "quantity": 3,
                    "unit": "days",
                    "comparator": "<=",
                    "hard": True,
                    "details": "The seminar notes must be ready within three days.",
                },
                {
                    "key": "review_passes",
                    "label": "Required review passes",
                    "quantity": 1,
                    "unit": "pass",
                    "comparator": ">=",
                    "hard": True,
                    "details": "At least one verification pass is required before acceptance.",
                },
                {
                    "key": "max_pages",
                    "label": "Maximum proof outline length",
                    "quantity": 2,
                    "unit": "pages",
                    "comparator": "<=",
                    "hard": False,
                    "details": "The outline should stay concise enough for seminar notes.",
                },
            ],
            "resources": [
                {
                    "key": "proof_notebook",
                    "label": "Structured proof notebook",
                    "quantity": 1,
                    "unit": "workspace",
                    "available": True,
                    "category": "tool",
                    "details": "A shared note workspace for the outline and checks.",
                },
                {
                    "key": "theorem_library",
                    "label": "Reference theorem library",
                    "quantity": 1,
                    "unit": "library",
                    "available": True,
                    "category": "reference",
                    "details": "Contains previous inequality proofs and notation conventions.",
                },
                {
                    "key": "reviewer",
                    "label": "Graduate reviewer",
                    "quantity": 1,
                    "unit": "reviewer",
                    "available": True,
                    "category": "personnel",
                    "details": "A reviewer can check one draft before the deadline.",
                },
            ],
            "allowed_substitutions": [
                {
                    "original": "graduate reviewer",
                    "alternative": "self-check rubric",
                    "condition": "Use only if the reviewer is unavailable.",
                    "tradeoff": "Requires a stricter written checklist inside the plan.",
                },
                {
                    "original": "full derivation",
                    "alternative": "proof sketch with explicit checkpoints",
                    "condition": "Use when page budget is tight.",
                    "tradeoff": "The plan must still spell out all justification steps.",
                },
            ],
            "budget_total": 300.0,
            "staff_count": 1,
            "time_limit_days": 3,
            "max_rounds": MAX_ROUNDS,
        },
        {
            "domain_id": "mathematics",
            "paper_title": "Planning a proof of Jensen's inequality for convex quadratics",
            "paper_hypothesis": "A convexity-first outline is shorter than an expectation-expansion route.",
            "paper_method": "Use the convexity definition, midpoint intuition, and one numerical sanity check.",
            "paper_key_finding": "The plan succeeds only if the convexity assumption and averaging step are both explicit.",
            "task_summary": "Produce a proof-planning workflow for Jensen's inequality on convex quadratics for a revision session.",
            "success_criteria": [
                "The convexity assumption is named before the main argument.",
                "Averaging and expectation steps are justified.",
                "The plan includes at least one sanity check example.",
            ],
            "reference_summary": "A valid plan states convexity early, justifies averaging, and uses one sanity check.",
            "required_elements": [
                "convexity assumption",
                "averaging step",
                "sanity check example",
                "closing statement tied to the task objective",
            ],
            "flexible_elements": [
                "example choice",
                "notation style",
                "proof sketch ordering",
            ],
            "target_metric": "proof_validity",
            "target_value": "convexity and averaging are justified with one sanity check",
            "constraints": [
                {
                    "key": "deadline_days",
                    "label": "Proof planning deadline",
                    "quantity": 2,
                    "unit": "days",
                    "comparator": "<=",
                    "hard": True,
                    "details": "The revision notes are due within two days.",
                },
                {
                    "key": "review_passes",
                    "label": "Required review passes",
                    "quantity": 1,
                    "unit": "pass",
                    "comparator": ">=",
                    "hard": True,
                    "details": "The plan needs at least one self-check or peer review.",
                },
                {
                    "key": "max_pages",
                    "label": "Maximum proof outline length",
                    "quantity": 1,
                    "unit": "page",
                    "comparator": "<=",
                    "hard": False,
                    "details": "The final outline should fit on one page.",
                },
            ],
            "resources": [
                {
                    "key": "whiteboard",
                    "label": "Whiteboard workspace",
                    "quantity": 1,
                    "unit": "workspace",
                    "available": True,
                    "category": "tool",
                    "details": "Used to sketch the proof structure and sanity check.",
                },
                {
                    "key": "reference_notes",
                    "label": "Reference lecture notes",
                    "quantity": 1,
                    "unit": "packet",
                    "available": True,
                    "category": "reference",
                    "details": "Contains the convexity definition and worked examples.",
                },
                {
                    "key": "peer_reviewer",
                    "label": "Peer reviewer",
                    "quantity": 1,
                    "unit": "reviewer",
                    "available": True,
                    "category": "personnel",
                    "details": "Available for one short review pass.",
                },
            ],
            "allowed_substitutions": [
                {
                    "original": "peer reviewer",
                    "alternative": "checklist-driven self-review",
                    "condition": "Use if the peer reviewer is unavailable.",
                    "tradeoff": "The final plan must include explicit verification checkpoints.",
                }
            ],
            "budget_total": 220.0,
            "staff_count": 1,
            "time_limit_days": 2,
            "max_rounds": MAX_ROUNDS,
        },
    ]
    return rng.choice(cases)
