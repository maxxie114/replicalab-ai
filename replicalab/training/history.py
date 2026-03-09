"""Cross-run benchmark history helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, ConfigDict

from replicalab.training.artifacts import append_jsonl


class BenchmarkHistoryRow(BaseModel):
    """One summary row persisted across runs for trend plotting."""

    model_config = ConfigDict(extra="forbid")

    recorded_at: str
    run_name: str
    kind: str
    label: str
    episode_count: int
    average_reward: float
    average_rounds: float
    agreement_rate: float
    invalid_action_rate: float
    average_invalid_bounded_tool_rate: float
    average_rigor: float
    average_feasibility: float
    average_fidelity: float
    average_parsimony: float
    average_tool_trace_count: float
    average_paper_understanding: float
    average_communication_quality: float


def append_benchmark_history(path: Path, rows: Iterable[BenchmarkHistoryRow]) -> None:
    """Append benchmark rows to the shared history file."""

    for row in rows:
        append_jsonl(path, row.model_dump(mode="json"))


def load_benchmark_history(path: Path) -> list[BenchmarkHistoryRow]:
    """Load benchmark history rows from a JSONL file."""

    if not path.exists():
        return []
    rows: list[BenchmarkHistoryRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(BenchmarkHistoryRow.model_validate(json.loads(line)))
    return rows


def build_benchmark_history_row(
    *,
    run_name: str,
    kind: str,
    label: str,
    metrics: dict[str, object],
) -> BenchmarkHistoryRow:
    """Create a benchmark history row from a summary-like metric payload."""

    average_parsimony = metrics.get("average_parsimony")
    return BenchmarkHistoryRow(
        recorded_at=datetime.now(UTC).isoformat(),
        run_name=run_name,
        kind=kind,
        label=label,
        episode_count=int(metrics.get("episode_count", 0) or 0),
        average_reward=float(metrics.get("average_reward", 0.0) or 0.0),
        average_rounds=float(metrics.get("average_rounds", 0.0) or 0.0),
        agreement_rate=float(metrics.get("agreement_rate", 0.0) or 0.0),
        invalid_action_rate=float(metrics.get("invalid_action_rate", 0.0) or 0.0),
        average_invalid_bounded_tool_rate=float(
            metrics.get("average_invalid_bounded_tool_rate", 0.0) or 0.0
        ),
        average_rigor=float(metrics.get("average_rigor", 0.0) or 0.0),
        average_feasibility=float(metrics.get("average_feasibility", 0.0) or 0.0),
        average_fidelity=float(metrics.get("average_fidelity", 0.0) or 0.0),
        average_parsimony=(
            float(average_parsimony) if average_parsimony is not None else 1.0
        ),
        average_tool_trace_count=float(
            metrics.get("average_tool_trace_count", 0.0) or 0.0
        ),
        average_paper_understanding=float(
            metrics.get("average_paper_understanding", 0.0) or 0.0
        ),
        average_communication_quality=float(
            metrics.get("average_communication_quality", 0.0) or 0.0
        ),
    )


__all__ = [
    "BenchmarkHistoryRow",
    "append_benchmark_history",
    "build_benchmark_history_row",
    "load_benchmark_history",
]
