.PHONY: help install dev dev-demo build docker-up docker-down clean venv certs

VENV_DIR = backend/.venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
UVICORN = ./$(VENV_DIR)/bin/uvicorn

BACKEND_PORT = 8200
FRONTEND_PORT = 5174

# Domyślny target
help:
	@echo "Dostępne komendy:"
	@echo ""
	@echo "  Środowisko deweloperskie:"
	@echo "    make install       - Instaluje zależności (backend + frontend)"
	@echo "    make dev           - Uruchamia backend + frontend (http)"
	@echo "    make dev-demo      - Uruchamia backend z DEMO_MODE + frontend"
	@echo "    make dev-backend   - Tylko backend (port $(BACKEND_PORT))"
	@echo "    make dev-frontend  - Tylko frontend (port $(FRONTEND_PORT))"
	@echo ""
	@echo "  Docker + HTTPS (Traefik):"
	@echo "    make certs         - Generuje self-signed certyfikaty dla semcod.localhost"
	@echo "    make docker-up     - Uruchamia Docker Compose + Traefik HTTPS"
	@echo "    make docker-down   - Zatrzymuje kontenery Docker"
	@echo ""
	@echo "  Budowanie:"
	@echo "    make build         - Buduje frontend do produkcji"
	@echo ""
	@echo "  Testy:"
	@echo "    make test          - Uruchamia wszystkie testy"
	@echo "    make test-fast     - Tylko szybkie testy unit (~2s)"
	@echo "    make test-backend  - Testy backendu (pytest)"
	@echo "    make test-e2e      - Testy E2E (Playwright headless)"
	@echo "    make test-e2e-ui   - Testy E2E z Playwright UI"
	@echo "    make test-demo     - Testy demo login (wymaga dev-demo)"
	@echo ""
	@echo "  Inne:"
	@echo "    make clean         - Czyści zainstalowane zależności"

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
	@echo "=== Uruchamianie backendu (port $(BACKEND_PORT)) ==="
	@cd backend && $(UVICORN) server:app --reload --port $(BACKEND_PORT) &
	@sleep 2
	@echo "=== Uruchamianie frontendu (port $(FRONTEND_PORT)) ==="
	@cd frontend && npm run dev -- --port $(FRONTEND_PORT) &
	@echo "=== Usługi uruchomione ==="
	@echo "Backend:  http://localhost:$(BACKEND_PORT)"
	@echo "Frontend: http://localhost:$(FRONTEND_PORT)"

# Środowisko deweloperskie z DEMO_MODE (logowanie bez GitHub)
dev-demo:
	@echo "=== Uruchamianie backendu z DEMO_MODE (port $(BACKEND_PORT)) ==="
	@cd backend && DEMO_MODE=1 APP_URL=http://localhost:$(BACKEND_PORT) FRONTEND_URL=http://localhost:$(FRONTEND_PORT) $(UVICORN) server:app --reload --port $(BACKEND_PORT) &
	@sleep 2
	@echo "=== Uruchamianie frontendu (port $(FRONTEND_PORT)) ==="
	@cd frontend && npm run dev -- --port $(FRONTEND_PORT) &
	@echo "=== Usługi uruchomione (DEMO_MODE) ==="
	@echo "Backend:  http://localhost:$(BACKEND_PORT)"
	@echo "Frontend: http://localhost:$(FRONTEND_PORT)"
	@echo "Demo login: kliknij 'Demo Login' na stronie"

# Tylko backend
dev-backend:
	cd backend && $(UVICORN) server:app --reload --port $(BACKEND_PORT)

# Tylko frontend
dev-frontend:
	cd frontend && npm run dev -- --port $(FRONTEND_PORT)

# Budowanie frontendu
build:
	cd frontend && npm run build

# Self-signed certyfikaty dla lokalnego HTTPS
certs:
	@./traefik/generate-certs.sh

# Docker Compose z Traefik HTTPS
docker-up: certs
	docker compose up -d
	@echo "=== Usługi Docker uruchomione ==="
	@echo "App:      https://semcod.localhost"
	@echo "Demo login: kliknij 'Demo Login' na stronie"

docker-down:
	docker compose down

# Czyszczenie
clean:
	@echo "=== Czyszczenie frontend ==="
	cd frontend && rm -rf node_modules dist
	@echo "=== Czyszczenie backend (opcjonalne) ==="
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "=== Czyszczenie e2e ==="
	cd e2e && rm -rf test-results node_modules 2>/dev/null || true

# Testy
test: test-backend test-e2e
	@echo "=== Wszystkie testy zakończone ==="

test-fast:
	@echo "=== Uruchamianie SZYBKICH testów (tylko unit/fast) ==="
	cd backend && python3 -m pytest ../tests/backend/ -v -m "fast or unit" --tb=line -q
	@echo "=== Szybkie testy zakończone (~2s) ==="

test-backend:
	@echo "=== Uruchamianie testów backendu ==="
	cd backend && python3 -m pytest ../tests/backend/ -v

test-e2e:
	@echo "=== Uruchamianie testów E2E (wymaga uruchomionego frontendu) ==="
	cd e2e && BASE_URL=http://localhost:$(FRONTEND_PORT) npx playwright test

test-e2e-ui:
	@echo "=== Uruchamianie testów E2E w trybie UI ==="
	cd e2e && BASE_URL=http://localhost:$(FRONTEND_PORT) npx playwright test --ui --headed

test-demo:
	@echo "=== Uruchamianie testów demo login (wymaga make dev-demo) ==="
	cd e2e && BASE_URL=http://localhost:$(FRONTEND_PORT) npx playwright test demo-login --headed
