"""Northflank- and notebook-friendly training entrypoints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from replicalab.agents import build_baseline_scientist_action
from replicalab.training.artifacts import (
    ArtifactLayout,
    append_jsonl,
    build_run_name,
    write_json,
)
from replicalab.training.evaluation import build_default_evaluation_cases, evaluate_policy
from replicalab.training.lab_manager_sft import (
    LabManagerSFTConfig,
    preview_lab_manager_training,
    train_lab_manager_sft,
)
from replicalab.training.metrics import episode_to_metrics
from replicalab.training.plots import plot_evaluation_bars, plot_training_history
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
    for record in records:
        append_jsonl(
            layout.metrics_jsonl,
            episode_to_metrics(record).model_dump(mode="json"),
        )
    summary_payload = summary.model_dump(mode="json")
    write_json(layout.summary_json, summary_payload)
    _plot_eval_summary(summary_payload, layout=layout)
    print(json.dumps(summary_payload, indent=2, sort_keys=True))
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


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
