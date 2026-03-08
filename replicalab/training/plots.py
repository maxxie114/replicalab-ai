"""Matplotlib plot helpers for training and evaluation outputs."""

from __future__ import annotations

from pathlib import Path
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


__all__ = [
    "plot_evaluation_bars",
    "plot_training_history",
]
