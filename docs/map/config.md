# Config Map — `replicalab/config.py`

> Shared constants used across the entire project.

## Constants

| Constant | Value | Used by |
|----------|-------|---------|
| `DEFAULT_SCENARIO_TEMPLATE` | `"math_reasoning"` | server (reset defaults) |
| `DEFAULT_DIFFICULTY` | `"easy"` | server (reset defaults) |
| `MAX_ROUNDS` | `6` | scenarios (observation.max_rounds), server |
| `MAX_BUDGET` | `5000.0` | scenarios (budget_total base) |
| `TIMEOUT_SECONDS` | `300` | server (session TTL base) |
| `ROUND_TIME_LIMIT_SECONDS` | `300` | server (per-round timeout) |
| `SESSION_TTL_SECONDS` | `300` (= TIMEOUT_SECONDS) | server (session cleanup) |
| `WS_IDLE_TIMEOUT_SECONDS` | `300` (= TIMEOUT_SECONDS) | server (WebSocket idle) |
| `STUB_ACCEPT_REWARD` | `5.0` | server (_StubEnv reward on accept) |
| `API_HOST` | `"0.0.0.0"` | server (uvicorn bind) |
| `API_PORT` | `7860` | server (uvicorn port) |

## Who Imports This

| Consumer | Constants used |
|----------|---------------|
| `scenarios/templates.py` | `MAX_BUDGET`, `MAX_ROUNDS` |
| `server/app.py` | `API_HOST`, `API_PORT`, `DEFAULT_SCENARIO_TEMPLATE`, `DEFAULT_DIFFICULTY`, `MAX_ROUNDS`, `ROUND_TIME_LIMIT_SECONDS`, `SESSION_TTL_SECONDS`, `STUB_ACCEPT_REWARD`, `WS_IDLE_TIMEOUT_SECONDS` |
| `tests/test_config.py` | All constants (validation tests) |

## Project Config — `pyproject.toml`

| Key | Value |
|-----|-------|
| Name | `replicalab` |
| Version | `0.1.0` |
| Python | `>=3.10` |
| License | MIT |

### Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `pydantic` | `>=2.7,<3.0` | Data validation |
| `fastapi` | `>=0.115,<1.0` | REST API framework |
| `uvicorn[standard]` | `>=0.34,<1.0` | ASGI server |
| `websockets` | `>=15.0,<17.0` | WebSocket support |
| `openenv-core[core]` | `>=0.2.1,<0.3.0` | Environment base (not yet used) |

### Dev Dependencies
| Package | Purpose |
|---------|---------|
| `pytest` | Testing |
| `pytest-cov` | Coverage |
| `pytest-asyncio` | Async test support |
| `httpx` | HTTP client for API tests |
| `ruff` | Linting |
| `mypy` | Type checking |

### Entry Point
```
[project.scripts]
server = "server.app:main"
```
