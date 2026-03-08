#!/usr/bin/env python3
"""Run a single ReplicaLab episode locally and dump logs.

OBS 07 — Quick local smoke-test script.  Resets the environment with a
given seed/scenario/difficulty, runs a baseline propose→accept sequence,
and writes the episode replay JSON + reward CSV/JSONL to the default
output directories.

Usage:
    python -m scripts.run_episode
    python -m scripts.run_episode --seed 42 --scenario ml_benchmark --difficulty hard
    python -m scripts.run_episode --max-rounds 3
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is importable when run as a script
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from replicalab.config import DEFAULT_DIFFICULTY, DEFAULT_SCENARIO_TEMPLATE
from replicalab.env.replicalab_env import ReplicaLabEnv
from replicalab.models import ScientistAction
from replicalab.scenarios import generate_scenario
from replicalab.utils.logging import log_episode_reward, write_episode_log


def _build_propose_action(env: ReplicaLabEnv, seed: int, scenario: str, difficulty: str) -> ScientistAction:
    """Build a baseline propose_protocol action from the scenario pack."""
    pack = generate_scenario(seed=seed, template=scenario, difficulty=difficulty)
    lab = pack.lab_manager_observation
    spec = pack.hidden_reference_spec
    return ScientistAction(
        action_type="propose_protocol",
        sample_size=10,
        controls=["baseline", "ablation"],
        technique=spec.summary[:60] if spec.summary else "replication_plan",
        duration_days=max(1, min(2, lab.time_limit_days)),
        required_equipment=list(lab.equipment_available[:1]) if lab.equipment_available else [],
        required_reagents=list(lab.reagents_in_stock[:1]) if lab.reagents_in_stock else [],
        questions=[],
        rationale=(
            f"Plan addresses: {', '.join(spec.required_elements[:2])}. "
            f"Target metric: {spec.target_metric}. "
            f"Target value: {spec.target_value}. "
            "Stay within budget and schedule."
        ),
    )


def _build_accept_action() -> ScientistAction:
    return ScientistAction(
        action_type="accept",
        sample_size=0,
        controls=[],
        technique="",
        duration_days=0,
        required_equipment=[],
        required_reagents=[],
        questions=[],
        rationale="",
    )


def run_episode(
    seed: int = 0,
    scenario: str = DEFAULT_SCENARIO_TEMPLATE,
    difficulty: str = DEFAULT_DIFFICULTY,
    max_rounds: int | None = None,
) -> None:
    """Run one episode and persist outputs."""
    env = ReplicaLabEnv()
    obs = env.reset(seed=seed, scenario=scenario, difficulty=difficulty)
    episode_id = env.episode_id()

    print(f"Episode {episode_id} | seed={seed} scenario={scenario} difficulty={difficulty}")
    print(f"  Paper: {obs.scientist.paper_title}")

    propose_action = _build_propose_action(env, seed, scenario, difficulty)
    total_steps = 0
    invalid_count = 0

    # Step 1: propose
    result = env.step(propose_action)
    total_steps += 1
    if result.info.error:
        invalid_count += 1
    print(f"  Round 1 propose | reward={result.reward:.4f} done={result.done}")

    if not result.done:
        # Step 2: accept
        result = env.step(_build_accept_action())
        total_steps += 1
        if result.info.error:
            invalid_count += 1
        print(f"  Round 2 accept  | reward={result.reward:.4f} done={result.done}")

    state = env.state()
    info = result.info

    # Build and persist episode log
    from replicalab.models import EpisodeLog

    episode_log = EpisodeLog(
        episode_id=episode_id,
        seed=state.seed,
        scenario_template=state.scenario_template,
        difficulty=state.difficulty,
        final_state=state,
        transcript=list(state.conversation_history),
        reward_breakdown=info.reward_breakdown,
        total_reward=state.reward,
        rounds_used=state.round_number,
        agreement_reached=info.agreement_reached,
        judge_notes=info.judge_notes or "",
        verdict=info.verdict or "",
        top_failure_reasons=list(info.top_failure_reasons),
        invalid_action_count=invalid_count,
        invalid_action_rate=round(invalid_count / total_steps, 6) if total_steps else 0.0,
    )

    replay_path = write_episode_log(episode_log)
    csv_path, jsonl_path = log_episode_reward(
        episode_id=episode_id,
        seed=state.seed,
        scenario_template=state.scenario_template,
        difficulty=state.difficulty,
        total_reward=state.reward,
        breakdown=info.reward_breakdown,
        rounds_used=state.round_number,
        agreement_reached=info.agreement_reached,
        verdict=info.verdict or "",
        judge_notes=info.judge_notes or "",
    )

    print(f"\n  Verdict: {info.verdict}")
    print(f"  Total reward: {state.reward:.4f}")
    print(f"  Agreement: {info.agreement_reached}")
    print(f"  Invalid actions: {invalid_count}/{total_steps}")
    print(f"\n  Replay JSON:  {replay_path}")
    print(f"  Reward CSV:   {csv_path}")
    print(f"  Reward JSONL: {jsonl_path}")

    env.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single ReplicaLab episode")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO_TEMPLATE)
    parser.add_argument("--difficulty", default=DEFAULT_DIFFICULTY)
    parser.add_argument("--max-rounds", type=int, default=None)
    args = parser.parse_args()
    run_episode(
        seed=args.seed,
        scenario=args.scenario,
        difficulty=args.difficulty,
        max_rounds=args.max_rounds,
    )


if __name__ == "__main__":
    main()
