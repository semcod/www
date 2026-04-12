#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Semcod Quick Ticket — stwórz ticket i wykonaj go przez reDSL
# Wymaga: gh (zalogowany), docker compose up (backend + redsl)
#
# Tryby:
#   --auto         Automatycznie wygeneruj najlepszy ticket z analizy
#   "Tytuł"        Ręcznie podany tytuł
#   --apply        Zastosuj refaktoryzację (commit realne zmiany w kontenerze)
#
# Przykłady:
#   ./quick-ticket.sh --auto                          # auto-ticket z analizy
#   ./quick-ticket.sh --auto semcod/vallm --apply     # auto-ticket + PR z realnymi zmianami
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
  echo "  --apply   Zastosuj refaktoryzację (commit realne zmiany)"
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
echo "║  Apply: ${DRY_RUN}"
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
docker exec www-redsl-1 bash -c "cd /tmp/${REPO_SLUG} && git pull && git checkout -- . && git clean -fd" 2>/dev/null || true

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

# Extract targets and scores
targets = []
scores = []
for line in explanation.split("\n"):
    if "Target:" in line:
        target = line.split("Target:")[-1].strip()
        if target and target != "-":
            targets.append(target)
    if "Score:" in line:
        score_str = line.split("Score:")[-1].strip().split()[0]
        try:
            scores.append(float(score_str))
        except:
            pass

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
    primary_score = scores[0] if scores else 0

    # Quality-focused title
    action_labels = {
        "split_module": "Split god module",
        "extract_functions": "Extract high-CC functions",
        "simplify_conditionals": "Simplify deep nesting",
        "reduce_fan_out": "Reduce fan-out",
        "inline_trivial": "Inline trivial wrappers",
        "deduplicate": "Deduplicate code",
    }
    quality_label = action_labels.get(primary_action, primary_action)
    title = f"{quality_label}: {primary_target}"

    desc_parts = [
        f"Auto-generated quality improvement ticket from code analysis.",
        f"",
        f"## Problem",
        f"File `{primary_target}` has quality issues requiring {primary_action}.",
        f"Score: {primary_score:.2f} (higher = more urgent)",
    ]

    # Add specific alert details for this target
    target_alerts = [a for a in alerts if primary_target.split("/")[-1].replace(".py","") in a.get("name","")]
    if target_alerts:
        desc_parts.append("")
        desc_parts.append("## Alerts for this file")
        for a in target_alerts[:5]:
            desc_parts.append(f"- {a.get('type','')}: {a.get('name','')} (value={a.get('value','')}, limit={a.get('limit','')})")

    desc_parts.append("")
    desc_parts.append("## Project metrics")
    desc_parts.append(f"- Files: {total_files}, LOC: {total_lines}, CC̄: {avg_cc}, Critical: {critical}")

    desc_parts.append("")
    desc_parts.append("## All refactoring decisions")
    for i, action in enumerate(top_actions[:5]):
        target = targets[i] if i < len(targets) else "?"
        score = scores[i] if i < len(scores) else 0
        label = action_labels.get(action, action)
        desc_parts.append(f"{i+1}. **{label}** → `{target}` (score: {score:.2f})")

    if docs_context:
        desc_parts.append("")
        desc_parts.append("## Platform context")
        for line in docs_context[:3]:
            desc_parts.append(f"- {line.strip()}")

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
        "top_score": primary_score,
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
        "description": "Project appears clean — no critical issues detected.",
        "priority": "low",
        "decisions_count": 0,
        "top_action": "none",
        "top_target": "",
        "top_score": 0,
        "metrics": {"files": total_files, "loc": total_lines, "avg_cc": avg_cc, "critical": critical, "alerts": len(alerts)}
    }

print(json.dumps(result, ensure_ascii=False))
PYEOF

  TITLE=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('title',''))" 2>/dev/null)
  PRIORITY=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('priority','medium'))" 2>/dev/null)
  DECISIONS_COUNT_AUTO=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('decisions_count',0))" 2>/dev/null)
  TOP_ACTION=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('top_action',''))" 2>/dev/null)
  TOP_TARGET=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('top_target',''))" 2>/dev/null)
  TOP_SCORE=$(python3 -c "import json; print(json.load(open('${AUTO_GEN}')).get('top_score',0))" 2>/dev/null)

  python3 -c "
import json
m = json.load(open('${AUTO_GEN}')).get('metrics', {})
print(f'  Pliki: {m.get(\"files\",0)} | LOC: {m.get(\"loc\",0)} | CC̄: {m.get(\"avg_cc\",0)} | Critical: {m.get(\"critical\",0)} | Alerty: {m.get(\"alerts\",0)}')
" 2>/dev/null

  echo "  Najlepsza akcja: ${TOP_ACTION} → ${TOP_TARGET} (score: ${TOP_SCORE})"
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
  DESCRIPTION_ESC=$(python3 -c "
import json
with open('${AUTO_GEN}') as f:
    data = json.load(f)
print(json.dumps(data.get('description', ''), ensure_ascii=False))
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

# ── 6. Jeśli --apply, stwórz PR z realnymi zmianami z kontenera ────────────
if [ "$APPLY" = "true" ] && [ "${DECISIONS_COUNT:-0}" -gt 0 ]; then
  echo ""
  echo "── reDSL: run_cycle (realne zmiany kodu) ──"

  # Clear reDSL history to avoid duplicate decision blocks
  docker exec www-redsl-1 bash -c "rm -rf /app/.redsl/history.jsonl /tmp/refactor_memory/chroma.sqlite3" 2>/dev/null

  # Use run_cycle which actually modifies files via LLM (not plan-only /refactor)
  LLM_MODEL="${LLM_MODEL:-openrouter/openai/gpt-4o-mini}"
  CYCLE_OUTPUT=$(docker exec -e LLM_MODEL="${LLM_MODEL}" www-redsl-1 python3 -c "
import os, sys
os.environ['LLM_MODEL'] = '${LLM_MODEL}'
from redsl.orchestrator import RefactorOrchestrator
from redsl.config import AgentConfig
config = AgentConfig.from_env()
config.llm.model = '${LLM_MODEL}'
config.refactor.dry_run = False
config.refactor.reflection_rounds = 1
orch = RefactorOrchestrator(config)
from pathlib import Path
report = orch.run_cycle(Path('/tmp/${REPO_SLUG}'), max_actions=3)
print(f'Applied: {report.proposals_applied}')
print(f'Rejected: {report.proposals_rejected}')
for e in report.errors[:3]:
    print(f'Error: {e[:200]}')
" 2>&1)

  APPLIED_COUNT=$(echo "$CYCLE_OUTPUT" | grep "Applied:" | awk '{print $2}')
  echo "  $CYCLE_OUTPUT" | grep -E "^(Applied|Rejected|Error):"

  # Check if reDSL actually modified files in the container
  CHANGED_FILES=$(docker exec www-redsl-1 bash -c "cd /tmp/${REPO_SLUG} && git diff --name-only && git diff --name-only --diff-filter=A && git ls-files --others --exclude-standard" 2>/dev/null)

  if [ -n "$CHANGED_FILES" ]; then
    echo ""
    echo "  Zmodyfikowane pliki w kontenerze:"
    echo "$CHANGED_FILES" | while read f; do echo "    → $f"; done

    # Export diff as patch from container
    PATCH_FILE="${TMPDIR}/redsl-patch-${TICKET_ID}.diff"
    docker exec www-redsl-1 bash -c "cd /tmp/${REPO_SLUG} && git diff HEAD && git diff --cached && echo '---newfiles---' && for f in \$(git ls-files --others --exclude-standard); do echo '--- /dev/null'; echo '+++ b/\$f'; cat \"\$f\"; done" > "${PATCH_FILE}" 2>/dev/null

    # Create branch, apply patch, push, create PR via gh on host
    BRANCH="redsl/quality-${TICKET_ID:0:12}"
    CLONE_DIR="${TMPDIR}/redsl-pr-${TICKET_ID}"

    rm -rf "${CLONE_DIR}" 2>/dev/null
    gh repo clone "${REPO}" "${CLONE_DIR}" -- --depth=1 2>/dev/null
    cd "${CLONE_DIR}" 2>/dev/null || true
    git checkout -b "${BRANCH}" 2>/dev/null

    # Apply the patch
    if git apply "${PATCH_FILE}" 2>/dev/null; then
      git add -A 2>/dev/null
      git commit -m "refactor: ${TITLE} (ticket ${TICKET_ID})

ReDSL auto-refactoring: ${TOP_ACTION} on ${TOP_TARGET}
Applied: ${APPLIED_COUNT:-?} proposals" 2>/dev/null
      git push origin "${BRANCH}" 2>/dev/null

      PR_URL=$(gh pr create --repo "${REPO}" --head "${BRANCH}" --base main \
        --title "refactor: ${TITLE}" \
        --body "Automated quality improvement by reDSL.

Ticket: ${TICKET_ID}
Priority: ${PRIORITY}
Decisions: ${DECISIONS_COUNT}
Applied: ${APPLIED_COUNT:-?}

## Modified files
$(echo "$CHANGED_FILES" | while read f; do echo "- \`$f\`"; done)

---
*Generated by [Semcod](https://semcod.com) reDSL engine*" 2>&1) || true

      if echo "$PR_URL" | grep -q 'github.com'; then
        echo "✔ PR stworzony: ${PR_URL}"
        semcod PATCH "/api/tickets/${TICKET_ID}" "{\"status\":\"pr_created\",\"pr_url\":\"${PR_URL}\"}" >/dev/null 2>&1 || true
      else
        echo "✘ PR nie stworzony: ${PR_URL}"
      fi
    else
      echo "  ⚠ Patch nie aplikuje się czysto — tworzę ticket z opisem"
      semcod PATCH "/api/tickets/${TICKET_ID}" "{\"status\":\"analyzed\"}" >/dev/null 2>&1 || true
    fi

    # Cleanup
    rm -rf "${CLONE_DIR}" "${PATCH_FILE}" 2>/dev/null
  else
    echo "  ⚠ reDSL nie zmodyfikował plików (brak LLM lub brak decyzji)"
    echo "  Tworzę ticket z opisem refaktoryzacji do ręcznego wykonania"
    semcod PATCH "/api/tickets/${TICKET_ID}" "{\"status\":\"analyzed\"}" >/dev/null 2>&1 || true
  fi
fi

# ── Podsumowanie ──────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  Ticket: ${TICKET_ID}"
echo "║  Tytuł: ${TITLE}"
echo "║  Priorytet: ${PRIORITY:-medium}"
echo "║  Status: ${PROCESS_STATUS}"
echo "║  Decyzje: ${DECISIONS_COUNT}"
[ "$APPLY" = "false" ] && echo "║  Tip: dodaj --apply aby zastosować zmiany"
echo "╚══════════════════════════════════════════════════════╝"
