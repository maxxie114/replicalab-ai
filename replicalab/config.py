"""Shared configuration constants for ReplicaLab.

MOD 12 centralizes the small set of repo-wide defaults that were previously
scattered across the stub server and scenario builders. Future environment,
scoring, and client modules should import from here instead of introducing
new magic numbers.
"""

from __future__ import annotations

import os

DEFAULT_SCENARIO_TEMPLATE = "math_reasoning"
DEFAULT_DIFFICULTY = "easy"

MAX_ROUNDS = 6
MAX_BUDGET = 5000.0

TIMEOUT_SECONDS = 300
ROUND_TIME_LIMIT_SECONDS = 300

SESSION_TTL_SECONDS = TIMEOUT_SECONDS
WS_IDLE_TIMEOUT_SECONDS = TIMEOUT_SECONDS

STUB_ACCEPT_REWARD = 5.0

API_HOST = "0.0.0.0"
API_PORT = 7860

LOG_LEVEL = os.environ.get("REPLICALAB_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

ORACLE_ENABLED = os.environ.get("REPLICALAB_ORACLE_ENABLED", "0") == "1"
ORACLE_EVENTS_ENABLED = os.environ.get("REPLICALAB_ORACLE_EVENTS_ENABLED", "0") == "1"
ORACLE_POST_MORTEM_ENABLED = (
    os.environ.get("REPLICALAB_ORACLE_POST_MORTEM_ENABLED", "0") == "1"
)
ORACLE_MODEL = os.environ.get("REPLICALAB_ORACLE_MODEL", "frontier-oracle")
ORACLE_SCENARIO_CACHE_DIR = os.environ.get(
    "REPLICALAB_ORACLE_SCENARIO_CACHE_DIR",
    ".scenario_cache",
)

# Deterministic reward shaping constants.
STEP_PROTOCOL_DELTA_SCALE = 0.25
STEP_PROTOCOL_DELTA_CAP = 0.3
STEP_INFO_GAIN_BONUS = 0.05
STEP_INFO_GAIN_CAP = 0.15
STEP_MOMENTUM_BONUS = 0.05
STEP_STALLING_PENALTY = 0.05
STEP_REPEATED_QUESTION_PENALTY = 0.03
STEP_REGRESSION_PENALTY = 0.1
STEP_CONTRADICTION_PENALTY = 0.05
STEP_INVALID_ACTION_PENALTY = 0.1
STEP_HALLUCINATION_PENALTY = 0.05
TERMINAL_TIMEOUT_PENALTY = 0.2
TERMINAL_NO_AGREEMENT_PENALTY = 0.1
