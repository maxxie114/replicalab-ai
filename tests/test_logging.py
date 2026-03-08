"""Tests for replicalab.utils.logging (MOD 07 + JDG 07)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from replicalab.models import (
    ConversationEntry,
    EpisodeLog,
    EpisodeState,
    RewardBreakdown,
)
from replicalab.utils.logging import (
    append_reward_csv,
    append_reward_jsonl,
    load_episode_log,
    log_episode_reward,
    write_episode_log,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_episode_log(episode_id: str = "test-ep-001") -> EpisodeLog:
    return EpisodeLog(
        episode_id=episode_id,
        seed=42,
        scenario_template="math_reasoning",
        difficulty="easy",
        final_state=EpisodeState(
            seed=42,
            scenario_template="math_reasoning",
            difficulty="easy",
            paper_title="Test Title",
            paper_hypothesis="Test Hypothesis",
            paper_method="Test Method",
            paper_key_finding="Test Finding",
            experiment_goal="Test Goal",
            round_number=2,
            max_rounds=6,
            done=True,
            agreement_reached=True,
            reward=5.0,
            rigor_score=0.8,
            feasibility_score=0.7,
            fidelity_score=0.9,
        ),
        transcript=[
            ConversationEntry(
                role="scientist",
                message="Proposing protocol.",
                round_number=1,
                action_type="propose_protocol",
            ),
            ConversationEntry(
                role="lab_manager",
                message="Feasible.",
                round_number=1,
                action_type="report_feasibility",
            ),
        ],
        reward_breakdown=RewardBreakdown(
            rigor=0.8,
            feasibility=0.7,
            fidelity=0.9,
        ),
        total_reward=5.0,
        rounds_used=2,
        agreement_reached=True,
        judge_notes="All checks passed.",
        verdict="accept",
    )


# ---------------------------------------------------------------------------
# write_episode_log / load_episode_log
# ---------------------------------------------------------------------------


class TestWriteAndLoadEpisodeLog:
    def test_round_trip_lossless(self, tmp_path: Path) -> None:
        log = _make_episode_log()
        path = write_episode_log(log, directory=tmp_path)

        assert path.exists()
        assert path.suffix == ".json"

        loaded = load_episode_log(path)
        assert loaded == log

    def test_filename_uses_episode_id(self, tmp_path: Path) -> None:
        log = _make_episode_log(episode_id="my-episode-42")
        path = write_episode_log(log, directory=tmp_path)
        assert path.name == "my-episode-42.json"

    def test_creates_missing_directories(self, tmp_path: Path) -> None:
        nested = tmp_path / "a" / "b" / "c"
        log = _make_episode_log()
        path = write_episode_log(log, directory=nested)
        assert path.exists()
        assert nested.exists()

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        log1 = _make_episode_log(episode_id="overwrite-test")
        log2 = _make_episode_log(episode_id="overwrite-test")
        # Mutate log2 so it differs
        log2 = log2.model_copy(update={"total_reward": 9.9})

        path1 = write_episode_log(log1, directory=tmp_path)
        path2 = write_episode_log(log2, directory=tmp_path)

        assert path1 == path2
        loaded = load_episode_log(path2)
        assert loaded.total_reward == 9.9

    def test_load_nonexistent_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_episode_log(tmp_path / "does-not-exist.json")

    def test_default_directory_used(self) -> None:
        """write_episode_log with no directory should target the default replays dir."""
        log = _make_episode_log(episode_id="default-dir-test")
        path = write_episode_log(log)
        try:
            assert "replays" in str(path)
            assert path.exists()
            loaded = load_episode_log(path)
            assert loaded == log
        finally:
            # Clean up: remove the file we just wrote to the real replays dir
            path.unlink(missing_ok=True)

    def test_transcript_preserved(self, tmp_path: Path) -> None:
        log = _make_episode_log()
        path = write_episode_log(log, directory=tmp_path)
        loaded = load_episode_log(path)
        assert len(loaded.transcript) == 2
        assert loaded.transcript[0].role == "scientist"
        assert loaded.transcript[1].role == "lab_manager"

    def test_reward_breakdown_preserved(self, tmp_path: Path) -> None:
        log = _make_episode_log()
        path = write_episode_log(log, directory=tmp_path)
        loaded = load_episode_log(path)
        assert loaded.reward_breakdown is not None
        assert loaded.reward_breakdown.rigor == 0.8
        assert loaded.reward_breakdown.feasibility == 0.7
        assert loaded.reward_breakdown.fidelity == 0.9


# ---------------------------------------------------------------------------
# append_reward_csv
# ---------------------------------------------------------------------------


class TestAppendRewardCsv:
    def test_creates_file_with_header(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "rewards.csv"
        result = append_reward_csv(
            csv_path,
            episode_id="ep-1",
            seed=42,
            scenario_template="math_reasoning",
            difficulty="easy",
            total_reward=5.0,
            rigor=0.8,
            feasibility=0.7,
            fidelity=0.9,
            parsimony=0.95,
            efficiency_bonus=0.4,
            penalty_total=0.1,
            rounds_used=2,
            agreement_reached=True,
            verdict="accept",
        )

        assert result == csv_path
        assert csv_path.exists()

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["episode_id"] == "ep-1"
        assert rows[0]["seed"] == "42"
        assert rows[0]["total_reward"] == "5.0"
        assert rows[0]["agreement_reached"] == "True"

    def test_v2_columns_present(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "rewards.csv"
        append_reward_csv(
            csv_path,
            episode_id="ep-v2",
            parsimony=0.85,
            efficiency_bonus=0.6,
            communication_bonus=0.0,
            penalty_total=0.2,
            verdict="accept",
        )

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        row = rows[0]
        assert row["parsimony"] == "0.85"
        assert row["efficiency_bonus"] == "0.6"
        assert row["communication_bonus"] == "0.0"
        assert row["penalty_total"] == "0.2"
        assert row["verdict"] == "accept"

    def test_appends_multiple_rows(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "rewards.csv"

        for i in range(3):
            append_reward_csv(
                csv_path,
                episode_id=f"ep-{i}",
                seed=i,
                total_reward=float(i),
            )

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        assert [r["episode_id"] for r in rows] == ["ep-0", "ep-1", "ep-2"]

    def test_no_duplicate_headers(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "rewards.csv"

        append_reward_csv(csv_path, episode_id="a")
        append_reward_csv(csv_path, episode_id="b")

        lines = csv_path.read_text(encoding="utf-8").strip().split("\n")
        header_count = sum(1 for line in lines if line.startswith("episode_id"))
        assert header_count == 1

    def test_csv_header_has_all_expected_columns(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "rewards.csv"
        append_reward_csv(csv_path, episode_id="hdr")

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            _ = list(reader)
            assert reader.fieldnames is not None
            cols = set(reader.fieldnames)

        expected = {
            "episode_id", "seed", "scenario_template", "difficulty",
            "total_reward", "rigor", "feasibility", "fidelity",
            "parsimony", "efficiency_bonus", "communication_bonus",
            "penalty_total", "rounds_used", "agreement_reached", "verdict",
        }
        assert cols == expected


# ---------------------------------------------------------------------------
# append_reward_jsonl (JDG 07)
# ---------------------------------------------------------------------------


class TestAppendRewardJsonl:
    def test_creates_file_with_one_record(self, tmp_path: Path) -> None:
        jsonl_path = tmp_path / "rewards.jsonl"
        result = append_reward_jsonl(
            jsonl_path,
            episode_id="ep-j1",
            seed=7,
            scenario_template="ml_benchmark",
            difficulty="hard",
            total_reward=3.5,
            breakdown=RewardBreakdown(
                rigor=0.6,
                feasibility=0.8,
                fidelity=0.7,
                parsimony=0.9,
                efficiency_bonus=0.3,
                penalties={"invalid_tool_use": 0.1},
            ),
            rounds_used=4,
            agreement_reached=True,
            verdict="accept",
            judge_notes="Good protocol.",
            bounded_tool_metrics={"search_evidence": 2, "run_code_check": 1},
        )

        assert result == jsonl_path
        assert jsonl_path.exists()

        lines = jsonl_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        rec = json.loads(lines[0])
        assert rec["episode_id"] == "ep-j1"
        assert rec["rigor"] == 0.6
        assert rec["parsimony"] == 0.9
        assert rec["penalties"] == {"invalid_tool_use": 0.1}
        assert rec["penalty_total"] == 0.1
        assert rec["bounded_tool_metrics"]["search_evidence"] == 2
        assert rec["verdict"] == "accept"
        assert rec["judge_notes"] == "Good protocol."

    def test_appends_multiple_records(self, tmp_path: Path) -> None:
        jsonl_path = tmp_path / "rewards.jsonl"
        for i in range(3):
            append_reward_jsonl(jsonl_path, episode_id=f"ep-{i}", seed=i)

        lines = jsonl_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3
        ids = [json.loads(line)["episode_id"] for line in lines]
        assert ids == ["ep-0", "ep-1", "ep-2"]

    def test_default_breakdown_used_when_none(self, tmp_path: Path) -> None:
        jsonl_path = tmp_path / "rewards.jsonl"
        append_reward_jsonl(jsonl_path, episode_id="no-bd")

        rec = json.loads(jsonl_path.read_text(encoding="utf-8").strip())
        assert rec["rigor"] == 0.0
        assert rec["feasibility"] == 0.0
        assert rec["fidelity"] == 0.0
        assert rec["parsimony"] == 1.0
        assert rec["penalties"] == {}
        assert rec["bounded_tool_metrics"] == {}

    def test_penalties_dict_preserved(self, tmp_path: Path) -> None:
        jsonl_path = tmp_path / "rewards.jsonl"
        bd = RewardBreakdown(
            rigor=0.5,
            feasibility=0.5,
            fidelity=0.5,
            penalties={"unsupported_claim": 0.05, "invalid_tool_use": 0.1},
        )
        append_reward_jsonl(jsonl_path, breakdown=bd)

        rec = json.loads(jsonl_path.read_text(encoding="utf-8").strip())
        assert rec["penalties"]["unsupported_claim"] == 0.05
        assert rec["penalties"]["invalid_tool_use"] == 0.1
        assert rec["penalty_total"] == pytest.approx(0.15)

    def test_creates_missing_directories(self, tmp_path: Path) -> None:
        nested = tmp_path / "a" / "b" / "rewards.jsonl"
        append_reward_jsonl(nested, episode_id="nested")
        assert nested.exists()


# ---------------------------------------------------------------------------
# log_episode_reward (JDG 07 convenience wrapper)
# ---------------------------------------------------------------------------


class TestLogEpisodeReward:
    def test_writes_both_csv_and_jsonl(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "rewards.csv"
        jsonl_path = tmp_path / "rewards.jsonl"
        bd = RewardBreakdown(
            rigor=0.7,
            feasibility=0.9,
            fidelity=0.8,
            parsimony=0.95,
            efficiency_bonus=0.5,
            penalties={"stalling": 0.05},
        )

        csv_out, jsonl_out = log_episode_reward(
            episode_id="dual-1",
            seed=99,
            scenario_template="finance_trading",
            difficulty="medium",
            total_reward=4.2,
            breakdown=bd,
            rounds_used=3,
            agreement_reached=True,
            verdict="accept",
            judge_notes="Solid plan.",
            bounded_tool_metrics={"search_evidence": 1},
            csv_path=csv_path,
            jsonl_path=jsonl_path,
        )

        assert csv_out == csv_path
        assert jsonl_out == jsonl_path

        # CSV check
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["episode_id"] == "dual-1"
        assert rows[0]["parsimony"] == "0.95"
        assert rows[0]["verdict"] == "accept"

        # JSONL check
        rec = json.loads(jsonl_path.read_text(encoding="utf-8").strip())
        assert rec["episode_id"] == "dual-1"
        assert rec["penalties"] == {"stalling": 0.05}
        assert rec["bounded_tool_metrics"] == {"search_evidence": 1}
        assert rec["judge_notes"] == "Solid plan."

    def test_deterministic_across_calls(self, tmp_path: Path) -> None:
        bd = RewardBreakdown(rigor=0.6, feasibility=0.7, fidelity=0.8)
        kwargs = dict(
            episode_id="det",
            seed=1,
            scenario_template="math_reasoning",
            difficulty="easy",
            total_reward=3.0,
            breakdown=bd,
            rounds_used=2,
            agreement_reached=False,
            verdict="timeout",
        )

        p1 = tmp_path / "run1"
        p1.mkdir()
        log_episode_reward(**kwargs, csv_path=p1 / "r.csv", jsonl_path=p1 / "r.jsonl")

        p2 = tmp_path / "run2"
        p2.mkdir()
        log_episode_reward(**kwargs, csv_path=p2 / "r.csv", jsonl_path=p2 / "r.jsonl")

        assert (p1 / "r.csv").read_text() == (p2 / "r.csv").read_text()
        assert (p1 / "r.jsonl").read_text() == (p2 / "r.jsonl").read_text()

    def test_default_breakdown_when_none(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "rewards.csv"
        jsonl_path = tmp_path / "rewards.jsonl"

        log_episode_reward(
            episode_id="no-bd",
            csv_path=csv_path,
            jsonl_path=jsonl_path,
        )

        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert rows[0]["parsimony"] == "1.0"

        rec = json.loads(jsonl_path.read_text(encoding="utf-8").strip())
        assert rec["parsimony"] == 1.0
        assert rec["penalties"] == {}
