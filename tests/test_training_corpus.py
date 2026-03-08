"""Tests for the frozen paper corpus and evidence-pack builder."""

from __future__ import annotations

from replicalab.training.corpus import (
    build_frozen_evidence_packs,
    evidence_pack_version,
    load_frozen_evidence_packs,
    load_paper_manifest,
    parse_training_plan,
    select_evidence_pack,
)


def test_training_plan_parses_all_50_scenarios() -> None:
    specs = parse_training_plan()

    assert len(specs) == 50
    assert specs[0].scenario_number == 1
    assert specs[-1].scenario_number == 50


def test_frozen_evidence_packs_cover_the_manifest() -> None:
    packs = load_frozen_evidence_packs()

    assert len(packs) == 50
    assert all(pack.pdf_path.endswith("paper.pdf") for pack in packs)
    assert evidence_pack_version(packs)


def test_select_evidence_pack_is_stable_for_supported_templates() -> None:
    packs = load_frozen_evidence_packs()

    first = select_evidence_pack(packs, template="ml_benchmark", seed=7)
    second = select_evidence_pack(packs, template="ml_benchmark", seed=7)

    assert first is not None
    assert second is not None
    assert first.evidence_id == second.evidence_id


def test_manifest_falls_back_to_plan_only_entries_when_local_corpus_is_missing(tmp_path) -> None:
    manifest = load_paper_manifest(path=tmp_path / "missing-manifest.json")

    assert len(manifest) == 50
    assert all(entry.match_type == "plan_only" for entry in manifest)
    assert all(entry.status == "synthetic" for entry in manifest)


def test_plan_only_manifest_still_builds_frozen_evidence_packs(tmp_path) -> None:
    packs = build_frozen_evidence_packs(
        manifest_entries=load_paper_manifest(path=tmp_path / "missing-manifest.json")
    )

    assert len(packs) == 50
    assert all(pack.match_type == "plan_only" for pack in packs)
    assert all(pack.pdf_path.endswith("paper.pdf") for pack in packs)
