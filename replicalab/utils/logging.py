"""Episode logging and replay persistence helpers.

MOD 07 provides the persistence boundary for episode replay, notebook
inspection, and later API replay retrieval.  All writes are atomic
(temp file + rename) so a crash never leaves a half-written replay.

JDG 07 adds reward-breakdown logging to CSV and JSONL so downstream
consumers (notebook plots, evaluation scripts, UI) can read per-episode
score components, penalties, and bounded-tool metrics without parsing
full replay JSON.
"""

from __future__ import annotations

import csv
import json
import io
import os
import tempfile
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from replicalab.models import EpisodeLog, RewardBreakdown

_M = TypeVar("_M", bound=BaseModel)

_DEFAULT_REPLAYS_DIR = Path(__file__).resolve().parents[2] / "replicalab" / "outputs" / "replays"
_DEFAULT_LOGS_DIR = Path(__file__).resolve().parents[2] / "replicalab" / "outputs" / "logs"


# ---------------------------------------------------------------------------
# Internal helper — atomic JSON write for any Pydantic model
# ---------------------------------------------------------------------------


def _write_json_model(model: BaseModel, path: Path) -> Path:
    """Serialize a Pydantic model to *path* atomically.

    Writes to a temporary file in the same directory, then renames so
    readers never see a partial file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = model.model_dump_json(indent=2)

    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(data)
        # On Windows, target must not exist for os.rename; use replace.
        os.replace(tmp, str(path))
    except BaseException:
        # Clean up the temp file on any failure.
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

    return path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def write_episode_log(
    log: EpisodeLog,
    directory: Path | str | None = None,
) -> Path:
    """Persist a completed episode log as JSON.

    Parameters
    ----------
    log:
        The completed episode record.
    directory:
        Target directory.  Defaults to ``replicalab/outputs/replays/``.

    Returns
    -------
    Path
        Absolute path to the written file.
    """
    directory = Path(directory) if directory is not None else _DEFAULT_REPLAYS_DIR
    filename = f"{log.episode_id}.json" if log.episode_id else "unknown.json"
    return _write_json_model(log, directory / filename)


def load_episode_log(path: Path | str) -> EpisodeLog:
    """Load an episode log from a JSON file.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    pydantic.ValidationError
        If the file contents do not match the ``EpisodeLog`` schema.
    """
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    return EpisodeLog.model_validate_json(raw)


def append_reward_csv(
    path: Path | str | None = None,
    *,
    episode_id: str = "",
    seed: int = 0,
    scenario_template: str = "",
    difficulty: str = "",
    total_reward: float = 0.0,
    rigor: float = 0.0,
    feasibility: float = 0.0,
    fidelity: float = 0.0,
    parsimony: float = 1.0,
    efficiency_bonus: float = 0.0,
    communication_bonus: float = 0.0,
    penalty_total: float = 0.0,
    rounds_used: int = 0,
    agreement_reached: bool = False,
    verdict: str = "",
) -> Path:
    """Append one row to a reward CSV file.

    Creates the file with a header if it does not exist.
    JDG 07 expanded the column set to include all V2 reward breakdown
    components: parsimony, bonuses, penalty total, and verdict.
    """
    path = Path(path) if path is not None else _DEFAULT_LOGS_DIR / "rewards.csv"
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "episode_id",
        "seed",
        "scenario_template",
        "difficulty",
        "total_reward",
        "rigor",
        "feasibility",
        "fidelity",
        "parsimony",
        "efficiency_bonus",
        "communication_bonus",
        "penalty_total",
        "rounds_used",
        "agreement_reached",
        "verdict",
    ]

    write_header = not path.exists() or path.stat().st_size == 0

    row = {
        "episode_id": episode_id,
        "seed": seed,
        "scenario_template": scenario_template,
        "difficulty": difficulty,
        "total_reward": total_reward,
        "rigor": rigor,
        "feasibility": feasibility,
        "fidelity": fidelity,
        "parsimony": parsimony,
        "efficiency_bonus": efficiency_bonus,
        "communication_bonus": communication_bonus,
        "penalty_total": penalty_total,
        "rounds_used": rounds_used,
        "agreement_reached": agreement_reached,
        "verdict": verdict,
    }

    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    return path


def append_reward_jsonl(
    path: Path | str | None = None,
    *,
    episode_id: str = "",
    seed: int = 0,
    scenario_template: str = "",
    difficulty: str = "",
    total_reward: float = 0.0,
    breakdown: RewardBreakdown | None = None,
    rounds_used: int = 0,
    agreement_reached: bool = False,
    verdict: str = "",
    judge_notes: str = "",
    bounded_tool_metrics: dict[str, Any] | None = None,
) -> Path:
    """Append one JSON object per line to a JSONL reward log.

    Unlike the CSV writer, JSONL preserves nested structures — the full
    penalties dict and bounded-tool metrics dict are stored verbatim so
    notebook and evaluation consumers can drill into per-penalty and
    per-tool breakdowns without parsing replay JSON.
    """
    path = Path(path) if path is not None else _DEFAULT_LOGS_DIR / "rewards.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)

    bd = breakdown or RewardBreakdown()
    record: dict[str, Any] = {
        "episode_id": episode_id,
        "seed": seed,
        "scenario_template": scenario_template,
        "difficulty": difficulty,
        "total_reward": total_reward,
        "rigor": bd.rigor,
        "feasibility": bd.feasibility,
        "fidelity": bd.fidelity,
        "parsimony": bd.parsimony,
        "efficiency_bonus": bd.efficiency_bonus,
        "communication_bonus": bd.communication_bonus,
        "penalties": dict(bd.penalties),
        "penalty_total": sum(bd.penalties.values()),
        "rounds_used": rounds_used,
        "agreement_reached": agreement_reached,
        "verdict": verdict,
        "judge_notes": judge_notes,
        "bounded_tool_metrics": bounded_tool_metrics or {},
    }

    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    return path


def log_episode_reward(
    *,
    episode_id: str = "",
    seed: int = 0,
    scenario_template: str = "",
    difficulty: str = "",
    total_reward: float = 0.0,
    breakdown: RewardBreakdown | None = None,
    rounds_used: int = 0,
    agreement_reached: bool = False,
    verdict: str = "",
    judge_notes: str = "",
    bounded_tool_metrics: dict[str, Any] | None = None,
    csv_path: Path | str | None = None,
    jsonl_path: Path | str | None = None,
) -> tuple[Path, Path]:
    """Write one episode's reward data to both CSV and JSONL logs.

    Convenience wrapper that calls ``append_reward_csv`` and
    ``append_reward_jsonl`` with the same metadata.  Returns the
    paths to both files.
    """
    bd = breakdown or RewardBreakdown()
    csv_out = append_reward_csv(
        csv_path,
        episode_id=episode_id,
        seed=seed,
        scenario_template=scenario_template,
        difficulty=difficulty,
        total_reward=total_reward,
        rigor=bd.rigor,
        feasibility=bd.feasibility,
        fidelity=bd.fidelity,
        parsimony=bd.parsimony,
        efficiency_bonus=bd.efficiency_bonus,
        communication_bonus=bd.communication_bonus,
        penalty_total=sum(bd.penalties.values()),
        rounds_used=rounds_used,
        agreement_reached=agreement_reached,
        verdict=verdict,
    )
    jsonl_out = append_reward_jsonl(
        jsonl_path,
        episode_id=episode_id,
        seed=seed,
        scenario_template=scenario_template,
        difficulty=difficulty,
        total_reward=total_reward,
        breakdown=bd,
        rounds_used=rounds_used,
        agreement_reached=agreement_reached,
        verdict=verdict,
        judge_notes=judge_notes,
        bounded_tool_metrics=bounded_tool_metrics,
    )
    return csv_out, jsonl_out
