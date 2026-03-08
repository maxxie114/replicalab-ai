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
  -d '{"seed": 42, "scenario": "math_reasoning", "difficulty": "easy"}'
```

---

## Docker (Local)

```bash
docker build -f server/Dockerfile -t replicalab .
docker run -p 7860:7860 replicalab
```

### Verified endpoints (API 08 sign-off, 2026-03-08)

After `docker run -p 7860:7860 replicalab`, the following were verified
against the **real env** (not stub):

```bash
curl http://localhost:7860/health
# → {"status":"ok","env":"real"}

curl http://localhost:7860/scenarios
# → {"scenarios":[{"family":"math_reasoning",...}, ...]}

curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"seed":42,"scenario":"math_reasoning","difficulty":"easy"}'
# → {"session_id":"...","episode_id":"...","observation":{...}}

# Use session_id from reset response:
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"session_id":"<SESSION_ID>","action":{"action_type":"propose_protocol","sample_size":3,"controls":["baseline"],"technique":"algebraic_proof","duration_days":1,"required_equipment":[],"required_reagents":[],"questions":[],"rationale":"Test."}}'
# → {"observation":{...},"reward":0.0,"done":false,"info":{...}}
```

With optional hosted-model secrets:

```bash
docker run -p 7860:7860 \
  -e MODEL_API_KEY=replace-me \
  replicalab
```

---

## Hugging Face Spaces Deployment

### What is already configured (API 09)

The repo is now deployment-ready for HF Spaces:

- **Root `Dockerfile`** — HF Spaces requires the Dockerfile at repo root.
  The root-level `Dockerfile` is identical to `server/Dockerfile`. Keep them
  in sync, or delete `server/Dockerfile` once the team standardizes.
- **`README.md` frontmatter** — The root README now contains the required
  YAML frontmatter that HF Spaces parses on push:
  ```yaml
  ---
  title: ReplicaLab
  emoji: 🧪
  colorFrom: blue
  colorTo: green
  sdk: docker
  app_port: 7860
  pinned: false
  ---
  ```
- **Non-root user** — The Dockerfile creates and runs as `appuser` (UID 1000),
  which HF Spaces requires for security.
- **Port 7860** — Both the `EXPOSE` directive and the `uvicorn` CMD use 7860,
  matching the `app_port` in the frontmatter.

### Step-by-step deployment (for Max)

#### 1. Create the Space

1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Owner:** your HF username or the team org
   - **Space name:** `replicalab` (or `replicalab-demo`)
   - **License:** MIT
   - **SDK:** Docker
   - **Hardware:** CPU Basic (free tier is fine for the server)
   - **Visibility:** Public
3. Click **Create Space**

#### 2. Add the Space as a git remote

```bash
# From the repo root
git remote add hf https://huggingface.co/spaces/<YOUR_HF_USERNAME>/replicalab

# If the org is different:
# git remote add hf https://huggingface.co/spaces/<ORG>/replicalab
```

#### 3. Push the repo

```bash
# Push the current branch to the Space
git push hf ayush:main

# Or if deploying from master:
# git push hf master:main
```

HF Spaces will automatically detect the `Dockerfile`, build the image, and
start the container.

#### 4. Monitor the build

1. Go to https://huggingface.co/spaces/\<YOUR_HF_USERNAME\>/replicalab
2. Click the **Logs** tab (or **Build** tab during first deploy)
3. Wait for the build to complete (typically 2-5 minutes)
4. The Space status should change from "Building" to "Running"

#### 5. Verify the deployment (API 10 scope)

Once the Space is running:

```bash
# Health check
curl https://<space-name>.hf.space/health

# Reset an episode
curl -X POST https://<space-name>.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"seed": 42, "scenario": "math_reasoning", "difficulty": "easy"}'

# List scenarios
curl https://<space-name>.hf.space/scenarios
```

WebSocket test (using websocat or wscat):
```bash
wscat -c wss://<space-name>.hf.space/ws
# Then type: {"type": "ping"}
# Expect: {"type": "pong"}
```

### Secrets configuration

If the deployed server needs hosted-model credentials later (e.g. for a
frontier evaluator), set them in the HF Space secret store:

1. Go to the Space **Settings** tab
2. Scroll to **Repository secrets**
3. Add each secret:

| Secret name | Purpose | Required now? |
|-------------|---------|---------------|
| `MODEL_API_KEY` | Hosted model access key (for frontier evaluator) | No — only for demo-time evaluator |
| `MODEL_BASE_URL` | Optional alternate provider endpoint | No |

Secrets are injected as environment variables at container runtime.
Access them in Python with `os.environ.get("MODEL_API_KEY")`.

### Re-deploying after code changes

```bash
# Just push again — HF rebuilds automatically
git push hf ayush:main
```

To force a full rebuild (e.g. after dependency changes):
1. Go to Space **Settings**
2. Click **Factory reboot** under the Danger zone section

### Known limitations

- **Free CPU tier** has 2 vCPU and 16 GB RAM. This is sufficient for the
  FastAPI server but NOT for running RL training. Training happens in Colab.
- **Cold starts** — Free-tier Spaces sleep after 48 hours of inactivity.
  The first request after sleep takes 30-60 seconds to rebuild.
- **Persistent storage** — Episode replays and logs are in-memory only.
  They reset when the container restarts. This is acceptable for the
  hackathon demo.

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
| `ReplicaLabEnv not found` warning at startup | The real env is now available; ensure `replicalab/scoring/rubric.py` is present and `httpx` + `websocket-client` are in `server/requirements.txt` |
| Docker build fails | Re-check `server/requirements.txt` and the Docker build context |
| CORS error from the frontend | Re-check allowed origins in `server/app.py` |
| WebSocket closes after idle time | Send periodic ping messages or reconnect |
| Session not found (REST) | Call `/reset` again to create a new session |
