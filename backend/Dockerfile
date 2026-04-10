# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Runtime deps only: git for repo cloning, curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends git curl && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY server.py config.py store.py database.py sample_projects.py worker.py quality_gate.py db_models.py db_session.py alembic.ini ./
COPY alembic/ ./alembic/
COPY services/ ./services/
COPY routers/ ./routers/
COPY scripts/ ./scripts/
COPY worker/ ./worker/
COPY events/ ./events/
COPY adapters/ ./adapters/
COPY scheduler/ ./scheduler/
COPY apps/ ./apps/
COPY db_module/ ./db_module/
COPY templates/ ./templates/

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
