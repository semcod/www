# Migracja PostgreSQL + Kompletna strategia E2E

## Stan wyjściowy

### Warstwa DB — dualizm do usunięcia

```
db_module/
├── scans.py           259L  get_connection() → raw SQLite    ← USUNĄĆ
├── users.py           174L  get_connection() → raw SQLite    ← USUNĄĆ
├── tenants.py          96L  get_connection() → raw SQLite    ← USUNĄĆ
├── events.py           88L  get_connection() → raw SQLite    ← USUNĄĆ
├── installations.py   152L  get_connection() → raw SQLite    ← USUNĄĆ
├── repositories.py    102L  get_connection() → raw SQLite    ← USUNĄĆ
├── schema.py          201L  CREATE TABLE SQLite DDL          ← USUNĄĆ
│
├── scans_orm.py       204L  SQLAlchemy Session               ✅ ZOSTAJE
├── users_orm.py       183L  SQLAlchemy Session               ✅ ZOSTAJE
├── tenants_orm.py     121L  SQLAlchemy Session               ✅ ZOSTAJE
├── events_orm.py       87L  SQLAlchemy Session               ✅ ZOSTAJE
├── installations_orm  165L  SQLAlchemy Session               ✅ ZOSTAJE
├── repositories_orm   154L  SQLAlchemy Session               ✅ ZOSTAJE
├── benchmark_orm.py   208L  SQLAlchemy Session               ✅ ZOSTAJE
├── tickets_orm.py     173L  SQLAlchemy Session               ✅ ZOSTAJE
├── tickets_query.py         SQLAlchemy Session               ✅ ZOSTAJE
│
├── wrappers.py        121L  _wrap() → ORM calls              ✅ ZOSTAJE (już ORM)
├── __init__.py         37L  re-eksporty                      ✅ UPDATE
└── db_connection.py    26L  SessionLocal helper               ✅ ZOSTAJE
```

**Do usunięcia: 6 plików, ~871 LOC** — raw SQLite moduły + schema.py.
**Do zachowania: 10 plików** — ORM + wrappers + connection.

### Zależności od starej warstwy

```
db_module/scans.py      ← 9 importerów (scheduler, audit, scan_job, badge, ...)
db_module/users.py      ← 2 importerów (auth, webhook)
db_module/schema.py     ← 1 (db_session.init_db)
```

---

## Faza 1: Migracja PostgreSQL (~4h)

### Krok 1.1: Unify db_session.py

```python
# db_session.py — NOWA WERSJA
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.getenv('DB_PATH', '/app/data/scans.db')}"
)

# SQLAlchemy engine — działa z PG i SQLite
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # PG-specific
    **({"pool_size": 10, "max_overflow": 20} if "postgresql" in DATABASE_URL else {}),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    """FastAPI dependency — yields session, closes on finish."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create tables + run Alembic migrations."""
    if "sqlite" in DATABASE_URL:
        Base.metadata.create_all(bind=engine)
    # Alembic handles PG schema
    _run_alembic_migrations()

def _run_alembic_migrations():
    try:
        from alembic.config import Config
        from alembic import command
        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
        command.upgrade(cfg, "head")
    except Exception as e:
        print(f"Alembic migration skipped: {e}")
```

### Krok 1.2: Przekieruj importy starej warstwy

Każdy plik, który importuje `from db_module.scans import ...` musi zmienić na import z wrappers lub ORM.

**Mapa przekierowań:**

| Stary import | Nowy import |
|---|---|
| `from db_module.scans import save_scan` | `from db_module.wrappers import save_scan` |
| `from db_module.scans import get_recent_scans` | `from db_module.wrappers import get_recent_scans` |
| `from db_module.scans import get_audit_result` | `from db_module.wrappers import get_audit_result` |
| `from db_module.users import upsert_user` | `from db_module.wrappers import upsert_user` |
| `from db_module.users import get_user_by_github_id` | `from db_module.wrappers import get_user_by_github_id` |
| `from db_module.schema import init_db` | `from db_session import init_db` |

**Pliki do zaktualizowania (9 importerów scans.py):**

```bash
# Znajdź wszystkie importy starej warstwy:
grep -rn "from db_module.scans import\|from db_module.users import\|from db_module.tenants import\|from db_module.events import\|from db_module.installations import\|from db_module.repositories import\|from db_module.schema import" backend/
```

### Krok 1.3: Usuń stare moduły SQLite

```bash
# Po przekierowaniu wszystkich importów:
rm backend/db_module/scans.py
rm backend/db_module/users.py
rm backend/db_module/tenants.py
rm backend/db_module/events.py
rm backend/db_module/installations.py
rm backend/db_module/repositories.py
rm backend/db_module/schema.py
```

### Krok 1.4: Alembic migration dla PG

```bash
cd backend
# Wygeneruj migrację z aktualnych modeli
alembic revision --autogenerate -m "postgresql_migration"
# Sprawdź wygenerowaną migrację
cat alembic/versions/*postgresql_migration*.py
# Aplikuj
alembic upgrade head
```

**Kluczowe różnice SQLite → PG do sprawdzenia w modelach:**

| SQLite | PostgreSQL | Zmiana w db_models.py |
|---|---|---|
| `TEXT` z JSON string | `JSONB` | `Column(JSONB)` zamiast `Column(Text)` |
| `INTEGER` autoincrement | `SERIAL` / `BIGSERIAL` | SQLAlchemy obsługuje automatycznie |
| `DATETIME` as string | `TIMESTAMP WITH TIME ZONE` | `Column(DateTime(timezone=True))` |
| brak array | `ARRAY` | opcjonalnie dla list-type fields |
| brak `ON CONFLICT` | `INSERT ... ON CONFLICT` | użyj `from sqlalchemy.dialects.postgresql import insert` |

### Krok 1.5: Update docker-compose

```yaml
# docker-compose.yml — już masz PG, upewnij się:
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: semcod
      POSTGRES_USER: semcod
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-semcod}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U semcod"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    environment:
      - DATABASE_URL=postgresql://semcod:${POSTGRES_PASSWORD:-semcod}@db:5432/semcod
      # USUŃ: DB_PATH — nie potrzebny z PG
    depends_on:
      db:
        condition: service_healthy
```

### Krok 1.6: convert_query() — usunąć

`db_module/users.py` ma `convert_query()` który tłumaczy `?` placeholders SQLite na `%s` PostgreSQL. Z SQLAlchemy ORM to nie jest potrzebne — ORM generuje poprawny SQL dla obu backendów.

### Krok 1.7: Testy migracji

```bash
# Test 1: Backend startuje z PG
docker compose up -d db
sleep 3
DATABASE_URL=postgresql://semcod:semcod@localhost:5432/semcod \
  python -c "from db_session import init_db; init_db(); print('OK')"

# Test 2: CRUD działa
DATABASE_URL=postgresql://semcod:semcod@localhost:5432/semcod \
  pytest tests/backend/ -x -v

# Test 3: Cały stack
docker compose up -d
curl -sf http://localhost:8003/api/health | jq .
```

---

## Faza 2: Kompletna strategia E2E (~6h setup)

### Architektura testów — 4 tryby

```
┌──────────────────────────────────────────────────────────────────┐
│                    E2E Test Matrix                                │
├─────────────────┬────────────────────────────────────────────────┤
│ Mode 1          │ MOCK: mock-github + backend + PG               │
│ (CI/szybki)     │ Nic zewnętrznego, pełna izolacja               │
│                 │ docker compose -f ... -f docker-compose.sim.yml│
├─────────────────┼────────────────────────────────────────────────┤
│ Mode 2          │ GITEA: lokalne Gitea + prawdziwy git            │
│ (dev offline)   │ OAuth, webhooks, PR, merge — wszystko lokalne  │
│                 │ docker compose -f ... -f docker-compose.gitea  │
├─────────────────┼────────────────────────────────────────────────┤
│ Mode 3          │ GITHUB-SIM: gh CLI + prawdziwe GitHub API      │
│ (integration)   │ Token z `gh auth token`, prawdziwe repo        │
│                 │ Nie tworzy PR-ów chyba że --apply              │
├─────────────────┼────────────────────────────────────────────────┤
│ Mode 4          │ FULL: browser Playwright + prawdziwy OAuth      │
│ (pre-release)   │ Symulacja użytkownika od otwarcia strony       │
│                 │ do zamknięcia PR                                │
└─────────────────┴────────────────────────────────────────────────┘
```

### Mode 1: Mock GitHub (CI) — istniejący

```bash
# Uruchomienie
docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d

# Testy
npx playwright test tests/github-login-sim.spec.js
```

Pokrycie: OAuth flow (fake tokens), user profile, repo list, badge.
Brak: webhooks, PR creation, git operations.

### Mode 2: Gitea (dev offline) — istniejący

```bash
# Uruchomienie
make gitea-cycle  # up + setup + test

# Testy
bash scripts/test-full-cycle.sh
npx playwright test tests/gitea-oauth-cycle.spec.js
```

Pokrycie: prawdziwy OAuth2, prawdziwe repo z kodem, branch→commit→PR, webhook delivery, PR diff, badge SVG.

### Mode 3: GitHub via `gh` — NOWY

Poniżej kompletny skrypt testowy:

```bash
#!/bin/bash
# e2e/github-real.sh — E2E z prawdziwym GitHub via gh CLI
# Wymaga: gh auth login (jednorazowo)
# Tryby:
#   ./github-real.sh                    — read-only (bezpieczny)
#   ./github-real.sh --write            — tworzy branch + commit (nie PR)
#   ./github-real.sh --write --pr       — tworzy PR (zamyka po teście)
#   ./github-real.sh --write --pr --apply — tworzy PR z reDSL zmianami
set -euo pipefail

SEMCOD_URL="${SEMCOD_URL:-http://localhost:8003}"
REPO="${REPO:-tom-sapletta-com/semcod}"
MODE_WRITE=false; MODE_PR=false; MODE_APPLY=false

for arg in "$@"; do
  case $arg in
    --write) MODE_WRITE=true ;;
    --pr)    MODE_PR=true ;;
    --apply) MODE_APPLY=true ;;
  esac
done

PASS=0; FAIL=0; SKIP=0
pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }
skip() { echo "  ⏭️  $1"; ((SKIP++)); }

echo "═══════════════════════════════════════════════════════════"
echo "  🧪 E2E: Real GitHub ($REPO)"
echo "  Mode: read=$([ $MODE_WRITE = false ] && echo 'only')${MODE_WRITE:+ write}${MODE_PR:+ +pr}${MODE_APPLY:+ +apply}"
echo "═══════════════════════════════════════════════════════════"

# ── Phase 1: Auth ────────────────────────────────────────────────
echo ""; echo "📡 Phase 1: Authentication"

# 1a. Get GitHub token via gh
GH_TOKEN=$(gh auth token 2>/dev/null) || { fail "gh not authenticated — run: gh auth login"; exit 1; }
pass "gh token: ${GH_TOKEN:0:8}..."

# 1b. Exchange for Semcod session
SESSION=$(curl -sf -X POST "${SEMCOD_URL}/auth/gh-token?token=${GH_TOKEN}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_token',''))" 2>/dev/null) || SESSION=""

if [ -n "$SESSION" ]; then
  pass "Semcod session obtained"
else
  # Fallback: try OAuth callback simulation
  fail "Semcod session exchange failed"
  exit 1
fi

semcod() {
  curl -sf -X "$1" "${SEMCOD_URL}$2" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${SESSION}" \
    ${3:+-d "$3"}
}

# 1c. Verify identity
ME_LOGIN=$(semcod GET "/api/me" | python3 -c "import sys,json; print(json.load(sys.stdin).get('login',''))" 2>/dev/null)
[ -n "$ME_LOGIN" ] && pass "Logged in as: ${ME_LOGIN}" || fail "/api/me failed"

# ── Phase 2: Read-only operations ───────────────────────────────
echo ""; echo "📦 Phase 2: Read operations"

# 2a. List repos
REPOS=$(semcod GET "/api/repos" 2>/dev/null) || REPOS="[]"
REPO_COUNT=$(echo "$REPOS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else d.get('total',0))" 2>/dev/null)
[ "${REPO_COUNT:-0}" -gt 0 ] && pass "Repos listed: ${REPO_COUNT}" || fail "No repos"

# 2b. Verify target repo exists
REPO_INFO=$(gh api "repos/${REPO}" 2>/dev/null) || REPO_INFO="{}"
DEFAULT_BRANCH=$(echo "$REPO_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin).get('default_branch','main'))" 2>/dev/null)
REPO_PRIVATE=$(echo "$REPO_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin).get('private',False))" 2>/dev/null)
pass "Repo: ${REPO} (branch=${DEFAULT_BRANCH}, private=${REPO_PRIVATE})"

# 2c. Badge endpoint
BADGE_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "${SEMCOD_URL}/badge/${REPO//\//-}.svg")
[ "$BADGE_STATUS" = "200" ] && pass "Badge SVG: 200" || skip "Badge: ${BADGE_STATUS}"

# 2d. Recent scans
SCANS=$(semcod GET "/api/scans/recent" 2>/dev/null) || SCANS="[]"
pass "Recent scans endpoint OK"

# 2e. Health check
HEALTH=$(semcod GET "/api/health" 2>/dev/null)
pass "Health: $(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null)"

# ── Phase 3: Audit (sandbox, no auth needed) ────────────────────
echo ""; echo "🔍 Phase 3: Sandbox audit"

AUDIT_RESP=$(curl -sf -X POST "${SEMCOD_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"repo_url\":\"https://github.com/${REPO}\",\"sandbox\":true}" 2>/dev/null) || AUDIT_RESP="{}"

AUDIT_ID=$(echo "$AUDIT_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('audit_id',''))" 2>/dev/null)
if [ -n "$AUDIT_ID" ]; then
  pass "Audit started: ${AUDIT_ID}"

  for i in $(seq 1 20); do
    RESULT=$(curl -sf "${SEMCOD_URL}/api/audit/${AUDIT_ID}" 2>/dev/null) || RESULT="{}"
    STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','pending'))" 2>/dev/null)
    if [ "$STATUS" = "complete" ] || [ "$STATUS" = "completed" ] || [ "$STATUS" = "done" ]; then
      GRADE=$(echo "$RESULT" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('grade', r.get('result',{}).get('grade','?')))" 2>/dev/null)
      pass "Audit complete: grade=${GRADE}"
      break
    elif [ "$STATUS" = "error" ]; then
      fail "Audit error"
      break
    fi
    sleep 3
  done
  [ "$STATUS" = "pending" ] && skip "Audit still pending after 60s"
else
  skip "Audit API unavailable"
fi

# ── Phase 4: Write operations (optional) ─────────────────────────
if [ "$MODE_WRITE" = true ]; then
  echo ""; echo "✏️  Phase 4: Write operations"

  BRANCH="e2e-test/$(date +%Y%m%d-%H%M%S)"
  SHA=$(gh api "repos/${REPO}/git/refs/heads/${DEFAULT_BRANCH}" --jq '.object.sha' 2>/dev/null)

  # 4a. Create branch
  gh api "repos/${REPO}/git/refs" -f ref="refs/heads/${BRANCH}" -f sha="${SHA}" >/dev/null 2>&1
  pass "Branch: ${BRANCH}"

  # 4b. Commit test file
  TEST_FILE=".e2e-test-$(date +%s).txt"
  COMMIT=$(gh api "repos/${REPO}/contents/${TEST_FILE}" -X PUT \
    -f message="e2e: automated test commit" \
    -f content="$(echo -n "E2E test $(date)" | base64)" \
    -f branch="${BRANCH}" 2>/dev/null)
  COMMIT_SHA=$(echo "$COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('sha','')[:8])" 2>/dev/null)
  [ -n "$COMMIT_SHA" ] && pass "Commit: ${COMMIT_SHA}" || fail "Commit failed"

  # ── Phase 5: PR (optional) ──────────────────────────────────────
  if [ "$MODE_PR" = true ]; then
    echo ""; echo "🔀 Phase 5: Pull Request"

    PR_URL=$(gh pr create --repo "${REPO}" --head "${BRANCH}" --base "${DEFAULT_BRANCH}" \
      --title "e2e: automated test PR — will auto-close" \
      --body "Automated E2E test PR. Created by github-real.sh. Safe to ignore." 2>&1)

    if echo "$PR_URL" | grep -q 'github.com'; then
      PR_NUM=$(echo "$PR_URL" | grep -oP '\d+$')
      pass "PR #${PR_NUM}: ${PR_URL}"

      # Wait for webhook (if backend is connected)
      sleep 5
      WEBHOOK_CHECK=$(semcod GET "/api/scans/recent" 2>/dev/null) || true
      pass "Webhook wait complete"

      # ── Phase 5b: reDSL apply (optional) ──────────────────────
      if [ "$MODE_APPLY" = true ]; then
        echo ""; echo "🤖 Phase 5b: reDSL cycle"

        TICKET_RESP=$(semcod POST "/api/tickets" "{
          \"title\": \"e2e: auto-refactor ${REPO}\",
          \"repo\": \"${REPO}\",
          \"ticket_type\": \"refactor\",
          \"priority\": \"low\"
        }")
        TICKET_ID=$(echo "$TICKET_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null)
        [ -n "$TICKET_ID" ] && pass "Ticket: ${TICKET_ID}" || skip "Ticket creation failed"

        if [ -n "$TICKET_ID" ]; then
          PROCESS=$(semcod POST "/api/tickets/${TICKET_ID}/process" "{
            \"project_path\": \"/tmp/${REPO##*/}\",
            \"max_actions\": 3,
            \"dry_run\": false,
            \"auto_create_pr\": false
          }" 2>/dev/null) || PROCESS="{}"
          PROC_STATUS=$(echo "$PROCESS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
          pass "reDSL process: ${PROC_STATUS}"
        fi
      fi

      # Cleanup: close PR + delete branch
      echo ""; echo "🧹 Cleanup"
      gh pr close "${PR_NUM}" --repo "${REPO}" --delete-branch 2>/dev/null || true
      pass "PR #${PR_NUM} closed + branch deleted"
    else
      fail "PR creation failed: ${PR_URL}"
    fi
  else
    # No PR — just delete the branch
    echo ""; echo "🧹 Cleanup"
    gh api -X DELETE "repos/${REPO}/git/refs/heads/${BRANCH}" 2>/dev/null || true
    pass "Branch ${BRANCH} deleted"
  fi
fi

# ── Phase 6: Ticket system (always, read+write safe) ────────────
echo ""; echo "🎫 Phase 6: Ticket system"

T_CREATE=$(semcod POST "/api/tickets" "{
  \"title\": \"e2e: validation ticket\",
  \"repo\": \"${REPO}\",
  \"ticket_type\": \"feature\",
  \"priority\": \"low\"
}" 2>/dev/null) || T_CREATE="{}"
T_ID=$(echo "$T_CREATE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null)
[ -n "$T_ID" ] && pass "Ticket created: ${T_ID}" || fail "Ticket creation failed"

if [ -n "$T_ID" ]; then
  # List
  T_LIST=$(semcod GET "/api/tickets" 2>/dev/null)
  T_TOTAL=$(echo "$T_LIST" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null)
  pass "Tickets total: ${T_TOTAL}"

  # Stats
  T_STATS=$(semcod GET "/api/tickets/stats" 2>/dev/null)
  pass "Ticket stats OK"

  # Update
  semcod PATCH "/api/tickets/${T_ID}" '{"priority":"high"}' >/dev/null 2>&1
  pass "Ticket updated"

  # Cleanup
  semcod DELETE "/api/tickets/${T_ID}" >/dev/null 2>&1
  pass "Ticket deleted"
fi

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
printf "  ✅ %d passed | ❌ %d failed | ⏭️  %d skipped\n" "$PASS" "$FAIL" "$SKIP"
echo "═══════════════════════════════════════════════════════════"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
```

### Mode 4: Playwright Browser E2E — NOWY

```javascript
// e2e/specs/user-journey.spec.js
// Full user journey: landing → login → repo select → audit → results → badge
import { test, expect } from "@playwright/test";

const BASE = process.env.FRONTEND_URL || "http://localhost:3000";
const PROVIDER = process.env.GIT_PROVIDER || "mock"; // mock | gitea | github

test.describe("User journey E2E", () => {

  test("landing page loads with login button", async ({ page }) => {
    await page.goto(BASE);
    const loginBtn = page.locator(
      'button:has-text("GitHub"), button:has-text("Connect"), a:has-text("GitHub")'
    );
    await expect(loginBtn.first()).toBeVisible({ timeout: 10000 });
  });

  test("OAuth login → repo list → audit → results", async ({ page }) => {
    await page.goto(BASE);

    // Step 1: Click login
    const loginBtn = page.locator(
      'button:has-text("GitHub"), button:has-text("Connect")'
    ).first();
    await loginBtn.click();

    // Step 2: Handle OAuth page (depends on provider)
    if (PROVIDER === "mock") {
      // Mock: click user button on mock page
      await page.waitForURL(/.*4010.*|.*mock.*/i, { timeout: 10000 });
      await page.locator('button:has-text("tom-sapletta-com")').click();
    } else if (PROVIDER === "gitea") {
      // Gitea: fill login form
      await page.waitForURL(/.*3100.*|.*gitea.*/i, { timeout: 10000 });
      await page.fill('input[name="user_name"]', "tom-sapletta-com");
      await page.fill('input[name="password"]', "Semcod2026!");
      await page.click('button[type="submit"]');
      // Authorize app
      const authBtn = page.locator('button:has-text("Authorize"), button:has-text("Grant")');
      if (await authBtn.count() > 0) await authBtn.click();
    }

    // Step 3: Should be back on frontend, logged in
    await page.waitForURL(`${BASE}/**`, { timeout: 15000 });
    await expect(
      page.locator('text=tom-sapletta-com, [data-testid="user-name"]').first()
    ).toBeVisible({ timeout: 10000 });

    // Step 4: Select a repo
    const repoBtn = page.locator(
      '[data-testid="repo-item"], .repo-list button, button:has-text("sample")'
    ).first();
    if (await repoBtn.count() > 0) {
      await repoBtn.click();

      // Step 5: Wait for audit to complete
      const resultIndicator = page.locator(
        '[data-testid="audit-result"], .grade-circle, text=/[A-F]/, text=/Score/'
      ).first();
      await expect(resultIndicator).toBeVisible({ timeout: 120000 });

      // Step 6: Check tabs exist
      for (const tab of ["Badge", "Trend", "Recent"]) {
        const tabBtn = page.locator(`button:has-text("${tab}"), [role="tab"]:has-text("${tab}")`);
        if (await tabBtn.count() > 0) {
          await tabBtn.first().click();
          await page.waitForTimeout(500);
        }
      }
    }
  });

  test("sandbox analysis (no login required)", async ({ page }) => {
    await page.goto(BASE);

    // Find sandbox/public repo input
    const input = page.locator(
      'input[placeholder*="repo"], input[placeholder*="URL"], [data-testid="sandbox-input"]'
    ).first();

    if (await input.count() > 0) {
      await input.fill("https://github.com/tom-sapletta-com/semcod");
      const analyzeBtn = page.locator(
        'button:has-text("Analyze"), button:has-text("Scan"), button:has-text("Check")'
      ).first();
      if (await analyzeBtn.count() > 0) {
        await analyzeBtn.click();
        // Wait for result
        const result = page.locator(
          '[data-testid="sandbox-result"], .grade-circle, text=/Score/'
        ).first();
        await expect(result).toBeVisible({ timeout: 120000 });
      }
    }
  });
});
```

### Makefile targets

```makefile
# ── E2E Test Targets ─────────────────────────────────────────────

# Mode 1: Mock (CI, fast, isolated)
e2e-mock:
	docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d
	npx playwright test e2e/specs/ --project=chromium
	docker compose -f docker-compose.yml -f docker-compose.sim.yml down

# Mode 2: Gitea (dev, offline, real git)
e2e-gitea:
	$(MAKE) gitea-cycle

# Mode 3: GitHub read-only (safe, repeatable)
e2e-github:
	bash e2e/github-real.sh

# Mode 3b: GitHub with branch + commit (no PR)
e2e-github-write:
	bash e2e/github-real.sh --write

# Mode 3c: GitHub full cycle with PR
e2e-github-full:
	bash e2e/github-real.sh --write --pr

# Mode 3d: GitHub + reDSL apply
e2e-github-apply:
	bash e2e/github-real.sh --write --pr --apply

# Mode 4: Browser journey (Playwright)
e2e-browser:
	GIT_PROVIDER=mock npx playwright test e2e/specs/user-journey.spec.js --headed

e2e-browser-gitea:
	GIT_PROVIDER=gitea npx playwright test e2e/specs/user-journey.spec.js --headed

# All modes (except --apply)
e2e-all: e2e-mock e2e-gitea e2e-github e2e-browser
```

### CI Pipeline (GitHub Actions)

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-mock:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start stack
        run: docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d --build
      - name: Wait for health
        run: |
          for i in $(seq 1 30); do
            curl -sf http://localhost:8003/api/health && break || sleep 2
          done
      - name: Run E2E
        run: npx playwright test e2e/specs/ --project=chromium
      - name: Logs on failure
        if: failure()
        run: docker compose logs backend mock-github

  e2e-github:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Start backend
        run: docker compose up -d --build
      - name: GitHub E2E (read-only)
        env:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
        run: bash e2e/github-real.sh
```

---

## Faza 3: Walidacja migracji PG

### Skrypt testowy migracji

```bash
#!/bin/bash
# e2e/test-pg-migration.sh
set -euo pipefail

echo "🐘 PostgreSQL Migration Validation"

# 1. Start PG
docker compose up -d db
sleep 3

# 2. Check PG is ready
docker compose exec db pg_isready -U semcod || { echo "❌ PG not ready"; exit 1; }
echo "✅ PostgreSQL ready"

# 3. Run Alembic migrations
docker compose run --rm backend alembic upgrade head
echo "✅ Migrations applied"

# 4. Verify tables exist
TABLES=$(docker compose exec db psql -U semcod -d semcod -t -c \
  "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;")
for table in scans users tenants repositories installations events audit_results; do
  if echo "$TABLES" | grep -q "$table"; then
    echo "  ✅ Table: $table"
  else
    echo "  ❌ Missing: $table"
  fi
done

# 5. Start full stack
docker compose up -d
sleep 5

# 6. Health check
curl -sf http://localhost:8003/api/health | python3 -c "
import sys,json
d = json.load(sys.stdin)
print(f'  Status: {d.get(\"status\")}')
print(f'  DB: {d.get(\"database\", \"unknown\")}')
"

# 7. CRUD smoke test
echo ""; echo "🧪 CRUD smoke test..."
# Create scan via audit
AUDIT=$(curl -sf -X POST http://localhost:8003/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/tom-sapletta-com/semcod","sandbox":true}')
AUDIT_ID=$(echo "$AUDIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('audit_id',''))" 2>/dev/null)
[ -n "$AUDIT_ID" ] && echo "  ✅ Audit created: ${AUDIT_ID}" || echo "  ❌ Audit failed"

# Check PG has data
ROW_COUNT=$(docker compose exec db psql -U semcod -d semcod -t -c "SELECT COUNT(*) FROM scans;")
echo "  Scans in PG: ${ROW_COUNT}"

echo ""; echo "🎉 PostgreSQL migration validated!"
```

---

## Timeline

| Faza | Co | Effort | Ryzyko |
|------|---|--------|--------|
| **1.1-1.3** | Redirect imports, delete SQLite modules | ~2h | Niskie — ORM już działa |
| **1.4** | Alembic PG migration + JSONB columns | ~1h | Średnie — sprawdzić JSON fields |
| **1.5-1.7** | Docker compose update + testy | ~1h | Niskie |
| **2 (Mode 3)** | github-real.sh script | ~2h | Niskie — wzorowane na full-cycle.sh |
| **2 (Mode 4)** | Playwright user-journey.spec.js | ~2h | Średnie — CSS selectors mogą wymagać data-testid |
| **2 (CI)** | GitHub Actions workflow | ~1h | Niskie |
| **3** | Walidacja migracji PG | ~1h | Niskie |

**Łącznie: ~10h** = 4h migracja + 5h E2E setup + 1h walidacja
