# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Sandbox/guest scans now persist to SQLite (were only in-memory, lost on restart)
- `_run_audit_pipeline` and `_run_sandbox_analysis` now call `save_scan()` after completion

### Changed
- All hardcoded values moved to environment variables (20 vars total in `.env`)
- `DB_PATH` — was hardcoded `Path("scans.db")` in database.py
- `SCAN_HISTORY_LIMIT` — was hardcoded `100` in audit.py
- `REPOS_PER_PAGE` — was hardcoded `30` in auth.py
- `GITHUB_OAUTH_SCOPE` — was hardcoded `"repo,read:org"` in auth.py
- `CORS_ORIGINS` — was hardcoded `[FRONTEND_URL, "https://semcod.com"]` in server.py
- `LARGE_FILE_THRESHOLD` — was hardcoded `300` in webhook.py
- Docker Compose: ports bound to `0.0.0.0`, URLs use hostname `nvidia` for LAN access
- Docker Compose: `env_file: .env` instead of individual variable pass-through
- Docker override: restored direct port mapping (3000, 8003) alongside Traefik
- `.env`: updated headers, URLs to `nvidia` hostname, fixed `CORS_ORIGINS` protocol

### Added
- `GITHUB_OAUTH_SCOPE` env var
- `DB_PATH` env var
- `SCAN_HISTORY_LIMIT` env var
- `REPOS_PER_PAGE` env var
- `CORS_ORIGINS` env var (comma-separated list)
- `LARGE_FILE_THRESHOLD` env var
- LAN access from other computers via `http://nvidia:3000` and `http://nvidia:8003`
- Quadlet deployment docs link in README
- Full env vars table in README

## [0.1.6] - 2026-04-10

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md
- Update backend/code2llm_output/README.md
- Update docs/README.md
- Update docs/roadmap.md
- Update project/README.md
- Update project/context.md
- Update quadlet/README.md

### Other
- Update .env.example
- Update backend/Dockerfile
- Update backend/config.py
- Update backend/database.py
- Update backend/routers/audit.py
- Update backend/routers/auth.py
- Update backend/routers/webhook.py
- Update backend/scans.db
- Update backend/server.py
- Update docker-compose.override.yml
- ... and 25 more files

## [0.1.5] - 2026-04-10

### Docs
- Update README.md

### Other
- Update backend/scans.db
- Update e2e/specs/metrics.spec.js
- Update frontend/vite.config.js

## [0.1.4] - 2026-04-10

### Docs
- Update README.md
- Update backend/code2llm_output/README.md
- Update backend/code2llm_output/context.md
- Update docs/README.md
- Update e2e/README.md
- Update project/README.md
- Update project/context.md

### Other
- Update Makefile
- Update backend/code2llm_output/analysis.json
- Update backend/routers/mcp.py
- Update backend/routers/system.py
- Update backend/scans.db
- Update backend/server.py
- Update backend/server_new.py
- Update e2e/playwright.config.js
- Update e2e/specs/demo-login.spec.js
- Update e2e/specs/demo-mode.spec.js
- ... and 20 more files

## [0.1.3] - 2026-04-10

### Docs
- Update README.md

### Other
- Update e2e/specs/recent-scans.spec.js

## [0.1.2] - 2026-04-10

### Docs
- Update README.md

### Other
- Update backend/scans.db
- Update backend/tests/test_auth.py
- Update docker-compose.override.yml
- Update frontend/src/App.jsx
- Update frontend/src/components/phases/AuthPhase.jsx
- Update frontend/src/components/phases/LandingPhase.jsx
- Update frontend/src/hooks/useAppState.js
- Update traefik/generate-certs.sh
- Update traefik/traefik.yml

## [0.1.1] - 2026-04-10

### Docs
- Update DOCS.md
- Update README.md
- Update docs/MCP.md
- Update docs/README.md
- Update docs/api.md
- Update docs/architecture.md
- Update docs/getting-started.md
- Update e2e/README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/backend/test_audit.py
- Update tests/backend/test_mcp.py
- Update tests/backend/test_scoring.py
- Update tests/backend/test_webhook.py
- Update tests/conftest.py

### Other
- Update .env.example
- Update .gitignore
- Update Makefile
- Update backend/.gitignore
- Update backend/Dockerfile
- Update backend/config.py
- Update backend/database.py
- Update backend/pytest.ini
- Update backend/routers/audit.py
- Update backend/routers/auth.py
- ... and 71 more files

