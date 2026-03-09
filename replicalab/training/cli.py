"""Northflank- and notebook-friendly training entrypoints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from replicalab.agents import build_baseline_scientist_action, build_remote_scientist_policy
from replicalab.training.artifacts import (
    ArtifactLayout,
    append_jsonl,
    build_run_name,
    write_json,
)
from replicalab.training.art_openenv import (
    ArtOpenEnvConfig,
    ArtScenarioSpec,
    run_art_openenv_training,
)
from replicalab.training.evaluation import (
    build_default_evaluation_cases,
    compare_policies,
    evaluate_policy,
)
from replicalab.training.history import (
    append_benchmark_history,
    build_benchmark_history_row,
    load_benchmark_history,
)
from replicalab.training.lab_manager_sft import (
    LabManagerSFTConfig,
    preview_lab_manager_training,
    train_lab_manager_sft,
)
from replicalab.training.metrics import episode_to_metrics
from replicalab.training.plots import (
    plot_benchmark_history,
    plot_evaluation_bars,
    plot_metrics_by_step,
    plot_training_history,
)
from replicalab.training.scientist_grpo import (
    ScientistGRPOConfig,
    preview_scientist_training,
    train_scientist_grpo,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the training CLI for local, Colab, or Northflank jobs."""

    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "scientist-preview":
        return _run_scientist_preview(args)
    if args.command == "scientist-train":
        return _run_scientist_train(args)
    if args.command == "lab-manager-preview":
        return _run_lab_manager_preview(args)
    if args.command == "lab-manager-train":
        return _run_lab_manager_train(args)
    if args.command == "baseline-eval":
        return _run_baseline_eval(args)
    if args.command == "scientist-compare-eval":
        return _run_scientist_compare_eval(args)
    if args.command == "art-scientist-train":
        return _run_art_scientist_train(args)

    parser.error(f"Unsupported command: {args.command}")
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ReplicaLab training entrypoints for notebook and Northflank runs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scientist_defaults = ScientistGRPOConfig()
    scientist_preview = subparsers.add_parser(
        "scientist-preview",
        help="Preview the Scientist GRPO dataset and artifact layout.",
    )
    _add_common_artifact_args(scientist_preview, prefix="scientist")
    _add_common_training_args(
        scientist_preview,
        model_name=scientist_defaults.model_name,
        templates=scientist_defaults.templates,
        difficulties=scientist_defaults.difficulties,
        seed_count=len(scientist_defaults.train_seeds),
    )
    scientist_preview.add_argument(
        "--max-steps",
        type=int,
        default=scientist_defaults.max_steps,
        help="Maximum GRPO training steps for the preview metadata.",
    )

    scientist_train = subparsers.add_parser(
        "scientist-train",
        help="Run the Scientist GRPO job.",
    )
    _add_common_artifact_args(scientist_train, prefix="scientist")
    _add_common_training_args(
        scientist_train,
        model_name=scientist_defaults.model_name,
        templates=scientist_defaults.templates,
        difficulties=scientist_defaults.difficulties,
        seed_count=len(scientist_defaults.train_seeds),
    )
    scientist_train.add_argument(
        "--max-steps",
        type=int,
        default=scientist_defaults.max_steps,
        help="Maximum GRPO training steps.",
    )
    scientist_train.add_argument(
        "--dry-run",
        action="store_true",
        help="Persist manifests and config without invoking TRL.",
    )

    lab_defaults = LabManagerSFTConfig()
    lab_preview = subparsers.add_parser(
        "lab-manager-preview",
        help="Preview the Lab Manager SFT dataset and artifact layout.",
    )
    _add_common_artifact_args(lab_preview, prefix="lab-manager")
    _add_common_training_args(
        lab_preview,
        model_name=lab_defaults.model_name,
        templates=lab_defaults.templates,
        difficulties=lab_defaults.difficulties,
        seed_count=len(lab_defaults.train_seeds),
    )

    lab_train = subparsers.add_parser(
        "lab-manager-train",
        help="Run the Lab Manager SFT job.",
    )
    _add_common_artifact_args(lab_train, prefix="lab-manager")
    _add_common_training_args(
        lab_train,
        model_name=lab_defaults.model_name,
        templates=lab_defaults.templates,
        difficulties=lab_defaults.difficulties,
        seed_count=len(lab_defaults.train_seeds),
    )
    lab_train.add_argument(
        "--dry-run",
        action="store_true",
        help="Persist manifests and config without invoking TRL.",
    )

    baseline_eval = subparsers.add_parser(
        "baseline-eval",
        help="Run deterministic baseline evaluation against a live ReplicaLab server.",
    )
    _add_common_artifact_args(baseline_eval, prefix="eval-baseline")
    baseline_eval.add_argument(
        "--base-url",
        default="https://ayushozha-replicalab.hf.space",
        help="ReplicaLab environment base URL.",
    )
    baseline_eval.add_argument(
        "--transport",
        default="rest",
        choices=("rest", "ws"),
        help="Transport used by ReplicaLabClient.",
    )
    baseline_eval.add_argument(
        "--eval-seeds",
        nargs="+",
        type=int,
        default=[101, 102],
        help="Evaluation seeds.",
    )
    baseline_eval.add_argument(
        "--scenarios",
        nargs="+",
        default=list(scientist_defaults.templates),
        help="Scenario families to evaluate.",
    )
    baseline_eval.add_argument(
        "--difficulties",
        nargs="+",
        default=list(scientist_defaults.difficulties),
        help="Difficulty levels to evaluate.",
    )

    compare_eval = subparsers.add_parser(
        "scientist-compare-eval",
        help="Compare baseline Scientist versus a trained ART Scientist checkpoint.",
    )
    _add_common_artifact_args(compare_eval, prefix="eval-compare")
    compare_eval.add_argument(
        "--base-url",
        default="https://ayushozha-replicalab.hf.space",
        help="ReplicaLab environment base URL.",
    )
    compare_eval.add_argument(
        "--transport",
        default="rest",
        choices=("rest", "ws"),
        help="Transport used by ReplicaLabClient.",
    )
    compare_eval.add_argument(
        "--eval-seeds",
        nargs="+",
        type=int,
        default=[101, 102],
        help="Evaluation seeds.",
    )
    compare_eval.add_argument(
        "--scenarios",
        nargs="+",
        default=list(scientist_defaults.templates),
        help="Scenario families to evaluate.",
    )
    compare_eval.add_argument(
        "--difficulties",
        nargs="+",
        default=list(scientist_defaults.difficulties),
        help="Difficulty levels to evaluate.",
    )
    compare_eval.add_argument(
        "--project",
        default="replicalab-ai",
        help="ART project name for the trained Scientist checkpoint.",
    )
    compare_eval.add_argument(
        "--model-name",
        default="replicalab-scientist-art-live",
        help="ART trainable model name for the trained Scientist checkpoint.",
    )
    compare_eval.add_argument(
        "--base-model",
        default="OpenPipe/Qwen3-14B-Instruct",
        help="Base model used for the ART trained Scientist.",
    )
    compare_eval.add_argument(
        "--checkpoint-step",
        type=int,
        default=None,
        help="Optional explicit ART checkpoint step to evaluate.",
    )
    compare_eval.add_argument(
        "--max-completion-tokens",
        type=int,
        default=450,
        help="Max completion tokens for the trained remote Scientist.",
    )
    compare_eval.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature for the trained remote Scientist.",
    )

    art_train = subparsers.add_parser(
        "art-scientist-train",
        help="Run ART serverless RL training against the ReplicaLab OpenEnv deployment.",
    )
    _add_common_artifact_args(art_train, prefix="art-scientist")
    art_train.add_argument(
        "--project",
        default="replicalab-art-openenv",
        help="Weights & Biases / ART project name.",
    )
    art_train.add_argument(
        "--model-name",
        default="replicalab-scientist-art",
        help="ART trainable model name.",
    )
    art_train.add_argument(
        "--base-model",
        default="OpenPipe/Qwen3-14B-Instruct",
        help="ART serverless base model.",
    )
    art_train.add_argument(
        "--base-url",
        default="https://ayushozha-replicalab.hf.space",
        help="ReplicaLab environment base URL.",
    )
    art_train.add_argument(
        "--transport",
        default="rest",
        choices=("rest",),
        help="Transport used for live environment interaction.",
    )
    art_train.add_argument(
        "--train-steps",
        type=int,
        default=1,
        help="Number of ART training updates to run.",
    )
    art_train.add_argument(
        "--rollouts-per-group",
        type=int,
        default=2,
        help="Number of sampled rollouts for each scenario group.",
    )
    art_train.add_argument(
        "--max-turns",
        type=int,
        default=6,
        help="Max environment turns per rollout.",
    )
    art_train.add_argument(
        "--max-completion-tokens",
        type=int,
        default=700,
        help="Assistant max completion tokens per turn.",
    )
    art_train.add_argument(
        "--max-parse-retries",
        type=int,
        default=2,
        help="Number of parser-driven correction retries per turn.",
    )
    art_train.add_argument(
        "--learning-rate",
        type=float,
        default=5e-6,
        help="ART learning rate.",
    )
    art_train.add_argument(
        "--beta",
        type=float,
        default=0.0,
        help="ART KL penalty coefficient.",
    )
    art_train.add_argument(
        "--scenario-spec",
        nargs="+",
        default=[
            "0:ml_benchmark:easy",
            "1:ml_benchmark:medium",
            "0:finance_trading:easy",
        ],
        help="Scenario specs in the form seed:scenario:difficulty.",
    )

    return parser


def _add_common_artifact_args(parser: argparse.ArgumentParser, *, prefix: str) -> None:
    parser.add_argument(
        "--persist-root",
        default=None,
        help="Override REPLICALAB_PERSIST_ROOT for this run.",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help=f"Explicit run name. Defaults to a UTC timestamped {prefix} name.",
    )


def _add_common_training_args(
    parser: argparse.ArgumentParser,
    *,
    model_name: str,
    templates: Sequence[str],
    difficulties: Sequence[str],
    seed_count: int,
) -> None:
    parser.add_argument(
        "--model-name",
        default=model_name,
        help="Base Hugging Face model name.",
    )
    parser.add_argument(
        "--templates",
        nargs="+",
        default=list(templates),
        help="Scenario families to include.",
    )
    parser.add_argument(
        "--difficulties",
        nargs="+",
        default=list(difficulties),
        help="Difficulty levels to include.",
    )
    parser.add_argument(
        "--seed-count",
        type=int,
        default=seed_count,
        help="Number of deterministic train seeds to include starting from 0.",
    )
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        help="Enable 4-bit loading for reduced-memory fallback runs.",
    )


def _build_layout(
    *,
    prefix: str,
    persist_root: str | None,
    run_name: str | None,
) -> ArtifactLayout:
    root = Path(persist_root).expanduser().resolve() if persist_root else None
    return ArtifactLayout.create(
        run_name=run_name or build_run_name(prefix),
        root=root,
    )


def _build_seed_range(seed_count: int) -> list[int]:
    return list(range(seed_count))


def _run_scientist_preview(args: argparse.Namespace) -> int:
    layout = _build_layout(
        prefix="scientist",
        persist_root=args.persist_root,
        run_name=args.run_name,
    )
    config = ScientistGRPOConfig(
        model_name=args.model_name,
        templates=args.templates,
        difficulties=args.difficulties,
        train_seeds=_build_seed_range(args.seed_count),
        load_in_4bit=args.load_in_4bit,
        max_steps=args.max_steps,
    )
    plan = preview_scientist_training(config, layout=layout)
    write_json(layout.config_json, plan.model_dump(mode="json"))
    write_json(
        layout.summary_json,
        {"kind": "scientist_preview", **plan.model_dump(mode="json")},
    )
    print(json.dumps(plan.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0


def _run_scientist_train(args: argparse.Namespace) -> int:
    layout = _build_layout(
        prefix="scientist",
        persist_root=args.persist_root,
        run_name=args.run_name,
    )
    config = ScientistGRPOConfig(
        model_name=args.model_name,
        templates=args.templates,
        difficulties=args.difficulties,
        train_seeds=_build_seed_range(args.seed_count),
        load_in_4bit=args.load_in_4bit,
        max_steps=args.max_steps,
    )
    result = train_scientist_grpo(config, layout=layout, dry_run=args.dry_run)
    _write_run_metadata(
        layout,
        {
            "kind": "scientist_train",
            "model_name": args.model_name,
            "templates": args.templates,
            "difficulties": args.difficulties,
            "seed_count": args.seed_count,
            "max_steps": args.max_steps,
            "bounded_tool_policy": [
                "search_evidence",
                "run_code_check",
                "inspect_image",
            ],
        },
    )
    _maybe_plot_training_history(
        layout=layout,
        state_name="scientist_trainer_state.json",
        output_name="scientist_training.png",
        title="Scientist GRPO training history",
    )
    write_json(layout.summary_json, {"kind": "scientist_train", **result})
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def _run_lab_manager_preview(args: argparse.Namespace) -> int:
    layout = _build_layout(
        prefix="lab-manager",
        persist_root=args.persist_root,
        run_name=args.run_name,
    )
    config = LabManagerSFTConfig(
        model_name=args.model_name,
        templates=args.templates,
        difficulties=args.difficulties,
        train_seeds=_build_seed_range(args.seed_count),
        load_in_4bit=args.load_in_4bit,
    )
    plan = preview_lab_manager_training(config, layout=layout)
    write_json(layout.config_json, plan.model_dump(mode="json"))
    write_json(
        layout.summary_json,
        {"kind": "lab_manager_preview", **plan.model_dump(mode="json")},
    )
    print(json.dumps(plan.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0


def _run_lab_manager_train(args: argparse.Namespace) -> int:
    layout = _build_layout(
        prefix="lab-manager",
        persist_root=args.persist_root,
        run_name=args.run_name,
    )
    config = LabManagerSFTConfig(
        model_name=args.model_name,
        templates=args.templates,
        difficulties=args.difficulties,
        train_seeds=_build_seed_range(args.seed_count),
        load_in_4bit=args.load_in_4bit,
    )
    result = train_lab_manager_sft(config, layout=layout, dry_run=args.dry_run)
    _write_run_metadata(
        layout,
        {
            "kind": "lab_manager_train",
            "model_name": args.model_name,
            "templates": args.templates,
            "difficulties": args.difficulties,
            "seed_count": args.seed_count,
            "bounded_tool_policy": [
                "search_evidence",
                "run_code_check",
                "inspect_image",
            ],
        },
    )
    _maybe_plot_training_history(
        layout=layout,
        state_name="lab_manager_trainer_state.json",
        output_name="lab_manager_training.png",
        title="Lab Manager SFT training history",
    )
    write_json(layout.summary_json, {"kind": "lab_manager_train", **result})
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def _run_baseline_eval(args: argparse.Namespace) -> int:
    layout = _build_layout(
        prefix="eval-baseline",
        persist_root=args.persist_root,
        run_name=args.run_name,
    )
    cases = build_default_evaluation_cases(
        seeds=args.eval_seeds,
        scenarios=args.scenarios,
        difficulties=args.difficulties,
    )
    records, summary = evaluate_policy(
        base_url=args.base_url,
        policy_fn=build_baseline_scientist_action,
        cases=cases,
        transport=args.transport,
    )
    write_json(
        layout.config_json,
        {
            "kind": "baseline_eval",
            "base_url": args.base_url,
            "transport": args.transport,
            "cases": [case.__dict__ for case in cases],
        },
    )
    _write_run_metadata(
        layout,
        {
            "kind": "baseline_eval",
            "base_url": args.base_url,
            "transport": args.transport,
            "eval_seeds": args.eval_seeds,
            "scenarios": args.scenarios,
            "difficulties": args.difficulties,
            "bounded_tool_policy": [
                "search_evidence",
                "run_code_check",
                "inspect_image",
            ],
        },
    )
    for record in records:
        append_jsonl(
            layout.metrics_jsonl,
            episode_to_metrics(record).model_dump(mode="json"),
        )
    summary_payload = summary.model_dump(mode="json")
    write_json(layout.summary_json, summary_payload)
    _plot_eval_summary(summary_payload, layout=layout)
    _append_history_and_plots(
        layout=layout,
        kind="baseline_eval",
        rows=[{"label": "baseline", **summary_payload}],
    )
    print(json.dumps(summary_payload, indent=2, sort_keys=True))
    return 0


def _run_scientist_compare_eval(args: argparse.Namespace) -> int:
    layout = _build_layout(
        prefix="eval-compare",
        persist_root=args.persist_root,
        run_name=args.run_name,
    )
    cases = build_default_evaluation_cases(
        seeds=args.eval_seeds,
        scenarios=args.scenarios,
        difficulties=args.difficulties,
    )
    trained_policy = build_remote_scientist_policy(
        project=args.project,
        model_name=args.model_name,
        base_model=args.base_model,
        checkpoint_step=args.checkpoint_step,
        max_completion_tokens=args.max_completion_tokens,
        temperature=args.temperature,
    )
    records_by_label, rows = compare_policies(
        base_url=args.base_url,
        policies=[
            ("baseline", build_baseline_scientist_action),
            ("trained", trained_policy),
        ],
        cases=cases,
        transport=args.transport,
    )
    write_json(
        layout.config_json,
        {
            "kind": "scientist_compare_eval",
            "base_url": args.base_url,
            "transport": args.transport,
            "cases": [case.__dict__ for case in cases],
            "project": args.project,
            "model_name": args.model_name,
            "base_model": args.base_model,
            "checkpoint_step": args.checkpoint_step,
        },
    )
    _write_run_metadata(
        layout,
        {
            "kind": "scientist_compare_eval",
            "base_url": args.base_url,
            "transport": args.transport,
            "eval_seeds": args.eval_seeds,
            "scenarios": args.scenarios,
            "difficulties": args.difficulties,
            "project": args.project,
            "model_name": args.model_name,
            "base_model": args.base_model,
            "checkpoint_step": args.checkpoint_step,
            "bounded_tool_policy": [
                "search_evidence",
                "run_code_check",
                "inspect_image",
            ],
        },
    )
    for label, records in records_by_label.items():
        for record in records:
            append_jsonl(
                layout.metrics_jsonl,
                {"label": label, **episode_to_metrics(record).model_dump(mode="json")},
            )
    rows_payload = [row.model_dump(mode="json") for row in rows]
    write_json(layout.summary_json, {"rows": rows_payload})
    _plot_comparison_summary(rows_payload, layout=layout)
    _append_history_and_plots(
        layout=layout,
        kind="scientist_compare_eval",
        rows=rows_payload,
    )
    print(json.dumps({"rows": rows_payload}, indent=2, sort_keys=True))
    return 0


def _run_art_scientist_train(args: argparse.Namespace) -> int:
    layout = _build_layout(
        prefix="art-scientist",
        persist_root=args.persist_root,
        run_name=args.run_name,
    )
    config = ArtOpenEnvConfig(
        project=args.project,
        model_name=args.model_name,
        base_model=args.base_model,
        base_url=args.base_url,
        transport=args.transport,
        train_steps=args.train_steps,
        rollouts_per_group=args.rollouts_per_group,
        max_turns=args.max_turns,
        max_completion_tokens=args.max_completion_tokens,
        max_parse_retries=args.max_parse_retries,
        learning_rate=args.learning_rate,
        beta=args.beta,
        scenarios=[_parse_art_scenario_spec(item) for item in args.scenario_spec],
    )
    result = run_art_openenv_training(config, layout=layout)
    _write_run_metadata(
        layout,
        {
            "kind": "art_scientist_train",
            "project": args.project,
            "model_name": args.model_name,
            "base_model": args.base_model,
            "base_url": args.base_url,
            "train_steps": args.train_steps,
            "rollouts_per_group": args.rollouts_per_group,
            "max_turns": args.max_turns,
            "max_parse_retries": args.max_parse_retries,
            "scenario_spec": args.scenario_spec,
            "bounded_tool_policy": [
                "search_evidence",
                "run_code_check",
                "inspect_image",
            ],
        },
    )
    _plot_art_metrics(layout)
    _append_history_and_plots(
        layout=layout,
        kind="art_scientist_train",
        rows=[{"label": "trained", **result}],
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def _maybe_plot_training_history(
    *,
    layout: ArtifactLayout,
    state_name: str,
    output_name: str,
    title: str,
) -> None:
    state_path = layout.reports_dir / state_name
    if not state_path.exists():
        return
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    log_history = payload.get("log_history", [])
    if not isinstance(log_history, list):
        return
    plot_training_history(
        log_history,
        output_path=layout.plots_dir / output_name,
        title=title,
    )


def _plot_eval_summary(
    summary: dict[str, float | int],
    *,
    layout: ArtifactLayout,
) -> None:
    rows = [{"label": "baseline", **summary}]
    plot_evaluation_bars(
        rows,
        output_path=layout.plots_dir / "baseline_average_reward.png",
        metric_key="average_reward",
        title="Baseline average reward",
    )
    plot_evaluation_bars(
        rows,
        output_path=layout.plots_dir / "baseline_agreement_rate.png",
        metric_key="agreement_rate",
        title="Baseline agreement rate",
    )
    plot_evaluation_bars(
        rows,
        output_path=layout.plots_dir / "baseline_paper_understanding.png",
        metric_key="average_paper_understanding",
        title="Baseline paper understanding",
    )
    plot_evaluation_bars(
        rows,
        output_path=layout.plots_dir / "baseline_communication_quality.png",
        metric_key="average_communication_quality",
        title="Baseline communication quality",
    )
    if "average_invalid_bounded_tool_rate" in summary:
        plot_evaluation_bars(
            rows,
            output_path=layout.plots_dir / "baseline_invalid_bounded_tool_rate.png",
            metric_key="average_invalid_bounded_tool_rate",
            title="Baseline invalid bounded-tool rate",
        )


def _plot_comparison_summary(
    rows: list[dict[str, float | str]],
    *,
    layout: ArtifactLayout,
) -> None:
    for metric_key, title, output_name in (
        ("average_reward", "Before vs after average reward", "compare_average_reward.png"),
        ("agreement_rate", "Before vs after agreement rate", "compare_agreement_rate.png"),
        ("invalid_action_rate", "Before vs after invalid action rate", "compare_invalid_action_rate.png"),
        (
            "average_paper_understanding",
            "Before vs after paper understanding",
            "compare_paper_understanding.png",
        ),
        (
            "average_communication_quality",
            "Before vs after communication quality",
            "compare_communication_quality.png",
        ),
        (
            "average_invalid_bounded_tool_rate",
            "Before vs after invalid bounded-tool rate",
            "compare_invalid_bounded_tool_rate.png",
        ),
    ):
        plot_evaluation_bars(
            rows,
            output_path=layout.plots_dir / output_name,
            metric_key=metric_key,
            title=title,
        )


def _plot_art_metrics(layout: ArtifactLayout) -> None:
    if not layout.metrics_jsonl.exists():
        return
    rows = [
        json.loads(line)
        for line in layout.metrics_jsonl.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        return
    plot_metrics_by_step(
        rows,
        output_path=layout.plots_dir / "art_reward_components.png",
        title="ART Scientist reward components by training step",
        metric_keys=[
            "reward",
            "rigor",
            "feasibility",
            "fidelity",
            "paper_understanding",
            "communication_quality",
            "agreement_reached",
            "invalid_action_count",
            "parse_error_count",
        ],
    )


def _write_run_metadata(layout: ArtifactLayout, payload: dict[str, object]) -> None:
    write_json(layout.reports_dir / "run_metadata.json", payload)


def _append_history_and_plots(
    *,
    layout: ArtifactLayout,
    kind: str,
    rows: list[dict[str, object]],
) -> None:
    history_rows = [
        build_benchmark_history_row(
            run_name=layout.run_name,
            kind=kind,
            label=str(row.get("label", kind)),
            metrics=row,
        )
        for row in rows
    ]
    append_benchmark_history(layout.benchmark_history_jsonl, history_rows)
    all_rows = [
        row.model_dump(mode="json")
        for row in load_benchmark_history(layout.benchmark_history_jsonl)
    ]
    if not all_rows:
        return
    for metric_key, title, filename in (
        ("average_reward", "Benchmark history: average reward", "history_average_reward.png"),
        ("agreement_rate", "Benchmark history: agreement rate", "history_agreement_rate.png"),
        (
            "average_paper_understanding",
            "Benchmark history: paper understanding",
            "history_paper_understanding.png",
        ),
        (
            "average_communication_quality",
            "Benchmark history: communication quality",
            "history_communication_quality.png",
        ),
        (
            "invalid_action_rate",
            "Benchmark history: invalid action rate",
            "history_invalid_action_rate.png",
        ),
    ):
        plot_benchmark_history(
            all_rows,
            output_path=layout.history_plots_dir / filename,
            metric_key=metric_key,
            title=title,
        )


def _parse_art_scenario_spec(value: str) -> ArtScenarioSpec:
    parts = value.split(":")
    if len(parts) != 3:
        raise ValueError(
            f"Invalid scenario spec {value!r}. Expected seed:scenario:difficulty."
        )
    seed_text, scenario, difficulty = parts
    return ArtScenarioSpec(
        seed=int(seed_text),
        scenario=scenario,
        difficulty=difficulty,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
