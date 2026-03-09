"""Matplotlib plot helpers for training and evaluation outputs."""

from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Iterable


def plot_training_history(
    log_history: Iterable[dict[str, object]],
    *,
    output_path: Path,
    title: str,
) -> None:
    """Plot a reward/loss curve from TRL trainer log history."""

    matplotlib = __import__("matplotlib.pyplot", fromlist=["pyplot"])
    plt = matplotlib

    steps: list[int] = []
    rewards: list[float] = []
    losses: list[float] = []

    for row in log_history:
        step = row.get("step")
        if isinstance(step, int):
            steps.append(step)
            rewards.append(float(row.get("reward", 0.0) or 0.0))
            losses.append(float(row.get("loss", 0.0) or 0.0))

    if not steps:
        raise ValueError("No step data found in trainer log history.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(steps, rewards, label="reward")
    axes[0].set_title("Reward")
    axes[0].set_xlabel("step")
    axes[0].set_ylabel("reward")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(steps, losses, label="loss", color="tab:red")
    axes[1].set_title("Loss")
    axes[1].set_xlabel("step")
    axes[1].set_ylabel("loss")
    axes[1].grid(True, alpha=0.3)

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_evaluation_bars(
    rows: list[dict[str, float | str]],
    *,
    output_path: Path,
    metric_key: str,
    title: str,
) -> None:
    """Plot a simple before/after comparison chart."""

    matplotlib = __import__("matplotlib.pyplot", fromlist=["pyplot"])
    plt = matplotlib

    labels = [str(row["label"]) for row in rows]
    values = [float(row[metric_key]) for row in rows]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values, color=["#335c67", "#e09f3e", "#9e2a2b"][: len(labels)])
    ax.set_title(title)
    ax.set_ylabel(metric_key.replace("_", " "))
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_metrics_by_step(
    rows: Iterable[dict[str, object]],
    *,
    output_path: Path,
    title: str,
    metric_keys: list[str],
    x_key: str = "training_step",
) -> None:
    """Plot averaged metric curves grouped by training step."""

    matplotlib = __import__("matplotlib.pyplot", fromlist=["pyplot"])
    plt = matplotlib

    grouped: dict[int, dict[str, list[float]]] = {}
    for row in rows:
        raw_step = row.get(x_key)
        if not isinstance(raw_step, int):
            continue
        bucket = grouped.setdefault(raw_step, {})
        for metric_key in metric_keys:
            raw_value = row.get(metric_key)
            if isinstance(raw_value, (int, float)):
                bucket.setdefault(metric_key, []).append(float(raw_value))

    if not grouped:
        raise ValueError(f"No '{x_key}' values found for metric plotting.")

    steps = sorted(grouped)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    for metric_key in metric_keys:
        values = [
            mean(grouped[step].get(metric_key, [0.0]))
            for step in steps
        ]
        ax.plot(steps, values, marker="o", label=metric_key.replace("_", " "))
    ax.set_title(title)
    ax.set_xlabel(x_key.replace("_", " "))
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_benchmark_history(
    rows: Iterable[dict[str, object]],
    *,
    output_path: Path,
    metric_key: str,
    title: str,
) -> None:
    """Plot a cross-run metric trend grouped by label."""

    matplotlib = __import__("matplotlib.pyplot", fromlist=["pyplot"])
    plt = matplotlib

    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        label = str(row.get("label", "unknown"))
        grouped.setdefault(label, []).append(dict(row))

    if not grouped:
        raise ValueError("No benchmark history rows provided.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5))
    for label, label_rows in grouped.items():
        ordered = sorted(label_rows, key=lambda item: str(item.get("recorded_at", "")))
        values = [float(item.get(metric_key, 0.0) or 0.0) for item in ordered]
        if not values:
            continue
        x_values = list(range(1, len(values) + 1))
        ax.plot(x_values, values, marker="o", label=label)

    ax.set_title(title)
    ax.set_xlabel("run index")
    ax.set_ylabel(metric_key.replace("_", " "))
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


__all__ = [
    "plot_benchmark_history",
    "plot_evaluation_bars",
    "plot_metrics_by_step",
    "plot_training_history",
]
