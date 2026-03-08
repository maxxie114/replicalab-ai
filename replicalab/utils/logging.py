"""Episode logging and replay persistence helpers.

MOD 07 provides the persistence boundary for episode replay, notebook
inspection, and later API replay retrieval.  All writes are atomic
(temp file + rename) so a crash never leaves a half-written replay.
"""

from __future__ import annotations

import csv
import io
import os
import tempfile
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from replicalab.models import EpisodeLog

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
    rounds_used: int = 0,
    agreement_reached: bool = False,
) -> Path:
    """Append one row to a reward CSV file.

    Creates the file with a header if it does not exist.
    Pre-stages the format that JDG 07 will consume.
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
        "rounds_used",
        "agreement_reached",
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
        "rounds_used": rounds_used,
        "agreement_reached": agreement_reached,
    }

    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    return path
