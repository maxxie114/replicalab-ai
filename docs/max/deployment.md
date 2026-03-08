# Deployment Guide (Max / Person C)

---

## Local Development

```bash
# Create and activate virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install server deps
pip install -r server/requirements.txt

# Install replicalab package
pip install -e . --no-deps

# Run the server
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
```

Server should be available at `http://localhost:7860`.

Quick smoke test:

```bash
curl http://localhost:7860/health

curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"seed": 42, "scenario": "cell_biology", "difficulty": "easy"}'
```

---

## Docker (Local)

```bash
docker build -f server/Dockerfile -t replicalab .
docker run -p 7860:7860 replicalab
```

With optional hosted-model secrets:

```bash
docker run -p 7860:7860 \
  -e MODEL_API_KEY=replace-me \
  replicalab
```

---

## Hosted Space Deployment

The repository is not yet marked as fully deployed. Use this section as the deployment checklist for the later API 09, API 10, API 15, and API 17 tasks.

### One-time setup

1. Create a Space with Docker support.
2. Add the Space as a remote.
3. Push the repository once the Docker path and README metadata are finalized.
4. Verify `/health`, `/reset`, and `/ws` after the Space build finishes.

### Secrets checklist

If the deployed server needs hosted-model credentials later, set them in the platform secret store rather than committing them to the repo.

Suggested secret names:

| Secret name | Purpose |
|-------------|---------|
| `MODEL_API_KEY` | Hosted model access key |
| `MODEL_BASE_URL` | Optional alternate provider endpoint |

---

## Environment URLs Reference

| Service | Local | Hosted |
|---------|-------|--------|
| FastAPI app | `http://localhost:7860` | `https://<space>.hf.space` |
| Health | `http://localhost:7860/health` | `https://<space>.hf.space/health` |
| WebSocket | `ws://localhost:7860/ws` | `wss://<space>.hf.space/ws` |
| Scenarios | `http://localhost:7860/scenarios` | `https://<space>.hf.space/scenarios` |

---

## Hand-off To Ayush

When the server path is verified locally:

- share the local WebSocket URL: `ws://localhost:7860/ws`
- share the expected REST health endpoint: `http://localhost:7860/health`
- note whether the server is still running against the stub env or the real env

When hosted deployment is eventually verified:

- share the hosted base URL
- confirm `/health` returns `200`
- confirm the WebSocket path is reachable

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ReplicaLabEnv not found` warning at startup | Normal while the real env implementation has not landed; the server will use the stub env |
| Docker build fails | Re-check `server/requirements.txt` and the Docker build context |
| CORS error from the frontend | Re-check allowed origins in `server/app.py` |
| WebSocket closes after idle time | Send periodic ping messages or reconnect |
| Session not found (REST) | Call `/reset` again to create a new session |
