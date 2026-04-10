FROM python:3.12-slim

WORKDIR /app

# Install git for repo cloning
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

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
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
