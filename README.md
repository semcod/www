# Semcod


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.31-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$3.15-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-12.7h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $3.1500 (21 commits)
- 👤 **Human dev:** ~$1274 (12.7h @ $100/h, 30min dedup)

Generated on 2026-04-10 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

**One-click Audit · PR Comment Bot · Code Health Badge · MCP Integration**

Zautomatyzowany pipeline jakości kodu jako GitHub App — od podłączenia repo do badge w README w 60 sekund.

```
semcod/
├── backend/                 # FastAPI server
│   ├── server.py           # Główny serwer (CORS, routers)
│   ├── config.py           # Konfiguracja z env (20 zmiennych)
│   ├── database.py         # SQLite persistence (scans, users)
│   ├── store.py            # In-memory cache (audit_results, badge_cache, scan_history)
│   ├── routers/
│   │   ├── audit.py        # Audit pipeline + sandbox analysis
│   │   ├── auth.py         # OAuth + demo login
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
│   │   ├── constants.js    # Colors, grades, demo data
│   │   ├── hooks/          # useAppState (URL hash routing)
│   │   ├── components/     # Phases, tabs, shared UI
│   │   └── screens/        # Screen layouts
│   └── Dockerfile
├── quadlet/                # Podman Quadlet (systemd deployment)
├── traefik/                # Traefik config (local HTTPS + production)
├── articles/               # 28 artykułów WordPress
├── .env.example            # Wszystkie zmienne konfiguracyjne
├── docker-compose.yml      # Production stack
├── docker-compose.override.yml # Local dev (Traefik + demo mode)
└── README.md
```

## Szybki start

### 1. Konfiguracja

```bash
cp .env.example .env
# Uzupełnij: GITHUB_APP_ID, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_WEBHOOK_SECRET
# Dostosuj: APP_URL, FRONTEND_URL, CORS_ORIGINS (dla LAN: http://HOSTNAME:PORT)
```

### 2. Backend

```bash
cd backend/
pip install -r requirements.txt
uvicorn server:app --reload --port 9000
```

### 3. Frontend

```bash
cd frontend/
npm install
npm run dev
# → http://localhost:5173
```

### 4. Docker (LAN access)

```bash
docker compose up -d
# Frontend: http://nvidia:3000  Backend: http://nvidia:8003
# HTTPS: https://semcod.localhost
```

### 5. Podman Quadlet (produkcja VPS)

Zobacz [quadlet/README.md](./quadlet/README.md) — systemd + Traefik + Let's Encrypt.

## Co jest w paczce

### Backend
- **OAuth flow** — `/auth/github` → GitHub → `/auth/callback` → JWT session
- **Demo login** — `/auth/demo` (gdy `DEMO_MODE=1`)
- **One-click Audit** — `/api/audit` → background pipeline (code2llm → redup → pyqual → regix) → raport JSON
- **Sandbox Analysis** — `/api/analyze` → public repo bez autoryzacji
- **PR Comment Bot** — `/webhook/github` → analiza plików PR → komentarz Markdown z metrykami
- **Badge SVG** — `/badge/{owner-repo}.svg` → dynamiczny shields.io-style badge
- **Scan History** — `/api/scans/recent` → SQLite + in-memory fallback
- **MCP Server** — `/mcp/*` → Model Context Protocol dla AI
- **Webhook security** — HMAC-SHA256 signature verification

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
| `GET /auth/github` | GET | OAuth start |
| `GET /auth/callback` | GET | OAuth callback → redirect z tokenem |
| `POST /auth/demo` | POST | Demo login (DEMO_MODE=1) |
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

## Testowanie

```bash
# Szybkie testy (~2 sekundy) - tylko unit tests
make test-fast

# Wszystkie testy backendu
make test-backend

# Testy E2E (wymaga uruchomionego frontendu)
make test-e2e
```

Testy są oznaczone markerami:
- `@pytest.mark.fast` - szybkie testy bez zewnętrznych zależności
- `@pytest.mark.unit` - izolowane testy jednostkowe
- `@pytest.mark.integration` - testy integracyjne
- `@pytest.mark.slow` - wolne testy (domyślnie pomijane w `test-fast`)

## Zmienne środowiskowe

Wszystkie ustawienia w `.env` — bez hardkodu w kodzie. Pełna lista w `.env.example`:

| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `GITHUB_APP_ID` | | GitHub App ID |
| `GITHUB_CLIENT_ID` | | OAuth Client ID |
| `GITHUB_CLIENT_SECRET` | | OAuth Client Secret |
| `GITHUB_WEBHOOK_SECRET` | | Webhook signing secret |
| `GITHUB_PRIVATE_KEY_PATH` | `private-key.pem` | Ścieżka do klucza prywatnego |
| `GITHUB_OAUTH_SCOPE` | `repo,read:org` | OAuth scope |
| `APP_URL` | `http://localhost:9000` | URL backendu |
| `FRONTEND_URL` | `http://localhost:5173` | URL frontendu |
| `PUBLIC_URL` | `$APP_URL` | Publiczny URL |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `9000` | Port backendu |
| `SECRET_KEY` | `dev-secret-change-me` | Klucz JWT (zmień w produkcji!) |
| `SESSION_EXPIRE_HOURS` | `168` | Czas wygaśnięcia sesji (7 dni) |
| `DEMO_MODE` | `0` | Włącz demo login (`1` = tak) |
| `DB_PATH` | `scans.db` | Ścieżka do SQLite |
| `SCAN_HISTORY_LIMIT` | `100` | Limit skanów w pamięci |
| `REPOS_PER_PAGE` | `30` | Repozytoria na stronę |
| `CORS_ORIGINS` | `$FRONTEND_URL,https://semcod.com` | Dozwolone origins (comma-separated) |
| `LARGE_FILE_THRESHOLD` | `300` | Próg zmian w pliku (PR bot) |

## Dokumentacja

📖 **[Pełna dokumentacja](https://semcod.github.io/www/)** - dostępna na GitHub Pages

- [Getting Started](./docs/getting-started.md) - Szybki start
- [API Reference](./docs/api.md) - Dokumentacja API
- [Architecture](./docs/architecture.md) - Architektura systemu
- [Roadmap](./docs/roadmap.md) - Roadmapa walidacji wartości, automatyzacji i deploymentu
- [Validation Benchmark](./docs/validation-benchmark.md) - Plan benchmarku, KPI i pilota wdrożeniowego
- [Benchmark Checklist](./docs/validation-benchmark-checklist.md) - Checklista wykonawcza benchmarku
- [Benchmark Template](./docs/validation-benchmark-template.md) - Szablon Markdown do wypełniania przypadków
- [Benchmark CSV Template](./docs/validation-benchmark-template.csv) - Szablon CSV do zbierania wyników
- [Benchmark KPI Product Plan](./docs/benchmark-kpi-product-plan.md) - Plan zmian UI/API do zbierania KPI
- [MCP Integration](./docs/MCP.md) - Integracja z AI
- [Quadlet Deployment](./quadlet/README.md) - VPS z Podman + systemd

## Licencja

Apache-2.0
