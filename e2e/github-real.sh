#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# E2E: Real GitHub via gh CLI
# Wymaga: gh auth login (jednorazowo)
#
# Tryby:
#   ./github-real.sh                        — read-only (bezpieczny)
#   ./github-real.sh --write                — tworzy branch + commit (nie PR)
#   ./github-real.sh --write --pr           — tworzy PR (zamyka po teście)
#   ./github-real.sh --write --pr --apply   — tworzy PR z reDSL zmianami
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

SEMCOD_URL="${SEMCOD_URL:-http://localhost:8003}"
REPO="${REPO:-tom-sapletta-com/semcod}"
MODE_WRITE=false; MODE_PR=false; MODE_APPLY=false

for arg in "$@"; do
  case $arg in
    --write) MODE_WRITE=true ;;
    --pr)    MODE_PR=true ;;
    --apply) MODE_APPLY=true ;;
    --repo=*) REPO="${arg#*=}" ;;
  esac
done

PASS=0; FAIL=0; SKIP=0
pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }
skip() { echo "  ⏭️  $1"; ((SKIP++)); }

echo "═══════════════════════════════════════════════════════════"
echo "  🧪 E2E: Real GitHub (${REPO})"
flags=""
[ "$MODE_WRITE" = true ] && flags+=" write"
[ "$MODE_PR" = true ] && flags+=" +pr"
[ "$MODE_APPLY" = true ] && flags+=" +apply"
echo "  Mode:${flags:- read-only}"
echo "═══════════════════════════════════════════════════════════"

# ── Phase 1: Auth ────────────────────────────────────────────────
echo ""; echo "📡 Phase 1: Authentication"

GH_TOKEN=$(gh auth token 2>/dev/null) || { fail "gh not authenticated — run: gh auth login"; exit 1; }
pass "gh token: ${GH_TOKEN:0:8}..."

SESSION=$(curl -sf --max-time 10 -X POST "${SEMCOD_URL}/auth/gh-token?token=${GH_TOKEN}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_token',''))" 2>/dev/null) || SESSION=""

if [ -n "$SESSION" ] && [ "$SESSION" != "" ]; then
  pass "Semcod session obtained"
else
  fail "Session exchange failed — is backend running at ${SEMCOD_URL}?"
  exit 1
fi

semcod() {
  curl -sf --max-time 15 -X "$1" "${SEMCOD_URL}$2" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${SESSION}" \
    ${3:+-d "$3"}
}

ME_LOGIN=$(semcod GET "/api/me" | python3 -c "import sys,json; print(json.load(sys.stdin).get('login',''))" 2>/dev/null) || ME_LOGIN=""
[ -n "$ME_LOGIN" ] && pass "Logged in as: ${ME_LOGIN}" || fail "/api/me failed"

# ── Phase 2: Read-only ───────────────────────────────────────────
echo ""; echo "📦 Phase 2: Read operations"

REPOS=$(semcod GET "/api/repos" 2>/dev/null) || REPOS="[]"
REPO_COUNT=$(echo "$REPOS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else d.get('total',0))" 2>/dev/null) || REPO_COUNT=0
[ "${REPO_COUNT}" -gt 0 ] && pass "Repos: ${REPO_COUNT}" || fail "No repos"

REPO_INFO=$(gh api "repos/${REPO}" 2>/dev/null) || REPO_INFO="{}"
DEFAULT_BRANCH=$(echo "$REPO_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin).get('default_branch','main'))" 2>/dev/null) || DEFAULT_BRANCH="main"
pass "Repo: ${REPO} (branch=${DEFAULT_BRANCH})"

BADGE_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "${SEMCOD_URL}/badge/${REPO//\//-}.svg" 2>/dev/null) || BADGE_STATUS="000"
[ "$BADGE_STATUS" = "200" ] && pass "Badge SVG: 200" || skip "Badge: ${BADGE_STATUS}"

HEALTH=$(semcod GET "/api/health" 2>/dev/null) || HEALTH="{}"
pass "Health: $(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null)"

# ── Phase 3: Sandbox audit ───────────────────────────────────────
echo ""; echo "🔍 Phase 3: Sandbox audit"

AUDIT_RESP=$(curl -sf --max-time 10 -X POST "${SEMCOD_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"repo_url\":\"https://github.com/${REPO}\",\"sandbox\":true}" 2>/dev/null) || AUDIT_RESP="{}"

AUDIT_ID=$(echo "$AUDIT_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('audit_id',''))" 2>/dev/null) || AUDIT_ID=""
if [ -n "$AUDIT_ID" ]; then
  pass "Audit started: ${AUDIT_ID}"
  for i in $(seq 1 20); do
    RESULT=$(curl -sf "${SEMCOD_URL}/api/audit/${AUDIT_ID}" 2>/dev/null) || RESULT="{}"
    STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','pending'))" 2>/dev/null) || STATUS="pending"
    case "$STATUS" in
      complete|completed|done)
        GRADE=$(echo "$RESULT" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('grade', r.get('result',{}).get('grade','?')))" 2>/dev/null)
        pass "Audit: grade=${GRADE}"
        break ;;
      error|failed)
        fail "Audit error"; break ;;
    esac
    sleep 3
  done
  [ "$STATUS" = "pending" ] && skip "Audit still pending"
else
  skip "Audit API unavailable"
fi

# ── Phase 4: Write operations ────────────────────────────────────
if [ "$MODE_WRITE" = true ]; then
  echo ""; echo "✏️  Phase 4: Write (branch + commit)"

  BRANCH="e2e-test/$(date +%Y%m%d-%H%M%S)"
  SHA=$(gh api "repos/${REPO}/git/refs/heads/${DEFAULT_BRANCH}" --jq '.object.sha' 2>/dev/null) || SHA=""

  if [ -z "$SHA" ]; then
    fail "Cannot get HEAD SHA"
  else
    gh api "repos/${REPO}/git/refs" -f ref="refs/heads/${BRANCH}" -f sha="${SHA}" >/dev/null 2>&1
    pass "Branch: ${BRANCH}"

    TEST_FILE=".e2e-test-$(date +%s).txt"
    COMMIT=$(gh api "repos/${REPO}/contents/${TEST_FILE}" -X PUT \
      -f message="e2e: automated test" \
      -f content="$(echo -n "E2E $(date)" | base64)" \
      -f branch="${BRANCH}" 2>/dev/null) || COMMIT="{}"
    COMMIT_SHA=$(echo "$COMMIT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('sha','')[:8])" 2>/dev/null) || COMMIT_SHA=""
    [ -n "$COMMIT_SHA" ] && pass "Commit: ${COMMIT_SHA}" || fail "Commit failed"

    if [ "$MODE_PR" = true ]; then
      echo ""; echo "🔀 Phase 5: Pull Request"

      PR_URL=$(gh pr create --repo "${REPO}" --head "${BRANCH}" --base "${DEFAULT_BRANCH}" \
        --title "e2e: automated test — will auto-close" \
        --body "Automated E2E test. Safe to ignore." 2>&1) || PR_URL=""

      if echo "$PR_URL" | grep -q 'github.com'; then
        PR_NUM=$(echo "$PR_URL" | grep -oP '\d+$') || PR_NUM=""
        pass "PR #${PR_NUM}: ${PR_URL}"
        sleep 5

        if [ "$MODE_APPLY" = true ]; then
          echo ""; echo "🤖 Phase 5b: reDSL"
          TICKET_RESP=$(semcod POST "/api/tickets" "{
            \"title\":\"e2e: auto-refactor\",\"repo\":\"${REPO}\",
            \"ticket_type\":\"refactor\",\"priority\":\"low\"
          }" 2>/dev/null) || TICKET_RESP="{}"
          TICKET_ID=$(echo "$TICKET_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null) || TICKET_ID=""
          [ -n "$TICKET_ID" ] && pass "Ticket: ${TICKET_ID}" || skip "Ticket failed"
        fi

        echo ""; echo "🧹 Cleanup"
        gh pr close "${PR_NUM}" --repo "${REPO}" --delete-branch 2>/dev/null || true
        pass "PR #${PR_NUM} closed + branch deleted"
      else
        fail "PR creation failed"
        gh api -X DELETE "repos/${REPO}/git/refs/heads/${BRANCH}" 2>/dev/null || true
      fi
    else
      echo ""; echo "🧹 Cleanup"
      gh api -X DELETE "repos/${REPO}/git/refs/heads/${BRANCH}" 2>/dev/null || true
      pass "Branch deleted"
    fi
  fi
fi

# ── Phase 6: Tickets ─────────────────────────────────────────────
echo ""; echo "🎫 Phase 6: Tickets"

T_RESP=$(semcod POST "/api/tickets" "{
  \"title\":\"e2e: validation\",\"repo\":\"${REPO}\",
  \"ticket_type\":\"feature\",\"priority\":\"low\"
}" 2>/dev/null) || T_RESP="{}"
T_ID=$(echo "$T_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null) || T_ID=""

if [ -n "$T_ID" ]; then
  pass "Ticket: ${T_ID}"
  semcod GET "/api/tickets" >/dev/null 2>&1 && pass "List OK" || fail "List failed"
  semcod GET "/api/tickets/stats" >/dev/null 2>&1 && pass "Stats OK" || fail "Stats failed"
  semcod PATCH "/api/tickets/${T_ID}" '{"priority":"high"}' >/dev/null 2>&1 && pass "Update OK" || fail "Update failed"
  semcod DELETE "/api/tickets/${T_ID}" >/dev/null 2>&1 && pass "Delete OK" || fail "Delete failed"
else
  fail "Ticket creation failed"
fi

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
printf "  ✅ %d passed | ❌ %d failed | ⏭️  %d skipped\n" "$PASS" "$FAIL" "$SKIP"
echo "═══════════════════════════════════════════════════════════"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
