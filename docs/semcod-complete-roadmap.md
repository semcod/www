# Semcod — Kompletny Roadmap

Data: 2026-04-10 | Wersja: 3.0
Źródło: toon files (73f, 5776L, CC̄=3.0, 10 crit)

---

### 1.1 Aktualny stan www

```
CC̄=3.0 | 73 pliki | 5776L | 10 critical | 4 high-CC (≥15)
Trend: CC̄ 2.9 → 3.0 (regresja +0.1)
Nowe: mcp.py (436L), auth.py rozbudowany (163L), ResultPhase urósł 285→544L
```

| Problem | Plik | CC | Fan-out | Priorytet |
|---------|------|----|---------|-----------|
| ResultPhase god component | ResultPhase.jsx | 54 | 26 | 🔴 KRYTYCZNY |
| useAppState monolith | useAppState.js | 51 | 48 | 🔴 KRYTYCZNY |
| MCP router complexity | mcp.py | 22 | 20 | 🟡 WYSOKI |
| MCP invoke tool | mcp.py | 17 | 14 | 🟡 WYSOKI |
| server_new.py pusty plik | server_new.py | — | — | cleanup |
| backend.routers fan-out=35 | routers/*.py | — | 35 | 🟡 smell |

### 1.2 Plan refaktoryzacji (instrukcje dla LLM)

Każdy blok poniżej jest samodzielnym taskiem, który LLM może wykonać
jako PR z testami. Format: cel → pliki → strategia → walidacja.

---

#### TASK-001: Split ResultPhase.jsx (CC=54 → CC<10)

**Cel:** Rozbić god component 544L na 5 modułów.

**Wejście:** `frontend/src/components/phases/ResultPhase.jsx` (544L, 15 func, CC=54)

**Strategia:**

```
frontend/src/components/phases/result/
├── index.jsx              (~60L)  — ResultPhase wrapper, layout, error state
├── ResultHeader.jsx       (~70L)  — tytuł, sandbox badge, share buttons
├── ResultMetrics.jsx      (~50L)  — GradeCircle + MetricCards grid
├── ResultRecommendations.jsx (~40L) — lista RecommendationCard
├── useDownloads.js        (~120L) — handleDownloadMetrics/Prompt/Markdown/Toon
└── ShareButtons.jsx       (~50L)  — Twitter/LinkedIn/Bluesky share bar
```

**Ekstrakcje:**
1. `handleDownloadMetrics`, `handleDownloadPrompt`, `handleDownloadMarkdown`, `handleDownloadToon` → `useDownloads.js` hook
2. Share buttons (Twitter/LinkedIn/Bluesky) → `ShareButtons.jsx` (reusable, używany też w RecentScansTab i LandingPhase)
3. Header z tytułem + sandbox badge + "New audit" → `ResultHeader.jsx`
4. Metryki (GradeCircle + MetricCard grid + LanguageBar) → `ResultMetrics.jsx`
5. Rekomendacje → `ResultRecommendations.jsx`

**Walidacja:**
- `npm run build` — brak błędów
- E2E: `npx playwright test e2e/specs/scan-workflow.spec.js` — pass
- CC każdego nowego pliku < 10
- Żaden nowy plik > 150L

---

#### TASK-002: Split useAppState.js (CC=51 → CC<10)

**Cel:** Rozbić monolityczny hook 308L na 4 hooki.

**Wejście:** `frontend/src/hooks/useAppState.js` (308L, 30 func, CC=51)

**Strategia:**

```
frontend/src/hooks/
├── useAppState.js     (~80L)  — thin orchestrator, łączy 3 hooki
├── useUrlState.js     (~55L)  — hash routing, parseRepoUrl
├── usePolling.js      (~80L)  — audit polling logic + progress labels
└── useAuth.js         (~60L)  — OAuth + demo login + token management
```

**Ekstrakcje:**
1. Parsowanie `window.location.hash`, `parseRepoUrl()` → `useUrlState.js`
2. Polling loop (`setInterval`, `fetchAudit`, progress) → `usePolling.js`
3. `startOAuth`, `confirmAuth`, `demoLogin`, token state → `useAuth.js`
4. `useAppState.js` zostaje jako orchestrator importujący 3 hooki

**Walidacja:**
- Import `useAppState` z App.jsx nie zmienia się
- Wszystkie e2e testy pass
- CC każdego hooka < 10

---

#### TASK-003: Split mcp.py (CC=22 → CC<10)

**Cel:** Rozbić MCP router 436L na 3 moduły.

**Wejście:** `backend/routers/mcp.py` (436L, 6 func, 4 classes, CC=22)

**Strategia:**

```
backend/routers/mcp/
├── __init__.py        (~20L)  — router = APIRouter(), include sub-routers
├── resources.py       (~150L) — mcp_list_resources, mcp_get_resource
├── tools.py           (~150L) — mcp_list_tools, mcp_invoke_tool
└── models.py          (~80L)  — 4 Pydantic classes (MCPResource, MCPTool, etc.)
```

**Ekstrakcje:**
1. 4 dataclass/Pydantic models → `models.py`
2. `mcp_get_resource` (CC=22) → rozbić na sub-functions per resource type
3. `mcp_invoke_tool` (CC=17) → rozbić na handler per tool type

**Walidacja:**
- `pytest backend/tests/` — pass
- API endpoint `/mcp/*` działa identycznie
- CC każdego pliku < 12

---

#### TASK-004: Cleanup dead files

**Pliki do usunięcia:**
- `backend/server_new.py` (0L, pusty)
- `frontend/src/components/PRCommentPreview.jsx` (0L, pusty)
- `frontend/src/screens/index.js` (0L, pusty)

**Weryfikacja:** `grep -r "server_new\|PRCommentPreview\|screens/index" frontend/ backend/`

---

#### TASK-005: Extract ShareButtons (reusable)

**Problem:** Share buttons (Twitter/LinkedIn/Bluesky) zduplikowane w 3 komponentach.

**Redukcja:** ~90L usunięte z ResultPhase, RecentScansTab, LandingPhase.

---

### 1.3 Metryki docelowe po refaktoryzacji

| Metryka | Teraz | Cel | Mechanizm |
|---------|-------|-----|-----------|
| CC̄ | 3.0 | ≤2.0 | split 4 high-CC |
| Critical | 10 | ≤2 | TASK-001..003 |
| High-CC (≥15) | 4 | 0 | split + extract |
| Max CC | 54 | ≤12 | ResultPhase + useAppState split |
| Fan-out max | 48 | ≤15 | useAppState → 4 hooki |

---

### 2.1 Flow: co nowego wykryto vs. poprzedni scan

**Obecny stan:** jednorazowy snapshot (health score).
**Docelowy stan:** delta report — co się zmieniło + propozycje.

```
POST /api/scan/{owner}/{repo}
  → clone → code2llm + redup + pyqual + vallm
  → porównaj z ostatnim scanem w DB
  → response:
    {
      "delta": {
        "score_change": -3,
        "new_issues": 5,
        "fixed_issues": 2,
        "regressions": ["CC̄ wzrosło", "ResultPhase urósł"]
      },
      "proposals": [
        {
          "type": "split_module",
          "target": "ResultPhase.jsx",
          "reason": "544L, CC=54",
          "impact": 1404,
          "auto_fixable": true,
          "llm_prompt": "Split ResultPhase.jsx into..."
        }
      ]
    }
```

### 2.2 Test pipeline — walidacja jakości zmian

```
1. BASELINE  → regix snapshot PRZED zmianą
2. APPLY     → LLM generuje fix → aplikuj na branchu
3. VALIDATE  → testy + metryki porównaj z baseline
4. VERDICT   → PASS: stwórz PR | FAIL: rollback + alternatywna strategia
```

### 2.3 Auto-PR generation

```
Propozycja z high auto_fixable score
    ↓
LLM generuje patch (używając llm_prompt z propozycji)
    ↓
Git: branch feat/semcod-fix-{id}
    ↓
Apply patch → run tests → run scan (metryki)
    ↓
PASS → Create PR:
  Title: "[Semcod] Split ResultPhase.jsx (CC 54→8)"
  Body: delta report + before/after metryki + diff preview
  Labels: semcod-autofix, refactoring
  Reviewers: auto-assign z CODEOWNERS
    ↓
FAIL → Create Issue:
  Title: "[Semcod] Manual fix needed: ResultPhase.jsx CC=54"
  Body: propozycja + co poszło nie tak + sugestia manual fix
```

---

### Model A: Self-managed (GitHub/GitLab klienta)

Klient instaluje Semcod GitHub App na swoich repo.
Semcod API skanuje, komentuje, tworzy PR-y.
Klient zatwierdza i merguje.

**Cennik:**

| Plan | Cena | Scany | Auto-PR | Scheduled |
|------|------|-------|---------|-----------|
| Free | $0 | 3/tydz | ❌ | ❌ |
| Pro | $9/mies | ∞ | 3/mies | co 6h |
| Team | $29/mies | ∞ | ∞ | co 1h |
| Annual | $81/rok | = Pro | = Pro | = Pro |

**Copy:**

> Install on GitHub → auto PR reviews → fix with one click.
> You control everything. We just make your code better.

---

### Model B: Semcod Managed Infrastructure

Klient łączy repo — Semcod robi wszystko:
scan, fix, test, deploy, monitoring.
Pierwszy miesiąc za darmo. Potem token-based.

**Co zawiera:**

```
✅ Sandbox runner (izolowany Docker per scan)
✅ CI/CD pipeline (auto-detect stack → build → test)
✅ Auto-ticketing (propozycje → LLM implementuje → PR)
✅ Deploy staging/prod (Docker → k8s / Railway / Fly.io)
✅ Monitoring + alerting (Slack/Discord/email)
✅ Marketplace publishing (SaaS/Desktop/Mobile/API)
```

**Cennik — token-based:**

| Pakiet | Tokeny | Cena | Co za token |
|--------|--------|------|-------------|
| Starter | 10 000 | $10 | 1 scan = 100 tok |
| Growth | 100 000 | $80 | 1 auto-PR = 500 tok |
| Scale | 1 000 000 | $500 | 1 deploy = 1000 tok |

**Albo time-based:**

| Tier | Compute hours/mies | Cena |
|------|--------------------|------|
| Hobby | 10h | $0 (1 miesiąc free) |
| Pro | 100h | $29/mies |
| Team | 500h | $99/mies |

**Copy:**

> Connect your repo. We scan, fix, test, and deploy.
> First month free. No credit card. No setup.
> Pay only for what you use — tokens or compute time.

---

### 4.1 Koncept

Developers publikują gotowe aplikacje na Semcod Marketplace.
Klienci końcowi kupują/subskrybują.
Semcod bierze 15-30% prowizji.

### 4.2 Typy artefaktów

| Typ | Format | Rozliczenie |
|-----|--------|-------------|
| **SaaS** | Docker → managed hosting | subskrypcja /mies |
| **Desktop** | Electron/Tauri | jednorazowo lub subskrypcja |
| **Mobile** | PWA / React Native | subskrypcja lub IAP |
| **API** | REST endpoint | per request / token |
| **Plugin** | npm/pip package | free / sponsor |

### 4.3 Rozliczanie

- **Stripe Connect** — payouty do developerów
- Developer dostaje 70-85% przychodu
- Semcod: 15-30% prowizji + hosting fee
- Klient płaci: subskrypcja, tokeny, jednorazowo, lub kombinacja

### 4.4 Flow publishera

```
Developer:
  1. Tworzy projekt → pushuje na GitHub
  2. Semcod skanuje → pokazuje health score
  3. Developer konfiguruje: pricing, tier, description
  4. Semcod buduje artefakt (Docker / binary / PWA)
  5. Publikacja na Marketplace
  6. Klienci kupują → developer dostaje payout co 2 tygodnie

Klient końcowy:
  1. Przegląda Marketplace → filtruje po kategorii
  2. Widzi: health score badge, opis, pricing, reviews
  3. Kupuje/subskrybuje
  4. Dostaje dostęp (URL/download/API key)
```

---

### Tydzień 1-2: Refaktoryzacja + foundation

- [x] Stripe + paywall (zrobione w v2)
- [x] Scheduled scans (zrobione w v2)
- [x] Trend API (zrobione w v2)
- [ ] TASK-001: Split ResultPhase.jsx
- [ ] TASK-002: Split useAppState.js
- [ ] TASK-003: Split mcp.py
- [ ] TASK-004: Cleanup dead files
- [ ] Scan diff API (delta vs previous)

### Tydzień 3-4: Auto-PR + onboarding

- [ ] Auto-PR generation (LLM → branch → PR)
- [ ] Test pipeline (baseline → apply → validate → verdict)
- [ ] Onboarding: Model A vs Model B selection screen
- [ ] Trial 1-month flow (managed infra)

### Tydzień 5-6: Managed Infrastructure

- [ ] Sandbox runner (Docker per scan)
- [ ] CI/CD pipeline auto-detection
- [ ] Auto-ticketing (propozycja → ticket → LLM → PR)
- [ ] Deploy staging/prod

### Tydzień 7-8: Marketplace MVP

- [ ] Marketplace API (publish/browse/buy)
- [ ] Stripe Connect (revenue share)
- [ ] Artifact builder (Docker → deploy)
- [ ] Marketplace landing page

---

## Część VI — KPI

| KPI | M1 | M3 | M6 |
|-----|----|----|-----|
| GitHub App installs | 50 | 300 | 1000 |
| Scany/tydzień | 200 | 2000 | 10000 |
| Płacący klienci | 5 | 30 | 100 |
| MRR | $45 | $400 | $2000 |
| Auto-PR acceptance | — | 40% | 65% |
| Marketplace products | — | — | 20 |
| README badges (viral) | 20 | 200 | 1000 |
