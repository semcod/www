# TODO — Migracja PostgreSQL + Kompletna strategia E2E

> Ostatnia aktualizacja: 2026-04-12

---

## Faza 1: Migracja PostgreSQL ✅

### Krok 1.1: Unify `db_session.py` ✅
- `pool_pre_ping=True`, `pool_size=10`, `max_overflow=20` (PG)
- SQLite fallback z `check_same_thread=False`
- Alembic migration w `init_db()` → `_run_alembic_migrations()`

### Krok 1.2: Przekieruj importy starej warstwy ✅
Zaktualizowane pliki (stary import → `db_module.wrappers`):
- `worker/tasks/quality_loop.py` — 2 importy
- `worker/tasks/redsl.py` — 3 importy
- `scheduler/scan_job.py`
- `routers/ecosystem.py`
- `routers/badge.py` — 2 importy
- `routers/marketplace/quality.py`
- `scripts/scan_samples.py`

Dodatkowe naprawy (raw `sqlite3` → SQLAlchemy `text()`):
- `services/billing.py` — 4 metody (`get_usage_report`, `_get_current_month_usage`, `_store_usage_record`, `check_limit`)
- `routers/billing.py` — `_find_sub_by_customer`
- `worker/tasks/quality_loop.py` — `_update_ticket_status`, `_update_ticket_error` → `SessionLocal`

### Krok 1.3: Usuń stare moduły SQLite ✅
Usunięto 8 plików (~871 LOC):
- `db_module/scans.py` (259L)
- `db_module/users.py` (174L)
- `db_module/tenants.py` (96L)
- `db_module/events.py` (88L)
- `db_module/installations.py` (152L)
- `db_module/repositories.py` (102L)
- `db_module/schema.py` (201L)
- `db_module/db_connection.py` (26L)

### Krok 1.4: Alembic migration ✅
- `alembic/versions/0001_initial_schema.py` — tworzy tabele jeśli nie istnieją
- `alembic/env.py` — czyta `DATABASE_URL` z env, fallback na `alembic.ini`
- Typy: `DateTime(timezone=True)` → PG `TIMESTAMP WITH TIME ZONE`
- JSON fields: `Text` z JSON string (kompatybilne SQLite+PG)

### Krok 1.5: docker-compose update ✅
- PG healthcheck: `pg_isready -U semcod`
- Backend/worker: `depends_on: db: condition: service_healthy`
- `POSTGRES_PASSWORD` z env var fallback
- `DATABASE_URL=postgresql://semcod:semcod@db:5432/semcod`

### Krok 1.6: Usunięcie `convert_query()` ✅
- Usunięty razem z `users.py` (Krok 1.3)

### Krok 1.7: Testy migracji ✅
- Backend pytest: **20 passed**
- Docker backend: healthy na PG
- Playwright E2E: **67 passed, 6 skipped, 0 failed**

---

## Faza 2: Kompletna strategia E2E ✅

### Mode 1: Mock GitHub (CI) ✅
- `make e2e-mock` — docker-compose.sim.yml + Playwright
- `frontend/e2e/specs/user-journey.spec.js` — 8 testów

### Mode 2: Gitea (dev offline) ✅ (istniejący)
- `make gitea-cycle` → `gitea-up` + `gitea-setup` + `gitea-test`
- `e2e/gitea-oauth-cycle.spec.js`

### Mode 3: GitHub via `gh` CLI ✅
- `e2e/github-real.sh` — 4 tryby:
  - `make e2e-github` — read-only (bezpieczny)
  - `make e2e-github-write` — tworzy branch + commit
  - `make e2e-github-full` — tworzy PR (zamyka po teście)
  - `make e2e-github-apply` — reDSL apply + PR

### Mode 4: Playwright Browser E2E ✅
- `make e2e-browser` — mock provider, headed
- `make e2e-browser-gitea` — Gitea provider, headed
- `make e2e-all` — mock + github + browser

### Makefile targets ✅
```
pg-migrate        — Alembic upgrade head
pg-validate       — test-pg-migration.sh
pg-reset          — drop volumes, recreate, migrate
pg-shell          — psql do PG
e2e-mock          — Mode 1
e2e-gitea         — Mode 2
e2e-github        — Mode 3 (read-only)
e2e-github-write  — Mode 3 (+write)
e2e-github-full   — Mode 3 (+PR)
e2e-github-apply  — Mode 3 (+reDSL)
e2e-browser       — Mode 4 (mock)
e2e-browser-gitea — Mode 4 (gitea)
e2e-all           — all modes
```

---

## Faza 3: Walidacja migracji PG ✅
- `e2e/test-pg-migration.sh` — PG connectivity, tables, Alembic, brak SQLite refs, CRUD smoke, pooling
- `make pg-validate`

---

## Pozostałe zadania (opcjonalne optymalizacje)

- [ ] **JSONB columns** — zmienić `Text` JSON fields na `JSONB` w `db_models.py` (wymaga nowej Alembic migration)
- [ ] **GitHub Actions CI** — `.github/workflows/e2e.yml` z `e2e-mock` job + opcjonalny `e2e-github` na `main`
- [ ] **alembic.ini default URL** — zmienić z `sqlite:///semcod.db` na placeholder (nie krytyczne, `env.py` nadpisuje)
- [ ] **data-testid selectors** — dodać `data-testid` do komponentów React dla stabilniejszych E2E selectors

---

## Architektura po migracji

```
db_module/
├── __init__.py         — re-eksporty z wrappers + tickets_orm
├── wrappers.py         — session-aware ORM wrappers (backward compat)
├── scans_orm.py        — SQLAlchemy ORM
├── users_orm.py        — SQLAlchemy ORM
├── tenants_orm.py      — SQLAlchemy ORM
├── events_orm.py       — SQLAlchemy ORM
├── installations_orm.py— SQLAlchemy ORM
├── repositories_orm.py — SQLAlchemy ORM
├── benchmark_orm.py    — SQLAlchemy ORM
├── tickets_orm.py      — SQLAlchemy ORM
└── tickets_query.py    — SQLAlchemy ORM

database.py             — re-eksport z db_module (backward compat)
db_session.py           — engine + SessionLocal (PG/SQLite)
db_models.py            — SQLAlchemy declarative models
```

## Wyniki testów

| Suite | Passed | Skipped | Failed |
|-------|--------|---------|--------|
| Backend pytest | 20 | 0 | 0 |
| Playwright E2E | 67 | 6 | 0 |
| **Total** | **87** | **6** | **0** |
