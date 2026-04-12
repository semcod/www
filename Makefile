# Makefile — Semcod WWW
# ────────────────────────────────────────────────────────────────
# Quick start:
#   make dev          — local dev (Vite :5174 + backend :8200)
#   make sim          — Docker + mock GitHub (frontend :3000, backend :8003)
#   make up           — Docker production stack
#   make test         — backend pytest
#   make e2e          — Playwright E2E tests
# ────────────────────────────────────────────────────────────────

.PHONY: help dev sim up down test e2e lint \
        gitea-up gitea-setup gitea-test gitea-down gitea-logs gitea-reset gitea-cycle \
        backend frontend install clean logs ps

# ── Help ────────────────────────────────────────────────────────
help:
	@echo "Semcod WWW — available targets:"
	@echo ""
	@echo "  make dev        — local dev server (Vite :5174 + backend :8200)"
	@echo "  make sim        — Docker + mock GitHub (:3000, :8003, mock :4010)"
	@echo "  make up         — Docker production stack"
	@echo "  make down       — stop all Docker services"
	@echo "  make test       — backend pytest"
	@echo "  make e2e        — Playwright E2E (requires sim or dev running)"
	@echo "  make lint       — ruff lint + format check"
	@echo "  make install    — install Python + Node dependencies"
	@echo "  make logs       — tail Docker logs"
	@echo "  make ps         — show running containers"
	@echo "  make clean      — remove caches and temp files"
	@echo ""
	@echo "Gitea targets:"
	@echo "  make gitea-up / gitea-down / gitea-setup / gitea-test / gitea-cycle"

# ── Local Development ──────────────────────────────────────────
# Backend on :8200, Frontend Vite on :5174

backend:
	cd backend && python server.py

frontend:
	cd frontend && npx vite --host

dev: install
	@echo "Starting local dev: backend :8200 + frontend :5174"
	@echo "Press Ctrl+C to stop"
	$(MAKE) -j2 backend frontend

# ── Docker + Mock GitHub (development) ──────────────────────────
# Frontend :3000, Backend :8003, Mock GitHub :4010

sim:
	docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d --build
	@echo ""
	@echo "✅ Stack ready with mock GitHub"
	@echo "   Frontend:  http://localhost:3000"
	@echo "   Backend:   http://localhost:8003"
	@echo "   Mock GH:   http://localhost:4010"

sim-down:
	docker compose -f docker-compose.yml -f docker-compose.sim.yml down

# ── Docker Production ───────────────────────────────────────────

up:
	docker compose up -d --build
	@echo ""
	@echo "✅ Production stack ready"
	@echo "   Frontend:  http://localhost:3000"
	@echo "   Backend:   http://localhost:8003"

down:
	docker compose down

# ── Testing ─────────────────────────────────────────────────────

test:
	cd backend && python -m pytest tests/ -v -m "not slow" --tb=short

test-all:
	cd backend && python -m pytest tests/ -v --tb=short

e2e:
	cd e2e && BASE_URL=http://localhost:3000 npx playwright test --reporter=list

e2e-dev:
	cd e2e && BASE_URL=http://localhost:5174 npx playwright test --reporter=list

e2e-install:
	cd e2e && npx playwright install chromium

# ── Lint ────────────────────────────────────────────────────────

lint:
	cd backend && python -m ruff check . && python -m ruff format --check .

# ── Dependencies ────────────────────────────────────────────────

install:
	cd backend && pip install -q -r requirements.txt 2>/dev/null || true
	cd frontend && npm install --silent 2>/dev/null || true
	cd e2e && npm install --silent 2>/dev/null || true

# ── Utilities ───────────────────────────────────────────────────

logs:
	docker compose logs -f backend frontend worker

ps:
	docker compose ps

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	rm -rf e2e/test-results/ e2e/playwright-report/

# ── Gitea (local Git hosting) ──────────────────────────────────

gitea-up:
	docker compose -f docker-compose.yml -f docker-compose.gitea.yml up -d
	@echo ""
	@echo "⏳ Waiting for Gitea to be ready..."
	@for i in $$(seq 1 30); do \
		curl -sf http://localhost:3100/api/v1/version >/dev/null 2>&1 && break; \
		sleep 2; \
	done
	@echo "✅ Stack ready — run 'make gitea-setup' next"

gitea-setup:
	bash scripts/setup-gitea.sh

gitea-test:
	bash scripts/test-full-cycle.sh

gitea-cycle: gitea-up
	@sleep 5
	$(MAKE) gitea-setup
	@sleep 2
	$(MAKE) gitea-test

gitea-down:
	docker compose -f docker-compose.yml -f docker-compose.gitea.yml down

gitea-logs:
	docker compose -f docker-compose.yml -f docker-compose.gitea.yml logs -f gitea backend

gitea-reset:
	docker compose -f docker-compose.yml -f docker-compose.gitea.yml down -v
	rm -f .env.gitea
	@echo "🗑️  Gitea data wiped"
