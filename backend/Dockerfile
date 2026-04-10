FROM python:3.12-slim

WORKDIR /app

# Install git for repo cloning + curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends git curl && rm -rf /var/lib/apt/lists/*

# Install semcod tools (when published to PyPI)
# RUN pip install code2llm redup pyqual regix vallm

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files including modular structure
COPY server.py config.py store.py database.py sample_projects.py ./
COPY services/ ./services/
COPY routers/ ./routers/
COPY scripts/ ./scripts/

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
