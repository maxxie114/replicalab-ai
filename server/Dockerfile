# ReplicaLab server image (port 7860)
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

# Install the replicalab package in editable mode
RUN pip install --no-cache-dir -e . --no-deps

# Run as a non-root user inside the container
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
