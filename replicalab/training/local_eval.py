"""Helpers for local-adapter evaluation against live ReplicaLab rollouts."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence

from pydantic import BaseModel, ConfigDict

from replicalab.agents.scientist_policy import (
    ScientistOutputParseError,
    _build_live_scientist_system_prompt,
    call_scientist_with_retry,
    format_scientist_observation,
)
from replicalab.models import ScientistAction, ScientistActionType, ScientistObservation
from replicalab.training.corpus import load_frozen_evidence_packs, select_evidence_pack
from replicalab.training.evaluation import EvaluationCase
from replicalab.training.runtime import require_module


class PaperBalancedEvaluationCase(BaseModel):
    """One deterministic rollout case with expected paper metadata."""

    model_config = ConfigDict(extra="forbid")

    case_index: int
    seed: int
    scenario: str
    difficulty: str
    expected_evidence_id: str
    expected_paper_title: str

    def to_evaluation_case(self) -> EvaluationCase:
        return EvaluationCase(
            seed=self.seed,
            scenario=self.scenario,
            difficulty=self.difficulty,
        )


def build_trainable_paper_cases(
    total_cases: int,
    *,
    case_index_offset: int = 0,
    difficulties: Sequence[str] = ("easy", "medium", "hard"),
) -> list[PaperBalancedEvaluationCase]:
    """Build a deterministic live-eval set balanced across trainable papers."""

    if total_cases < 1:
        raise ValueError("total_cases must be at least 1")
    if case_index_offset < 0:
        raise ValueError("case_index_offset must be at least 0")
    if not difficulties:
        raise ValueError("difficulties must not be empty")

    packs = [pack for pack in load_frozen_evidence_packs() if pack.trainable_in_env]
    if not packs:
        raise ValueError("No trainable evidence packs are wired into the current env.")

    by_template: dict[str, list[object]] = {}
    for pack in packs:
        assert pack.template is not None
        by_template.setdefault(pack.template, []).append(pack)
    for template in by_template:
        by_template[template] = sorted(
            by_template[template],
            key=lambda pack: pack.scenario_number,  # type: ignore[attr-defined]
        )

    targets: list[tuple[str, int, object]] = []
    for template in sorted(by_template):
        for pack_index, pack in enumerate(by_template[template]):
            targets.append((template, pack_index, pack))

    cases: list[PaperBalancedEvaluationCase] = []
    for local_index in range(total_cases):
        case_index = case_index_offset + local_index
        template, pack_index, pack = targets[case_index % len(targets)]
        cycle_index = case_index // len(targets)
        template_pack_count = len(by_template[template])
        seed = pack_index + cycle_index * template_pack_count
        difficulty = difficulties[(case_index + pack_index) % len(difficulties)]
        cases.append(
            PaperBalancedEvaluationCase(
                case_index=case_index,
                seed=seed,
                scenario=template,
                difficulty=difficulty,
                expected_evidence_id=pack.evidence_id,  # type: ignore[attr-defined]
                expected_paper_title=pack.downloaded_paper_title,  # type: ignore[attr-defined]
            )
        )

    return cases


def build_local_scientist_policy(
    *,
    base_model: str,
    adapter_dir: str | Path,
    max_completion_tokens: int = 450,
    temperature: float = 0.0,
    max_retries: int = 2,
) -> Callable[[ScientistObservation], ScientistAction]:
    """Create a sync Scientist policy callable backed by a local PEFT adapter."""

    torch = require_module("torch")
    transformers = require_module("transformers")
    peft = require_module("peft")

    adapter_path = Path(adapter_dir).expanduser().resolve()
    if not adapter_path.exists():
        raise FileNotFoundError(f"Adapter directory does not exist: {adapter_path}")

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        str(adapter_path),
        trust_remote_code=True,
    )
    model = transformers.AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model = peft.PeftModel.from_pretrained(model, str(adapter_path))
    model.eval()
    device = next(model.parameters()).device

    evidence_packs = [
        pack for pack in load_frozen_evidence_packs() if pack.trainable_in_env
    ]

    def generate_fn(messages: list[dict[str, str]]) -> str:
        prompt_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        enc = tokenizer(prompt_text, return_tensors="pt").to(device)
        generation_kwargs = {
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "max_new_tokens": max_completion_tokens,
            "pad_token_id": tokenizer.eos_token_id,
            "do_sample": temperature > 0.0,
        }
        if temperature > 0.0:
            generation_kwargs["temperature"] = temperature
        with torch.no_grad():
            outputs = model.generate(**generation_kwargs)
        generated_ids = outputs[0][enc["input_ids"].shape[1]:]
        return tokenizer.decode(generated_ids, skip_special_tokens=True)

    def policy_fn(
        observation: ScientistObservation,
        *,
        seed: int | None = None,
        scenario: str | None = None,
        difficulty: str | None = None,
    ) -> ScientistAction:
        evidence_pack = None
        if seed is not None and scenario is not None:
            evidence_pack = select_evidence_pack(
                evidence_packs,
                template=scenario,  # type: ignore[arg-type]
                seed=seed,
            )

        user_message = format_scientist_observation(observation)
        if evidence_pack is not None:
            user_message += "\n\nFrozen evidence pack:\n" + evidence_pack.prompt_block()

        try:
            result = call_scientist_with_retry(
                generate_fn,
                _build_live_scientist_system_prompt(
                    observation,
                    evidence_pack=evidence_pack,
                    difficulty=difficulty,
                    scenario=scenario,
                ),
                observation,
                max_retries=max_retries,
                user_message_override=user_message,
            )
            return result.action
        except ScientistOutputParseError:
            return ScientistAction(
                action_type=ScientistActionType.REQUEST_INFO,
                sample_size=0,
                controls=[],
                technique="",
                duration_days=0,
                required_equipment=[],
                required_reagents=[],
                questions=[
                    "Please restate the main blocking requirement or missing evidence."
                ],
                rationale="",
            )

    return policy_fn


__all__ = [
    "PaperBalancedEvaluationCase",
    "build_local_scientist_policy",
    "build_trainable_paper_cases",
]
