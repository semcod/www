# Semcod

**One-click Audit · PR Comment Bot · Code Health Badge · MCP Integration**

Zautomatyzowany pipeline jakości kodu z GitHub OAuth — od podłączenia repo do badge w README w 60 sekund.

## ✅ **Current Status: Production Ready**

- 🔐 **GitHub OAuth Authentication** - Complete OAuth flow with mock GitHub for development
- 🚀 **One-click Audit** - Automated code analysis with detailed reports
- 🤖 **PR Comment Bot** - Automatic pull request analysis and comments
- 🏆 **Code Health Badges** - Dynamic SVG badges for README files
- 🔌 **MCP Integration** - Model Context Protocol for AI assistants
- 🐳 **Docker Ready** - Complete containerization with mock GitHub
- 🧪 **Comprehensive Testing** - Unit, integration, and E2E tests

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

### 2. Uruchomienie deweloperskie (rekomendowane)

```bash
# Zainstaluj zależności i uruchom obie usługi
make install
make dev

# Usługi dostępne na:
# Frontend: http://localhost:5174
# Backend:  http://localhost:8200
```

### 3. Uruchomienie z Docker Compose

```bash
# Z mock GitHub (dewelopment)
docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d

# Produkcja (wymaga prawdziwych credentials GitHub)
docker compose up -d

# Dostępne na:
# Frontend: http://localhost:3000
# Backend:  http://localhost:8003
# Mock GitHub: http://localhost:4010
```

### 4. Produkcja VPS (Podman Quadlet)

Zobacz [quadlet/README.md](./quadlet/README.md) — systemd + Traefik + Let's Encrypt.

### 5. Testowanie

```bash
# Szybkie testy jednostkowe
make test-fast

# Pełne testy E2E (wymaga uruchomionych usług)
make test-e2e
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

## MCP Integration

Semcod supports [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for AI assistant integration. AI assistants can programmatically:
- Start audits: `POST /mcp/invoke` with `{"name": "start_audit"}`
- Check scan status: `{"name": "get_scan_status"}`
- Query metrics: `GET /mcp/resources/content?uri=metrics://summary`

📚 [Full MCP Documentation](./docs/MCP.md)

## 🛠️ Makefile - Najważniejsze komendy

### Środowisko deweloperskie
```bash
make install          # Instaluje zależności (backend + frontend)
make dev              # Uruchom backend + frontend (http://localhost:8200/5174)
make dev-backend      # Tylko backend (port 8200)
make dev-frontend     # Tylko frontend (port 5174)
```

### Docker i deployment
```bash
make certs            # Generuje certyfikaty HTTPS dla semcod.localhost
make docker-up        # Uruchom Docker Compose + Traefik HTTPS
make docker-down      # Zatrzymaj kontenery Docker
make build            # Buduje frontend do produkcji
```

### Testowanie
```bash
make test             # Wszystkie testy
make test-fast        # Szybkie testy jednostkowe (~2s)
make test-backend     # Testy backendu (pytest)
make test-e2e         # Testy E2E (Playwright headless)
make test-e2e-ui      # Testy E2E z UI (headed)
```

### Jakość kodu
```bash
make quality          # Uruchom quality gate
make quality-baseline # Zapisz baseline jakości
make pre-commit-install # Instaluj pre-commit hook
```

### Czyszczenie
```bash
make clean            # Czyści zależności i cache
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
| `APP_URL` | `http://localhost:9000` | URL backendu |
| `FRONTEND_URL` | `http://localhost:5173` | URL frontendu |
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
- [KPI Product Plan](./docs/benchmark-kpi-product-plan.md) - Plan zmian UI/API

### 🔧 Inne
- [REFACTORING-SUMMARY.md](./REFACTORING-SUMMARY.md) - Podsumowanie refaktoryzacji OAuth
- [DEMO-REMOVAL-SUMMARY.md](./DEMO-REMOVAL-SUMMARY.md) - Usunięcie demo login
- [FINAL-TEST-REPORT.md](./FINAL-TEST-REPORT.md) - Raport końcowych testów

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
