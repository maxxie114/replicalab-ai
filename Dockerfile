# Root-level Dockerfile for Hugging Face Spaces deployment.
#
# Multi-stage build:
#   Stage 1: Build the React frontend with Node.js
#   Stage 2: Python runtime serving both API and static frontend

# ── Stage 1: Frontend build ──────────────────────────────────────────
FROM node:20-slim AS frontend-build

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --ignore-scripts

COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python runtime ──────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install system deps (curl needed for HEALTHCHECK)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch with CUDA 12.1 support (works on T4/A10 GPU Spaces;
# falls back to CPU silently if no GPU is present)
RUN pip install --no-cache-dir \
    torch \
    --index-url https://download.pytorch.org/whl/cu121

# Install unsloth + model-serving dependencies
RUN pip install --no-cache-dir \
    unsloth \
    transformers \
    peft \
    accelerate \
    bitsandbytes \
    huggingface_hub

# Install server dependencies
COPY server/requirements.txt ./server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt

# Copy package source
COPY replicalab/ ./replicalab/
COPY server/ ./server/
COPY pyproject.toml ./

# Install the replicalab package (non-editable, deps already present)
RUN pip install --no-cache-dir . --no-deps

# Copy built frontend from stage 1
COPY --from=frontend-build /build/dist ./frontend/dist

# Run as a non-root user inside the container (HF Spaces requirement)
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
