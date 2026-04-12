# Plan produktowy: zmiany UI/API do zbierania KPI benchmarku

## Status implementacji

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

## Luki produktowe

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

## Zmiany backendowe

## 1. Nowa warstwa danych

### Plik: `backend/database.py`

Obecny stan:

- tabela `scans` przechowuje tylko wynik skanu,
- brak powiązania z benchmarkiem,
- brak eventów użytkownika,
- brak feedbacku do rekomendacji.

### Zalecana zmiana

Dodać nowe tabele:

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

## 2. Stabilne ID rekomendacji

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

## 3. Rozszerzenie flow audytu

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

## 4. Nowy router benchmarkowy

### Zalecany nowy plik: `backend/routers/benchmark.py`

Zamiast przeciążać `metrics.py`, lepiej dodać osobny router benchmarkowy.

### Proponowane endpointy

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

### Przykładowe payloady API

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

## 5. Metryki i eksport

### Plik: `backend/routers/metrics.py`

Obecny stan:

- endpointy pokazują standardowe metryki skanów,
- nie ma tam benchmark summary ani eksportu case-by-case.

### Zalecana zmiana

`metrics.py` zostawić jako warstwę ogólną, a benchmark summary trzymać w osobnym routerze. Można dodać tylko odsyłacz lub lekki agregat, ale nie mieszać dwóch modeli danych.

## Zmiany frontendowe

### 1. Rozszerzenie klienta API

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

### 2. Przenoszenie metadanych benchmarkowych przez flow skanu

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

### 3. Panel benchmarkowy w widoku wyniku

### Plik: `frontend/src/components/phases/ResultPhase.jsx`

Obecny stan:

- widok pokazuje metryki i listę rekomendacji,
- użytkownik nie może ocenić przydatności wyniku,
- nie ma decyzji `accepted/rejected`, `PR candidate`, `deployment model`.

### Zalecana zmiana

Dodać sekcję `Benchmark Review` poniżej rekomendacji.

### Minimalny zakres pól UI

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

### 4. Rozszerzenie eksportów wyniku

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

### 5. Widok historii benchmarku

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

## Mapowanie KPI -> dane -> UI/API

| KPI | Dane wejściowe | UI | API |
|---|---|---|---|
| Novel actionable finding rate | novelty score, baseline_detected | `ResultPhase.jsx` | `POST /api/benchmark/.../feedback` |
| Recommendation acceptance rate | recommendation_accepted | `ResultPhase.jsx` | `POST /api/benchmark/.../feedback` |
| False positive rate | accuracy score, reviewer verdict | `ResultPhase.jsx` | `POST /api/benchmark/.../feedback` |
| Time to first useful recommendation | benchmark start + first accepted useful recommendation | `useAppState.helpers.js`, `ResultPhase.jsx` | `POST /api/benchmark/.../events` |
| PR conversion rate | pr_candidate, next_action | `ResultPhase.jsx`, `RecentScansTab.jsx` | `POST /api/benchmark/.../decision` |
| Deployment decision rate | deployment_model_selected | `ResultPhase.jsx`, `RecentScansTab.jsx` | `POST /api/benchmark/.../decision` |

## Kolejność wdrożenia

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

### Etap 3 — domknięcie pilota

- dodać powiązanie z ticketami i PR reference,
- dodać approval flow,
- dodać automatyczne przejście z benchmark case do szkicu PR,
- dodać dashboard deployment decisions.

## Definicja gotowości produktowej

Można uznać warstwę produktową za gotową do benchmarku, jeśli:

- każdy przypadek ma `case_id` i pełny rekord benchmarkowy,
- każda rekomendacja ma stabilne `recommendation_id`,
- użytkownik może ocenić rekomendację bez opuszczania UI,
- API potrafi zapisać feedback i decyzję deploymentową,
- benchmark można wyeksportować do `CSV`, `JSON` i `Markdown`,
- summary KPI jest liczone bez ręcznego składania danych poza systemem.
