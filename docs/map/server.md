# Server Map - `server/app.py`

> FastAPI backend with REST + WebSocket endpoints. The normal path now uses
> the real `ReplicaLabEnv`; `_StubEnv` remains only as a fallback if the env
> package cannot be imported.
>
> **Tasks implemented:** API 01-09, 13, 15

## Environment path

### `ReplicaLabEnv`
Primary environment implementation imported from
`replicalab.env.replicalab_env`.

### `_StubEnv`
Legacy fallback kept so the server can still boot if the real env import
fails. It is no longer the intended local or Docker runtime.

### `_make_env()`
Factory that prefers `ReplicaLabEnv` and falls back to `_StubEnv` only on
import failure.

## REST endpoints

### `GET /health`
Returns a liveness payload. When the real env path is active, the response
includes `env: "real"`.

### `POST /reset`
Starts a new episode and returns:

- `session_id`
- `episode_id`
- typed `Observation`

### `POST /step`
Submits a typed `ScientistAction` and returns `StepResult`.

When `done=true`, the terminal `StepResult` is also used to build the replay
log so `reward_breakdown`, `judge_notes`, and `verdict` stay aligned with the
real env result.

### `GET /scenarios`
Returns the available scenario families and supported difficulties.

### `GET /replay/{episode_id}`
Returns the stored `EpisodeLog` for a completed episode or 404 if not found.

## WebSocket endpoint

### `WS /ws`
Per-connection isolated environment session supporting:

- `reset`
- `step`
- `ping`

Idle timeout and disconnect cleanup are implemented and verified.

## Session management

| Store | Purpose |
| --- | --- |
| `_sessions` | Active REST sessions |
| `_replay_store` | Completed episode logs |

## Key helpers

| Function | Purpose |
| --- | --- |
| `_build_episode_log(episode_id, state, result)` | Build replay log from final state and terminal step result |
| `_touch(session_id)` | Refresh REST session last-active timestamp |
| `_cleanup_stale_sessions()` | Remove expired REST sessions |

## Current deployment state

- Local OpenEnv validation passes
- Local Docker build and run verification passes
- HF Spaces metadata is present in the root `README.md` and root `Dockerfile`
- Live hosted verification remains `API 10`
