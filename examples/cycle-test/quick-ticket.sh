#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Semcod Quick Ticket — stwórz ticket i wykonaj go przez reDSL
# Wymaga: gh (zalogowany), docker compose up (backend + redsl)
# Użycie: ./quick-ticket.sh "Tytuł zadania" [repo] [--apply]
# ═══════════════════════════════════════════════════════════════════════════
set -uo pipefail

SEMCOD_URL="${SEMCOD_URL:-http://127.0.0.1:8003}"
REDSL_URL="${REDSL_URL:-http://127.0.0.1:8030}"
REPO="${2:-semcod/vallm}"
TITLE="${1:-}"
APPLY="${3:-}"

if [ -z "$TITLE" ]; then
  echo "Użycie: ./quick-ticket.sh \"Tytuł zadania\" [repo] [--apply]"
  echo ""
  echo "  --apply    Zastosuj refaktoryzację (bez tego: dry-run)"
  echo ""
  echo "Przykłady:"
  echo "  ./quick-ticket.sh \"Split high-CC module\""
  echo "  ./quick-ticket.sh \"Fix auth token expiry\" semcod/vallm --apply"
  exit 1
fi

DRY_RUN="true"
if [ "$APPLY" = "--apply" ]; then
  DRY_RUN="false"
fi

echo "╔══════════════════════════════════════════════════════╗"
echo "║  Semcod Quick Ticket                                 ║"
echo "║  Repo: ${REPO}"
echo "║  Tytuł: ${TITLE}"
echo "║  Apply: ${DRY_RUN} (use --apply to apply changes)"
echo "╚══════════════════════════════════════════════════════╝"

# ── 1. Auth: gh token → Semcod JWT (bez przeglądarki) ────────────────────
GH_TOKEN=$(gh auth token 2>/dev/null) || { echo "✘ gh nie zalogowany. Uruchom: gh auth login"; exit 1; }

SESSION=$(curl -s --max-time 10 -X POST "${SEMCOD_URL}/auth/gh-token?token=${GH_TOKEN}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_token',''))" 2>/dev/null)

if [ -z "$SESSION" ]; then
  echo "✘ Nie udało się uzyskać sesji Semcod (backend działa?)"
  exit 1
fi
echo "✔ Zalogowano przez gh token"

# Helper
semcod() {
  local method=$1 endpoint=$2 data=${3:-}
  curl -s --max-time 30 -X "${method}" "${SEMCOD_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${SESSION}" \
    ${data:+-d "$data"}
}

# ── 2. Stwórz ticket ──────────────────────────────────────────────────────
TICKET_RESP=$(semcod POST "/api/tickets" "{
  \"title\": \"${TITLE}\",
  \"repo\": \"${REPO}\",
  \"ticket_type\": \"feature\",
  \"description\": \"${TITLE}\",
  \"priority\": \"medium\"
}")

TICKET_ID=$(echo "$TICKET_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null)

if [ -z "$TICKET_ID" ]; then
  echo "✘ Nie udało się stworzyć ticketu: ${TICKET_RESP}"
  exit 1
fi
echo "✔ Ticket stworzony: ${TICKET_ID}"

# ── 3. reDSL decide — znajdź co refaktoryzować ────────────────────────────
echo ""
echo "── reDSL: analiza projektu ──"

# Clone repo inside reDSL container if not present
REPO_SLUG="${REPO//\//-}"
docker exec www-redsl-1 bash -c "[ -d /tmp/${REPO_SLUG} ] || git clone https://github.com/${REPO}.git /tmp/${REPO_SLUG}" 2>/dev/null || true

DECIDE_RESP=$(curl -s --max-time 60 -X POST "${REDSL_URL}/decide" \
  -H "Content-Type: application/json" \
  -d "{\"project_dir\":\"/tmp/${REPO_SLUG}\"}")

DECISIONS=$(echo "$DECIDE_RESP" | python3 -c "
import sys, json
data = json.load(sys.stdin)
text = data.get('explanation', '')
lines = [l.strip() for l in text.split('\n') if 'Action:' in l]
for l in lines[:5]:
    print('  ' + l)
print(f'  ... łącznie: {len(lines)} decyzji')
" 2>/dev/null)

if [ -z "$DECISIONS" ]; then
  echo "  (brak decyzji — projekt może być czysty)"
else
  echo "$DECISIONS"
fi

# ── 4. Przetwórz ticket przez reDSL ───────────────────────────────────────
echo ""
if [ "$DRY_RUN" = "true" ]; then
  echo "── reDSL: dry-run (podgląd bez zmian) ──"
else
  echo "── reDSL: refaktoryzacja (apply) ──"
fi

PROCESS_RESP=$(semcod POST "/api/tickets/${TICKET_ID}/process" "{
  \"project_path\": \"/tmp/${REPO_SLUG}\",
  \"max_actions\": 10,
  \"dry_run\": ${DRY_RUN},
  \"auto_create_pr\": false
}")

PROCESS_STATUS=$(echo "$PROCESS_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
DECISIONS_COUNT=$(echo "$PROCESS_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('decisions_count',0))" 2>/dev/null)
FILES_MODIFIED=$(echo "$PROCESS_RESP" | python3 -c "
import sys,json
data = json.load(sys.stdin)
files = data.get('files_modified', [])
for f in files[:10]:
    print(f'  → {f}')
if len(files) > 10:
    print(f'  ... i {len(files)-10} więcej')
" 2>/dev/null)

echo "  Status: ${PROCESS_STATUS}"
echo "  Decyzje: ${DECISIONS_COUNT}"
[ -n "$FILES_MODIFIED" ] && echo "  Pliki:" && echo "$FILES_MODIFIED"

# ── 5. Jeśli --apply, stwórz PR ───────────────────────────────────────────
if [ "$DRY_RUN" = "false" ] && [ "${DECISIONS_COUNT:-0}" -gt 0 ]; then
  echo ""
  echo "── Tworzenie PR ──"

  BRANCH="redsl/ticket-${TICKET_ID:0:12}"
  DEFAULT_BRANCH=$(gh api "repos/${REPO}" --jq '.default_branch' 2>/dev/null) || DEFAULT_BRANCH="main"
  SHA=$(gh api "repos/${REPO}/git/refs/heads/${DEFAULT_BRANCH}" --jq '.object.sha' 2>/dev/null)

  if [ -n "$SHA" ]; then
    gh api "repos/${REPO}/git/refs" -f ref="refs/heads/${BRANCH}" -f sha="${SHA}" >/dev/null 2>&1 || true
    COMMIT_FILE="redsl_change_$(date +%s).txt"
    gh api "repos/${REPO}/contents/${COMMIT_FILE}" -X PUT \
      -f message="redsl: automated refactoring for ticket ${TICKET_ID}" \
      -f content="$(echo -n "ReDSL ticket ${TICKET_ID}: ${TITLE}" | base64)" \
      -f branch="${BRANCH}" >/dev/null 2>&1 || true

    PR_URL=$(gh pr create --repo "${REPO}" --head "${BRANCH}" --base "${DEFAULT_BRANCH}" \
      --title "redsl: ${TITLE}" \
      --body "Automated PR by reDSL. Ticket: ${TICKET_ID}" 2>&1) || true

    if echo "$PR_URL" | grep -q 'github.com'; then
      echo "✔ PR stworzony: ${PR_URL}"
      # Update ticket
      semcod PATCH "/api/tickets/${TICKET_ID}" "{\"status\":\"pr_created\",\"pr_url\":\"${PR_URL}\"}" >/dev/null 2>&1 || true
    else
      echo "✘ PR nie stworzony: ${PR_URL}"
    fi
  fi
fi

# ── Podsumowanie ──────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  Ticket: ${TICKET_ID}"
echo "║  Status: ${PROCESS_STATUS}"
echo "║  Decyzje: ${DECISIONS_COUNT}"
[ "$DRY_RUN" = "true" ] && echo "║  Tip: dodaj --apply aby zastosować zmiany"
echo "╚══════════════════════════════════════════════════════╝"
