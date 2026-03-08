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
