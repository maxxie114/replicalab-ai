"""Reusable environment client for ReplicaLab (TRN 13).

Wraps both REST and WebSocket server transports behind a unified
sync interface.  Consumers (notebook, training loop, eval scripts)
import this module instead of duplicating connection logic.

Usage::

    from replicalab.client import ReplicaLabClient

    with ReplicaLabClient("http://localhost:7860", transport="websocket") as client:
        obs = client.reset(seed=42, scenario="math_reasoning", difficulty="easy")
        while True:
            action = policy(obs)
            result = client.step(action)
            obs = result.observation
            if result.done:
                break
"""

from __future__ import annotations

import json
import threading
from typing import Optional

import httpx
import websocket as ws_lib  # websocket-client

from replicalab.config import (
    API_PORT,
    DEFAULT_DIFFICULTY,
    DEFAULT_SCENARIO_TEMPLATE,
)
from replicalab.models import (
    EpisodeLog,
    Observation,
    ScientistAction,
    StepInfo,
    StepResult,
)

__all__ = ["ReplicaLabClient"]

# ---------------------------------------------------------------------------
# Transport backends
# ---------------------------------------------------------------------------


class _RestTransport:
    """Sync REST transport using httpx."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._http = httpx.Client(base_url=self._base_url, timeout=timeout)
        self._session_id: Optional[str] = None
        self._episode_id: Optional[str] = None

    # -- lifecycle -----------------------------------------------------------

    def connect(self) -> None:
        resp = self._http.get("/health")
        resp.raise_for_status()

    def close(self) -> None:
        self._session_id = None
        self._episode_id = None
        self._http.close()

    # -- env operations ------------------------------------------------------

    def reset(
        self,
        seed: int,
        scenario: str,
        difficulty: str,
    ) -> Observation:
        payload: dict = {
            "seed": seed,
            "scenario": scenario,
            "difficulty": difficulty,
        }
        if self._session_id is not None:
            payload["session_id"] = self._session_id

        resp = self._http.post("/reset", json=payload)
        resp.raise_for_status()
        data = resp.json()
        self._session_id = data["session_id"]
        self._episode_id = data["episode_id"]
        return Observation.model_validate(data["observation"])

    def step(self, action: ScientistAction) -> StepResult:
        if self._session_id is None:
            raise RuntimeError("Call reset() before step()")
        resp = self._http.post(
            "/step",
            json={
                "session_id": self._session_id,
                "action": action.model_dump(),
            },
        )
        resp.raise_for_status()
        return StepResult.model_validate(resp.json())

    def state(self) -> dict:
        if self._session_id is None:
            raise RuntimeError("Call reset() before state()")
        resp = self._http.get(f"/state/{self._session_id}")
        resp.raise_for_status()
        return resp.json()

    def replay(self, episode_id: str) -> EpisodeLog:
        resp = self._http.get(f"/replay/{episode_id}")
        resp.raise_for_status()
        return EpisodeLog.model_validate(resp.json())

    # -- properties ----------------------------------------------------------

    @property
    def session_id(self) -> Optional[str]:
        return self._session_id

    @property
    def episode_id(self) -> Optional[str]:
        return self._episode_id


class _WsTransport:
    """Sync WebSocket transport using websocket-client."""

    def __init__(self, base_url: str, timeout: float) -> None:
        # Convert http(s):// → ws(s)://
        ws_url = base_url.rstrip("/")
        ws_url = ws_url.replace("https://", "wss://").replace("http://", "ws://")
        self._ws_url = ws_url + "/ws"
        self._timeout = timeout
        self._ws: Optional[ws_lib.WebSocket] = None
        self._episode_id: Optional[str] = None
        self._lock = threading.Lock()

    # -- lifecycle -----------------------------------------------------------

    def connect(self) -> None:
        self._ws = ws_lib.create_connection(
            self._ws_url, timeout=self._timeout
        )

    def close(self) -> None:
        if self._ws is not None:
            try:
                self._ws.close()
            except Exception:
                pass
            self._ws = None
        self._episode_id = None

    # -- low-level send/recv -------------------------------------------------

    def _send(self, payload: dict) -> dict:
        if self._ws is None:
            raise RuntimeError("Call connect() before sending messages")
        with self._lock:
            self._ws.send(json.dumps(payload))
            raw = self._ws.recv()
        data = json.loads(raw)
        if data.get("type") == "error":
            raise RuntimeError(f"Server error: {data.get('message', '')}")
        return data

    # -- env operations ------------------------------------------------------

    def reset(
        self,
        seed: int,
        scenario: str,
        difficulty: str,
    ) -> Observation:
        data = self._send({
            "type": "reset",
            "seed": seed,
            "scenario": scenario,
            "difficulty": difficulty,
        })
        if data.get("type") != "reset_ok":
            raise RuntimeError(f"Unexpected response type: {data.get('type')}")
        self._episode_id = data.get("episode_id")
        return Observation.model_validate(data["observation"])

    def step(self, action: ScientistAction) -> StepResult:
        data = self._send({
            "type": "step",
            "action": action.model_dump(),
        })
        if data.get("type") != "step_ok":
            raise RuntimeError(f"Unexpected response type: {data.get('type')}")
        return StepResult(
            observation=Observation.model_validate(data["observation"])
            if data.get("observation")
            else None,
            reward=data.get("reward", 0.0),
            done=data.get("done", False),
            info=StepInfo.model_validate(data.get("info", {})),
        )

    def state(self) -> dict:
        raise NotImplementedError(
            "state() is not available over WebSocket. Use REST transport or "
            "track state from step() results."
        )

    def replay(self, episode_id: str) -> EpisodeLog:
        raise NotImplementedError(
            "replay() is not available over WebSocket. Use REST transport or "
            "a separate httpx call to GET /replay/{episode_id}."
        )

    # -- properties ----------------------------------------------------------

    @property
    def session_id(self) -> Optional[str]:
        return None  # WS sessions are implicit per-connection

    @property
    def episode_id(self) -> Optional[str]:
        return self._episode_id


# ---------------------------------------------------------------------------
# Public client
# ---------------------------------------------------------------------------


class ReplicaLabClient:
    """Reusable sync client for the ReplicaLab environment server.

    Parameters
    ----------
    base_url:
        Server URL, e.g. ``"http://localhost:7860"``.
    transport:
        ``"websocket"`` (default) or ``"rest"``.
    timeout:
        Request/connection timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = f"http://localhost:{API_PORT}",
        *,
        transport: str = "websocket",
        timeout: float = 30.0,
    ) -> None:
        if transport == "websocket":
            self._transport: _RestTransport | _WsTransport = _WsTransport(
                base_url, timeout
            )
        elif transport == "rest":
            self._transport = _RestTransport(base_url, timeout)
        else:
            raise ValueError(f"Unknown transport: {transport!r}. Use 'websocket' or 'rest'.")
        self._connected = False

    # -- context manager -----------------------------------------------------

    def __enter__(self) -> "ReplicaLabClient":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- lifecycle -----------------------------------------------------------

    def connect(self) -> None:
        """Open the connection to the server."""
        self._transport.connect()
        self._connected = True

    def close(self) -> None:
        """Close the connection and release resources."""
        self._transport.close()
        self._connected = False

    # -- env operations ------------------------------------------------------

    def reset(
        self,
        seed: int = 0,
        scenario: str = DEFAULT_SCENARIO_TEMPLATE,
        difficulty: str = DEFAULT_DIFFICULTY,
    ) -> Observation:
        """Start a new episode. Returns the initial observation."""
        self._ensure_connected()
        return self._transport.reset(seed, scenario, difficulty)

    def step(self, action: ScientistAction) -> StepResult:
        """Submit a Scientist action. Returns the step result."""
        self._ensure_connected()
        return self._transport.step(action)

    def state(self) -> dict:
        """Get current episode state (REST only)."""
        self._ensure_connected()
        return self._transport.state()

    def replay(self, episode_id: str) -> EpisodeLog:
        """Fetch a completed episode log (REST only)."""
        self._ensure_connected()
        return self._transport.replay(episode_id)

    # -- properties ----------------------------------------------------------

    @property
    def session_id(self) -> Optional[str]:
        """REST session ID, or ``None`` for WebSocket transport."""
        return self._transport.session_id

    @property
    def episode_id(self) -> Optional[str]:
        """Current episode ID set after the most recent ``reset()``."""
        return self._transport.episode_id

    @property
    def connected(self) -> bool:
        """Whether ``connect()`` has been called."""
        return self._connected

    # -- internal ------------------------------------------------------------

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("Client not connected. Call connect() or use as context manager.")
