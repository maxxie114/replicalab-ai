"""Optional-dependency helpers for Unsloth / TRL training code."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, Iterable

DEFAULT_QWEN_TARGET_MODULES = (
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
)


def require_module(module_name: str) -> Any:
    """Import a module and raise an actionable error if it is missing."""

    try:
        return import_module(module_name)
    except ImportError as exc:
        raise RuntimeError(
            f"Missing optional training dependency '{module_name}'. "
            "Install the notebook/job dependencies before running training."
        ) from exc


def build_hf_dataset(rows: list[dict[str, object]]) -> Any:
    """Construct a Hugging Face Dataset lazily."""

    datasets_module = require_module("datasets")
    return datasets_module.Dataset.from_list(rows)


def load_qwen_lora_model(
    *,
    model_name: str,
    max_seq_length: int,
    load_in_4bit: bool,
    fast_inference: bool,
    lora_rank: int,
    lora_alpha: int,
    random_state: int,
    target_modules: Iterable[str] = DEFAULT_QWEN_TARGET_MODULES,
) -> tuple[Any, Any]:
    """Load a Qwen-compatible model through Unsloth and attach a LoRA adapter."""

    unsloth_module = require_module("unsloth")
    fast_language_model = unsloth_module.FastLanguageModel
    model, tokenizer = fast_language_model.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
        fast_inference=fast_inference,
    )
    model = fast_language_model.get_peft_model(
        model,
        r=lora_rank,
        target_modules=list(target_modules),
        lora_alpha=lora_alpha,
        lora_dropout=0,
        use_gradient_checkpointing="unsloth",
        random_state=random_state,
    )
    return model, tokenizer


def save_adapter(model: Any, tokenizer: Any, output_dir: Path) -> None:
    """Persist the adapter in a way that works across Unsloth versions."""

    output_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(model, "save_lora"):
        model.save_lora(str(output_dir))
    else:
        model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))


__all__ = [
    "DEFAULT_QWEN_TARGET_MODULES",
    "build_hf_dataset",
    "load_qwen_lora_model",
    "require_module",
    "save_adapter",
]
