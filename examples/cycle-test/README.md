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

# Podgląd refaktoryzacji (dry-run, bez zmian)
./quick-ticket.sh "Split high-CC module"

# Faktyczne zastosowanie zmian + PR
./quick-ticket.sh "Split high-CC module" semcod/vallm --apply
```

**Nie musisz się logować w przeglądarce** — skrypt automatycznie:
1. Pobiera token z `gh auth token`
2. Wymienia go na sesję Semcod (`POST /auth/gh-token`)
3. Tworzy ticket w systemie
4. Uruchamia reDSL (decide + refactor)
5. Opcjonalnie tworzy PR

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
