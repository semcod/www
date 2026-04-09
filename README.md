# Semcod GitHub App

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

## Model cenowy (rekomendowany)

| Tier | Cena | Co dostaje |
|------|------|-----------|
| **Free** | $0 | Public repo, 3 skany/mies., badge, PR bot (metrics only) |
| **Pro** | $9/mies. | Private repo, unlimited, PR bot + auto-fix suggestions |
| **Team** | $29/mies. | Org-wide, dashboard, custom rules, priority support |

## Licencja

Apache-2.0
