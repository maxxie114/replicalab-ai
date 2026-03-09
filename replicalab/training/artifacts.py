"""Artifact path helpers for H100, Colab, and Northflank training runs."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_OUTPUT_ROOT = _REPO_ROOT / "replicalab" / "outputs" / "training"


def default_training_root() -> Path:
    """Return the persistent training root for local or Northflank runs."""

    configured = os.environ.get("REPLICALAB_PERSIST_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return _DEFAULT_OUTPUT_ROOT.resolve()


def build_run_name(prefix: str) -> str:
    """Build a sortable UTC run name."""

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{stamp}"


@dataclass(frozen=True)
class ArtifactLayout:
    """Stable folder layout shared by Scientist, Lab Manager, and eval runs."""

    root: Path
    run_name: str
    run_dir: Path
    checkpoints_dir: Path
    scientist_adapter_dir: Path
    lab_manager_adapter_dir: Path
    plots_dir: Path
    reports_dir: Path
    manifests_dir: Path
    history_dir: Path
    history_plots_dir: Path
    hf_cache_dir: Path
    metrics_jsonl: Path
    summary_json: Path
    config_json: Path
    evidence_manifest_json: Path
    benchmark_history_jsonl: Path

    @classmethod
    def create(
        cls,
        *,
        run_name: str,
        root: Path | None = None,
        create_dirs: bool = True,
    ) -> "ArtifactLayout":
        base_root = (root or default_training_root()).resolve()
        run_dir = base_root / run_name
        layout = cls(
            root=base_root,
            run_name=run_name,
            run_dir=run_dir,
            checkpoints_dir=run_dir / "checkpoints",
            scientist_adapter_dir=run_dir / "checkpoints" / "scientist_lora",
            lab_manager_adapter_dir=run_dir / "checkpoints" / "lab_manager_lora",
            plots_dir=run_dir / "plots",
            reports_dir=run_dir / "reports",
            manifests_dir=run_dir / "manifests",
            history_dir=base_root / "history",
            history_plots_dir=base_root / "history" / "plots",
            hf_cache_dir=base_root / "hf_cache",
            metrics_jsonl=run_dir / "reports" / "metrics.jsonl",
            summary_json=run_dir / "reports" / "summary.json",
            config_json=run_dir / "manifests" / "run_config.json",
            evidence_manifest_json=run_dir / "manifests" / "evidence_packs.json",
            benchmark_history_jsonl=base_root / "history" / "benchmark_history.jsonl",
        )
        if create_dirs:
            layout.ensure_directories()
        return layout

    def ensure_directories(self) -> None:
        """Create all directories used by the run."""

        for path in (
            self.root,
            self.run_dir,
            self.checkpoints_dir,
            self.scientist_adapter_dir,
            self.lab_manager_adapter_dir,
            self.plots_dir,
            self.reports_dir,
            self.manifests_dir,
            self.history_dir,
            self.history_plots_dir,
            self.hf_cache_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    """Write JSON with stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def append_jsonl(path: Path, payload: Any) -> None:
    """Append one JSON line to a metrics file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


__all__ = [
    "ArtifactLayout",
    "append_jsonl",
    "build_run_name",
    "default_training_root",
    "write_json",
]
