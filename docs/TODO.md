# Semcod — TODO

## ✅ Done (2026-04-12)

### 🔥 Critical Bug Fixes
- **Marketplace artifact generation fixed** — billing recording was dead code (indentation bug in deploy.py:99-105)
- **Missing API functions added** — `triggerAutoFix()` and `triggerRedslAutoPR()` in `api.js`
- **Step 3: Generate Artifact UI** — MarketplaceDashboard now has buttons for Auto-fix PR and reDSL Refactor PR

### 🧪 Testing
- **95 Playwright E2E tests** — 4 new spec files covering full user flow:
  - `customer-journey.spec.js` — landing → sandbox scan → marketplace
  - `marketplace-flow.spec.js` — apps → install → billing → autofix artifact
  - `auth-flow.spec.js` — OAuth → repos → audit → badge
  - `redsl-flow.spec.js` — ReDSL status → health → refactor → badge
- **Backend marketplace tests** — 4 new tests for autofix deploy endpoint including regression test

### ✨ Features Completed
- **Marketplace 3-step flow:**
  1. Select Repository (OAuth repo list)
  2. Preview & Configure (apps + InstallButton + "Generate Artifact" button)
  3. **Generate Artifact** — 🤖 Auto-fix PR / 🔄 reDSL Refactor PR
- **ReDSL Integration** — /api/redsl/* endpoints, health score, badge
- **Auto-PR endpoints** — `/api/autopr` (LLM patches) + `/api/autopr/redsl` (DSL refactor)

## ✅ Done (2026-04-10)

- **Bug fix:** sandbox/guest scans not appearing in recent scans — `save_scan()` was missing in both pipeline functions
- **Config:** all hardcoded values extracted to `.env` (20 variables: `DB_PATH`, `SCAN_HISTORY_LIMIT`, `REPOS_PER_PAGE`, `GITHUB_OAUTH_SCOPE`, `CORS_ORIGINS`, `LARGE_FILE_THRESHOLD`, etc.)
- **Network:** Docker containers accessible from LAN via `http://nvidia:3000` (frontend) and `http://nvidia:8003` (backend)
- **Docs:** README, CHANGELOG, .env.example updated

## 📋 Next

### Product / Biznes
- Walidacja co nowego wykrywa skan — czy to nowa jakość?
- Propozycja co może zostać poprawione po skanie
- Pytanie do użytkownika: wdrożyć na swoim GitHub/GitLab czy na naszym środowisku?
- Nasze środowisko bezplatne przez 1 miesiąc → oferować od razu generowanie automatyzacji z opcją PR
- Druga opcja: automatyzacja na GitLab/GitHub z opcją deploymentu na naszej infra
- Z partnerami: środowisko uruchomieniowe + generowanie automatyczne na bazie ticketów (zmiany, bugfix, features)
- Marketplace: oferowanie deploymentu artefaktów (SaaS, desktop, mobile) — płatne, z łatwą dystrybucją i rozliczaniem (tokeny, czas, usługa)

### Tech
- [x] Testy E2E dla sandbox scans w recent scans — `e2e/specs/sandbox-recent-scans.spec.js` (5 scenariuszy)
- [x] Quadlet: update `semcod-backend.container` z nowymi env vars (`DATABASE_URL`, `REDIS_URL`, `SESSION_EXPIRE_HOURS`, `DEMO_MODE`, `GITHUB_PRIVATE_KEY_PATH`)
- [x] Quadlet README: update env vars list — pełna lista z sekcjami (GitHub, GitLab, Gitea, App, DB, Redis, Stripe)
- [x] CI/CD: GitHub Actions deploy z nowymi env vars — `quality-gate` job, pytest z env, Write .env step, deploy via SSH + `alembic upgrade head`



można też dodać paczke python semcod ktora bedzie robiła te metryki przez cli shell, api rest i api mcp
