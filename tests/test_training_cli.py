from __future__ import annotations

import json

from replicalab.models import RewardBreakdown
from replicalab.training.cli import main
from replicalab.training.evaluation import PolicyComparisonRow
from replicalab.training.metrics import EvaluationSummary
from replicalab.training.rollout import EpisodeRecord


def test_scientist_preview_cli_writes_plan(tmp_path) -> None:
    exit_code = main(
        [
            "scientist-preview",
            "--persist-root",
            str(tmp_path),
            "--run-name",
            "scientist-preview-test",
            "--seed-count",
            "2",
            "--max-steps",
            "12",
        ]
    )

    assert exit_code == 0
    summary_path = tmp_path / "scientist-preview-test" / "reports" / "summary.json"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["kind"] == "scientist_preview"
    assert payload["dataset_size"] > 0
    assert payload["model_name"] == "Qwen/Qwen3.5-9B"


def test_baseline_eval_cli_writes_summary_and_metrics(tmp_path, monkeypatch) -> None:
    breakdown = RewardBreakdown(
        rigor=0.6,
        feasibility=0.8,
        fidelity=0.7,
        parsimony=0.9,
        efficiency_bonus=0.1,
        communication_bonus=0.0,
        penalties={},
    )
    record = EpisodeRecord(
        seed=101,
        scenario="ml_benchmark",
        difficulty="easy",
        episode_id="episode-1",
        total_reward=4.2,
        reward_breakdown=breakdown,
        verdict="accept",
        agreement_reached=True,
    )
    summary = EvaluationSummary(
        episode_count=1,
        average_reward=4.2,
        average_rounds=1.0,
        agreement_rate=1.0,
        invalid_action_rate=0.0,
        average_invalid_bounded_tool_rate=0.0,
        average_rigor=0.6,
        average_feasibility=0.8,
        average_fidelity=0.7,
        average_parsimony=0.9,
        average_tool_trace_count=0.0,
        average_paper_understanding=0.75,
        average_communication_quality=0.0,
    )

    monkeypatch.setattr(
        "replicalab.training.cli.evaluate_policy",
        lambda **_: ([record], summary),
    )
    monkeypatch.setattr(
        "replicalab.training.cli.plot_evaluation_bars",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "replicalab.training.cli.plot_benchmark_history",
        lambda *args, **kwargs: None,
    )

    exit_code = main(
        [
            "baseline-eval",
            "--persist-root",
            str(tmp_path),
            "--run-name",
            "baseline-eval-test",
            "--eval-seeds",
            "101",
        ]
    )

    assert exit_code == 0
    summary_path = tmp_path / "baseline-eval-test" / "reports" / "summary.json"
    metrics_path = tmp_path / "baseline-eval-test" / "reports" / "metrics.jsonl"
    history_path = tmp_path / "history" / "benchmark_history.jsonl"
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary_payload["average_reward"] == 4.2
    metrics_lines = metrics_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(metrics_lines) == 1
    metric = json.loads(metrics_lines[0])
    assert metric["scenario"] == "ml_benchmark"
    assert metric["agreement_reached"] is True
    assert history_path.exists()


def test_scientist_compare_eval_cli_writes_rows(tmp_path, monkeypatch) -> None:
    baseline_record = EpisodeRecord(
        seed=101,
        scenario="ml_benchmark",
        difficulty="easy",
        episode_id="baseline-1",
        total_reward=1.0,
        reward_breakdown=RewardBreakdown(rigor=0.4, feasibility=0.5, fidelity=0.6),
        verdict="timeout",
        agreement_reached=False,
    )
    trained_record = EpisodeRecord(
        seed=101,
        scenario="ml_benchmark",
        difficulty="easy",
        episode_id="trained-1",
        total_reward=3.5,
        reward_breakdown=RewardBreakdown(rigor=0.8, feasibility=0.9, fidelity=0.85),
        verdict="accept",
        agreement_reached=True,
    )
    rows = [
        PolicyComparisonRow(
            label="baseline",
            episode_count=1,
            average_reward=1.0,
            average_rounds=2.0,
            agreement_rate=0.0,
            invalid_action_rate=0.5,
            average_invalid_bounded_tool_rate=0.0,
            average_rigor=0.4,
            average_feasibility=0.5,
            average_fidelity=0.6,
            average_parsimony=1.0,
            average_tool_trace_count=0.0,
            average_paper_understanding=0.35,
            average_communication_quality=0.0,
        ),
        PolicyComparisonRow(
            label="trained",
            episode_count=1,
            average_reward=3.5,
            average_rounds=1.0,
            agreement_rate=1.0,
            invalid_action_rate=0.0,
            average_invalid_bounded_tool_rate=0.0,
            average_rigor=0.8,
            average_feasibility=0.9,
            average_fidelity=0.85,
            average_parsimony=1.0,
            average_tool_trace_count=0.0,
            average_paper_understanding=0.78,
            average_communication_quality=0.0,
        ),
    ]

    monkeypatch.setattr(
        "replicalab.training.cli.build_remote_scientist_policy",
        lambda **_: (lambda _obs: None),
    )
    monkeypatch.setattr(
        "replicalab.training.cli.compare_policies",
        lambda **_: (
            {"baseline": [baseline_record], "trained": [trained_record]},
            rows,
        ),
    )
    monkeypatch.setattr(
        "replicalab.training.cli.plot_evaluation_bars",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "replicalab.training.cli.plot_benchmark_history",
        lambda *args, **kwargs: None,
    )

    exit_code = main(
        [
            "scientist-compare-eval",
            "--persist-root",
            str(tmp_path),
            "--run-name",
            "compare-eval-test",
            "--eval-seeds",
            "101",
            "--scenarios",
            "ml_benchmark",
            "--difficulties",
            "easy",
        ]
    )

    assert exit_code == 0
    summary_path = tmp_path / "compare-eval-test" / "reports" / "summary.json"
    history_path = tmp_path / "history" / "benchmark_history.jsonl"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert [row["label"] for row in payload["rows"]] == ["baseline", "trained"]
    assert payload["rows"][1]["average_reward"] == 3.5
    assert history_path.exists()


def test_scientist_local_compare_eval_cli_writes_cases_and_metrics(tmp_path, monkeypatch) -> None:
    baseline_record = EpisodeRecord(
        seed=0,
        scenario="ml_benchmark",
        difficulty="easy",
        episode_id="baseline-1",
        total_reward=1.0,
        reward_breakdown=RewardBreakdown(rigor=0.3, feasibility=0.4, fidelity=0.5),
        verdict="timeout",
        agreement_reached=False,
    )
    trained_record = EpisodeRecord(
        seed=0,
        scenario="ml_benchmark",
        difficulty="easy",
        episode_id="trained-1",
        total_reward=2.5,
        reward_breakdown=RewardBreakdown(rigor=0.7, feasibility=0.8, fidelity=0.75),
        verdict="accept",
        agreement_reached=True,
    )
    rows = [
        PolicyComparisonRow(
            label="baseline",
            episode_count=1,
            average_reward=1.0,
            average_rounds=2.0,
            agreement_rate=0.0,
            invalid_action_rate=0.0,
            average_invalid_bounded_tool_rate=0.0,
            average_rigor=0.3,
            average_feasibility=0.4,
            average_fidelity=0.5,
            average_parsimony=1.0,
            average_tool_trace_count=0.0,
            average_paper_understanding=0.2,
            average_communication_quality=0.0,
        ),
        PolicyComparisonRow(
            label="trained",
            episode_count=1,
            average_reward=2.5,
            average_rounds=1.0,
            agreement_rate=1.0,
            invalid_action_rate=0.0,
            average_invalid_bounded_tool_rate=0.0,
            average_rigor=0.7,
            average_feasibility=0.8,
            average_fidelity=0.75,
            average_parsimony=1.0,
            average_tool_trace_count=0.0,
            average_paper_understanding=0.6,
            average_communication_quality=0.0,
        ),
    ]

    class _CaseSpec:
        case_index = 7
        expected_evidence_id = "ml:paper-1"
        expected_paper_title = "Paper 1"

        def to_evaluation_case(self) -> object:
            return object()

        def model_dump(self, mode: str = "json") -> dict[str, object]:
            return {
                "case_index": 7,
                "seed": 0,
                "scenario": "ml_benchmark",
                "difficulty": "easy",
                "expected_evidence_id": "ml:paper-1",
                "expected_paper_title": "Paper 1",
            }

    monkeypatch.setattr(
        "replicalab.training.cli.build_trainable_paper_cases",
        lambda *args, **kwargs: [_CaseSpec()],
    )
    monkeypatch.setattr(
        "replicalab.training.cli.build_local_scientist_policy",
        lambda **_: (lambda _obs: None),
    )
    monkeypatch.setattr(
        "replicalab.training.cli.compare_policies",
        lambda **_: (
            {"baseline": [baseline_record], "trained": [trained_record]},
            rows,
        ),
    )
    monkeypatch.setattr(
        "replicalab.training.cli.plot_evaluation_bars",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "replicalab.training.cli.plot_benchmark_history",
        lambda *args, **kwargs: None,
    )

    exit_code = main(
        [
            "scientist-local-compare-eval",
            "--persist-root",
            str(tmp_path),
            "--run-name",
            "local-compare-test",
            "--adapter-dir",
            str(tmp_path / "adapter"),
            "--case-count",
            "1",
            "--case-offset",
            "7",
        ]
    )

    assert exit_code == 0
    summary_path = tmp_path / "local-compare-test" / "reports" / "summary.json"
    metrics_path = tmp_path / "local-compare-test" / "reports" / "metrics.jsonl"
    cases_path = tmp_path / "local-compare-test" / "manifests" / "evaluation_cases.json"
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["case_count"] == 1
    assert payload["unique_expected_papers"] == 1
    metrics_lines = metrics_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(metrics_lines) == 2
    first_metric = json.loads(metrics_lines[0])
    assert first_metric["case_index"] == 7
    assert first_metric["expected_evidence_id"] == "ml:paper-1"
    assert cases_path.exists()
