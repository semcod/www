# Semcod - Dokumentacja

## Co to jest Semcod?

Semcod to narzędzie do automatycznej analizy zdrowia kodu (code health analysis) dla repozytoriów Git. Analizuje złożoność, duplikacje, jakość i generuje raporty z rekomendacjami refaktoryzacji.

## Funkcjonalności

### 🔍 Analiza Kodu
- **Automatyczne skanowanie** repozytoriów GitHub, GitLab, Bitbucket
- **Analiza złożoności** (Cyclomatic Complexity)
- **Wykrywanie duplikatów** kodu
- **Kontrola jakości** (linting, type checking)
- **Generowanie oceny zdrowia** (A+ do F)

### 📊 Metryki i Raporty
- **Health Score** - ogólna ocena zdrowia kodu (0-100%)
- **Grade** - literowa ocena (A+, A, B+, B, C, D, F)
- **Szczegółowe metryki** - pliki, linie kodu, języki
- **Rekomendacje** - konkretne sugestie refaktoryzacji

### 🏆 Badge'y
- Automatyczne generowanie badge'ów SVG
- Możliwość osadzenia w README
- Aktualizowane po każdym skanie

### 📤 Udostępnianie
- Przyciski do udostępniania w social media:
  - X (Twitter)
  - LinkedIn
  - Bluesky
- Automatyczne generowanie tekstu do udostępnienia

### 🤖 Integracja z LLM
- **Pobieranie metryk** jako JSON
- **Generowanie promptów** dla LLM
- **Formaty eksportu**:
  - JSON - pełne dane strukturalne
  - TXT - prompt dla LLM
  - Markdown - sformatowany raport
  - TOON YAML - format analizy kodu

### 📊 Benchmark KPI
- **Benchmark Cases** — tworzenie przypadków testowych z metadanymi (repo, source_type, change_type)
- **Recommendation Feedback** — ocena rekomendacji (akceptacja/odrzucenie + 5 score 0-3 + notatki)
- **Decyzje deploymentowe** — PR candidate, deployment model, reviewer verdict
- **Zdarzenia produktowe** — śledzenie eventów (result_viewed, recommendation_seen, itp.)
- **Eksport** — CSV i JSON z pełnymi danymi benchmarkowymi
- **Summary KPI** — automatycznie liczone: novelty rate, acceptance rate, false positive rate, PR conversion

### 🔄 ReDSL (Refactoring DSL)
- **Analiza** — automatyczna analiza projektu z reDSL
- **Refaktoryzacja** — 15 akcji (SPLIT_MODULE, REDUCE_FAN_OUT, EXTRACT_FUNCTIONS, itp.)
- **Health Score** — ocena zdrowia z grade i metrykami
- **Decide** — ewaluacja reguł DSL bez wykonania (dry-run)
- **Batch Hybrid** — automatyczna refaktoryzacja hybrydowa (bez LLM)
- **Badge SVG** — badge z health score do osadzenia w README
- **Scheduler** — godzinne quality check + tygodniowe auto-refactor

### 📜 Historia Skanów
- Trwałe przechowywanie w SQLite
- Wyświetlanie ostatnich 5 skanów na stronie głównej
- Pełna historia dostępna w zakładce "Ostatnie Skany"
- API do pobierania metryk dla klientów

## API

### Endpoint'y Benchmark KPI

#### Utwórz przypadek benchmarkowy
```bash
curl -X POST http://localhost:9000/api/benchmark/cases \
  -H 'Content-Type: application/json' \
  -d '{"case_id":"BM-001","repo":"owner/repo","source_type":"pr","change_type":"bugfix"}'
```

#### Prześlij feedback do rekomendacji
```bash
curl -X POST http://localhost:9000/api/benchmark/cases/BM-001/recommendations/abc123/feedback \
  -H 'Content-Type: application/json' \
  -d '{"accepted":true,"novelty_score":3,"usefulness_score":3}'
```

#### Pobierz podsumowanie KPI
```bash
curl http://localhost:9000/api/benchmark/summary
```

#### Eksport benchmarku
```bash
curl http://localhost:9000/api/benchmark/export.json -o benchmark.json
curl http://localhost:9000/api/benchmark/export.csv -o benchmark.csv
```

### Endpoint'y ReDSL

#### Status silnika
```bash
curl http://localhost:9000/api/redsl/status
```

#### Analiza projektu
```bash
curl -X POST http://localhost:9000/api/redsl/analyze \
  -H 'Content-Type: application/json' \
  -d '{"project_path":"/path/to/project"}'
```

#### Health score
```bash
curl -X POST http://localhost:9000/api/redsl/health \
  -H 'Content-Type: application/json' \
  -d '{"project_path":"/path/to/project"}'
```

#### Refaktoryzacja (dry-run)
```bash
curl -X POST http://localhost:9000/api/redsl/refactor \
  -H 'Content-Type: application/json' \
  -d '{"project_path":"/path/to/project","max_actions":10,"dry_run":true}'
```

#### Badge SVG
```markdown
![Code Health](https://semcod.com/api/redsl/badge/owner/repo)
```

### Endpoint'y Metryk

#### Pobierz standardowe metryki
```bash
curl http://localhost:9000/api/metrics/standard?limit=10
```

Odpowiedź:
```json
{
  "meta": {
    "generated_at": "2026-04-10T...",
    "total_scans": 100,
    "returned_scans": 10
  },
  "scans": [...]
}
```

#### Pobierz podsumowanie
```bash
curl http://localhost:9000/api/metrics/summary
```

#### Pobierz metryki repozytorium
```bash
curl http://localhost:9000/api/metrics/repository/owner/repo
```

#### Pobierz ostatnie skany
```bash
curl http://localhost:9000/api/scans/recent?limit=5
```

#### Pobierz prompt projektu (dla LLM)
```bash
curl http://localhost:9000/api/metrics/prompt -o prompt.txt
```

#### Pobierz prompt jako Markdown
```bash
curl http://localhost:9000/api/metrics/prompt/markdown -o prompt.md
```

### Endpoint'y Badge'ów

#### Pobierz badge zdrowia kodu
```bash
curl http://localhost:9000/badge/owner-repo.svg -o badge.svg
```

Markdown dla README:
```markdown
![Code Health](https://semcod.com/badge/owner-repo.svg)
```

## Użycie

### Szybki Start (Sandbox Mode)

1. Wejdź na https://semcod.com
2. Wpisz URL repozytorium publicznego (np. `github.com/python/cpython`)
3. Kliknij "Scan"
4. Poczekaj na wyniki analizy

### Pełna Integracja (GitHub App)

1. Kliknij "Connect GitHub"
2. Autoryzuj aplikację GitHub
3. Wybierz repozytorium do skanowania
4. Pobierz wyniki i rekomendacje

### Pobieranie Metryk dla LLM

Po skanowaniu możesz pobrać dane w różnych formatach:

1. **JSON** - pełne dane do przetwarzania
2. **LLM Prompt** - tekst gotowy do użycia z LLM
3. **Markdown** - sformatowany raport
4. **TOON** - format analizy kodu

Te dane możesz następnie użyć z Claude, GPT-4, lub innym LLM do uzyskania szczegółowych sugestii refaktoryzacji.

## Przykład Użycia z LLM

```bash
# Pobierz prompt
curl https://semcod.com/api/metrics/prompt -o prompt.txt

# Wyślij do Claude/GPT
cat prompt.txt | claude
```

Lub użyj przycisku "🤖 LLM Prompt" w interfejsie po skanowaniu.

## Narzędzia Analizy

Semcod wykorzystuje następujące narzędzia:

- **code2llm** - analiza złożoności i struktury kodu
- **redup** - wykrywanie duplikatów kodu
- **pyqual** - kontrola jakości Python (ruff, mypy, bandit)
- **regix** - analiza regex
- **vallm** - walidacja LLM
- **reDSL** - silnik refaktoryzacji DSL (15 akcji, health score, auto-PR)

## Konfiguracja

### Zmienne Środowiskowe

```env
# Backend
FRONTEND_URL=http://localhost:5173
PUBLIC_URL=https://semcod.com
APP_URL=https://semcod.com
HOST=0.0.0.0
PORT=8000

# GitHub (dla GitHub App)
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# ReDSL Engine
REDLS_URL=http://localhost:8000
```

### Uruchomienie Lokalne

```bash
# Backend
cd backend
pip install -r requirements.txt
python server.py

# Frontend
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up -d
```

## Testy

### E2E Tests

```bash
cd e2e
npx playwright test
```

### Unit Tests

```bash
cd backend
pytest tests/
```

## Wspierane Platformy

- ✅ GitHub (publiczne + prywatne przez App)
- ✅ GitLab (publiczne)
- ✅ Bitbucket (publiczne)

## Licencja

MIT

## Support

- Dokumentacja: https://semcod.com/docs
- GitHub Issues: https://github.com/semcod/www/issues
- Email: support@semcod.com

---

*Generated by Semcod - Code Health Analysis Tool*
