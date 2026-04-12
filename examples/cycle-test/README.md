# Cycle Test — pełny cykl ticket → reDSL → PR

Skrypty do walidacji i uruchamiania cyklu Semcod **bez logowania w przeglądarce** — używają `gh` (który już ma token).

## Skrypty

| Skrypt | Opis | Tworzy PR? |
|--------|------|------------|
| `quick-ticket.sh` | **Najszybszy**: stwórz ticket → reDSL → wynik | Opcjonalnie (`--apply`) |
| `validate-steps.sh` | Sprawdza każdy endpoint API osobno | Nie — bezpieczny do powtarzania |
| `full-cycle.sh` | Pełny cykl: auth → ticket → reDSL → PR → merge | Tak |

## Szybki start

### Najprostsze: quick-ticket (jedna komenda)

```bash
cd examples/cycle-test
chmod +x quick-ticket.sh

# AUTO: automatycznie wygeneruj ticket z analizy kodu + docs
./quick-ticket.sh --auto

# AUTO + PR: wygeneruj ticket i stwórz PR
./quick-ticket.sh --auto semcod/vallm --apply

# Ręczny tytuł
./quick-ticket.sh "Split high-CC module"
```

**Nie musisz się logować w przeglądarce** — skrypt automatycznie:
1. Pobiera token z `gh auth token`
2. Wymienia go na sesję Semcod (`POST /auth/gh-token`)
3. **`--auto`**: analizuje kod (reDSL analyze + decide) + czyta `docs/*.md` → generuje najlepszy ticket
4. Tworzy ticket w systemie
5. Uruchamia reDSL (decide + refactor)
6. Opcjonalnie tworzy PR (`--apply`)

#### Jak działa `--auto`

```
docs/*.md ──┐
            ├─→ python3 generator ──→ najlepszy ticket
reDSL      ──┘    (analyze + decide)    (tytuł, opis, priorytet)
```

- **reDSL analyze**: metryki (CC̄, critical count, alerty)
- **reDSL decide**: konkretne akcje (split_module, extract_functions, simplify_conditionals)
- **docs/*.md**: kontekst platformy (architektura, roadmap, znane problemy)
- **Generator**: łączy oba źródła → tytuł = `quality_label: target_file`, opis z metrykami + alertami + kontekstem docs

#### Przykład wygenerowanego ticketu

```
Title: Split god module: src/vallm/cli/batch_processor_impl.py
Priority: high

## Problem
File `src/vallm/cli/batch_processor_impl.py` has quality issues requiring split_module.
Score: 1.17 (higher = more urgent)

## All refactoring decisions
1. Split god module → batch_processor_impl.py (score: 1.17)
2. Extract high-CC functions → test_batch_toon_output.py (score: 0.85)
3. Simplify deep nesting → batch_processor_impl.py (score: 0.85)
```

#### Uwaga o `--apply`

reDSL działa w trybie **plan-only** — zwraca plan refaktoryzacji ale nie modyfikuje plików na dysku. Gdy użyjesz `--apply`:
- Skrypt sprawdza czy reDSL faktycznie zmodyfikował pliki w kontenerze
- Jeśli tak → tworzy PR z realnymi zmianami kodu
- Jeśli nie → ticket dostaje status `analyzed` z opisem do ręcznego wykonania

### Walidacja endpointów (bez PR)

```bash
chmod +x validate-steps.sh
./validate-steps.sh    # 19 endpoint checks
```

### Pełny cykl z PR i merge

```bash
chmod +x full-cycle.sh
./full-cycle.sh
```

## Kroki walidowane przez validate-steps.sh

1. **Infrastructure** — Backend, reDSL, mock-github health
2. **Authentication** — gh token → Semcod session JWT
3. **User** — GET /api/me
4. **Ticket CRUD** — POST create, GET list, GET stats, GET single, PATCH update, GET status, POST process (dry_run), DELETE
5. **reDSL** — GET status, POST health, POST decide, POST refactor (dry-run)
6. **Webhook** — POST /api/tickets/webhook/pr-updated

## Kroki pełnego cyklu (full-cycle.sh)

1. Check services
2. Authenticate (gh → Semcod JWT)
3. Verify identity (/api/me)
4. Check reDSL availability
5. Create ticket
6. reDSL decide
7. reDSL refactor (dry-run)
8. Process ticket via Semcod API
9. Check ticket status
10. List tickets
11. Ticket statistics
12. Create PR via gh
13. Merge PR
14. Update ticket to merged

## Zmienne środowiskowe

| Zmienna | Default | Opis |
|---------|---------|------|
| `SEMCOD_URL` | http://localhost:8003 | Backend API |
| `REDLS_URL` | http://localhost:8030 | reDSL engine |
| `REPO` | semcod/vallm | Target repo |
