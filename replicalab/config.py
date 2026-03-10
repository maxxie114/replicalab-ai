"""Shared configuration constants for ReplicaLab.

MOD 12 centralizes the small set of repo-wide defaults that were previously
scattered across the stub server and scenario builders. Future environment,
scoring, and client modules should import from here instead of introducing
new magic numbers.
"""

from __future__ import annotations

import os


def _get_env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _get_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default

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


def get_scientist_runtime() -> str:
    configured = os.environ.get("REPLICALAB_SCIENTIST_RUNTIME")
    if configured:
        return configured.strip().lower()
    return "anthropic" if os.environ.get("ANTHROPIC_API_KEY") else "baseline"


def get_scientist_model() -> str:
    return os.environ.get("REPLICALAB_SCIENTIST_MODEL", "claude-haiku-4-5-20251001")


def get_scientist_ollama_model() -> str:
    return os.environ.get("REPLICALAB_SCIENTIST_OLLAMA_MODEL", "glm-5:cloud")


def get_scientist_ollama_base_url() -> str:
    return os.environ.get(
        "REPLICALAB_SCIENTIST_OLLAMA_BASE_URL",
        "http://127.0.0.1:11434/api/chat",
    )


def get_scientist_max_retries() -> int:
    return _get_env_int("REPLICALAB_SCIENTIST_MAX_RETRIES", 2)


def get_scientist_max_completion_tokens() -> int:
    return _get_env_int("REPLICALAB_SCIENTIST_MAX_COMPLETION_TOKENS", 450)


def get_scientist_temperature() -> float:
    return _get_env_float("REPLICALAB_SCIENTIST_TEMPERATURE", 0.0)


def get_scientist_timeout_seconds() -> float:
    return _get_env_float("REPLICALAB_SCIENTIST_TIMEOUT_SECONDS", 60.0)

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

# LLM judge toggle
LLM_JUDGE_ENABLED = os.environ.get("REPLICALAB_LLM_JUDGE_ENABLED", "0") == "1"

# Adaptive reward shaping — later rounds carry heavier penalties
ADAPTIVE_SHAPING_ENABLED = os.environ.get("REPLICALAB_ADAPTIVE_SHAPING", "1") == "1"

# Domain-specific scoring emphasis
DOMAIN_WEIGHTS: dict[str, dict[str, float]] = {
    "mathematics": {"rigor": 0.40, "feasibility": 0.25, "fidelity": 0.35},
    "machine_learning": {"rigor": 0.25, "feasibility": 0.40, "fidelity": 0.35},
    "finance_trading": {"rigor": 0.30, "feasibility": 0.35, "fidelity": 0.35},
}
DEFAULT_DOMAIN_WEIGHTS: dict[str, float] = {
    "rigor": 0.33, "feasibility": 0.34, "fidelity": 0.33,
}

# Communication bonus cap
MAX_COMMUNICATION_BONUS = 0.5


def get_judge_runtime() -> str:
    return os.environ.get("REPLICALAB_JUDGE_RUNTIME", "deterministic").strip().lower()


def get_judge_model() -> str:
    return os.environ.get(
        "REPLICALAB_JUDGE_MODEL", "google/gemini-2.5-pro-preview-03-25",
    )


def get_openrouter_api_key() -> str:
    return os.environ.get("OPENROUTER_API_KEY", "")


def get_openrouter_base_url() -> str:
    return os.environ.get(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1",
    )
