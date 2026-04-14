### Etap 1 (MVP) - ✅ Zakończony (2026-04-11)

**Backend:**
- `backend/db_models.py` — dodano modele ORM: `BenchmarkCase`, `BenchmarkEvent`, `RecommendationFeedback`
- `backend/db_module/benchmark_orm.py` — funkcje CRUD + summary
- `backend/db_module/wrappers.py` + `__init__.py` — eksport wrapperów z obsługą sesji
- `backend/services/scoring.py` — stabilne `recommendation_id` (sha1[:12]) w każdej rekomendacji
- `backend/routers/benchmark.py` — pełne REST API:
  - `POST/GET/PATCH /api/benchmark/cases` — zarządzanie przypadkami
  - `POST /api/benchmark/cases/{id}/decision` — decyzje PR/deployment
  - `POST /api/benchmark/cases/{id}/recommendations/{rid}/feedback` — feedback do rekomendacji
  - `POST /api/benchmark/cases/{id}/events` — zdarzenia produktowe
  - `GET /api/benchmark/summary` — podsumowanie KPI
  - `GET /api/benchmark/export.csv` i `export.json` — eksport danych
- `backend/server.py` — router zamontowany pod `/api/benchmark`

**Frontend:**
- `frontend/src/api.js` — funkcje: `createBenchmarkCase`, `updateBenchmarkCase`, `submitRecommendationFeedback`, `submitBenchmarkDecision`, `trackBenchmarkEvent`, `fetchBenchmarkSummary`, `downloadBenchmarkExport`
- `frontend/src/components/benchmark/BenchmarkReviewPanel.jsx` — tworzenie case + zwijany panel feedbacku per-rekomendacja
- `frontend/src/components/benchmark/RecommendationFeedbackForm.jsx` — akceptacja/odrzucenie + 5 score (0-3) + notatki
- `frontend/src/components/benchmark/BenchmarkDecisionPanel.jsx` — decyzja PR/deployment + przyciski eksportu CSV/JSON
- `frontend/src/components/phases/result/index.jsx` — zintegrowany `BenchmarkReviewPanel` poniżej rekomendacji

**Testy:** 193 passing (10 nowych testów benchmark w `tests/backend/test_benchmark.py`)

### Etap 2 — W planie
- Filtrowanie benchmarkowe w `RecentScansTab.jsx`
- Dashboard summary z wykresami
- Osobna zakładka "Benchmark" (alternatywnie rozszerzenie Recent Scans)

### Etap 3 — W planie
- Powiązanie z ticketami i PR reference
- Approval flow
- Automatyczne przejście z benchmark case do szkicu PR

---

## Cel dokumentu

Ten dokument przekłada KPI z `docs/validation-benchmark.md` na konkretne zmiany w produkcie Semcod.

Celem nie jest jeszcze implementacja, tylko precyzyjne wskazanie:

- gdzie w obecnym kodzie należy zbierać dane,
- jakie pola trzeba dodać,
- jakie endpointy muszą powstać,
- jakie akcje użytkownika muszą być mierzone,
- które zmiany są niezbędne do operacyjnego benchmarku i pilota.

## Stan obecny

Na dziś Semcod potrafi:

- uruchomić audyt repo przez `backend/routers/audit.py`,
- pobrać wynik przez `GET /api/audit/{audit_id}`,
- przechować historię skanów przez `save_scan()` i `get_recent_scans()` w `backend/database.py`,
- pokazać wynik skanu w `frontend/src/components/phases/ResultPhase.jsx`,
- pokazać ostatnie skany w `frontend/src/components/tabs/RecentScansTab.jsx`,
- udostępnić zagregowane metryki przez `backend/routers/metrics.py`.

To wystarcza do pokazywania wyniku analizy, ale nie wystarcza do zbierania KPI benchmarku takich jak:

- nowość wykrycia względem baseline,
- akceptacja rekomendacji,
- czas do pierwszej użytecznej rekomendacji,
- przejście do PR,
- decyzja deploymentowa.

### Brak modelu benchmark case

Aktualnie wynik skanu istnieje jako `audit_id` oraz zapis w tabeli `scans`, ale nie ma pojęcia:

- `case_id`,
- `source_type` (`repo`, `pr`, `ticket`),
- `change_type`,
- baseline klienta,
- oceny eksperckiej po wyniku,
- decyzji o PR lub deploymentcie.

### Brak feedbacku do rekomendacji

`generate_recommendations()` w `backend/services/scoring.py` zwraca rekomendacje bez trwałych identyfikatorów i bez mechanizmu zapisu opinii użytkownika:

- zaakceptowana,
- odrzucona,
- użyteczna,
- nietrafna,
- kandydat do PR,
- kandydat do deploymentu.

### Brak eventów produktowych

Frontend pokazuje wynik, ale nie zapisuje zdarzeń takich jak:

- otwarcie wyniku,
- pierwszy widok rekomendacji,
- kliknięcie akcji eksportu,
- akceptacja rekomendacji,
- oznaczenie przypadku jako kandydat do PR,
- wybór modelu wdrożenia.

### Brak API benchmarkowego

Obecne API ma endpointy audytu i metryk ogólnych, ale nie ma dedykowanej warstwy benchmarkowej.

## Zakres minimalny MVP instrumentacji

Minimalny zakres zmian potrzebny do pierwszego benchmarku:

1. dodać model `benchmark_case`,
2. dodać model `benchmark_event`,
3. dodać feedback dla rekomendacji,
4. dodać zapis decyzji `PR candidate` i `deployment model`,
5. dodać eksport benchmarku do `CSV` i `JSON`,
6. dodać prosty panel oceny w UI wyniku skanu.

### Plik: `backend/database.py`

Obecny stan:

- tabela `scans` przechowuje tylko wynik skanu,
- brak powiązania z benchmarkiem,
- brak eventów użytkownika,
- brak feedbacku do rekomendacji.

#### `benchmark_cases`

Polecane pola:

- `case_id` — publiczny identyfikator benchmarkowy,
- `audit_id` — powiązanie z wynikiem skanu,
- `repo` — repo lub moduł,
- `source_type` — `repo`, `pr`, `ticket`,
- `change_type` — `bugfix`, `feature`, `refactor`, `maintenance`,
- `baseline_tools` — tekst lub JSON,
- `baseline_findings` — tekst lub JSON,
- `baseline_detected` — bool,
- `reviewer_verdict` — końcowa decyzja,
- `recommendation_accepted` — bool,
- `pr_candidate` — bool,
- `deployment_candidate` — bool,
- `deployment_model_selected` — `client_scm`, `semcod_managed`, `hybrid`,
- `time_to_first_result_seconds`,
- `time_to_first_useful_recommendation_seconds`,
- `created_at`, `updated_at`.

#### `benchmark_events`

Polecane pola:

- `id`,
- `case_id`,
- `audit_id`,
- `event_name`,
- `event_value`,
- `metadata_json`,
- `created_at`.

#### `recommendation_feedback`

Polecane pola:

- `id`,
- `case_id`,
- `audit_id`,
- `recommendation_id`,
- `accepted`,
- `novelty_score`,
- `usefulness_score`,
- `accuracy_score`,
- `actionability_score`,
- `business_value_score`,
- `notes`,
- `created_at`.

### Plik: `backend/services/scoring.py`

Obecny stan:

- rekomendacje mają pola `priority`, `category`, `title`, `description`, `tool`, `action`,
- brak `recommendation_id`, przez co feedback nie ma stabilnego punktu odniesienia.

### Zalecana zmiana

Każda rekomendacja powinna dostać dodatkowe pola:

- `recommendation_id`,
- `severity`,
- `benchmark_category`,
- `evidence`,
- `suggested_next_step`.

### Efekt

Dzięki temu frontend i API mogą zapisywać feedback dla konkretnej rekomendacji, a nie dla luźnego tekstu.

### Plik: `backend/routers/audit.py`

Obecny stan:

- `POST /api/audit` przyjmuje tylko `repo`,
- `POST /api/analyze` przyjmuje tylko `repo_url` i `sandbox`,
- wynik skanu nie zawiera danych benchmarkowych,
- historia skanów nie zna `case_id` ani decyzji pilotowych.

### Zalecana zmiana

Rozszerzyć wejście do obu endpointów o opcjonalne pola:

- `case_id`,
- `source_type`,
- `change_type`,
- `baseline_detected`,
- `benchmark_mode`,
- `ticket_id` lub `pr_reference`.

### Dodatkowo

Wynik `GET /api/audit/{audit_id}` powinien zwracać także:

- `case_id`,
- `started`,
- `completed`,
- `duration_seconds`,
- `benchmark_mode`,
- `recommendation_feedback_status`,
- `deployment_decision_status`.

### Cel KPI

To jest niezbędne do policzenia:

  - `time_to_first_result`,
  - przejścia z benchmarku do oceny,
  - konwersji do PR i deploymentu.

### Zalecany nowy plik: `backend/routers/benchmark.py`

Zamiast przeciążać `metrics.py`, lepiej dodać osobny router benchmarkowy.

#### Cases

- `POST /api/benchmark/cases`
- `GET /api/benchmark/cases`
- `GET /api/benchmark/cases/{case_id}`
- `PATCH /api/benchmark/cases/{case_id}`

#### Feedback i scoring

- `POST /api/benchmark/cases/{case_id}/recommendations/{recommendation_id}/feedback`
- `POST /api/benchmark/cases/{case_id}/decision`
- `POST /api/benchmark/cases/{case_id}/events`

#### Eksport i dashboard

- `GET /api/benchmark/export.csv`
- `GET /api/benchmark/export.json`
- `GET /api/benchmark/summary`

### Co powinien zwracać `summary`

- liczba przypadków,
- `novel actionable finding rate`,
- `recommendation acceptance rate`,
- `false positive rate`,
- `PR conversion rate`,
- `deployment decision rate`,
- rozkład po `source_type`, `change_type`, `deployment_model_selected`.

#### `POST /api/benchmark/cases`

```json
{
  "case_id": "BM-001",
  "repo": "owner/repo",
  "source_type": "pr",
  "change_type": "bugfix",
  "baseline_detected": true,
  "baseline_tools": ["ci", "ruff", "manual-pr-review"],
  "pr_reference": "https://github.com/owner/repo/pull/123",
  "benchmark_mode": true
}
```

#### `POST /api/benchmark/cases/{case_id}/recommendations/{recommendation_id}/feedback`

```json
{
  "accepted": true,
  "novelty_score": 3,
  "usefulness_score": 3,
  "accuracy_score": 2,
  "actionability_score": 3,
  "business_value_score": 2,
  "notes": "Dobra rekomendacja, gotowa do przejścia w PR"
}
```

#### `POST /api/benchmark/cases/{case_id}/decision`

```json
{
  "pr_candidate": true,
  "deployment_candidate": true,
  "deployment_model_selected": "hybrid",
  "reviewer_verdict": "go",
  "next_action": "prepare_pr"
}
```

### Plik: `backend/routers/metrics.py`

Obecny stan:

- endpointy pokazują standardowe metryki skanów,
- nie ma tam benchmark summary ani eksportu case-by-case.

### Zalecana zmiana

`metrics.py` zostawić jako warstwę ogólną, a benchmark summary trzymać w osobnym routerze. Można dodać tylko odsyłacz lub lekki agregat, ale nie mieszać dwóch modeli danych.

### Plik: `frontend/src/api.js`

Obecny stan:

- klient umie rozpocząć audyt, pobrać audit, pobrać repo i uruchomić sandbox analysis,
- brak funkcji benchmarkowych.

### Zalecana zmiana

Dodać funkcje:

- `createBenchmarkCase(payload)`
- `updateBenchmarkCase(caseId, payload)`
- `submitRecommendationFeedback(caseId, recommendationId, payload)`
- `submitBenchmarkDecision(caseId, payload)`
- `trackBenchmarkEvent(caseId, payload)`
- `fetchBenchmarkSummary()`
- `downloadBenchmarkExport(format)`

### Efekt

Frontend zyskuje pełną warstwę zapisu oceny benchmarkowej zamiast samego pobierania wyniku skanu.

### Plik: `frontend/src/hooks/useAppState.helpers.js`

Obecny stan:

- flow niesie `repo`, `auditId`, `sandbox`, `phase`,
- brak `case_id`, `source_type`, `change_type`, `benchmark_mode`.

### Zalecana zmiana

Dodać do stanu i hash routing:

- `benchmarkMode`,
- `benchmarkCaseId`,
- `sourceType`,
- `changeType`,
- `baselineDetected`,
- `benchmarkStartedAt`.

### Moment logowania eventów

W momencie:

- startu audytu,
- wejścia na `ResultPhase`,
- pierwszego otwarcia panelu rekomendacji,
- kliknięcia eksportu,
- decyzji o PR,
- decyzji o deploymentcie,

frontend powinien wysyłać event do `benchmark_events`.

### Efekt

To pozwoli policzyć `time_to_first_result` i `time_to_first_useful_recommendation` bez ręcznego dopisywania danych po benchmarku.

### Plik: `frontend/src/components/phases/ResultPhase.jsx`

Obecny stan:

- widok pokazuje metryki i listę rekomendacji,
- użytkownik nie może ocenić przydatności wyniku,
- nie ma decyzji `accepted/rejected`, `PR candidate`, `deployment model`.

### Zalecana zmiana

Dodać sekcję `Benchmark Review` poniżej rekomendacji.

#### Na poziomie przypadku

- `source_type`
- `change_type`
- `baseline_detected`
- `time_to_first_useful_recommendation`
- `pr_candidate`
- `deployment_candidate`
- `preferred_deployment_model`
- `reviewer_verdict`
- `next_action`

#### Na poziomie rekomendacji

Przy każdej rekomendacji:

- przycisk `Akceptuj`
- przycisk `Odrzuć`
- `novelty score (0-3)`
- `usefulness score (0-3)`
- `accuracy score (0-3)`
- `actionability score (0-3)`
- `business value score (0-3)`
- `notes`

### Dodatkowy UX

- badge `New vs baseline`,
- badge `PR candidate`,
- badge `Deployment candidate`,
- CTA `Export benchmark row` do Markdown/CSV.

### Proponowana struktura komponentów UI

Żeby nie przeciążać dalej `ResultPhase.jsx`, warto wydzielić:

- `frontend/src/components/benchmark/BenchmarkReviewPanel.jsx`
- `frontend/src/components/benchmark/RecommendationFeedbackForm.jsx`
- `frontend/src/components/benchmark/BenchmarkDecisionPanel.jsx`

Minimalny podział odpowiedzialności:

- `BenchmarkReviewPanel` — dane case-level i status benchmarku,
- `RecommendationFeedbackForm` — scoring jednej rekomendacji,
- `BenchmarkDecisionPanel` — decyzja `PR / deployment / next action`.

### Minimalny flow użytkownika w UI

1. Użytkownik uruchamia skan w trybie benchmarkowym.
2. `ResultPhase` pokazuje banner `Benchmark mode` z `case_id`.
3. Użytkownik ocenia każdą rekomendację.
4. Użytkownik zaznacza decyzję `PR candidate` i `deployment model`.
5. Użytkownik zapisuje review i opcjonalnie eksportuje rekord do Markdown/CSV.

### Plik: `frontend/src/components/phases/resultPhaseContent.js`

Obecny stan:

- eksportuje JSON, Markdown, prompt i TOON z wyniku skanu,
- nie eksportuje danych benchmarkowych.

### Zalecana zmiana

Dodać dodatkowe warianty eksportu:

- `benchmark-markdown`
- `benchmark-json`
- `benchmark-csv-row`

### Efekt

Pozwoli to przejść z UI bezpośrednio do artefaktów operacyjnych używanych w benchmarku.

### Plik: `frontend/src/components/tabs/RecentScansTab.jsx`

Obecny stan:

- karta pokazuje historię skanów,
- nie odróżnia zwykłych scanów od benchmark cases,
- nie pokazuje statusu oceny i decyzji.

### Zalecana zmiana

Dodać do listy skanów:

- filtr `benchmark only`,
- kolumnę lub chip `case_id`,
- status `reviewed / pending review`,
- status `PR candidate`,
- status `deployment selected`,
- skrót do eksportu benchmark row.

### Alternatywa docelowa

Jeżeli zakres urośnie, warto dodać osobną zakładkę `Benchmark` zamiast przeciążać `RecentScansTab`.

## Zdarzenia produktowe do śledzenia

Minimalny zestaw eventów:

- `benchmark_case_created`
- `audit_started`
- `audit_completed`
- `result_viewed`
- `recommendation_seen`
- `recommendation_feedback_submitted`
- `benchmark_case_reviewed`
- `pr_candidate_marked`
- `deployment_candidate_marked`
- `deployment_model_selected`
- `benchmark_export_downloaded`

Każdy event powinien zawierać co najmniej:

- `case_id`
- `audit_id`
- `repo`
- `source_type`
- `change_type`
- `timestamp`
- `metadata`

### ReDSL Engine — Autonomiczna Refaktoryzacja

**ReDSL** (Re-factor + DSL + Self-Learning) to zaawansowany system refaktoryzacji kodu Python zintegrowany z Semcod. Działa jako osobny serwis HTTP (port 8000/8010) wywoływany przez API.

**Lokalizacja projektu:** `/home/tom/github/semcod/redsl`

### Stan reDSL (2026-04-12)

| Komponent | Status | Testy |
|-----------|--------|-------|
| Core engine | ✅ Działa | 580 passing |
| FastAPI server | ✅ Działa | 6/6 API tests |
| 15 RefactorActions | ✅ Dostępne | SPLIT_MODULE, REDUCE_FAN_OUT, EXTRACT_FUNCTIONS, etc. |
| CLI interface | ✅ Działa | `redsl refactor ./project --max-actions 10` |
| HTTP API | ✅ Działa | `POST /refactor`, `POST /batch/semcod`, `GET /health` |

### Integracja Semcod ↔ ReDSL

**Backend Semcod:**
- `backend/services/redsl_client.py` — `RedslClient` z metodami: `analyze()`, `decide()`, `refactor()`, `batch_hybrid()`, `health()`
- `backend/routers/redsl.py` — router `/api/redsl/*` endpointy:
  - `GET /api/redsl/status` — status silnika
  - `POST /api/redsl/analyze` — analiza projektu
  - `POST /api/redsl/health` — health score
  - `POST /api/redsl/refactor` — refaktoryzacja
  - `POST /api/redsl/decide` — decyzje DSL
  - `POST /api/redsl/batch-hybrid` — hybrydowa refaktoryzacja
  - `GET /api/redsl/badge/{owner}/{repo}` — SVG badge
- `backend/routers/autopr.py` — `POST /api/autopr/redsl` — tworzenie PR z refaktoryzacją
- `backend/routers/tickets.py` — `POST /api/tickets/{id}/process` — auto-PR z ticketu przez reDSL

**Celery Tasks:**
- `backend/worker/tasks/redsl.py` — `task_redsl_analyze`, `task_redsl_refactor`, `task_redsl_health_check`
- Scheduler: godzinny quality check + tygodniowy auto-refactor

**Frontend:**
- `frontend/src/api.js` — `getRedslStatus`, `redslAnalyze`, `redslHealth`, `redslRefactor`, `redslDecide`
- `frontend/src/components/RedslHealthCard.jsx` — widget dashboard z GradeCircle i badge

#### Scenariusz A: Health Score + Badge
1. Użytkownik wchodzi w ReDSL tab
2. System wywołuje `GET /api/redsl/status` → sprawdza czy engine działa
3. `POST /api/redsl/health` → analiza projektu → health score (0-100)
4. Wygenerowany badge: `/api/redsl/badge/owner/repo.svg`

#### Scenariusz B: Auto-Refactor PR
1. Użytkownik wybiera repo w Marketplace
2. Klikna "🔄 reDSL Refactor PR"
3. Backend: `POST /api/autopr/redsl` z `project_path`
4. reDSL: `refactor()` → transformacja plików
5. Auto-PR: branch → commits → PR na GitHub

#### Scenariusz C: Ticket-driven Development (NOWY)
1. Użytkownik tworzy ticket: "Dodaj paginację do listy użytkowników"
2. Ticket typ: `feature` lub `bugfix`
3. `POST /api/tickets/{id}/process` → reDSL `decide()` lokalizuje pliki
4. reDSL `refactor()` generuje zmiany
5. Auto-PR z linkiem do ticketu
6. Webhook aktualizuje ticket przy merge/close

## Mapowanie KPI -> dane -> UI/API

| KPI | Dane wejściowe | UI | API |
|---|---|---|---|
| Novel actionable finding rate | novelty score, baseline_detected | `ResultPhase.jsx` | `POST /api/benchmark/.../feedback` |
| Recommendation acceptance rate | recommendation_accepted | `ResultPhase.jsx` | `POST /api/benchmark/.../feedback` |
| False positive rate | accuracy score, reviewer verdict | `ResultPhase.jsx` | `POST /api/benchmark/.../feedback` |
| Time to first useful recommendation | benchmark start + first accepted useful recommendation | `useAppState.helpers.js`, `ResultPhase.jsx` | `POST /api/benchmark/.../events` |
| PR conversion rate | pr_candidate, next_action | `ResultPhase.jsx`, `RecentScansTab.jsx` | `POST /api/benchmark/.../decision` |
| Deployment decision rate | deployment_model_selected | `ResultPhase.jsx`, `RecentScansTab.jsx` | `POST /api/benchmark/.../decision` |

### Etap 1 — MVP pod benchmark

- dodać `benchmark_cases`, `benchmark_events`, `recommendation_feedback`,
- dodać router `benchmark.py`,
- dodać podstawowe funkcje do `frontend/src/api.js`,
- dodać prosty panel oceny w `ResultPhase.jsx`,
- dodać eksport benchmark row.

### Etap 2 — dashboard i wygoda operacyjna

- dodać filtr benchmarkowy w `RecentScansTab.jsx`,
- dodać benchmark summary endpoint,
- dodać eksport CSV i JSON dla całego benchmarku,
- dodać czytelne statusy review / PR / deployment.

### Etap 3 — Ticket-driven Development ✅ (2026-04-12) ZAKOŃCZONY

- ✅ **Ticket System** — model `Ticket` w `db_models.py` (feature/bugfix)
- ✅ **Tickets API** — CRUD endpointy `/api/tickets/*` + reDSL integracja
- ✅ **Auto-PR z ticketu** — `POST /api/tickets/{id}/process` → reDSL → PR
- ✅ **Webhook PR updates** — auto-aktualizacja statusu ticketu przy merge/close
- ✅ **Powiązanie z PR reference** — `pr_url`, `pr_branch`, `pr_number` w ticketach
- ✅ **Frontend API** — 12 funkcji dla ticket management

### Etap 4 — domknięcie pilota (W planie)

- dodać approval flow dla ticketów,
- dodać automatyczne przejście z benchmark case do szkicu PR,
- dodać dashboard deployment decisions,
- dodać integrację z zewnętrznymi systemami ticketów (Jira, Linear, GitHub Issues).

### Dla Benchmark KPI:

- każdy przypadek ma `case_id` i pełny rekord benchmarkowy,
- każda rekomendacja ma stabilne `recommendation_id`,
- użytkownik może ocenić rekomendację bez opuszczania UI,
- API potrafi zapisać feedback i decyzję deploymentową,
- benchmark można wyeksportować do `CSV`, `JSON` i `Markdown`,
- summary KPI jest liczone bez ręcznego składania danych poza systemem.

### Dla Ticket-driven Development:

- użytkownik może utworzyć ticket (feature/bugfix) z poziomu UI,
- system może przetworzyć ticket przez reDSL i wygenerować PR,
- ticket ma pełną historię statusów: open → analyzing → in_progress → pr_created → merged/closed,
- PR jest automatycznie linkowane do ticketu,
- webhook aktualizuje ticket przy zmianach w PR,
- statystyki ticketów są dostępne przez API (`/api/tickets/stats`).

## Podsumowanie architektury — 6 Scenariuszy Użycia

| # | Scenariusz | Główne komponenty | Status |
|---|-----------|-------------------|--------|
| 1 | GitHub OAuth → Audit | `auth.py`, `audit.py`, `ResultPhase.jsx` | ✅ |
| 2 | Sandbox Mode | `analyze` endpoint, sandbox scan | ✅ |
| 3 | Marketplace Auto-Fix | `marketplace/`, `MarketplaceDashboard.jsx` Step 3 | ✅ |
| 4 | PR Comment Bot | `webhook.py`, GitHub App | ✅ |
| 5 | Badge Generator | `badge.py`, `badge_router` | ✅ |
| 6 | **Ticket-driven Auto-PR** | `tickets.py`, `RedslClient`, reDSL engine | ✅ **NOWY** |

## ReDSL — Podsumowanie Integracji

**ReDSL** działa jako autonomiczny silnik refaktoryzacji z 580 testami. Jego integracja z Semcod umożliwia:

1. **Analizę jakości kodu** — health score, 15 refactor actions
2. **Auto-Refactor PR** — transformacja kodu + PR na GitHub
3. **Ticket-driven Development** — od zgłoszenia feature/bugfix do gotowego PR

**Kluczowe endpointy reDSL:**
- `POST /refactor` — refaktoryzacja projektu
- `POST /decide` — decyzje gdzie wprowadzić zmiany
- `POST /batch/semcod` — batch processing projektów semcod
- `GET /health` — health check silnika

**Kluczowe endpointy Semcod wykorzystujące reDSL:**
- `POST /api/redsl/refactor` — proxy do reDSL
- `POST /api/autopr/redsl` — auto-PR z refaktoryzacją
- `POST /api/tickets/{id}/process` — ticket → reDSL → PR
