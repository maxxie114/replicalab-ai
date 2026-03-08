"""Frozen evidence-pack helpers backed by the local 50-paper corpus."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, ConfigDict

from replicalab.scenarios.templates import TemplateName

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRAINING_PLAN_PATH = _REPO_ROOT / "ReplicaLab_50_Scenarios_Training_Plan.md"
DEFAULT_PAPER_MANIFEST_PATH = _REPO_ROOT / "data" / "papers" / "manifest.json"

FIELD_TO_TEMPLATE_MAP: dict[str, TemplateName] = {
    "computational_ml_dl": "ml_benchmark",
    "quantitative_finance": "finance_trading",
}


class ScenarioPaperSpec(BaseModel):
    """Structured scenario metadata parsed from the 50-scenario training plan."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    scenario_number: int
    field: str
    cluster: str
    scenario_title: str
    claim: str
    key_technique: str
    original_resources: str
    primary_constraint_tension: str
    template: TemplateName | None = None

    @property
    def slug(self) -> str:
        return _slugify(self.scenario_title)

    @property
    def trainable_in_env(self) -> bool:
        return self.template is not None


class PaperManifestEntry(BaseModel):
    """Downloaded-paper metadata recorded in ``data/papers/manifest.json``."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    id: int
    field: str
    scenario_title: str
    download_folder: str
    requested_paper_title: str
    downloaded_paper_title: str
    planned_reference_title: str
    match_type: str
    status: str
    source_url: str
    sha256: str

    @property
    def slug(self) -> str:
        return _slugify(self.scenario_title)


class FrozenEvidencePack(BaseModel):
    """Canonical evidence pack used by training and evaluation code."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    evidence_id: str
    scenario_number: int
    scenario_title: str
    field: str
    cluster: str
    template: TemplateName | None = None
    claim: str
    key_technique: str
    original_resources: str
    primary_constraint_tension: str
    requested_paper_title: str
    downloaded_paper_title: str
    planned_reference_title: str
    match_type: str
    source_url: str
    pdf_path: str
    metadata_path: str
    sha256: str

    @property
    def trainable_in_env(self) -> bool:
        return self.template is not None

    def prompt_block(self) -> str:
        """Render the pack into a compact prompt-side evidence summary."""

        lines = [
            f"- Scenario paper: {self.scenario_title}",
            f"- Grounding paper: {self.downloaded_paper_title}",
            f"- Claim: {self.claim}",
            f"- Technique: {self.key_technique}",
            f"- Original resources: {self.original_resources}",
            f"- Constraint tension: {self.primary_constraint_tension}",
            f"- Match type: {self.match_type}",
            f"- Local PDF: {self.pdf_path}",
        ]
        return "\n".join(lines)


def parse_training_plan(
    path: Path = DEFAULT_TRAINING_PLAN_PATH,
) -> list[ScenarioPaperSpec]:
    """Parse the markdown training plan into structured scenario specs."""

    current_field: str | None = None
    current_cluster = ""
    specs: list[ScenarioPaperSpec] = []
    domain_map = {
        "Computational ML/DL": "computational_ml_dl",
        "Wet-Lab Biology": "wet_lab_biology",
        "Behavioral and Cognitive": "behavioral_cognitive",
        "Environmental and Ecological": "environmental_ecological",
        "Quantitative Finance": "quantitative_finance",
    }

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## Domain"):
            current_field = None
            for title, field_key in domain_map.items():
                if title in line:
                    current_field = field_key
                    break
            continue

        if line.startswith("### "):
            current_cluster = line[4:].strip()
            continue

        if not line.startswith("|"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 6:
            continue
        if not cells[0].isdigit():
            continue

        if current_field is None:
            raise ValueError(f"Found scenario row without active field: {line}")

        specs.append(
            ScenarioPaperSpec(
                scenario_number=int(cells[0]),
                field=current_field,
                cluster=current_cluster,
                scenario_title=cells[1],
                claim=cells[2],
                key_technique=cells[3],
                original_resources=cells[4],
                primary_constraint_tension=cells[5],
                template=FIELD_TO_TEMPLATE_MAP.get(current_field),
            )
        )

    return specs


def load_paper_manifest(
    path: Path = DEFAULT_PAPER_MANIFEST_PATH,
) -> list[PaperManifestEntry]:
    """Load the downloaded-paper manifest from disk."""

    if not path.exists():
        return _build_plan_only_manifest(parse_training_plan())

    rows = json.loads(path.read_text(encoding="utf-8"))
    return [PaperManifestEntry.model_validate(row) for row in rows]


def build_frozen_evidence_packs(
    *,
    plan_specs: Iterable[ScenarioPaperSpec] | None = None,
    manifest_entries: Iterable[PaperManifestEntry] | None = None,
) -> list[FrozenEvidencePack]:
    """Merge the markdown plan and paper manifest into frozen evidence packs."""

    plan = list(plan_specs or parse_training_plan())
    manifest = list(manifest_entries or load_paper_manifest())
    by_slug = {entry.slug: entry for entry in manifest}

    packs: list[FrozenEvidencePack] = []
    for spec in plan:
        entry = by_slug.get(spec.slug)
        if entry is None:
            raise ValueError(f"No manifest entry found for scenario: {spec.scenario_title}")

        folder = _REPO_ROOT / entry.download_folder
        packs.append(
            FrozenEvidencePack(
                evidence_id=f"{spec.field}:{spec.slug}",
                scenario_number=spec.scenario_number,
                scenario_title=spec.scenario_title,
                field=spec.field,
                cluster=spec.cluster,
                template=spec.template,
                claim=spec.claim,
                key_technique=spec.key_technique,
                original_resources=spec.original_resources,
                primary_constraint_tension=spec.primary_constraint_tension,
                requested_paper_title=entry.requested_paper_title,
                downloaded_paper_title=entry.downloaded_paper_title,
                planned_reference_title=entry.planned_reference_title,
                match_type=entry.match_type,
                source_url=entry.source_url,
                pdf_path=str((folder / "paper.pdf").resolve()),
                metadata_path=str((folder / "metadata.json").resolve()),
                sha256=entry.sha256,
            )
        )

    return sorted(packs, key=lambda item: item.scenario_number)


def load_frozen_evidence_packs() -> list[FrozenEvidencePack]:
    """Convenience loader for the repo-local evidence corpus."""

    return build_frozen_evidence_packs()


def select_evidence_pack(
    packs: Iterable[FrozenEvidencePack],
    *,
    template: TemplateName,
    seed: int,
) -> FrozenEvidencePack | None:
    """Select one stable evidence pack for a template and seed."""

    matching = sorted(
        (pack for pack in packs if pack.template == template),
        key=lambda pack: pack.scenario_number,
    )
    if not matching:
        return None
    return matching[seed % len(matching)]


def evidence_pack_version(packs: Iterable[FrozenEvidencePack]) -> str:
    """Return a stable version hash for the current evidence-pack set."""

    payload = [
        {
            "evidence_id": pack.evidence_id,
            "sha256": pack.sha256,
            "match_type": pack.match_type,
        }
        for pack in sorted(packs, key=lambda item: item.evidence_id)
    ]
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return digest[:12]


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "scenario"


def _build_plan_only_manifest(
    specs: Iterable[ScenarioPaperSpec],
) -> list[PaperManifestEntry]:
    entries: list[PaperManifestEntry] = []
    for spec in specs:
        slug = spec.slug
        digest = hashlib.sha256(
            json.dumps(
                {
                    "scenario_number": spec.scenario_number,
                    "scenario_title": spec.scenario_title,
                    "claim": spec.claim,
                    "key_technique": spec.key_technique,
                },
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        entries.append(
            PaperManifestEntry(
                id=spec.scenario_number,
                field=spec.field,
                scenario_title=spec.scenario_title,
                download_folder=f"data/papers/{spec.field}/{slug}",
                requested_paper_title=spec.scenario_title,
                downloaded_paper_title=spec.scenario_title,
                planned_reference_title=spec.scenario_title,
                match_type="plan_only",
                status="synthetic",
                source_url=f"training-plan://{slug}",
                sha256=digest,
            )
        )
    return entries


__all__ = [
    "DEFAULT_PAPER_MANIFEST_PATH",
    "DEFAULT_TRAINING_PLAN_PATH",
    "FIELD_TO_TEMPLATE_MAP",
    "FrozenEvidencePack",
    "PaperManifestEntry",
    "ScenarioPaperSpec",
    "build_frozen_evidence_packs",
    "evidence_pack_version",
    "load_frozen_evidence_packs",
    "load_paper_manifest",
    "parse_training_plan",
    "select_evidence_pack",
]
