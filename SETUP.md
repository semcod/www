# Semcod GitHub App — Setup & Deployment Guide

## Architektura

```
┌─────────────────────────────────────────────────────┐
│                   GitHub                              │
│  ┌─────────┐  ┌─────────┐  ┌──────────────────┐    │
│  │  OAuth   │  │ Webhook │  │  Badge endpoint  │    │
│  │  flow    │  │  PR bot │  │  (SVG in README) │    │
│  └────┬─────┘  └────┬────┘  └────────┬─────────┘    │
└───────┼──────────────┼───────────────┼───────────────┘
        │              │               │
        ▼              ▼               ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend (server.py)              │
│  ┌──────────┐ ┌──────────┐ ┌───────────────────┐   │
│  │/auth/*   │ │/webhook/ │ │/badge/*.svg       │   │
│  │One-click │ │PR Comment│ │Health Score Badge  │   │
│  │Audit     │ │Bot       │ │                    │   │
│  └────┬─────┘ └────┬────┘ └────────┬──────────┘   │
│       │             │               │               │
│       ▼             ▼               ▼               │
│  ┌──────────────────────────────────────────────┐   │
│  │          Pipeline (background tasks)          │   │
│  │  code2llm → redup → pyqual → regix → report  │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Szybki start (development)

### 1. Utwórz GitHub App

1. Idź do https://github.com/settings/apps/new
2. Użyj `github-app-manifest.json` jako template
3. Zapisz:
   - `App ID` → `GITHUB_APP_ID`
   - `Client ID` → `GITHUB_CLIENT_ID`  
   - `Client Secret` → `GITHUB_CLIENT_SECRET`
   - `Webhook Secret` → `GITHUB_WEBHOOK_SECRET`
4. Pobierz private key → zapisz jako `private-key.pem`

### 2. Konfiguracja

```bash
# Skopiuj .env
cp .env.example .env

# Uzupełnij dane z GitHub App
GITHUB_APP_ID=123456
GITHUB_CLIENT_ID=Iv1.abc123
GITHUB_CLIENT_SECRET=secret123
GITHUB_WEBHOOK_SECRET=whsec_123
APP_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

### 3. Uruchom backend

```bash
cd backend/
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

### 4. Uruchom frontend (React)

Frontend to plik `semcod-app.jsx` — React component z trzema tabami:
- **One-click Audit** — OAuth → wybór repo → skan → raport
- **PR Bot** — podgląd komentarza PR  
- **Badge** — generator badge do README

## Deployment (produkcja)

### Docker Compose

```bash
# Ustaw zmienne środowiskowe
export GITHUB_APP_ID=...
export GITHUB_CLIENT_ID=...
export GITHUB_CLIENT_SECRET=...
export GITHUB_WEBHOOK_SECRET=...

# Uruchom
docker-compose up -d
```

### VPS (Ubuntu)

```bash
# 1. Zainstaluj zależności
apt-get install -y python3-pip git nginx certbot
pip install -r backend/requirements.txt

# 2. Zainstaluj narzędzia Semcod
pip install code2llm redup pyqual regix vallm

# 3. Systemd service
cat > /etc/systemd/system/semcod.service << 'EOF'
[Unit]
Description=Semcod API
After=network.target

[Service]
User=semcod
WorkingDirectory=/opt/semcod
ExecStart=/usr/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
EnvironmentFile=/opt/semcod/.env

[Install]
WantedBy=multi-user.target
EOF

systemctl enable --now semcod

# 4. Nginx reverse proxy
cat > /etc/nginx/sites-available/semcod << 'EOF'
server {
    server_name api.semcod.dev;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/semcod /etc/nginx/sites-enabled/
certbot --nginx -d api.semcod.dev
```

## Endpointy API

| Endpoint | Metoda | Opis |
|----------|--------|------|
| `/auth/github` | GET | Start OAuth flow |
| `/auth/callback` | GET | OAuth callback |
| `/api/repos` | GET | Lista repozytoriów użytkownika |
| `/api/audit` | POST | Uruchom audyt (async) |
| `/api/audit/{id}` | GET | Pobierz wynik audytu |
| `/webhook/github` | POST | Webhook dla PR bot |
| `/badge/{owner-repo}.svg` | GET | Badge SVG |
| `/api/health` | GET | Health check |

## Webhook Events

| Event | Action | Reakcja |
|-------|--------|---------|
| `pull_request` | `opened` | Analiza zmian → komentarz z metrykami |
| `pull_request` | `synchronize` | Re-analiza → aktualizacja komentarza |
| `installation` | `created` | Log nowej instalacji |

## Model biznesowy (rekomendowany)

### Freemium

| Tier | Cena | Limit |
|------|------|-------|
| Free | $0 | Publiczne repo, 3 skany/mies., badge |
| Pro | $9/mies. | Prywatne repo, unlimited skany, PR bot |
| Team | $29/mies. | Org-wide, dashboard, custom rules, priority |

### Dlaczego nie audyty za 2-5k PLN?

1. **Tarcie**: formularz → wycena → decyzja → realizacja = 4+ kroki, każdy traci klientów
2. **Skalowalność**: ręczna realizacja = ograniczenie do 2-3 klientów/tydzień
3. **Adopcja**: developer nie zapłaci 2k za raport, ale zapłaci $9/mies. za narzędzie w workflow
4. **Virality**: badge w README → każdy widzi → klika → sprawdza swoje repo → konwertuje

### Jak sprzedawać ReDSL?

ReDSL nie jest produktem do sprzedaży bezpośredniej. Jest **engine'em pod spodem**, który:
- Generuje automatyczne poprawki w PR bot (feature Pro)
- Wykonuje cleanup w "Auto-fix" mode (feature Team)
- Dostarcza rekomendacje z konkretnymi komendami (feature Free)

Sprzedajesz **wynik ReDSL** (poprawiony kod, niższy CC, mniej duplikacji), nie sam ReDSL.
