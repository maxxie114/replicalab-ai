from __future__ import annotations

import json
from pathlib import Path


def _load_notebook(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_train_minimal_colab_has_unsloth_trl_training_flow() -> None:
    notebook = _load_notebook("notebooks/train_minimal_colab.ipynb")
    text = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "unsloth" in text.lower()
    assert "trl" in text.lower()
    assert "ScientistGRPOConfig" in text
    assert "preview_scientist_training" in text
    assert "train_scientist_grpo" in text
    assert 'MODEL_NAME = "Qwen/Qwen3-4B"' in text
    assert "RUN_REAL_TRAINING = False" in text


def test_train_colab_remains_full_driver_notebook() -> None:
    notebook = _load_notebook("notebooks/train_colab.ipynb")
    text = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])

    assert "LabManagerSFTConfig" in text
    assert "ScientistGRPOConfig" in text
    assert "train_lab_manager_sft" in text
    assert "train_scientist_grpo" in text
