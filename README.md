# Semcod

**One-click Audit · PR Comment Bot · Code Health Badge · MCP Integration · Marketplace Auto-Fix**

Semcod to zautomatyzowana platforma CI/CD jakości kodu. Umożliwia deweloperom ciągły audyt repozytoriów, automatyczne komentarze w PR, oraz generowanie auto-fix Pull Requestów przez AI (reDSL). 

## 🎯 **Project Purpose (Test Project)**

Ten projekt służy jako **kompletna platforma SaaS do analizy jakości kodu** z następującymi scenariuszami użycia:

### Scenariusze Użycia (User Stories)

#### 1. 🔐 **GitHub OAuth → Audit (One-click)**
- Użytkownik klika "Connect GitHub" → OAuth → wybiera repo → klikna "Audit"
- System skanuje kod (code2llm → redup → pyqual → regix) i generuje raport z grade (A-F)
- Wynik: raport z metrykami, rekomendacjami, health score

#### 2. 🏆 **Sandbox Mode (bez logowania)**
- Użytkownik wpisuje URL publicznego repo np. `https://github.com/torvalds/linux`
- Klikna "Analyze" → system skanuje bez autoryzacji
- Wynik: ten sam raport, ale oznaczony "Sandbox" badge

#### 3. 🛒 **Marketplace → Install → Auto-fix PR (Full Flow)**
- **Step 1**: Marketplace tab → Select Repository z listy OAuth
- **Step 2**: Preview & Configure → Install App (webhook setup)
- **Step 3**: **Generate Artifact** → wybiera między:
  - 🤖 **Auto-fix PR** — patch generator (trailing whitespace, blank lines)
  - 🔄 **reDSL Refactor PR** — 15 DSL refactor actions (SPLIT_MODULE, REDUCE_FAN_OUT, EXTRACT_FUNCTIONS)
- System tworzy branch, commituje zmiany, otwiera PR na GitHub
- Wynik: PR URL z auto-fixami, task_id do trackowania w Celery

#### 4. 🤖 **PR Comment Bot (GitHub App)**
- Użytkownik instaluje GitHub App na repo
- Każdy nowy PR triggeruje webhook → analiza zmian → komentarz z metrykami
- Wynik: automatyczny code review w PR

#### 5. 🏷️ **Badge Generator**
- Użytkownik kopiuje Markdown badge z panelu
- Wkleja do README → dynamiczny SVG z health score
- Wynik: `![Code Health](https://semcod.com/badge/owner-repo.svg)`

#### 6. 🎫 **Ticket-driven Auto-PR (NEW)**
- **Step 1**: Użytkownik tworzy ticket w panelu Semcod:
  - Typ: `feature` (nowa funkcja) lub `bugfix` (naprawa usterki)
  - Tytuł: np. "Dodaj paginację do listy użytkowników"
  - Opis: szczegóły zmiany lub stack trace błędu
  - Target repo: wybór z zainstalowanych repozytoriów
- **Step 2**: System analizuje ticket przez reDSL:
  - `redsl.decide()` — ocena gdzie w kodzie wprowadzić zmiany
  - `redsl.refactor()` — automatyczna refaktoryzacja dla nowego feature
  - Lokalizacja plików do modyfikacji na podstawie opisu ticketu
- **Step 3**: Auto-generacja PR:
  - Tworzony jest branch `ticket-{id}-{typ}`
  - reDSL commituje zmiany (nowe funkcje lub fixy)
  - Otwierany jest PR na GitHub z linkiem do ticketu
  - W PR: komentarz z opisem zmian i referencją do ticketu
- **Step 4**: Aktualizacja ticketu:
  - Status zmienia się na `in_progress` → `pr_created` → `merged`
  - Po merge ticket automatycznie zamykany
- Wynik: **Pełna automatyzacja od zgłoszenia do wdrożenia**

## ✅ **Current Status: Production Ready**

- 🔐 **GitHub OAuth Authentication** - Complete OAuth flow with mock GitHub for development
- 🚀 **One-click Audit** - Automated code analysis with detailed reports
- 🤖 **PR Comment Bot** - Automatic pull request analysis and comments
- 🏆 **Code Health Badges** - Dynamic SVG badges for README files
- 🔌 **MCP Integration** - Model Context Protocol for AI assistants
- 📊 **Benchmark KPI MVP** - Instrumentacja do zbierania metryk benchmarkowych (cases, feedback, decisions, export)
- 🔄 **ReDSL Integration** - Automatyczna refaktoryzacja kodu przez DSL (analyze, refactor, health score, auto-PR)
- 🛒 **Marketplace Auto-Fix** — 3-step flow: select repo → install → generate artifact (PR)
- 🐳 **Docker Ready** - Complete containerization with mock GitHub
- 🧪 **Comprehensive Testing** - Unit, integration, and E2E tests (95 Playwright tests)

![Version](https://img.shields.io/badge/version-1.0.0-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![OAuth](https://img.shields.io/badge/OAuth-GitHub-green) ![Mock](https://img.shields.io/badge/Mock-Enabled-orange)

```
semcod/
├── backend/                 # FastAPI server
│   ├── server.py           # Główny serwer (CORS, routers)
│   ├── config.py           # Konfiguracja z env (20 zmiennych)
│   ├── database.py         # SQLite persistence (scans, users)
│   ├── store.py            # In-memory cache (audit_results, badge_cache, scan_history)
│   ├── routers/
│   │   ├── audit.py        # Audit pipeline + sandbox analysis
│   │   ├── auth.py         # GitHub OAuth authentication
│   │   ├── webhook.py      # GitHub webhook (PR bot)
│   │   ├── badge.py        # SVG badge generator
│   │   ├── metrics.py      # Standardized metrics API
│   │   ├── mcp.py          # Model Context Protocol
│   │   └── system.py       # Health check, domain config
│   ├── services/
│   │   ├── analyzer.py     # code2llm, redup, pyqual runners
│   │   ├── scoring.py      # Health score, grades, recommendations
│   │   └── github_client.py # GitHub App JWT auth
│   └── Dockerfile
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── App.jsx         # Główny komponent
│   │   ├── api.js          # API client
│   │   ├── config.js       # Frontend config (VITE_ vars)
│   │   ├── constants.js    # Colors, grades, configuration data
│   │   ├── hooks/          # useAppState (URL hash routing)
│   │   ├── components/     # Phases, tabs, shared UI
│   │   └── screens/        # Screen layouts
│   └── Dockerfile
├── quadlet/                # Podman Quadlet (systemd deployment)
├── traefik/                # Traefik config (local HTTPS + production)
├── articles/               # 28 artykułów WordPress
├── .env.example            # Wszystkie zmienne konfiguracyjne
├── docker-compose.yml      # Production stack
├── docker-compose.sim.yml  # Mock GitHub simulation (development)
└── README.md
```

## 📋 **Wymagania systemowe**

- **Python 3.9+** - Backend FastAPI
- **Node.js 16+** - Frontend React + Vite
- **Docker & Docker Compose** - Konteneryzacja (opcjonalne)
- **Git** - Wersjonowanie kodu

---

## 🚀 Szybki start

### 1. Instalacja i konfiguracja

```bash
# Sklonuj repozytorium
git clone <repository-url>
cd semcod/www

# Skonfiguruj środowisko
cp .env.example .env
# Dla dewelopmentu z mock GitHub - zmienne są już ustawione
# Dla produkcji - uzupełnij GITHUB_APP_ID, GITHUB_CLIENT_ID, etc.
```

### 2. Uruchomienie deweloperskie

```bash
# Lokalnie (Vite :5174 + backend :8200)
make dev

# Lub z Docker + mock GitHub (rekomendowane)
make sim

# Usługi dostępne na:
# Lokalnie:  Frontend http://localhost:5174, Backend http://localhost:8200
# Docker:    Frontend http://localhost:3000, Backend http://localhost:8003, Mock GH http://localhost:4010
```

Pełna lista komend: `make help`

### 3. Uruchomienie z Docker Compose

```bash
# Z mock GitHub (dewelopment) — równoważne: make sim
make sim

# Produkcja (wymaga prawdziwych credentials GitHub) — równoważne: make up
make up

# Zatrzymanie: make down  lub  make sim-down

# Dostępne na:
# Frontend: http://localhost:3000
# Backend:  http://localhost:8003
# Mock GitHub: http://localhost:4010
# ReDSL: http://localhost:8030
```

### 4. Produkcja VPS (Podman Quadlet)

Zobacz [quadlet/README.md](./quadlet/README.md) — systemd + Traefik + Let's Encrypt.

### 5. Testowanie

```bash
# Testy jednostkowe backend
make test

# Pełne testy backend
make test-all

# E2E Playwright (wymaga make sim lub make dev)
make e2e

# E2E na lokalnym dev serwerze
make e2e-dev

# Instalacja Playwright (pierwszy raz)
make e2e-install
```

---

## 📊 **Performance & Metrics**

### 🚀 **System Performance**
- **Audit completion:** ~30-60 seconds (depending on repository size)
- **API response time:** <200ms for most endpoints
- **Database:** SQLite with in-memory caching for speed
- **Frontend build:** <30 seconds production build
- **Docker startup:** <10 seconds full stack

### 📈 **Scalability Features**
- **Background processing** - Async audit pipeline
- **Redis caching** - Session and result caching
- **Database pooling** - Efficient connection management
- **Load balancing ready** - Traefik integration
- **Horizontal scaling** - Stateless services

### 🧪 **Test Coverage**
- **Unit tests:** Backend pytest with markers
- **Integration tests:** API endpoint testing
- **E2E tests:** Playwright GUI automation
- **Performance tests:** Load testing capabilities
- **Quality gates:** Automated code quality checks

## Co jest w paczce

### Backend
- **GitHub OAuth flow** — `/auth/github` → Mock GitHub → `/auth/callback` → JWT session
- **One-click Audit** — `/api/audit` → background pipeline (code2llm → redup → pyqual → regix) → raport JSON
- **Sandbox Analysis** — `/api/analyze` → public repo bez autoryzacji
- **PR Comment Bot** — `/webhook/github` → analiza plików PR → komentarz Markdown z metrykami
- **Badge SVG** — `/badge/{owner-repo}.svg` → dynamiczny shields.io-style badge
- **Scan History** — `/api/scans/recent` → SQLite + in-memory fallback
- **MCP Server** — `/mcp/*` → Model Context Protocol dla AI
- **Benchmark KPI** — `/api/benchmark/*` → cases, feedback, decisions, events, summary, export CSV/JSON
- **ReDSL Engine** — `/api/redsl/*` → analyze, refactor, health score, batch-hybrid, badge generation
- **Webhook security** — HMAC-SHA256 signature verification
- **Mock GitHub integration** — pełne symulowanie OAuth flow dla dewelopmentu

### Frontend
- **Tab: Audit** — OAuth → wybór repo → animowany skan → raport z grade, metrykami, rekomendacjami
- **Tab: Recent Scans** — lista ostatnich skanów z metrykami i share buttons
- **Tab: Badge** — generator kodu Markdown/HTML z live preview badge'ów
- **Sandbox mode** — skanowanie publicznych repo bez logowania

### Deployment
- **Docker Compose** — lokalny dev z Traefik HTTPS + LAN access
- **Podman Quadlet** — produkcja VPS z systemd + Let's Encrypt
- **20 zmiennych env** — pełna konfiguracja bez hardkodu (zobacz `.env.example`)

## Endpointy API

| Endpoint | Metoda | Opis |
|----------|--------|------|
| `GET /auth/github` | GET | GitHub OAuth start |
| `GET /auth/callback` | GET | OAuth callback → redirect z tokenem |
| `GET /api/me` | GET | Profil użytkownika |
| `GET /api/repos` | GET | Lista repozytoriów użytkownika |
| `POST /api/audit` | POST | Uruchom audyt `{repo}` → `{audit_id}` |
| `POST /api/analyze` | POST | Sandbox analysis `{repo_url, sandbox}` |
| `GET /api/audit/{id}` | GET | Pobierz wynik audytu |
| `GET /api/scans/recent` | GET | Ostatnie skany z metrykami |
| `GET /api/metrics/standard` | GET | Standaryzowane metryki |
| `GET /api/config/domain` | GET | Konfiguracja domeny |
| `GET /api/health` | GET | Health check |
| `POST /webhook/github` | POST | Webhook (PR bot, instalacje) |
| `GET /badge/{owner-repo}.svg` | GET | Badge SVG |
| `GET /mcp/info` | GET | MCP server info |
| `GET /mcp/resources` | GET | MCP resources list |
| `POST /mcp/invoke` | POST | MCP tool invocation |
| **Benchmark KPI** | | |
| `POST /api/benchmark/cases` | POST | Create benchmark case |
| `GET /api/benchmark/cases` | GET | List benchmark cases |
| `GET /api/benchmark/cases/{id}` | GET | Get benchmark case |
| `PATCH /api/benchmark/cases/{id}` | PATCH | Update benchmark case |
| `POST /api/benchmark/cases/{id}/decision` | POST | Submit deployment decision |
| `POST /api/benchmark/cases/{id}/recommendations/{rid}/feedback` | POST | Submit recommendation feedback |
| `POST /api/benchmark/cases/{id}/events` | POST | Track benchmark event |
| `GET /api/benchmark/summary` | GET | Benchmark KPI summary |
| `GET /api/benchmark/export.json` | GET | Export benchmark data (JSON) |
| `GET /api/benchmark/export.csv` | GET | Export benchmark data (CSV) |
| **ReDSL** | | |
| `GET /api/redsl/status` | GET | ReDSL engine status |
| `POST /api/redsl/analyze` | POST | Run reDSL analysis |
| `POST /api/redsl/health` | POST | Get project health score |
| `POST /api/redsl/refactor` | POST | Run reDSL refactoring |
| `POST /api/redsl/decide` | POST | Evaluate DSL rules (dry-run) |
| `POST /api/redsl/batch-hybrid` | POST | Hybrid quality refactoring |
| `GET /api/redsl/badge/{owner}/{repo}` | GET | SVG health badge |

## MCP Integration

Semcod supports [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for AI assistant integration. AI assistants can programmatically:
- Start audits: `POST /mcp/invoke` with `{"name": "start_audit"}`
- Check scan status: `{"name": "get_scan_status"}`
- Query metrics: `GET /mcp/resources/content?uri=metrics://summary`

📚 [Full MCP Documentation](./docs/MCP.md)

## 🛠️ Makefile - Najważniejsze komendy

Pełna lista: `make help`

### Środowisko deweloperskie
```bash
make install          # Instaluje zależności (backend + frontend + e2e)
make dev              # Lokalnie: backend :8200 + Vite :5174
make backend          # Tylko backend (port 8200)
make frontend         # Tylko frontend Vite (port 5174)
```

### Docker + Mock GitHub
```bash
make sim              # Docker + mock GitHub (frontend :3000, backend :8003, mock :4010)
make sim-down         # Zatrzymaj stack z mock GitHub
make up               # Docker production stack
make down             # Zatrzymaj production stack
```

### Testowanie
```bash
make test             # Backend pytest (bez slow)
make test-all         # Pełne testy backend
make e2e              # Playwright E2E na Docker (port 3000)
make e2e-dev          # Playwright E2E na lokalnym dev (port 5174)
make e2e-install      # Instaluj Playwright Chromium
```

### Jakość kodu i utilities
```bash
make lint             # ruff lint + format check
make logs             # Tail Docker logs (backend, frontend, worker)
make ps               # Pokaż kontenery Docker
make clean            # Czyści cache i node_modules
```

### Testy - szczegóły
Testy są oznaczone markerami:
- `@pytest.mark.fast` - szybkie testy bez zewnętrznych zależności
- `@pytest.mark.unit` - izolowane testy jednostkowe  
- `@pytest.mark.integration` - testy integracyjne
- `@pytest.mark.slow` - wolne testy (domyślnie pomijane w `test-fast`)

## 🔧 Zmienne środowiskowe

Wszystkie ustawienia w `.env` — bez hardkodu w kodzie. Pełna lista w `.env.example`:

### GitHub OAuth Configuration
| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `GITHUB_APP_ID` | | GitHub App ID |
| `GITHUB_CLIENT_ID` | | OAuth Client ID |
| `GITHUB_CLIENT_SECRET` | | OAuth Client Secret |
| `GITHUB_WEBHOOK_SECRET` | | Webhook signing secret |
| `GITHUB_PRIVATE_KEY_PATH` | `private-key.pem` | Ścieżka do klucza prywatnego |
| `GITHUB_OAUTH_SCOPE` | `repo,read:org` | OAuth scope |

### Mock GitHub Configuration (dewelopment)
| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `MOCK_GITHUB_CLIENT_ID` | `Iv1.mock_test_client` | Mock OAuth Client ID |
| `MOCK_GITHUB_CLIENT_SECRET` | `mock_secret_for_testing` | Mock OAuth Client Secret |
| `MOCK_GITHUB_APP_ID` | `999999` | Mock GitHub App ID |
| `MOCK_GITHUB_WEBHOOK_SECRET` | `whsec_mock_test` | Mock Webhook Secret |
| `MOCK_USER_LOGIN` | `tom-sapletta-com` | Mock user login |
| `MOCK_USER_NAME` | `Tom Sapletta` | Mock user name |
| `MOCK_USER_EMAIL` | `tom@sapletta.com` | Mock user email |
| `MOCK_USER_ID` | `5669315` | Mock user ID |
| `MOCK_USER_BIO` | `Architect & Developer` | Mock user bio |
| `MOCK_USER_COMPANY` | `Softreck` | Mock user company |
| `MOCK_USER_LOCATION` | `Gdańsk, Poland` | Mock user location |
| `MOCK_USER_AVATAR_URL` | | Mock user avatar URL |
| `MOCK_USER_PUBLIC_REPOS` | `150` | Mock user public repos count |

### Application Configuration
| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `APP_URL` | `http://localhost:8003` | URL backendu (Docker) / `:8200` (local) |
| `FRONTEND_URL` | `http://localhost:3000` | URL frontendu (Docker) / `:5174` (local) |
| `PUBLIC_URL` | `$APP_URL` | Publiczny URL |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `9000` | Port backendu |
| `SECRET_KEY` | `dev-secret-change-me` | Klucz JWT (zmień w produkcji!) |
| `SESSION_EXPIRE_HOURS` | `168` | Czas wygaśnięcia sesji (7 dni) |
| `DB_PATH` | `scans.db` | Ścieżka do SQLite |
| `SCAN_HISTORY_LIMIT` | `100` | Limit skanów w pamięci |
| `REPOS_PER_PAGE` | `30` | Repozytoria na stronę |
| `CORS_ORIGINS` | `$FRONTEND_URL,https://semcod.com` | Dozwolone origins |
| `LARGE_FILE_THRESHOLD` | `300` | Próg zmian w pliku (PR bot) |

## 📚 Dokumentacja

### 🚀 Szybki start
- [Getting Started](./docs/getting-started.md) - Szybki start i instalacja
- [Platform Overview](./docs/01-semcod-platform-overview.md) - Przegląd platformy

### 🏗️ Architektura i API
- [Architecture](./docs/architecture.md) - Architektura systemu
- [API Reference](./docs/api.md) - Dokumentacja API
- [MCP Integration](./docs/MCP.md) - Integracja z AI asystentami

### 🚀 Deployment
- [Quadlet Deployment](./quadlet/README.md) - VPS z Podman + systemd
- [Platform Status](./docs/02-semcod-www-status.md) - Status platformy

### 📈 Roadmap i planowanie
- [Roadmap](./docs/roadmap.md) - Roadmapa rozwoju
- [Complete Roadmap](./docs/semcod-complete-roadmap.md) - Szczegółowa roadmapa
- [Marketplace Business](./docs/04-semcod-marketplace-business.md) - Model biznesowy

### 📊 Benchmark i walidacja
- [Validation Benchmark](./docs/validation-benchmark.md) - Plan benchmarku i KPI
- [Benchmark Checklist](./docs/validation-benchmark-checklist.md) - Checklista wykonawcza
- [Benchmark Template](./docs/validation-benchmark-template.md) - Szablon przypadków testowych
- [Benchmark CSV Template](./docs/validation-benchmark-template.csv) - Szablon CSV do wyników
- [KPI Product Plan](./docs/benchmark-kpi-product-plan.md) - Plan zmian UI/API (Etap 1 ✅ zakończony)

### 🔄 ReDSL (Refactoring DSL)
- [ReDSL Engine Status](./docs/03-redsl-engine-status.md) - Status silnika refaktoryzacji
- API endpoints: `/api/redsl/*` — analyze, refactor, health, decide, batch-hybrid, badge

### 🔧 Inne
- [REFACTORING-SUMMARY.md](./docs/REFACTORING-SUMMARY.md) - Podsumowanie refaktoryzacji OAuth
- [DEMO-REMOVAL-SUMMARY.md](./docs/DEMO-REMOVAL-SUMMARY.md) - Usunięcie demo login
- [FINAL-TEST-REPORT.md](./docs/FINAL-TEST-REPORT.md) - Raport końcowych testów

## 🔧 **Troubleshooting**

### Common Issues

#### **Port conflicts**
```bash
# Jeśli porty są zajęte, zmień je w .env:
BACKEND_PORT=8201
FRONTEND_PORT=5175
```

#### **Python virtual environment issues**
```bash
# Clean setup
make clean
make install
```

#### **Docker issues**
```bash
# Reset Docker containers
docker compose down -v
docker compose up -d
```

#### **Mock GitHub not working**
```bash
# Check mock GitHub status
curl http://localhost:4010/health

# Should return:
{"status": "ok", "mode": "github-simulation", "users": ["tom-sapletta-com"]}
```

#### **Frontend build issues**
```bash
# Clean and rebuild
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

---

## 📚 **Dokumentacja**

📖 **[Pełna dokumentacja](https://semcod.github.io/www/)** - dostępna na GitHub Pages

## Licencja

Apache-2.0
