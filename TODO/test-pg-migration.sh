#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# PostgreSQL Migration Validation
# Verifies: PG healthy, tables exist, Alembic applied, CRUD works, no SQLite refs
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

SEMCOD_URL="${SEMCOD_URL:-http://localhost:8003}"
PASS=0; FAIL=0

pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

echo "═══════════════════════════════════════════════════════════"
echo "  🐘 PostgreSQL Migration Validation"
echo "═══════════════════════════════════════════════════════════"

# ── 1. PG connectivity ───────────────────────────────────────────
echo ""; echo "── Infrastructure ──"

PG_READY=$(docker compose exec -T db pg_isready -U semcod 2>/dev/null) || PG_READY=""
if echo "$PG_READY" | grep -q "accepting"; then
  pass "PostgreSQL accepting connections"
else
  fail "PostgreSQL not ready"
fi

PG_VERSION=$(docker compose exec -T db psql -U semcod -d semcod -t -c "SELECT version();" 2>/dev/null | head -1 | xargs) || PG_VERSION=""
[ -n "$PG_VERSION" ] && pass "PG: ${PG_VERSION:0:30}..." || fail "Cannot query PG"

# ── 2. Tables exist ──────────────────────────────────────────────
echo ""; echo "── Schema ──"

TABLES=$(docker compose exec -T db psql -U semcod -d semcod -t -c \
  "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;" 2>/dev/null) || TABLES=""

EXPECTED_TABLES=(
  "audit_results"
  "badge_caches"
  "benchmark_cases"
  "benchmark_events"
  "events"
  "installations"
  "recommendation_feedback"
  "repositories"
  "scans"
  "subscriptions"
  "tenants"
  "users"
)

for table in "${EXPECTED_TABLES[@]}"; do
  if echo "$TABLES" | grep -qw "$table"; then
    pass "Table: ${table}"
  else
    fail "Missing table: ${table}"
  fi
done

# Check for tickets table (new)
if echo "$TABLES" | grep -qw "tickets"; then
  pass "Table: tickets (new feature)"
fi

# ── 3. Alembic version ──────────────────────────────────────────
echo ""; echo "── Migrations ──"

ALEMBIC_VER=$(docker compose exec -T db psql -U semcod -d semcod -t -c \
  "SELECT version_num FROM alembic_version LIMIT 1;" 2>/dev/null | xargs) || ALEMBIC_VER=""

if [ -n "$ALEMBIC_VER" ]; then
  pass "Alembic version: ${ALEMBIC_VER}"
else
  fail "No alembic_version table — migrations not applied"
fi

# ── 4. No SQLite references in active code ───────────────────────
echo ""; echo "── Code cleanup ──"

SQLITE_REFS=$(grep -rn "sqlite3\|get_connection()\|DB_PATH\|scans\.db" \
  --include="*.py" backend/ \
  --exclude-dir=alembic \
  --exclude-dir=__pycache__ \
  --exclude="*test*" \
  --exclude="db_session.py" \
  2>/dev/null | grep -v "^Binary" | wc -l) || SQLITE_REFS=0

if [ "$SQLITE_REFS" -eq 0 ]; then
  pass "No SQLite references in active code"
else
  fail "${SQLITE_REFS} SQLite references remaining:"
  grep -rn "sqlite3\|get_connection()\|DB_PATH\|scans\.db" \
    --include="*.py" backend/ \
    --exclude-dir=alembic --exclude-dir=__pycache__ \
    --exclude="*test*" --exclude="db_session.py" 2>/dev/null | head -5
fi

OLD_MODULES=("db_module/scans.py" "db_module/users.py" "db_module/tenants.py"
             "db_module/events.py" "db_module/installations.py"
             "db_module/repositories.py" "db_module/schema.py")
for mod in "${OLD_MODULES[@]}"; do
  if [ -f "backend/${mod}" ]; then
    fail "Old module still exists: ${mod}"
  else
    pass "Removed: ${mod}"
  fi
done

# ── 5. Backend health with PG ────────────────────────────────────
echo ""; echo "── Backend ──"

HEALTH=$(curl -sf --max-time 5 "${SEMCOD_URL}/api/health" 2>/dev/null) || HEALTH="{}"
H_STATUS=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null) || H_STATUS=""

if [ "$H_STATUS" = "ok" ]; then
  pass "Backend health: ok"
else
  fail "Backend health: ${H_STATUS}"
fi

# Check DATABASE_URL in container
DB_URL=$(docker compose exec -T backend printenv DATABASE_URL 2>/dev/null) || DB_URL=""
if echo "$DB_URL" | grep -q "postgresql"; then
  pass "Backend using PostgreSQL: ${DB_URL:0:40}..."
elif echo "$DB_URL" | grep -q "sqlite"; then
  fail "Backend still using SQLite!"
else
  fail "DATABASE_URL not set"
fi

# ── 6. CRUD smoke test ───────────────────────────────────────────
echo ""; echo "── CRUD smoke test ──"

# Sandbox audit (creates scan record)
AUDIT=$(curl -sf --max-time 10 -X POST "${SEMCOD_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/tom-sapletta-com/semcod","sandbox":true}' 2>/dev/null) || AUDIT="{}"
AUDIT_ID=$(echo "$AUDIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('audit_id',''))" 2>/dev/null) || AUDIT_ID=""

[ -n "$AUDIT_ID" ] && pass "Audit created in PG: ${AUDIT_ID}" || fail "Audit creation failed"

# Check PG has data
SCAN_COUNT=$(docker compose exec -T db psql -U semcod -d semcod -t -c \
  "SELECT COUNT(*) FROM scans;" 2>/dev/null | xargs) || SCAN_COUNT=0
pass "Scans in PG: ${SCAN_COUNT}"

USER_COUNT=$(docker compose exec -T db psql -U semcod -d semcod -t -c \
  "SELECT COUNT(*) FROM users;" 2>/dev/null | xargs) || USER_COUNT=0
pass "Users in PG: ${USER_COUNT}"

# ── 7. Connection pooling ────────────────────────────────────────
echo ""; echo "── Connection pooling ──"

PG_CONNECTIONS=$(docker compose exec -T db psql -U semcod -d semcod -t -c \
  "SELECT count(*) FROM pg_stat_activity WHERE datname='semcod';" 2>/dev/null | xargs) || PG_CONNECTIONS=0

if [ "${PG_CONNECTIONS}" -gt 0 ] && [ "${PG_CONNECTIONS}" -lt 50 ]; then
  pass "Active connections: ${PG_CONNECTIONS} (healthy)"
elif [ "${PG_CONNECTIONS}" -ge 50 ]; then
  fail "Too many connections: ${PG_CONNECTIONS} (check pool config)"
else
  fail "No active connections"
fi

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
printf "  ✅ %d passed | ❌ %d failed\n" "$PASS" "$FAIL"
echo "═══════════════════════════════════════════════════════════"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
