"""ReplicaLab FastAPI + WebSocket server.

Serves the ReplicaLab environment over REST and WebSocket.
Each client session gets an isolated environment instance.

REST endpoints:
  GET  /health                    -- liveness check
  POST /reset                     -- start new episode, returns observation + session_id
  POST /step                      -- submit action, returns StepResult
  GET  /scenarios                 -- list available scenario families and difficulties
  GET  /replay/{episode_id}       -- fetch completed episode log

WebSocket:
  WS   /ws                        -- bidirectional session; send reset/step messages

Run locally:
  uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from replicalab.agents import (
    check_feasibility,
    compose_lab_manager_response,
    suggest_alternative,
)
from replicalab.config import (
    API_HOST,
    API_PORT,
    DEFAULT_DIFFICULTY,
    DEFAULT_SCENARIO_TEMPLATE,
    LOG_FORMAT,
    LOG_LEVEL,
    SESSION_TTL_SECONDS,
    STUB_ACCEPT_REWARD,
    WS_IDLE_TIMEOUT_SECONDS,
)
from replicalab.scenarios import (
    NormalizedScenarioPack,
    available_scenario_families,
    generate_scenario,
)
from replicalab.models import (
    ConversationEntry,
    EpisodeLog,
    EpisodeState,
    LabManagerAction,
    LabManagerObservation,
    Observation,
    Protocol,
    RewardBreakdown,
    ScientistAction,
    ScientistObservation,
    StepInfo,
    StepResult,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
)
log = logging.getLogger("replicalab.server")

# ---------------------------------------------------------------------------
# Environment factory — prefer ReplicaLabEnv, retain _StubEnv only as fallback
# ---------------------------------------------------------------------------

try:
    from replicalab.env.replicalab_env import ReplicaLabEnv  # type: ignore

    _HAS_REAL_ENV = True
    log.info("Using real ReplicaLabEnv")
except ImportError:
    _HAS_REAL_ENV = False
    log.warning("ReplicaLabEnv not found — using _StubEnv (replace when Person A ships env)")


def _build_episode_log(
    episode_id: str,
    state: EpisodeState,
    result: StepResult,
) -> EpisodeLog:
    """Build an EpisodeLog from the terminal StepResult.

    Uses the real reward_breakdown, judge_notes, and verdict from the env
    instead of rebuilding from state with stale stub values.
    """
    info = result.info
    return EpisodeLog(
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
    )


class _StubEnv:
    """Minimal stub that returns valid Pydantic model instances.

    Swap out for the real ReplicaLabEnv once replicalab/env/replicalab_env.py
    is implemented by Person A. The interface is identical.
    """

    def __init__(self) -> None:
        self._state = EpisodeState()
        self._logs: list[ConversationEntry] = []
        self._episode_id: str = ""
        self._scenario_pack: Optional[NormalizedScenarioPack] = None

    # ── public interface (matches ReplicaLabEnv) ──────────────────────────

    def reset(
        self,
        seed: int = 0,
        scenario: str = DEFAULT_SCENARIO_TEMPLATE,
        difficulty: str = DEFAULT_DIFFICULTY,
    ) -> Observation:
        self._episode_id = str(uuid.uuid4())
        self._logs = []
        pack = generate_scenario(seed=seed, template=scenario, difficulty=difficulty)
        self._scenario_pack = pack
        self._state = EpisodeState(
            seed=seed,
            scenario_template=scenario,
            difficulty=difficulty,
            paper_title=pack.scientist_observation.paper_title,
            paper_hypothesis="Compound X inhibits cell growth at 10 µM",
            paper_method=pack.scientist_observation.paper_method,
            paper_key_finding="IC50 = 8.3 µM",
            experiment_goal=pack.scientist_observation.experiment_goal,
            lab_budget_total=pack.lab_manager_observation.budget_total,
            lab_budget_remaining=pack.lab_manager_observation.budget_remaining,
            lab_equipment=list(pack.lab_manager_observation.equipment_available),
            lab_reagents=["MTT reagent", "DMSO", "cell culture media"],
            lab_staff_count=pack.lab_manager_observation.staff_count,
            lab_time_limit_days=pack.lab_manager_observation.time_limit_days,
            max_rounds=pack.scientist_observation.max_rounds,
            round_number=0,
        )
        self._state.paper_hypothesis = pack.scientist_observation.paper_hypothesis
        self._state.paper_key_finding = pack.scientist_observation.paper_key_finding
        self._state.lab_reagents = list(pack.lab_manager_observation.reagents_in_stock)
        self._state.conversation_history = list(self._logs)
        log.info("Stub reset | episode=%s seed=%d scenario=%s", self._episode_id, seed, scenario)
        return self._make_observation()

    def step(self, action: ScientistAction) -> StepResult:
        self._state.round_number += 1
        proposed_protocol = self._protocol_from_action(action)
        self._logs.append(self._scientist_log_entry(action))
        lab_manager_action = self._lab_manager_action(proposed_protocol)
        self._logs.append(self._lab_manager_log_entry(lab_manager_action))
        self._state.conversation_history = list(self._logs)
        self._state.current_protocol = proposed_protocol
        done = (
            action.action_type == "accept"
            or self._state.round_number >= self._state.max_rounds
        )
        reward = STUB_ACCEPT_REWARD if done and action.action_type == "accept" else 0.0
        if done:
            self._state.done = True
            self._state.agreement_reached = action.action_type == "accept"
            self._state.reward = reward
            if self._state.agreement_reached:
                self._state.rigor_score = 0.8
                self._state.feasibility_score = 0.8
                self._state.fidelity_score = 0.8
        return StepResult(
            observation=self._make_observation(),
            reward=reward,
            done=done,
            info=StepInfo(
                agreement_reached=self._state.agreement_reached,
                error=None,
                reward_breakdown=RewardBreakdown(
                    rigor=self._state.rigor_score,
                    feasibility=self._state.feasibility_score,
                    fidelity=self._state.fidelity_score,
                ) if done else None,
                judge_notes="Stub audit until judge integration lands." if done else None,
                verdict=("accept" if self._state.agreement_reached else "revise") if done else None,
                round=self._state.round_number,
                stub=True,
                episode_id=self._episode_id,
            ),
        )

    def state(self) -> EpisodeState:
        return self._state

    def episode_id(self) -> str:
        return self._episode_id

    def close(self) -> None:
        pass

    # ── internal helpers ──────────────────────────────────────────────────

    def _scientist_log_entry(self, action: ScientistAction) -> ConversationEntry:
        action_type = (
            action.action_type.value
            if hasattr(action.action_type, "value")
            else str(action.action_type)
        )
        message = action.rationale or f"Scientist chose action '{action_type}'."
        return ConversationEntry(
            role="scientist",
            message=message,
            round_number=self._state.round_number,
            action_type=action_type,
        )

    def _lab_manager_log_entry(self, action: LabManagerAction) -> ConversationEntry:
        action_type = (
            action.action_type.value
            if hasattr(action.action_type, "value")
            else str(action.action_type)
        )
        return ConversationEntry(
            role="lab_manager",
            message=action.explanation,
            round_number=self._state.round_number,
            action_type=action_type,
        )

    def _lab_manager_action(self, protocol: Optional[Protocol]) -> LabManagerAction:
        if protocol is None or self._scenario_pack is None:
            return LabManagerAction(
                action_type="report_feasibility",
                feasible=True,
                budget_ok=True,
                equipment_ok=True,
                reagents_ok=True,
                schedule_ok=True,
                staff_ok=True,
                suggested_technique="",
                suggested_sample_size=0,
                suggested_controls=[],
                explanation="No concrete protocol is available to review yet.",
            )

        check_result = check_feasibility(protocol, self._scenario_pack)
        suggestion = suggest_alternative(protocol, check_result, self._scenario_pack)
        return compose_lab_manager_response(check_result, suggestion)

    def _protocol_from_action(self, action: ScientistAction) -> Optional[Protocol]:
        if action.action_type not in {"propose_protocol", "revise_protocol"}:
            return self._state.current_protocol
        return Protocol(
            technique=action.technique,
            sample_size=action.sample_size,
            controls=list(action.controls),
            duration_days=action.duration_days,
            required_equipment=list(action.required_equipment),
            required_reagents=list(action.required_reagents),
            rationale=action.rationale,
        )

    def _make_observation(self) -> Observation:
        s = self._state
        return Observation(
            scientist=ScientistObservation(
                paper_title=s.paper_title,
                paper_hypothesis=s.paper_hypothesis,
                paper_method=s.paper_method,
                paper_key_finding=s.paper_key_finding,
                experiment_goal=s.experiment_goal,
                conversation_history=list(self._logs),
                current_protocol=s.current_protocol,
                round_number=s.round_number,
                max_rounds=s.max_rounds,
            ),
            lab_manager=LabManagerObservation(
                budget_total=s.lab_budget_total,
                budget_remaining=s.lab_budget_remaining,
                equipment_available=list(s.lab_equipment),
                equipment_booked=[],
                reagents_in_stock=list(s.lab_reagents),
                reagents_out_of_stock=[],
                staff_count=s.lab_staff_count,
                time_limit_days=s.lab_time_limit_days,
                safety_restrictions=[],
                conversation_history=list(self._logs),
                current_protocol=s.current_protocol,
                round_number=s.round_number,
                max_rounds=s.max_rounds,
            ),
        )


def _make_env() -> "_StubEnv":
    if _HAS_REAL_ENV:
        return ReplicaLabEnv()  # type: ignore[return-value]
    return _StubEnv()


# ---------------------------------------------------------------------------
# In-memory session store (REST sessions)
# ---------------------------------------------------------------------------

_SESSION_TTL_SECONDS = SESSION_TTL_SECONDS

_sessions: dict[str, dict[str, Any]] = {}
# { session_id: { "env": env_instance, "last_active": float, "episode_id": str } }

_replay_store: dict[str, EpisodeLog] = {}
# { episode_id: EpisodeLog }


def _touch(session_id: str) -> None:
    if session_id in _sessions:
        _sessions[session_id]["last_active"] = time.monotonic()


def _cleanup_stale_sessions() -> None:
    now = time.monotonic()
    stale = [
        sid
        for sid, data in _sessions.items()
        if now - data["last_active"] > _SESSION_TTL_SECONDS
    ]
    for sid in stale:
        try:
            _sessions[sid]["env"].close()
        except Exception:
            pass
        del _sessions[sid]
        log.info("Cleaned up stale session %s", sid)


# ---------------------------------------------------------------------------
# Background cleanup task
# ---------------------------------------------------------------------------

async def _session_cleanup_loop() -> None:
    while True:
        await asyncio.sleep(60)
        _cleanup_stale_sessions()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_session_cleanup_loop())
    log.info("ReplicaLab server starting up")
    yield
    task.cancel()
    log.info("ReplicaLab server shutting down")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ReplicaLab",
    description="Multi-agent scientific replication environment",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:7860",
    ],
    allow_origin_regex=r"https://.*\.hf\.space",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Available scenarios constant
# ---------------------------------------------------------------------------

SCENARIOS = available_scenario_families()

# ---------------------------------------------------------------------------
# REST request/response schemas
# ---------------------------------------------------------------------------


class ResetRequest(BaseModel):
    seed: int = 0
    scenario: str = DEFAULT_SCENARIO_TEMPLATE
    difficulty: str = DEFAULT_DIFFICULTY
    session_id: Optional[str] = None  # pass to reuse an existing session slot


class ResetResponse(BaseModel):
    session_id: str
    episode_id: str
    observation: Observation


class ScenariosResponse(BaseModel):
    scenarios: list[dict]


class StepRequest(BaseModel):
    session_id: str
    action: ScientistAction


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    env_name = "real ReplicaLabEnv" if _HAS_REAL_ENV else "stub ReplicaLabEnv"
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>ReplicaLab API</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body {{ font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.5; }}
      code {{ background: #f4f4f4; padding: 0.1rem 0.3rem; border-radius: 4px; }}
      ul {{ padding-left: 1.25rem; }}
    </style>
  </head>
  <body>
    <h1>ReplicaLab API</h1>
    <p>The container is running and serving the <strong>{env_name}</strong>.</p>
    <p>This Space currently hosts the backend API. Available endpoints:</p>
    <ul>
      <li><code>GET /health</code></li>
      <li><code>GET /scenarios</code></li>
      <li><code>POST /reset</code></li>
      <li><code>POST /step</code></li>
      <li><code>WS /ws</code></li>
    </ul>
    <p>If you expected the frontend, the backend is healthy but the hosted web UI is not mounted at <code>/</code> yet.</p>
  </body>
</html>"""


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "env": "real" if _HAS_REAL_ENV else "stub",
        "version": app.version,
    }


@app.get("/scenarios", response_model=ScenariosResponse)
async def list_scenarios():
    return ScenariosResponse(scenarios=SCENARIOS)


@app.post("/reset", response_model=ResetResponse)
async def reset_episode(req: ResetRequest):
    session_id = req.session_id or str(uuid.uuid4())

    # Close old env if reusing session
    if session_id in _sessions:
        try:
            _sessions[session_id]["env"].close()
        except Exception:
            pass

    env = _make_env()
    obs = env.reset(seed=req.seed, scenario=req.scenario, difficulty=req.difficulty)
    episode_id = env.episode_id() if hasattr(env, "episode_id") else str(uuid.uuid4())

    _sessions[session_id] = {
        "env": env,
        "last_active": time.monotonic(),
        "episode_id": episode_id,
    }

    log.info("REST reset | session=%s episode=%s", session_id, episode_id)
    return ResetResponse(session_id=session_id, episode_id=episode_id, observation=obs)


@app.post("/step", response_model=StepResult)
async def step_episode(req: StepRequest):
    if req.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found. Call /reset first.")

    _touch(req.session_id)
    session = _sessions[req.session_id]
    env = session["env"]

    result = env.step(req.action)

    # Store completed episode log for replay
    if result.done:
        state = env.state()
        _replay_store[session["episode_id"]] = _build_episode_log(
            session["episode_id"],
            state,
            result,
        )
        log.info(
            "Episode done | session=%s episode=%s reward=%.2f",
            req.session_id,
            session["episode_id"],
            result.reward,
        )

    return result


@app.get("/replay/{episode_id}", response_model=EpisodeLog)
async def get_replay(episode_id: str):
    if episode_id not in _replay_store:
        raise HTTPException(status_code=404, detail="Replay not found for this episode_id.")
    return _replay_store[episode_id]


# ---------------------------------------------------------------------------
# WebSocket handler (API 06)
# Each connection gets its own isolated env instance.
# ---------------------------------------------------------------------------

# WebSocket message protocol:
#   Client → Server:
#     { "type": "reset", "seed": 42, "scenario": DEFAULT_SCENARIO_TEMPLATE, "difficulty": DEFAULT_DIFFICULTY }
#     { "type": "step", "action": { ...ScientistAction fields... } }
#     { "type": "ping" }
#
#   Server → Client:
#     { "type": "reset_ok", "episode_id": "...", "observation": {...} }
#     { "type": "step_ok", "observation": {...}, "reward": 0.0, "done": false, "info": {} }
#     { "type": "pong" }
#     { "type": "error", "message": "..." }

_WS_IDLE_TIMEOUT = WS_IDLE_TIMEOUT_SECONDS


async def _ws_send(ws: WebSocket, payload: dict) -> None:
    await ws.send_text(json.dumps(payload))


def main(host: str = API_HOST, port: int = API_PORT) -> None:
    import uvicorn

    uvicorn.run("server.app:app", host=host, port=port, reload=False)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    env = _make_env()
    episode_id: str = ""
    log.info("WebSocket connected")

    try:
        while True:
            try:
                raw = await asyncio.wait_for(ws.receive_text(), timeout=_WS_IDLE_TIMEOUT)
            except asyncio.TimeoutError:
                log.info("WebSocket idle timeout — closing")
                await ws.close(code=1000, reason="idle timeout")
                break

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await _ws_send(ws, {"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = msg.get("type")

            if msg_type == "ping":
                await _ws_send(ws, {"type": "pong"})

            elif msg_type == "reset":
                seed = int(msg.get("seed", 0))
                scenario = str(msg.get("scenario", DEFAULT_SCENARIO_TEMPLATE))
                difficulty = str(msg.get("difficulty", DEFAULT_DIFFICULTY))

                try:
                    obs = env.reset(seed=seed, scenario=scenario, difficulty=difficulty)
                    episode_id = (
                        env.episode_id() if hasattr(env, "episode_id") else str(uuid.uuid4())
                    )
                    await _ws_send(
                        ws,
                        {
                            "type": "reset_ok",
                            "episode_id": episode_id,
                            "observation": obs.model_dump(),
                        },
                    )
                    log.info("WS reset | episode=%s seed=%d", episode_id, seed)
                except Exception as exc:
                    log.exception("WS reset error")
                    await _ws_send(ws, {"type": "error", "message": str(exc)})

            elif msg_type == "step":
                raw_action = msg.get("action")
                if raw_action is None:
                    await _ws_send(ws, {"type": "error", "message": "Missing 'action' field"})
                    continue

                try:
                    action = ScientistAction.model_validate(raw_action)
                except Exception as exc:
                    await _ws_send(
                        ws, {"type": "error", "message": f"Invalid action: {exc}"}
                    )
                    continue

                try:
                    result = env.step(action)

                    # Store completed episode for REST replay
                    if result.done and episode_id:
                        state = env.state()
                        _replay_store[episode_id] = _build_episode_log(
                            episode_id, state, result
                        )

                    await _ws_send(
                        ws,
                        {
                            "type": "step_ok",
                            "observation": result.observation.model_dump()
                            if result.observation
                            else None,
                            "reward": result.reward,
                            "done": result.done,
                            "info": result.info.model_dump(),
                        },
                    )
                except Exception as exc:
                    log.exception("WS step error")
                    await _ws_send(ws, {"type": "error", "message": str(exc)})

            else:
                await _ws_send(
                    ws,
                    {"type": "error", "message": f"Unknown message type: {msg_type!r}"},
                )

    except WebSocketDisconnect:
        log.info("WebSocket disconnected | episode=%s", episode_id)
    except Exception as exc:
        log.exception("WebSocket unexpected error: %s", exc)
    finally:
        env.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=API_PORT)
    parser.add_argument("--host", default=API_HOST)
    args = parser.parse_args()
    if args.host == API_HOST and args.port == API_PORT:
        main()
    else:
        main(host=args.host, port=args.port)
