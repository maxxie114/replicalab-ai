"""Tests for replicalab.utils.logging (MOD 07)."""

from __future__ import annotations

import csv
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
    load_episode_log,
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
            rounds_used=2,
            agreement_reached=True,
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
