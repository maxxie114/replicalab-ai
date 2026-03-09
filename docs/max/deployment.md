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
curl https://ayushozha-replicalab.hf.space/health

# Reset an episode
curl -X POST https://ayushozha-replicalab.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"seed": 42, "scenario": "math_reasoning", "difficulty": "easy"}'

# List scenarios
curl https://ayushozha-replicalab.hf.space/scenarios
```

WebSocket test (using websocat or wscat):
```bash
wscat -c wss://ayushozha-replicalab.hf.space/ws
# Then type: {"type": "ping"}
# Expect: {"type": "pong"}
```

### Verified live deployment (API 10 sign-off, 2026-03-08)

**Public Space URL:** https://huggingface.co/spaces/ayushozha/replicalab
**API base URL:** `https://ayushozha-replicalab.hf.space`

All four endpoints verified against the live Space with real env:

```
GET  /health    → 200 {"status":"ok","env":"real"}
GET  /scenarios → 200 {"scenarios":[...3 families...]}
POST /reset     → 200 {"session_id":"...","episode_id":"...","observation":{...}}
POST /step      → 200 {"reward":2.312798,"done":true,"info":{"verdict":"accept",...}}
```

Full episode verified: reset → propose_protocol → accept → terminal reward
with real judge scoring (rigor=0.465, feasibility=1.000, fidelity=0.325,
total_reward=2.313, verdict=accept).

---

## Secrets and API Key Management (API 17)

### Current state

The server is **fully self-contained with no external API calls**.
No secrets or API keys are required to run the environment, judge, or
scoring pipeline. All reward computation is deterministic and local.

### Where secrets live (by context)

| Context | Location | What to set | Required? |
|---------|----------|-------------|-----------|
| **HF Space** | Space Settings → Repository secrets | Nothing currently | No |
| **Local dev** | Shell env vars or `.env` file (gitignored) | Nothing currently | No |
| **Docker** | `-e KEY=value` flags on `docker run` | Nothing currently | No |
| **Colab notebook** | `google.colab.userdata` or env vars | `HF_TOKEN` for model downloads, `REPLICALAB_URL` for hosted env | Yes for training |

### Colab notebook secrets

When running the training notebook, the following are needed:

| Secret | Purpose | Where to set | Required? |
|--------|---------|-------------|-----------|
| `HF_TOKEN` | Download gated models (Qwen3-4B) from HF Hub | Colab Secrets panel (key icon) | Yes |
| `REPLICALAB_URL` | URL of the hosted environment | Hardcode or Colab secret | Optional — defaults to `https://ayushozha-replicalab.hf.space` |

To set in Colab:
1. Click the key icon in the left sidebar
2. Add `HF_TOKEN` with your Hugging Face access token
3. Access in code:
```python
from google.colab import userdata
hf_token = userdata.get("HF_TOKEN")
```

### Future secrets (not currently needed)

If a frontier hosted evaluator is added later:

| Secret name | Purpose | Required? |
|-------------|---------|-----------|
| `MODEL_API_KEY` | Hosted evaluator access key | Only if a hosted evaluator is added |
| `MODEL_BASE_URL` | Alternate provider endpoint | Only if using a proxy |

These would be set in HF Space Settings → Repository secrets, and
accessed via `os.environ.get("MODEL_API_KEY")` in server code.

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
- **Heavy hosted models require billing-enabled hardware** — as of
  2026-03-09, the checked HF token authenticates successfully but the backing
  account reports `canPay=false` and has no org attached, so it is currently
  suitable for model downloads but not for provisioning paid large-model
  serving through HF Spaces hardware or Inference Endpoints.

---

## Environment URLs Reference

| Service | Local | Hosted |
|---------|-------|--------|
| FastAPI app | `http://localhost:7860` | `https://ayushozha-replicalab.hf.space` |
| Health | `http://localhost:7860/health` | `https://ayushozha-replicalab.hf.space/health` |
| WebSocket | `ws://localhost:7860/ws` | `wss://ayushozha-replicalab.hf.space/ws` |
| Scenarios | `http://localhost:7860/scenarios` | `https://ayushozha-replicalab.hf.space/scenarios` |

---

## Northflank CLI Access

### Local verification (2026-03-08)

- Installed globally with `npm i -g @northflank/cli`
- Verified locally with `northflank --version`
- Current verified version: `0.10.16`

### Login

```bash
northflank login -n <context-name> -t <token>
```

`<token>` must come from the user's Northflank account or team secret
manager. Do not commit it to the repo.

### Service access commands for `replica-labs/replicalab-ai`

```bash
northflank forward service --projectId replica-labs --serviceId replicalab-ai
northflank get service logs --tail --projectId replica-labs --serviceId replicalab-ai
northflank ssh service --projectId replica-labs --serviceId replicalab-ai
northflank exec service --projectId replica-labs --serviceId replicalab-ai
northflank upload service file --projectId replica-labs --serviceId replicalab-ai --localPath dir/file.txt --remotePath /home/file.txt
northflank download service file --projectId replica-labs --serviceId replicalab-ai --localPath dir/file.txt --remotePath /home/file.txt
```

### Current Northflank runtime findings (2026-03-09)

- The manual training job `replicalab-train` exists in `replica-labs`, but
  `northflank start job run --projectId replica-labs --jobId replicalab-train`
  currently fails with `409 No deployment configured`.
- The job still has runtime variables configured, including the older remote
  `MODEL_NAME=Qwen/Qwen3-8B`, so even after the missing deployment is fixed the
  runtime config should be reviewed before launching training.
- The live service `replicalab-ai` is deployed on the same
  `nf-gpu-hack-16-64` billing plan, but a direct probe from inside the
  container found no `nvidia-smi` binary and no `/dev/nvidia*` device nodes.
  Treat GPU/H100 availability as unverified until a container can prove
  hardware visibility from inside the runtime.

### Current Northflank notebook findings (2026-03-09)

- There is a separate live notebook service in project `notebook-openport`:
  `jupyter-pytorch`.
- The active public notebook DNS is
  `app--jupyter-pytorch--9y6g97v7czb9.code.run` on port `8888` (`/lab` for the
  Jupyter UI).
- Northflank reports that service with GPU config
  `gpuType=h100-80`, `gpuCount=1`, and an in-container probe confirmed
  `NVIDIA H100 80GB HBM3`.
- The notebook image is `quay.io/jupyter/pytorch-notebook:cuda12-2025-08-18`.
- The notebook currently contains a repo clone and GRPO outputs, but the saved
  notebook/log state is not clean: training produced adapter checkpoints
  through step 200, then later notebook evaluation/inference failed with a
  `string indices must be integers, not 'str'` content-format error.

### Windows note

Global npm binaries resolve from `C:\Users\ayush\AppData\Roaming\npm` on this
machine. If `northflank` is not found in a new shell, reopen the terminal so
the updated PATH is reloaded.

---

## Hand-off To Ayush

**Local server:**
- WebSocket: `ws://localhost:7860/ws`
- REST health: `http://localhost:7860/health`
- Running against: **real env** (not stub)

**Hosted deployment (verified 2026-03-08):**
- Base URL: `https://ayushozha-replicalab.hf.space`
- `/health` returns `200` with `{"status":"ok","env":"real"}`
- WebSocket path: `wss://ayushozha-replicalab.hf.space/ws`
- Full episode tested: propose → accept → reward with real judge scores

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ReplicaLabEnv not found` warning at startup | The real env is now available; ensure `replicalab/scoring/rubric.py` is present and `httpx` + `websocket-client` are in `server/requirements.txt` |
| Docker build fails | Re-check `server/requirements.txt` and the Docker build context |
| CORS error from the frontend | Re-check allowed origins in `server/app.py` |
| WebSocket closes after idle time | Send periodic ping messages or reconnect |
| Session not found (REST) | Call `/reset` again to create a new session |
