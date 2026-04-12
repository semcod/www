#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Semcod Quick Ticket — stwórz ticket i wykonaj go przez reDSL
# Wymaga: gh (zalogowany), docker compose up (backend + redsl)
#
# Tryby:
#   --auto         Automatycznie wygeneruj najlepszy ticket z analizy
#   "Tytuł"        Ręcznie podany tytuł
#   --apply        Zastosuj refaktoryzację (bez tego: dry-run)
#
# Przykłady:
#   ./quick-ticket.sh --auto                          # auto-ticket z analizy
#   ./quick-ticket.sh --auto semcod/vallm --apply     # auto-ticket + PR
#   ./quick-ticket.sh "Split high-CC module"          # ręczny tytuł
# ═══════════════════════════════════════════════════════════════════════════
set -uo pipefail

SEMCOD_URL="${SEMCOD_URL:-http://127.0.0.1:8003}"
REDSL_URL="${REDSL_URL:-http://127.0.0.1:8030}"
DOCS_DIR="${DOCS_DIR:-$(cd "$(dirname "$0")/../../docs" && pwd)}"
TMPDIR="${TMPDIR:-/tmp}"
AUTO_GEN="${TMPDIR}/semcod-auto-ticket.json"

# ── Parse args ────────────────────────────────────────────────────────────
AUTO_MODE=false
APPLY=false
TITLE=""
REPO="semcod/vallm"

for arg in "$@"; do
  case "$arg" in
    --auto)   AUTO_MODE=true ;;
    --apply)  APPLY=true ;;
    semcod/*) REPO="$arg" ;;
    *)        [ -z "$TITLE" ] && TITLE="$arg" ;;
  esac
done

DRY_RUN="true"
if [ "$APPLY" = "true" ]; then
  DRY_RUN="false"
fi

if [ "$AUTO_MODE" = "false" ] && [ -z "$TITLE" ]; then
  echo "Użycie: ./quick-ticket.sh [--auto] [\"Tytuł\"] [repo] [--apply]"
  echo ""
  echo "  --auto    Wygeneruj ticket automatycznie z analizy kodu + docs"
  echo "  --apply   Zastosuj refaktoryzację (bez tego: dry-run)"
  echo ""
  echo "Przykłady:"
  echo "  ./quick-ticket.sh --auto                          # auto-ticket"
  echo "  ./quick-ticket.sh --auto semcod/vallm --apply     # auto-ticket + PR"
  echo "  ./quick-ticket.sh \"Split high-CC module\"          # ręczny tytuł"
  exit 1
fi

echo "╔══════════════════════════════════════════════════════╗"
echo "║  Semcod Quick Ticket                                 ║"
echo "║  Repo: ${REPO}"
[ "$AUTO_MODE" = "true" ] && echo "║  Tryb: AUTO (analiza kodu + docs)"
[ -n "$TITLE" ] && echo "║  Tytuł: ${TITLE}"
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

# ── 2. Clone repo inside reDSL container ──────────────────────────────────
REPO_SLUG="${REPO//\//-}"
echo "✔ Przygotowanie repo w reDSL..."
docker exec www-redsl-1 bash -c "[ -d /tmp/${REPO_SLUG} ] || git clone https://github.com/${REPO}.git /tmp/${REPO_SLUG}" 2>/dev/null || true
docker exec www-redsl-1 bash -c "cd /tmp/${REPO_SLUG} && git pull" 2>/dev/null || true

# ── 3. AUTO: Analiza kodu + docs → wygeneruj najlepszy ticket ─────────────
if [ "$AUTO_MODE" = "true" ]; then
  echo ""
  echo "── AUTO: Analiza projektu ──"

  # 3a. reDSL analyze — metryki i alerty
  curl -s --max-time 60 -X POST "${REDSL_URL}/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"project_dir\":\"/tmp/${REPO_SLUG}\"}" > "${TMPDIR}/semcod-analyze.json" 2>/dev/null

  # 3b. reDSL decide — konkretne decyzje refaktoryzacji
  curl -s --max-time 60 -X POST "${REDSL_URL}/decide" \
    -H "Content-Type: application/json" \
    -d "{\"project_dir\":\"/tmp/${REPO_SLUG}\"}" > "${TMPDIR}/semcod-decide.json" 2>/dev/null

  # 3c. Generuj ticket z analizy + docs
  python3 << 'PYEOF' > "${AUTO_GEN}"
import json, os, glob

# Load analyze
try:
    with open(os.environ.get("TMPDIR", "/tmp") + "/semcod-analyze.json") as f:
        analyze = json.load(f)
except:
    analyze = {}

# Load decide
try:
    with open(os.environ.get("TMPDIR", "/tmp") + "/semcod-decide.json") as f:
        decide = json.load(f)
except:
    decide = {}

# Extract metrics
total_files = analyze.get("total_files", 0)
total_lines = analyze.get("total_lines", 0)
avg_cc = analyze.get("avg_cc", 0)
critical = analyze.get("critical_count", 0)
alerts = analyze.get("alerts", [])

# Extract top decisions
explanation = decide.get("explanation", "")
decision_lines = [l.strip() for l in explanation.split("\n") if "Action:" in l]
top_actions = []
for line in decision_lines[:5]:
    parts = line.split("Action:")
    if len(parts) > 1:
        action = parts[1].strip().split()[0] if parts[1].strip() else ""
        top_actions.append(action)

# Extract target files
targets = []
for line in explanation.split("\n"):
    if "Target:" in line:
        target = line.split("Target:")[-1].strip()
        if target and target != "-":
            targets.append(target)

# Read docs context
docs_dir = os.environ.get("DOCS_DIR", "")
docs_context = []
if docs_dir and os.path.isdir(docs_dir):
    for f in sorted(glob.glob(os.path.join(docs_dir, "*.md")))[:8]:
        try:
            with open(f, "r") as fh:
                text = fh.read()[:2000]
                headings = [l.strip().lstrip("#").strip() for l in text.split("\n") if l.strip().startswith("#")][:3]
                metrics = [l.strip() for l in text.split("\n") if "|" in l and any(k in l.lower() for k in ["cc", "complexity", "critical", "god", "fan-out", "hotspot"])][:3]
                key_lines = headings + metrics
                if key_lines:
                    docs_context.append(f"[{os.path.basename(f)}]: {' | '.join(key_lines)}")
        except:
            pass

# Build ticket
if top_actions:
    primary_action = top_actions[0]
    primary_target = targets[0] if targets else "unknown"
    title = f"{primary_action}: {primary_target}"

    desc_parts = [
        "Auto-generated ticket from code analysis + docs context.",
        "",
        f"Project: {total_files} files, {total_lines} LOC, CC̄={avg_cc}, critical={critical}",
        f"Top actions: {', '.join(top_actions[:3])}",
        f"Target files: {', '.join(targets[:3])}",
    ]

    if docs_context:
        desc_parts.append("")
        desc_parts.append("Platform context from docs:")
        for line in docs_context[:5]:
            desc_parts.append(f"  {line}")

    if alerts:
        desc_parts.append("")
        desc_parts.append(f"Alerts ({len(alerts)}):")
        for a in alerts[:5]:
            desc_parts.append(f"  {a.get('type','')}: {a.get('name','')} (value={a.get('value','')}, limit={a.get('limit','')})")

    description = "\n".join(desc_parts)

    if critical > 5 or avg_cc > 8:
        priority = "high"
    elif critical > 2 or avg_cc > 5:
        priority = "medium"
    else:
        priority = "low"

    result = {
        "title": title,
        "description": description,
        "priority": priority,
        "decisions_count": len(decision_lines),
        "top_action": primary_action,
        "top_target": primary_target,
        "metrics": {
            "files": total_files,
            "loc": total_lines,
            "avg_cc": avg_cc,
            "critical": critical,
            "alerts": len(alerts)
        }
    }
else:
    result = {
        "title": "No refactoring needed",
        "description": "Project appears clean.",
        "priority": "low",
        "decisions_count": 0,
        "top_action": "none",
        "top_target": "",
        "metrics": {"files": total_files, "loc": total_lines, "avg_cc": avg_cc, "critical": critical, "alerts": len(alerts)}
    }

print(json.dumps(result, ensure_ascii=False))
PYEOF

  TITLE=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('title',''))" 2>/dev/null)
  PRIORITY=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('priority','medium'))" 2>/dev/null)
  DECISIONS_COUNT_AUTO=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('decisions_count',0))" 2>/dev/null)
  TOP_ACTION=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('top_action',''))" 2>/dev/null)
  TOP_TARGET=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('top_target',''))" 2>/dev/null)

  python3 -c "
import json
m = json.load(open('${AUTO_GEN}')).get('metrics', {})
print(f'  Pliki: {m.get(\"files\",0)} | LOC: {m.get(\"loc\",0)} | CC̄: {m.get(\"avg_cc\",0)} | Critical: {m.get(\"critical\",0)} | Alerty: {m.get(\"alerts\",0)}')
" 2>/dev/null

  echo "  Najlepsza akcja: ${TOP_ACTION} → ${TOP_TARGET}"
  echo "  Wygenerowany tytuł: ${TITLE}"

  if [ "${DECISIONS_COUNT_AUTO:-0}" -eq 0 ]; then
    echo ""
    echo "✔ Projekt czysty — brak krytycznych problemów"
    exit 0
  fi

  # Show top decisions
  echo ""
  echo "  Top decyzje reDSL:"
  python3 -c "
import json
data = json.load(open('${TMPDIR}/semcod-decide.json'))
text = data.get('explanation', '')
lines = [l.strip() for l in text.split('\n') if 'Action:' in l]
for l in lines[:5]:
    print('    ' + l)
print(f'    ... łącznie: {len(lines)} decyzji')
" 2>/dev/null
fi

# ── 4. Stwórz ticket ──────────────────────────────────────────────────────
if [ "$AUTO_MODE" = "true" ]; then
  DESCRIPTION=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('description',''))" 2>/dev/null)
  DESCRIPTION_ESC=$(python3 -c "import json; print(json.dumps(open('${AUTO_GEN}').read()))" 2>/dev/null | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
desc = json.loads(data).get('description', '')
print(json.dumps(desc))
" 2>/dev/null)
  TICKET_RESP=$(semcod POST "/api/tickets" "{
    \"title\": \"${TITLE}\",
    \"repo\": \"${REPO}\",
    \"ticket_type\": \"feature\",
    \"description\": ${DESCRIPTION_ESC},
    \"priority\": \"${PRIORITY}\"
  }")
else
  TICKET_RESP=$(semcod POST "/api/tickets" "{
    \"title\": \"${TITLE}\",
    \"repo\": \"${REPO}\",
    \"ticket_type\": \"feature\",
    \"description\": \"${TITLE}\",
    \"priority\": \"medium\"
  }")
fi

TICKET_ID=$(echo "$TICKET_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null)

if [ -z "$TICKET_ID" ]; then
  echo "✘ Nie udało się stworzyć ticketu: ${TICKET_RESP}"
  exit 1
fi
echo ""
echo "✔ Ticket stworzony: ${TICKET_ID}"

# ── 5. Przetwórz ticket przez reDSL ────────────────────────────────────────
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
unique = list(dict.fromkeys(files))
for f in unique[:10]:
    print(f'  → {f}')
if len(unique) > 10:
    print(f'  ... i {len(unique)-10} więcej')
" 2>/dev/null)

echo "  Status: ${PROCESS_STATUS}"
echo "  Decyzje: ${DECISIONS_COUNT}"
[ -n "$FILES_MODIFIED" ] && echo "  Pliki:" && echo "$FILES_MODIFIED"

# ── 6. Jeśli --apply, stwórz PR ───────────────────────────────────────────
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
echo "║  Tytuł: ${TITLE}"
echo "║  Status: ${PROCESS_STATUS}"
echo "║  Decyzje: ${DECISIONS_COUNT}"
[ "$DRY_RUN" = "true" ] && echo "║  Tip: dodaj --apply aby zastosować zmiany"
echo "╚══════════════════════════════════════════════════════╝"
