# Root-level Dockerfile for Hugging Face Spaces deployment.
#
# HF Spaces with sdk:docker expects the Dockerfile at the repo root.
# This is identical to server/Dockerfile. Keep them in sync or remove
# server/Dockerfile once the team standardizes on this root copy.

FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY server/requirements.txt ./server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt

# Copy package source
COPY replicalab/ ./replicalab/
COPY server/ ./server/
COPY pyproject.toml ./

# Install the replicalab package (non-editable, deps already present)
RUN pip install --no-cache-dir . --no-deps

# Run as a non-root user inside the container (HF Spaces requirement)
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
