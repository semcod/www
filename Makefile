# Makefile — Gitea local development cycle
# Place in www/ alongside existing docker-compose.yml

.PHONY: gitea-up gitea-setup gitea-test gitea-down gitea-logs gitea-reset

# Start full stack with Gitea
gitea-up:
	docker compose -f docker-compose.yml -f docker-compose.gitea.yml up -d
	@echo ""
	@echo "⏳ Waiting for Gitea to be ready..."
	@for i in $$(seq 1 30); do \
		curl -sf http://localhost:3100/api/v1/version >/dev/null 2>&1 && break; \
		sleep 2; \
	done
	@echo "✅ Stack ready — run 'make gitea-setup' next"

# Provision Gitea with user, repos, webhooks
gitea-setup:
	bash scripts/setup-gitea.sh

# Run full developer cycle test
gitea-test:
	bash scripts/test-full-cycle.sh

# All-in-one: start + setup + test
gitea-cycle: gitea-up
	@sleep 5
	$(MAKE) gitea-setup
	@sleep 2
	$(MAKE) gitea-test

# Stop everything
gitea-down:
	docker compose -f docker-compose.yml -f docker-compose.gitea.yml down

# Logs
gitea-logs:
	docker compose -f docker-compose.yml -f docker-compose.gitea.yml logs -f gitea backend

# Full reset (delete volumes)
gitea-reset:
	docker compose -f docker-compose.yml -f docker-compose.gitea.yml down -v
	rm -f .env.gitea
	@echo "🗑️  Gitea data wiped"
