# Semcod GitHub App


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.3-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.90-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-4.2h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.9000 (6 commits)
- 👤 **Human dev:** ~$425 (4.2h @ $100/h, 30min dedup)

Generated on 2026-04-10 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

**One-click Audit · PR Comment Bot · Code Health Badge**

Zautomatyzowany pipeline jakości kodu jako GitHub App — od podłączenia repo do badge w README w 60 sekund.

```
semcod-github-app/
├── backend/                 # FastAPI server
│   ├── server.py           # Główny serwer (OAuth, Webhook, Badge, Audit pipeline)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── App.jsx         # Główny komponent (3 taby: Audit, PR Bot, Badge)
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── articles/               # 28 artykułów WordPress (Markdown + frontmatter)
├── .github/workflows/
│   └── deploy.yml          # CI/CD: build + deploy
├── docker-compose.yml      # Pełny deployment stack
├── github-app-manifest.json # Manifest do rejestracji GitHub App
├── .env.example
├── SETUP.md                # Szczegółowa instrukcja wdrożenia
└── README.md               # Ten plik
```

## Szybki start

### 1. Zarejestruj GitHub App

```bash
# Idź do https://github.com/settings/apps/new
# Użyj github-app-manifest.json jako template
# Zapisz credentials do .env
cp .env.example .env
# Uzupełnij: GITHUB_APP_ID, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_WEBHOOK_SECRET
```

### 2. Backend

```bash
cd backend/
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend/
npm install
npm run dev
# → http://localhost:5173
```

### 4. Produkcja (Docker)

```bash
docker-compose up -d
# Backend: :8000, Frontend: :3000
```

## Co jest w paczce

### Backend (`server.py`)
- **OAuth flow** — `/auth/github` → GitHub → `/auth/callback` → token
- **One-click Audit** — `/api/audit` → background pipeline (code2llm → redup → pyqual → regix) → raport JSON
- **PR Comment Bot** — `/webhook/github` → analiza plików PR → komentarz Markdown z metrykami
- **Badge SVG** — `/badge/{owner-repo}.svg` → dynamiczny shields.io-style badge
- **Webhook security** — HMAC-SHA256 signature verification

### Frontend (`App.jsx`)
- **Tab: One-click Audit** — OAuth → wybór repo → animowany skan → raport z grade circle, metrykami, language bar, rekomendacjami z komendami ReDSL/redup/pyqual
- **Tab: PR Bot** — realistyczny preview komentarza GitHub (tabela metryk, flagi ryzyka, sugestie)
- **Tab: Badge** — generator kodu Markdown/HTML z live preview badge'ów

### Artykuły (`articles/`)
28 artykułów WordPress-ready (Markdown + YAML frontmatter):
- 1 overview ekosystemu Semcod
- 1 strategia biznesowa
- 26 artykułów per-projekt (code2llm, pyqual, redup, regix, vallm, llx, proxym, preLLM, goal, planfile, pfix, algitex, metrun, nfo, cost, code2docs, domd, clickmd, toonic, code2logic, prefact, qualbench, weekly, pactfix, heal, ats-benchmark)

## Endpointy API

| Endpoint | Metoda | Opis |
|----------|--------|------|
| `GET /auth/github` | OAuth start |
| `GET /auth/callback` | OAuth callback → redirect z tokenem |
| `GET /api/repos?token=` | Lista repozytoriów użytkownika |
| `POST /api/audit` | Uruchom audyt `{repo, token}` → `{audit_id}` |
| `GET /api/audit/{id}` | Pobierz wynik audytu |
| `POST /webhook/github` | Webhook (PR bot, instalacje) |
| `GET /badge/{owner-repo}.svg` | Badge SVG |
| `GET /api/health` | Health check |
| `GET /mcp/info` | MCP server info |
| `GET /mcp/resources` | MCP resources list |
| `POST /mcp/invoke` | MCP tool invocation |

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

## Model cenowy (rekomendowany)

| Tier | Cena | Co dostaje |
|------|------|-----------|
| **Free** | $0 | Public repo, 3 skany/mies., badge, PR bot (metrics only) |
| **Pro** | $9/mies. | Private repo, unlimited, PR bot + auto-fix suggestions |
| **Team** | $29/mies. | Org-wide, dashboard, custom rules, priority support |

## Dokumentacja

📖 **[Pełna dokumentacja](https://semcod.github.io/www/)** - dostępna na GitHub Pages

- [Getting Started](./docs/getting-started.md) - Szybki start
- [API Reference](./docs/api.md) - Dokumentacja API
- [Architecture](./docs/architecture.md) - Architektura systemu
- [MCP Integration](./docs/MCP.md) - Integracja z AI

## Licencja

Apache-2.0
