---
title: "Semcod WWW — status projektu i plan rozwoju"
slug: semcod-www-project-status
date: 2026-04-10
category: Engineering
tags: [semcod, www, fastapi, react, code-quality, status-update]
excerpt: "Raport z analizy jakości kodu platformy semcod.dev: 73 pliki, CC̄=3.0, architektura routers/services, oraz plan kolejnych kroków."
author: Tom Softreck
---

## Przegląd projektu

Semcod WWW to główna platforma webowa organizacji Semcod. Backend w Python (FastAPI), frontend w React (Vite), deployment via Docker. Produkt umożliwia one-click audit repozytoriów, generowanie health badge, integrację z GitHub przez webhooks i OAuth, oraz integrację z agentami AI przez Model Context Protocol (MCP).

**Repozytorium:** [github.com/semcod/www](https://github.com/semcod/www)

## Metryki jakości kodu

Dane z automatycznej analizy code2llm z dnia 2026-04-10:

| Metryka | Wartość | Ocena |
|---------|---------|-------|
| Pliki | 73 | — |
| Linie kodu | 5 776 | — |
| Funkcje | 244 | — |
| CC̄ (śr. złożoność) | 3.0 | 🟢 dobra |
| Critical hotspots | 10 | 🟡 wymaga uwagi |
| High-CC (≥15) | 4 | 🟡 wymaga uwagi |
| Duplikacja | 0 grup | 🟢 czysto |
| Cykle architektoniczne | 0 | 🟢 czysto |

Trend CC̄: 2.9 → 3.0 (lekka regresja +0.1 w ostatniej iteracji).

## Architektura

Projekt ma czystą separację warstw:

**Backend** (Python/FastAPI) — 20 modułów, 2026L:

- `server.py` (51L) — cienki entrypoint montujący routery
- `routers/audit.py` (331L) — główny pipeline analizy
- `routers/webhook.py` (255L) — obsługa PR webhooków z GitHub
- `routers/mcp.py` (436L) — integracja Model Context Protocol
- `routers/metrics.py` (257L) — API metryk i eksportów
- `routers/auth.py` (163L) — GitHub OAuth + demo login + JWT
- `services/` — analyzer, scoring, github_client
- `database.py` (170L) — SQLite persistence

**Frontend** (React/Vite) — 51 modułów, 3413L:

- Fazy onboardingu: Landing → Auth → Repos → Scanning → Result
- Taby: Audit, Repo, PR Bot, Badge, Recent Scans
- Hook `useAppState` (308L) — orkiestrator stanu aplikacji
- Komponenty UI: GradeCircle, MetricCard, LanguageBar, BadgeSVG

**Testy E2E** (Playwright) — 10 specyfikacji pokrywających: smoke, audit, badge, metrics, scan workflow, recent scans, social sharing, demo mode.

## Hotspoty do rozwiązania

Analiza evolution.toon.yaml wskazuje 4 priorytety:

**1. ResultPhase.jsx** (CC=54, fan-out=26, 544L)
Komponent wynikowy urósł z 285L do 544L w ostatniej iteracji. Zawiera logikę pobierania (4 formaty eksportu), share buttons (3 platformy) i wyświetlanie metryk w jednym pliku. Plan: split na 5 sub-komponentów + hook useDownloads.

**2. useAppState.js** (CC=51, fan-out=48, 308L)
Monolityczny hook zarządzający całym stanem aplikacji: routing, polling, auth, audit flow. Plan: wydzielenie useUrlState, usePolling, useAuth i zostawienie cienkiego orchestratora.

**3. mcp.py** (CC=22, fan-out=20, 436L)
Router MCP z dwoma złożonymi funkcjami: mcp_get_resource (CC=22) i mcp_invoke_tool (CC=17). Plan: podział na resources.py, tools.py i models.py.

**4. backend.routers fan-out=35**
Warstwa routerów importuje z 35 miejsc. Rozszerzanie o scheduled scans, billing i marketplace wymaga najpierw redukcji couplingu.

## Co już zostało zrobione (od początku projektu)

Projekt przeszedł już jedną dużą refaktoryzację:

- `server.py` (762L) → rozbity na `routers/` + `services/` + `config.py` + `store.py`
- `App.jsx` (680L) → rozbity na phases/ + tabs/ + components/ + hooks/
- Dodana baza SQLite zamiast pure in-memory
- Dodane testy E2E (Playwright)
- Dodany MCP router do integracji z agentami AI
- Dodany system auth (OAuth + demo login + JWT)

## Pipeline analizy

Semcod analizuje repozytoria czterema narzędziami:

1. **code2llm** — generuje pliki .toon.yaml z metrykami: CC per funkcja, fan-out, hotspoty, pipeline purity, warstwy architektoniczne, coupling
2. **redup** — skanuje duplikację na poziomie AST z similarity score
3. **pyqual** — uruchamia ruff, mypy, bandit i agreguje wyniki w bramy jakości
4. **vallm** — walidacja semantyczna (imports, syntax, module resolution)

Wynik jest agregowany w health score (0-100) i ocenę literową (A+ do F).

## Plan najbliższych iteracji

**Tydzień 1-2:**
- Split ResultPhase.jsx (CC=54 → <10)
- Split useAppState.js (CC=51 → <10)
- Cleanup dead files (server_new.py, PRCommentPreview.jsx)
- Scan diff API — porównanie z poprzednim scanem

**Tydzień 3-4:**
- Stripe billing (checkout, webhook, portal)
- Paywall component (po wyczerpaniu limitu 3 skanów/tydzień)
- Scheduled scans (APScheduler, co 1-6h)
- Auto-PR generation (LLM → patch → walidacja → PR)

**Tydzień 5-6:**
- Trend dashboard (wykres health score w czasie)
- Slack/Discord alerts (webhook na degradację)
- GitHub Check Runs API (natywne ✅/❌ w PR)
- Settings tab (zarządzanie schedulami i alertami)

## Jak uruchomić

```bash
git clone https://github.com/semcod/www.git && cd www

# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8000

# Frontend (w osobnym terminalu)
cd frontend && npm install && npm run dev
```

Aplikacja dostępna pod `http://localhost:3000`. Publiczne repozytoria można skanować bez logowania (sandbox mode).
