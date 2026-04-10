.PHONY: help install dev build docker-up docker-down clean venv

VENV_DIR = backend/.venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
UVICORN = ./$(VENV_DIR)/bin/uvicorn

# Domyślny target
help:
	@echo "Dostępne komendy:"
	@echo "  make install      - Instaluje zależności (backend + frontend)"
	@echo "  make dev          - Uruchamia środowisko deweloperskie (obie usługi)"
	@echo "  make dev-backend  - Uruchamia tylko backend (port 8200)"
	@echo "  make dev-frontend - Uruchamia tylko frontend (port 5174)"
	@echo "  make build        - Buduje frontend do produkcji"
	@echo "  make docker-up    - Uruchamia wszystko przez Docker Compose"
	@echo "  make docker-down  - Zatrzymuje kontenery Docker"
	@echo "  make test         - Uruchamia wszystkie testy"
	@echo "  make test-backend - Uruchamia testy backendu (pytest)"
	@echo "  make test-e2e     - Uruchamia testy E2E (Playwright)"
	@echo "  make clean        - Czyści zainstalowane zależności"

# Tworzenie wirtualnego środowiska Python
venv:
	@echo "=== Tworzenie wirtualnego środowiska Python ==="
	cd backend && python3 -m venv .venv

# Instalacja zależności
install: venv
	@echo "=== Instalacja backend (Python) ==="
	./$(PIP) install -r backend/requirements.txt
	@echo "=== Instalacja frontend (Node.js) ==="
	cd frontend && npm install

# Środowisko deweloperskie - obie usługi (w tle)
dev:
	@echo "=== Uruchamianie backendu (port 8200) ==="
	@cd backend && $(UVICORN) server:app --reload --port 8200 &
	@sleep 2
	@echo "=== Uruchamianie frontendu (port 5174) ==="
	@cd frontend && npm run dev -- --port 5174 &
	@echo "=== Usługi uruchomione ==="
	@echo "Backend:  http://localhost:8200"
	@echo "Frontend: http://localhost:5174"

# Tylko backend
dev-backend:
	cd backend && $(UVICORN) server:app --reload --port 8200

# Tylko frontend
dev-frontend:
	cd frontend && npm run dev -- --port 5174

# Budowanie frontendu
build:
	cd frontend && npm run build

# Docker
docker-up:
	docker-compose up -d
	@echo "=== Usługi Docker uruchomione ==="
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

docker-down:
	docker-compose down

# Czyszczenie
clean:
	@echo "=== Czyszczenie frontend ==="
	cd frontend && rm -rf node_modules dist
	@echo "=== Czyszczenie backend (opcjonalne) ==="
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Testy
test: test-backend test-e2e
	@echo "=== Wszystkie testy zakończone ==="

test-backend:
	@echo "=== Uruchamianie testów backendu ==="
	cd backend && python3 -m pytest ../tests/backend/ -v

test-e2e:
	@echo "=== Uruchamianie testów E2E (wymaga uruchomionego frontendu) ==="
	cd frontend && npm run test:e2e

test-e2e-ui:
	@echo "=== Uruchamianie testów E2E w trybie UI ==="
	cd frontend && npm run test:e2e:ui
