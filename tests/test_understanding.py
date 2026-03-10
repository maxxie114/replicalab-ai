from __future__ import annotations

from replicalab.models import ScientistAction, ScientistObservation
from replicalab.scoring import score_paper_understanding


def _observation() -> ScientistObservation:
    return ScientistObservation(
        paper_title="ResNet augmentation study",
        paper_hypothesis="Data augmentation improves CIFAR-10 classification accuracy.",
        paper_method="Train a ResNet model on CIFAR-10 with and without augmentation.",
        paper_key_finding="The augmented run improves top-1 accuracy over the baseline.",
        experiment_goal="Replicate the augmentation-driven accuracy gain on CIFAR-10.",
        conversation_history=[],
        current_protocol=None,
        round_number=0,
        max_rounds=6,
    )


def test_grounded_protocol_scores_higher_than_generic_protocol() -> None:
    observation = _observation()
    grounded = ScientistAction(
        action_type="propose_protocol",
        sample_size=8,
        controls=["no_augmentation_baseline"],
        technique="ResNet replication on CIFAR-10 with augmentation ablation",
        duration_days=2,
        required_equipment=["gpu_h100"],
        required_reagents=[],
        questions=[],
        rationale=(
            "Train the CIFAR-10 ResNet baseline and the augmented variant to test "
            "whether augmentation improves top-1 accuracy."
        ),
    )
    generic = ScientistAction(
        action_type="propose_protocol",
        sample_size=8,
        controls=["baseline"],
        technique="general benchmark workflow",
        duration_days=2,
        required_equipment=["gpu_h100"],
        required_reagents=[],
        questions=[],
        rationale="Run a generic experiment and compare the outputs.",
    )

    assert score_paper_understanding(observation, grounded) > score_paper_understanding(
        observation, generic
    )


def test_relevant_blocking_question_scores_above_irrelevant_question() -> None:
    observation = _observation()
    relevant = ScientistAction(
        action_type="request_info",
        sample_size=0,
        controls=[],
        technique="",
        duration_days=0,
        required_equipment=[],
        required_reagents=[],
        questions=["Which CIFAR-10 augmentation setting was used in the paper?"],
        rationale="",
    )
    irrelevant = ScientistAction(
        action_type="request_info",
        sample_size=0,
        controls=[],
        technique="",
        duration_days=0,
        required_equipment=[],
        required_reagents=[],
        questions=["What is the office Wi-Fi password?"],
        rationale="",
    )

    assert score_paper_understanding(observation, relevant) > score_paper_understanding(
        observation, irrelevant
    )


def test_score_is_bounded() -> None:
    score = score_paper_understanding(
        _observation(),
        ScientistAction(
            action_type="propose_protocol",
            sample_size=4,
            controls=["baseline"],
            technique="ResNet augmentation replication",
            duration_days=1,
            required_equipment=["gpu_h100"],
            required_reagents=[],
            questions=[],
            rationale="Replicate the CIFAR-10 augmentation finding.",
        ),
    )

    assert 0.0 <= score <= 1.0
