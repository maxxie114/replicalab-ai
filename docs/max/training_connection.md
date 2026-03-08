# Training Connection Guide

This note closes `TRN 11`: how notebook-based training code should connect to
the ReplicaLab environment, which URLs to use, which client transport to
prefer, which secrets matter, and what to check first when a connection fails.

## Preferred Connection Order

Use the environment in this order:

1. Local backend for smoke tests and fast debugging
2. Hosted Hugging Face Space for shared team validation
3. H100 notebook runtime for training compute

The notebook runtime and the environment server are separate concerns. The
notebook supplies compute; the environment server supplies `reset`, `step`,
`state`, and `replay`.

## Base URLs

### Local

- REST base URL: `http://localhost:7860`
- WebSocket URL: `ws://localhost:7860/ws`

### Hosted

- Space page: `https://huggingface.co/spaces/ayushozha/replicalab`
- REST base URL: `https://ayushozha-replicalab.hf.space`
- WebSocket URL: `wss://ayushozha-replicalab.hf.space/ws`

## Which Transport To Use

Prefer `transport="rest"` first in notebooks:

- easier to debug with plain responses
- simpler error handling
- easier to reproduce single-step failures

Use `transport="websocket"` when you specifically want:

- long-lived per-connection sessions
- parity with frontend interactive behavior
- lower-overhead repeated `step()` calls after reset

## Required Secrets

### For environment access

No secret is required to talk to the current deterministic environment when it
is publicly reachable.

### For model downloads in notebook training

- `HF_TOKEN`
  - needed for gated model downloads and authenticated Hugging Face access
- `REPLICALAB_URL`
  - optional convenience variable for the environment base URL
  - defaults can still be hardcoded in a notebook cell

### Important security note

Do not commit notebook URLs, notebook passwords, or temporary runtime access
links to the repo. Keep notebook credentials out-of-band.

## Minimal Client Usage

### Direct environment client

```python
import os

from replicalab.agents import build_baseline_scientist_action
from replicalab.client import ReplicaLabClient

base_url = os.getenv("REPLICALAB_URL", "http://localhost:7860")

with ReplicaLabClient(base_url, transport="rest") as client:
    observation = client.reset(seed=42, scenario="ml_benchmark", difficulty="easy")
    result = client.step(build_baseline_scientist_action(observation.scientist))
    print(result.reward, result.done, result.info.verdict)
```

### Rollout worker

```python
import os

from replicalab.agents import build_baseline_scientist_action
from replicalab.client import ReplicaLabClient
from replicalab.training import RolloutWorker

base_url = os.getenv("REPLICALAB_URL", "http://localhost:7860")

with ReplicaLabClient(base_url, transport="rest") as client:
    worker = RolloutWorker(client)
    episode = worker.rollout(
        build_baseline_scientist_action,
        seed=42,
        scenario="ml_benchmark",
        difficulty="easy",
    )
    print(episode.total_reward, episode.verdict, episode.rounds_used)
```

## Troubleshooting

### `GET /` returns 404 or a simple landing page

That is not the training interface. The environment lives behind:

- `/health`
- `/scenarios`
- `/reset`
- `/step`
- `/ws`

### `Call reset() before step()`

The client has no active session yet. Always call `reset()` first.

### `404` on `/step`

Usually means the `session_id` is stale or the server restarted. Call `reset()`
again and start a fresh episode.

### WebSocket disconnects or times out

Retry with REST first. If REST works and WebSocket does not, the problem is
usually transport-specific rather than environment-specific.

### Space is up but root path looks broken

Check `GET /health` and `GET /scenarios` directly. The Space can be healthy
even if the root route is only a small landing page.

### Hugging Face Space is slow on the first request

Cold starts are expected on the free tier. Retry after the Space has fully
started.

### Notebook can download models but cannot reach the env

Verify:

1. `REPLICALAB_URL` points to the correct server
2. local server is running on port `7860` or the HF Space is healthy
3. you are using the matching transport (`rest` vs `websocket`)

## Relationship To Other Docs

- Deployment and hosted verification: [deployment.md](C:\Users\ayush\Desktop\Hackathons\replicalab-ai\docs\max\deployment.md)
- Client implementation: [client.py](C:\Users\ayush\Desktop\Hackathons\replicalab-ai\replicalab\client.py)
- Rollout implementation: [rollout.py](C:\Users\ayush\Desktop\Hackathons\replicalab-ai\replicalab\training\rollout.py)

This file is the notebook-facing connection note. Deployment-specific secret
management and HF Space operations remain in `docs/max/deployment.md`.
