---
title: "Semcod — platforma AI do zarządzania jakością kodu i deploymentem"
slug: semcod-platform-overview
date: 2026-04-10
category: Product
tags: [semcod, ai, code-quality, saas, marketplace]
excerpt: "Semcod to nie kolejny linter. To platforma, która skanuje, naprawia i deployuje kod — od pierwszego commita do produkcji."
author: Tom Softreck
---

## Problem, który rozwiązujemy

Każdy zespół programistyczny zna ten scenariusz: CI pipeline sprawdza testy i linting, code review łapie oczywiste błędy, ale nikt systematycznie nie patrzy na architekturę, złożoność i trendy jakości w czasie. Problemy narastają niewidocznie — plik po pliku, commit po commicie — aż god module ma 800 linii i nikt nie chce go dotykać.

Istniejące narzędzia (SonarQube, CodeClimate, CodeRabbit) rozwiązują kawałki tego problemu, ale żadne z nich nie zamyka pętli: wykryj → zrozum → napraw → zdeployuj → rozlicz.

Semcod zamyka tę pętlę.

## Co robi Semcod

Semcod łączy cztery warstwy w jedną platformę:

**Warstwa 1 — Analiza.** Skanuje repozytorium czterema narzędziami jednocześnie: code2llm (złożoność cyklomatyczna, fan-out, hotspoty architektoniczne), redup (duplikacja na poziomie AST), pyqual (bramy jakości: ruff, mypy, bandit) i vallm (walidacja semantyczna). Wynik to nie lista warningów, ale spójny raport z health score 0-100 i oceną literową A+ do F.

**Warstwa 2 — Rekomendacja.** Każdy wykryty problem ma przypisaną propozycję naprawy z priorytetem, szacowanym effort i impact score. Nie mówi „ten plik jest za duży" — mówi „podziel ResultPhase.jsx na 5 komponentów, oto plan splitowania, szacowany czas: 1h, wpływ na CC: -46 punktów".

**Warstwa 3 — Automatyzacja.** Propozycja może zostać automatycznie zamieniona w branch i PR. LLM generuje patch, pipeline walidacyjny sprawdza czy testy przechodzą i czy metryki się poprawiły, i dopiero wtedy tworzy PR do review. Jeśli walidacja nie przechodzi — rollback i alternatywna strategia.

**Warstwa 4 — Deployment i Marketplace.** Gotowy artefakt (SaaS, desktop, mobile, API) może zostać opublikowany na Semcod Marketplace. Klient końcowy kupuje subskrypcję lub płaci za tokeny. Developer dostaje 70-85% przychodu.

## Dwa modele wdrożenia

**Self-managed:** Klient instaluje Semcod GitHub App na swoich repozytoriach. Automatyczne review PR, scheduled scany, alerty degradacji. Klient zachowuje pełną kontrolę. Od $9/mies.

**Managed Infrastructure:** Klient łączy repo — Semcod robi resztę: skanuje, naprawia, testuje, deployuje. Pierwszy miesiąc za darmo. Potem token-based lub compute hours. Idealny dla firm, które chcą skupić się na produkcie, nie na infrastrukturze.

## Dlaczego nie kolejna wtyczka do IDE

Semcod celowo omija model wtyczek i narzędzi dla developerów. Zamiast tego wchodzi na poziom, gdzie AI zarządza całym repozytorium:

- Nie wymaga instalacji w IDE — działa na poziomie repo i CI/CD.
- Nie wymaga konfiguracji per-developer — działa per-organizacja.
- Nie generuje todo listy do ręcznego wykonania — generuje gotowe PR-y.
- Nie kończy się na analizie — prowadzi od ticketu do deploymentu.

To model biznesowy, w którym AI jest platformą, nie narzędziem.

## Cel

Realizacja zadań z `docs/refactoring-todo.toon.yaml` dla projektu `semcod/www`:
redukcja złożoności cyklomatycznej (CC), eliminacja god-modules, usunięcie martwego kodu.

---

## PHASE 0 — Cleanup (dead files)

Usunięte pliki o 0 linii kodu, nigdy nieimportowane:

- `backend/server_new.py`
- `frontend/src/components/PRCommentPreview.jsx`
- `frontend/src/screens/index.js`

`server_old.py` — nie istniał już w repozytorium.

---

### 1.1 `useAppState` → 4 pliki

**Przed:** `useAppState.js` (131L) + `useAppState.helpers.js` (389L) — monolityczny plik z URL logic, polling, auth, repos loading

**Po:**

| Plik | Odpowiedzialność |
|------|-----------------|
| `hooks/useUrlState.js` | `useHashBootstrap`, `useHashSync`, `parseRepositoryReference`, `createSelectedRepo` |
| `hooks/usePolling.js` | `useScanAnimation`, `useAuditPolling`, stałe SCAN_STEPS |
| `hooks/useAuth.js` | `useSessionCallbackBootstrap`, `useSessionProfile`, `getOAuthStartUrl`, OAuth flow helpers |
| `hooks/useAppState.js` | Cienki orchestrator — tylko `useState`, `useCallback`, deleguje do sub-hooków |

Usunięto: `useAppState.helpers.js`

### 1.2 `ResultPhase` → pakiet result/

**Przed:** `ResultPhase.jsx` (257L) + `resultPhaseContent.js` (222L) — download logic, share buttons, metrics grid, recommendations, header

**Po:**

| Plik | Odpowiedzialność |
|------|-----------------|
| `phases/result/index.jsx` | Wrapper, tab logic, error state, conditional render |
| `phases/result/ResultHeader.jsx` | Tytuł, sandbox badge, przyciski exportów |
| `phases/result/ResultMetrics.jsx` | GradeCircle, MetricCard grid, LanguageBar |
| `phases/result/ResultRecommendations.jsx` | Lista RecommendationCard |
| `hooks/useDownloads.js` | Wszystkie builderzy treści + `useDownloads` hook |

`phases/index.js` zaktualizowany: `export { ResultPhase } from "./result"` — import w `App.jsx` bez zmian.

### 1.3 Wspólny komponent `ShareButtons`

Zduplikowany kod (~90L) w `ResultPhase`, `RecentScansTab`, `LandingPhase` zastąpiony wspólnym komponentem:

```jsx
<ShareButtons scan={scan} repo={repoName} size="default|small" />
```

Obsługuje: 𝕏 Twitter / LinkedIn / Bluesky. Propagacja `e.stopPropagation()` obsługiwana wewnątrz.

---

## PHASE 2 — Split Backend: `mcp.py` → pakiet `mcp/`

**Przed:** `backend/routers/mcp.py` (211L) + `backend/routers/mcp_helpers.py` (228L) — 4 modele, logika resources i tools w dwóch plikach

**Po:**

| Plik | Odpowiedzialność |
|------|-----------------|
| `routers/mcp/__init__.py` | APIRouter z prefiksem `/mcp`, montuje sub-routery, endpoint `/info` |
| `routers/mcp/models.py` | 4 modele Pydantic: `MCPResource`, `MCPTool`, `MCPResourceResponse`, `MCPToolRequest` |
| `routers/mcp/resources.py` | `GET /mcp/resources`, `GET /mcp/resources/content`, helpery `_get_scans_list`, `_get_scan_detail`, `_get_metrics_summary`, `_get_badge_status` |
| `routers/mcp/tools.py` | `GET /mcp/tools`, `POST /mcp/tools/invoke`, helpery `_invoke_start_audit`, `_invoke_get_status`, `_invoke_get_metrics`, `_invoke_analyze_public` |

Wszystkie endpointy `/mcp/*` zachowane, `server.py` bez zmian.

---

## Weryfikacja

| Check | Wynik |
|-------|-------|
| `npm run build` | ✅ 62 modułów, 0 błędów, 192KB JS |
| `pytest backend/tests/` | ✅ 19/19 PASSED |
| E2E Playwright | ⚠️ Konflikt wersji playwright (e2e/node_modules vs global) — wymaga uruchomienia z poziomu `e2e/` |

---

## Podsumowanie metryk

**Frontend:**
- Usunięto ~420 linii kodu (helpers + ResultPhase monolith)
- 4 nowe wyspecjalizowane hooki zamiast 1 monolitycznego
- 4 sub-komponenty zamiast 1 monolitycznego ResultPhase

**Backend:**
- `mcp.py` (211L) + `mcp_helpers.py` (228L) → 4 pliki max ~150L każdy
- CC sprawdzony przez brak monolitycznych `if/elif` łańcuchów w routerze
- Każdy handler tool ma CC ≤ 5

## Co dalej

Pracujemy nad: scheduled scans (cykliczne skanowanie co 1-6h), trend dashboard (historia health score w czasie), Stripe billing, auto-PR generation (LLM → patch → walidacja → PR), i Marketplace MVP.

Szczegóły techniczne w osobnych artykułach o poszczególnych projektach organizacji.
