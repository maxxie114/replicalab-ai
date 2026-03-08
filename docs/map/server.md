# Server Map — `server/app.py`

> FastAPI backend with REST + WebSocket endpoints and stub environment.
>
> **Tasks implemented:** API 01-04, 06 (partial)

## Environment

### `_StubEnv`
Minimal environment stub used until the real `ReplicaLabEnv` is implemented (ENV 01-11).

**State:**
| Attribute | Type | Purpose |
|-----------|------|---------|
| `_state` | `EpisodeState` | Full episode state |
| `_episode_id` | `str` | UUID for this episode |
| `_scenario_pack` | `NormalizedScenarioPack \| None` | Stored for lab manager pipeline |
| `_logs` | `list[ConversationEntry]` | Conversation transcript |

**Methods:**

| Method | Returns | Behavior |
|--------|---------|----------|
| `reset(seed, scenario, difficulty)` | `Observation` | Generates scenario, builds initial observations |
| `step(action: ScientistAction)` | `StepResult` | Processes scientist action, runs lab manager pipeline |
| `state()` | `EpisodeState` | Returns current state snapshot |
| `episode_id()` | `str` | Returns episode UUID |
| `close()` | `None` | No-op |

**Lab Manager Integration (AGT 07):**
The `_lab_manager_action()` method runs the full deterministic pipeline:
1. `check_feasibility(protocol, scenario_pack)` → `FeasibilityCheckResult`
2. `suggest_alternative(protocol, check_result, scenario_pack)` → `AlternativeSuggestion | None`
3. `compose_lab_manager_response(check_result, suggestion)` → `LabManagerAction`

**Termination logic:**
- Episode ends (`done=True`) when `agreement_reached=True` (both agents accept)
- `agreement_reached` when lab manager action_type is `accept` (2-round stub logic)
- On termination: reward = `STUB_ACCEPT_REWARD` (5.0)

### `_make_env() -> _StubEnv`
Factory that tries to import `ReplicaLabEnv` from `replicalab.env`, falls back to `_StubEnv`.

## REST Endpoints

### `GET /health`
Returns `{"status": "ok"}`.

### `POST /reset`
**Request:** `ResetRequest`
| Field | Type | Default |
|-------|------|---------|
| `seed` | `int \| None` | `None` (random) |
| `scenario` | `str` | `DEFAULT_SCENARIO_TEMPLATE` |
| `difficulty` | `str` | `DEFAULT_DIFFICULTY` |
| `session_id` | `str \| None` | `None` (auto-generated) |

**Response:** `ResetResponse`
| Field | Type |
|-------|------|
| `session_id` | `str` |
| `episode_id` | `str` |
| `observation` | `Observation` |

### `POST /step`
**Request:** `StepRequest`
| Field | Type |
|-------|------|
| `session_id` | `str` |
| `action` | `ScientistAction` |

**Response:** `StepResult` (observation, reward, done, info)

When `done=True`, the episode log is stored in `_replay_store`.

### `GET /scenarios`
Returns `available_scenario_families()` — list of families with difficulties.

### `GET /replay/{episode_id}`
Returns `EpisodeLog` for a completed episode, or 404 if not found.

## WebSocket Endpoint

### `WS /ws`
Bidirectional session with JSON messages.

**Client → Server messages:**
| Type | Payload | Behavior |
|------|---------|----------|
| `reset` | `{seed, scenario, difficulty}` | Creates env, returns initial state |
| `step` | `{action: ScientistAction}` | Steps env, returns result |
| `ping` | — | Returns `{"type": "pong"}` |

**Server → Client messages:**
| Type | Payload |
|------|---------|
| `state` | `{observation, episode_id}` |
| `step_result` | `StepResult.info.model_dump()` |
| `pong` | `{}` |
| `error` | `{message}` |

## Session Management

| Store | Type | Purpose |
|-------|------|---------|
| `_sessions` | `dict[str, dict]` | Active REST sessions (env + last_active) |
| `_replay_store` | `dict[str, EpisodeLog]` | Completed episode logs |

**Cleanup:** Background task runs every 60s, removes sessions older than `SESSION_TTL_SECONDS` (300s).

## Helper Functions

| Function | Purpose |
|----------|---------|
| `_reward_breakdown_from_state(state)` | Extract RewardBreakdown from EpisodeState scores |
| `_build_episode_log(episode_id, state)` | Build EpisodeLog from final state |
| `_touch(session_id)` | Update last_active timestamp |
| `_cleanup_stale_sessions()` | Remove expired sessions |

## Dependencies

```python
from replicalab.agents import check_feasibility, compose_lab_manager_response, suggest_alternative
from replicalab.config import API_HOST, API_PORT, DEFAULT_DIFFICULTY, ...
from replicalab.models import (ConversationEntry, EpisodeLog, EpisodeState, LabManagerAction,
                                Observation, Protocol, RewardBreakdown, ScientistAction, StepInfo, StepResult, ...)
from replicalab.scenarios import NormalizedScenarioPack, available_scenario_families, generate_scenario
```
