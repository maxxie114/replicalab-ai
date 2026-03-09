"""Judge scoring engine — deterministic protocol evaluation."""

from .communication import score_communication
from .explain import explain_reward
from .feasibility import score_feasibility
from .fidelity import score_fidelity
from .llm_judge import build_llm_reward_breakdown
from .rigor import score_rigor
from .rubric import build_reward_breakdown, compute_total_reward
from .understanding import score_paper_understanding

__all__ = [
    "build_llm_reward_breakdown",
    "build_reward_breakdown",
    "compute_total_reward",
    "explain_reward",
    "score_communication",
    "score_feasibility",
    "score_fidelity",
    "score_paper_understanding",
    "score_rigor",
]
