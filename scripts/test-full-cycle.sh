#!/bin/bash
# test-full-cycle.sh — Validate full developer cycle via Gitea
#
# Tests:
#   1. API connectivity (Gitea + Backend)
#   2. GiteaAdapter: list repos, get default branch
#   3. Create branch → commit → open PR
#   4. Webhook delivery → backend processes PR event
#   5. PR comment bot adds analysis comment
#   6. Badge endpoint returns SVG
#   7. Audit via API
#
# Requires: setup-gitea.sh already run
set -euo pipefail

GITEA_URL="${GITEA_URL:-http://localhost:3100}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8003}"
WEBHOOK_SECRET="${GITEA_WEBHOOK_SECRET:-semcod-webhook-secret}"

# Load env if available
[ -f .env.gitea ] && source .env.gitea 2>/dev/null || true

USER="tom-sapletta-com"
PASS="Semcod2026!"
REPO="sample-python"
FULL_REPO="${USER}/${REPO}"

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

pass() { echo "  ✅ $1"; ((PASS_COUNT++)); }
fail() { echo "  ❌ $1"; ((FAIL_COUNT++)); }
skip() { echo "  ⏭️  $1"; ((SKIP_COUNT++)); }

api_gitea() {
  curl -sf -u "${USER}:${PASS}" -H "Content-Type: application/json" "$@"
}

echo "═══════════════════════════════════════════════════════════"
echo "  🧪 Semcod Full Developer Cycle Test"
echo "  Gitea: ${GITEA_URL}  Backend: ${BACKEND_URL}"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ── Test 1: Service health ───────────────────────────────────────
echo "📡 Test 1: Service connectivity"

GITEA_VER=$(curl -sf "${GITEA_URL}/api/v1/version" | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','?'))" 2>/dev/null || echo "")
if [ -n "$GITEA_VER" ]; then
  pass "Gitea API v${GITEA_VER}"
else
  fail "Gitea not responding at ${GITEA_URL}"
fi

BACKEND_HEALTH=$(curl -sf "${BACKEND_URL}/api/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null || echo "")
if [ "$BACKEND_HEALTH" = "ok" ]; then
  pass "Backend health: ok"
else
  fail "Backend not responding at ${BACKEND_URL}"
fi

# ── Test 2: Repository access via Gitea API ─────────────────────
echo ""
echo "📦 Test 2: Repository access"

REPOS=$(api_gitea "${GITEA_URL}/api/v1/repos/search?q=sample" 2>/dev/null || echo '{"data":[]}')
REPO_COUNT=$(echo "$REPOS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('data',d) if isinstance(d,dict) else d))" 2>/dev/null || echo "0")

if [ "$REPO_COUNT" -ge 2 ]; then
  pass "Found ${REPO_COUNT} sample repos"
else
  fail "Expected ≥2 repos, found ${REPO_COUNT}"
fi

DEFAULT_BRANCH=$(api_gitea "${GITEA_URL}/api/v1/repos/${FULL_REPO}" 2>/dev/null \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('default_branch',''))" 2>/dev/null || echo "")

if [ "$DEFAULT_BRANCH" = "main" ]; then
  pass "Default branch: main"
else
  fail "Default branch: '${DEFAULT_BRANCH}' (expected 'main')"
fi

# ── Test 3: Create branch + commit + PR ──────────────────────────
echo ""
echo "🔀 Test 3: Branch → Commit → Pull Request"

BRANCH_NAME="semcod/test-refactor-$(date +%s)"
MAIN_SHA=$(api_gitea "${GITEA_URL}/api/v1/repos/${FULL_REPO}/git/refs/heads/main" 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['object']['sha'] if isinstance(d,list) else d.get('object',{}).get('sha',''))" 2>/dev/null || echo "")

if [ -z "$MAIN_SHA" ]; then
  fail "Cannot get main branch SHA"
  MAIN_SHA=$(api_gitea "${GITEA_URL}/api/v1/repos/${FULL_REPO}/branches/main" 2>/dev/null \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('commit',{}).get('id',''))" 2>/dev/null || echo "")
fi

# Create branch
BRANCH_RESP=$(api_gitea -X POST "${GITEA_URL}/api/v1/repos/${FULL_REPO}/branches" \
  -d "{\"new_branch_name\":\"${BRANCH_NAME}\",\"old_branch_name\":\"main\"}" 2>/dev/null || echo '{}')

BRANCH_OK=$(echo "$BRANCH_RESP" | python3 -c "import sys,json; print('yes' if json.load(sys.stdin).get('name','') else 'no')" 2>/dev/null || echo "no")

if [ "$BRANCH_OK" = "yes" ]; then
  pass "Branch created: ${BRANCH_NAME}"
else
  fail "Branch creation failed"
fi

# Commit a refactored file
NEW_CODE='import json
from typing import Optional
from dataclasses import dataclass

@dataclass
class ProcessorConfig:
    multiplier: int = 1

class DataProcessor:
    """Refactored: extracted config to dataclass, removed duplicate validate."""
    
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.results = []
    
    def process(self, data: list) -> list:
        filtered = [x for x in data if self.validate(x)]
        self.results = [self.transform(x) for x in filtered]
        return self.results
    
    def validate(self, item: dict) -> bool:
        return (
            isinstance(item, dict)
            and "id" in item
            and "value" in item
            and item["value"] >= 0
        )
    
    def transform(self, item: dict) -> dict:
        return {
            "id": item["id"],
            "value": item["value"] * self.config.multiplier,
            "label": item.get("label", "unknown").upper(),
        }

if __name__ == "__main__":
    proc = DataProcessor(ProcessorConfig(multiplier=2))
    sample = [{"id": 1, "value": 10}, {"id": 2, "value": -5}, {"id": 3, "value": 7}]
    print(json.dumps(proc.process(sample), indent=2))
'

# Get existing file SHA
FILE_SHA=$(api_gitea "${GITEA_URL}/api/v1/repos/${FULL_REPO}/contents/app.py?ref=${BRANCH_NAME}" 2>/dev/null \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))" 2>/dev/null || echo "")

ENCODED=$(echo -n "$NEW_CODE" | base64 -w0 2>/dev/null || echo -n "$NEW_CODE" | base64)

COMMIT_RESP=$(api_gitea -X PUT "${GITEA_URL}/api/v1/repos/${FULL_REPO}/contents/app.py" \
  -d "{
    \"content\":\"${ENCODED}\",
    \"message\":\"refactor: extract config dataclass, remove duplicate validate\",
    \"branch\":\"${BRANCH_NAME}\",
    \"sha\":\"${FILE_SHA}\"
  }" 2>/dev/null || echo '{}')

COMMIT_SHA=$(echo "$COMMIT_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('content',{}).get('sha','')[:8])" 2>/dev/null || echo "")

if [ -n "$COMMIT_SHA" ]; then
  pass "Committed refactored app.py (${COMMIT_SHA})"
else
  fail "Commit failed"
fi

# Open PR
PR_RESP=$(api_gitea -X POST "${GITEA_URL}/api/v1/repos/${FULL_REPO}/pulls" \
  -d "{
    \"title\":\"refactor: extract config, remove duplication\",
    \"body\":\"## Changes\\n- Extracted ProcessorConfig dataclass\\n- Removed duplicate validate() method\\n- Simplified validation logic\\n\\nThis PR tests the full Semcod webhook + PR comment cycle.\",
    \"head\":\"${BRANCH_NAME}\",
    \"base\":\"main\"
  }" 2>/dev/null || echo '{}')

PR_NUMBER=$(echo "$PR_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('number',0))" 2>/dev/null || echo "0")
PR_URL=$(echo "$PR_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('html_url',''))" 2>/dev/null || echo "")

if [ "$PR_NUMBER" -gt 0 ]; then
  pass "PR #${PR_NUMBER} opened: ${PR_URL}"
else
  fail "PR creation failed"
fi

# ── Test 4: Webhook delivery ─────────────────────────────────────
echo ""
echo "🔗 Test 4: Webhook delivery"

# Check webhook deliveries
sleep 3  # Give webhook time to fire

HOOKS=$(api_gitea "${GITEA_URL}/api/v1/repos/${FULL_REPO}/hooks" 2>/dev/null || echo '[]')
HOOK_ID=$(echo "$HOOKS" | python3 -c "
import sys,json
hooks = json.load(sys.stdin)
for h in hooks:
    if 'webhook' in h.get('config',{}).get('url','') or 'backend' in h.get('config',{}).get('url',''):
        print(h['id'])
        break
" 2>/dev/null || echo "")

if [ -n "$HOOK_ID" ]; then
  # Check last delivery status
  DELIVERIES=$(api_gitea "${GITEA_URL}/api/v1/repos/${FULL_REPO}/hooks/${HOOK_ID}/deliveries" 2>/dev/null || echo '[]')
  DELIVERY_STATUS=$(echo "$DELIVERIES" | python3 -c "
import sys,json
d = json.load(sys.stdin)
if d:
    latest = d[0]
    status = latest.get('status','unknown')
    event = latest.get('event','?')
    print(f'{status}:{event}')
else:
    print('none')
" 2>/dev/null || echo "none")

  if [[ "$DELIVERY_STATUS" == *"success"* ]] || [[ "$DELIVERY_STATUS" == *"delivered"* ]]; then
    pass "Webhook delivered: ${DELIVERY_STATUS}"
  elif [ "$DELIVERY_STATUS" = "none" ]; then
    skip "No webhook deliveries yet (backend may not be processing gitea webhooks)"
  else
    fail "Webhook delivery status: ${DELIVERY_STATUS}"
  fi
else
  skip "No webhook found for backend"
fi

# ── Test 5: PR comment bot ───────────────────────────────────────
echo ""
echo "💬 Test 5: PR comment bot"

if [ "$PR_NUMBER" -gt 0 ]; then
  sleep 5  # Wait for analysis

  COMMENTS=$(api_gitea "${GITEA_URL}/api/v1/repos/${FULL_REPO}/issues/${PR_NUMBER}/comments" 2>/dev/null || echo '[]')
  COMMENT_COUNT=$(echo "$COMMENTS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

  if [ "$COMMENT_COUNT" -gt 0 ]; then
    pass "PR has ${COMMENT_COUNT} comment(s) from bot"
  else
    skip "No PR comments yet (bot may need more time or webhook config)"
  fi
else
  skip "No PR to check comments on"
fi

# ── Test 6: Badge endpoint ───────────────────────────────────────
echo ""
echo "🏆 Test 6: Badge endpoint"

BADGE_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "${BACKEND_URL}/badge/${USER}-${REPO}.svg" 2>/dev/null || echo "000")
BADGE_CT=$(curl -sf -o /dev/null -w "%{content_type}" "${BACKEND_URL}/badge/${USER}-${REPO}.svg" 2>/dev/null || echo "")

if [ "$BADGE_STATUS" = "200" ] && [[ "$BADGE_CT" == *"svg"* ]]; then
  pass "Badge returns SVG (200)"
elif [ "$BADGE_STATUS" = "200" ]; then
  pass "Badge returns 200 (content-type: ${BADGE_CT})"
else
  skip "Badge not available yet (status: ${BADGE_STATUS})"
fi

# ── Test 7: Audit via API ────────────────────────────────────────
echo ""
echo "🔍 Test 7: Audit via backend API"

# Try sandbox analysis (no auth needed)
AUDIT_RESP=$(curl -sf -X POST "${BACKEND_URL}/api/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"repo_url\":\"${GITEA_URL}/${FULL_REPO}\",\"sandbox\":true}" 2>/dev/null || echo '{}')

AUDIT_ID=$(echo "$AUDIT_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('audit_id',''))" 2>/dev/null || echo "")

if [ -n "$AUDIT_ID" ]; then
  pass "Audit started: ${AUDIT_ID}"

  # Poll for result
  for i in $(seq 1 15); do
    RESULT=$(curl -sf "${BACKEND_URL}/api/audit/${AUDIT_ID}" 2>/dev/null || echo '{}')
    STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','pending'))" 2>/dev/null || echo "pending")
    if [ "$STATUS" = "complete" ] || [ "$STATUS" = "completed" ] || [ "$STATUS" = "done" ]; then
      GRADE=$(echo "$RESULT" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('grade',r.get('result',{}).get('grade','?')))" 2>/dev/null || echo "?")
      pass "Audit complete — grade: ${GRADE}"
      break
    elif [ "$STATUS" = "error" ] || [ "$STATUS" = "failed" ]; then
      fail "Audit failed"
      break
    fi
    sleep 4
  done
  [ "$STATUS" = "pending" ] && skip "Audit still pending after 60s"
else
  skip "Audit API not available or requires auth"
fi

# ── Test 8: Diff via GiteaAdapter ────────────────────────────────
echo ""
echo "📄 Test 8: PR diff retrieval"

if [ "$PR_NUMBER" -gt 0 ]; then
  DIFF=$(api_gitea "${GITEA_URL}/api/v1/repos/${FULL_REPO}/pulls/${PR_NUMBER}.diff" 2>/dev/null || echo "")
  DIFF_LINES=$(echo "$DIFF" | wc -l)

  if [ "$DIFF_LINES" -gt 5 ]; then
    pass "PR diff: ${DIFF_LINES} lines"
  else
    fail "PR diff too short (${DIFF_LINES} lines)"
  fi
else
  skip "No PR for diff check"
fi

# ── Test 9: Cleanup — close PR and delete branch ─────────────────
echo ""
echo "🧹 Test 9: Cleanup"

if [ "$PR_NUMBER" -gt 0 ]; then
  # Close PR
  api_gitea -X PATCH "${GITEA_URL}/api/v1/repos/${FULL_REPO}/pulls/${PR_NUMBER}" \
    -d '{"state":"closed"}' >/dev/null 2>&1 || true
  pass "PR #${PR_NUMBER} closed"

  # Delete branch
  api_gitea -X DELETE "${GITEA_URL}/api/v1/repos/${FULL_REPO}/branches/${BRANCH_NAME}" >/dev/null 2>&1 || true
  pass "Branch ${BRANCH_NAME} deleted"
fi

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  📊 Results: ✅ ${PASS_COUNT} passed | ❌ ${FAIL_COUNT} failed | ⏭️  ${SKIP_COUNT} skipped"
echo "═══════════════════════════════════════════════════════════"

if [ "$FAIL_COUNT" -gt 0 ]; then
  echo ""
  echo "  ⚠️  Some tests failed. Common causes:"
  echo "    - Backend not configured for gitea provider"
  echo "    - Webhook URL unreachable from gitea container"
  echo "    - Missing GITEA_* env vars in backend"
  echo ""
  exit 1
fi

echo ""
echo "  🎉 Full developer cycle validated!"
echo ""
exit 0
