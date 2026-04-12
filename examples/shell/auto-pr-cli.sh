#!/bin/bash
# Semcod Auto-PR CLI — uses `gh` for GitHub + Semcod API for reDSL/tickets
# Auth: exchange gh token for Semcod session token via POST /auth/gh-token

SEMCOD_URL="http://localhost:8003"

# Auto-authenticate: gh token → Semcod session token
GH_TOKEN=$(gh auth token 2>/dev/null)
if [ -z "$GH_TOKEN" ]; then
  echo "ERROR: gh not authenticated. Run: gh auth login"
  exit 1
fi

GH_USER=$(gh api user --jq '.login' 2>/dev/null)

# Get Semcod session token
SEMCOD_SESSION=$(curl -s -X POST "${SEMCOD_URL}/auth/gh-token?token=${GH_TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_token',''))" 2>/dev/null)

if [ -z "$SEMCOD_SESSION" ]; then
  echo "WARNING: Could not get Semcod session token (backend may be down)"
  echo "gh CLI will still work for GitHub operations"
fi

# Helper: Semcod API
semcod() {
  local method=$1 endpoint=$2 data=$3
  curl -s -X "${method}" \
    "${SEMCOD_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${SEMCOD_SESSION}" \
    ${data:+-d "$data"}
}

# 1. Quick Auto-PR (gh only — no Semcod needed)
quick_autopr() {
  local repo=$1 title=$2
  echo "Creating PR for ${repo}..."
  if ! gh api repos/${repo} --jq '.full_name' >/dev/null 2>&1; then
    echo "ERROR: Cannot access repo ${repo}"
    return 1
  fi
  local branch="semcod-fix-$(date +%s)"
  local default=$(gh api repos/${repo} --jq '.default_branch')
  local sha=$(gh api repos/${repo}/git/refs/heads/${default} --jq '.object.sha')
  gh api repos/${repo}/git/refs -f ref="refs/heads/${branch}" -f sha="${sha}" >/dev/null 2>&1
  gh api repos/${repo}/contents/semcod_fix.txt \
    -X PUT -f message="semcod: auto-fix" \
    -f content="$(echo -n '# Semcod Auto-Fix\nApplied automatically' | base64)" \
    -f branch="${branch}" >/dev/null 2>&1
  local pr_url=$(gh pr create --repo ${repo} --head ${branch} --base ${default} \
    --title "${title:-semcod: auto-fix}" --body "Automated PR by Semcod" \
    --json url --jq '.url' 2>&1)
  echo "✅ PR: ${pr_url}"
}

# 2. Ticket + reDSL Auto-PR
ticket_autopr() {
  local title=$1 repo=$2 type=${3:-feature} desc=${4:-$title}
  echo "Creating ticket: ${title}..."
  local resp=$(semcod "POST" "/api/tickets" "{
    \"title\": \"${title}\", \"repo\": \"${repo}\",
    \"ticket_type\": \"${type}\", \"description\": \"${desc}\",
    \"priority\": \"medium\"
  }")
  local ticket_id=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ticket_id',''))" 2>/dev/null)
  if [ -z "$ticket_id" ]; then
    echo "Semcod ticket failed. Falling back to gh CLI..."
    quick_autopr "$repo" "$title"
    return
  fi
  echo "Ticket: ${ticket_id}"
  echo "Processing with reDSL..."
  semcod "POST" "/api/tickets/${ticket_id}/process" "{
    \"project_path\": \"/mnt/project/${repo//\//-}\",
    \"max_actions\": 10, \"dry_run\": false, \"auto_create_pr\": true
  }" | python3 -m json.tool 2>/dev/null
}

# 3. Health check repos
health_check() {
  echo "Checking health for ${GH_USER}'s repos..."
  gh repo list --limit 10 --json nameWithOwner --jq '.[].nameWithOwner' | while read repo; do
    local health=$(semcod "POST" "/api/redsl/health" "{\"project_path\": \"/mnt/project/${repo//\//-}\"}")
    local score=$(echo "$health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('score','?'))" 2>/dev/null)
    echo "  ${repo}: health=${score}"
  done
}

# 4. Monitor PR
monitor_pr() {
  local repo=$1 pr=$2
  while true; do
    local state=$(gh pr view ${pr} --repo ${repo} --json state --jq '.state' 2>&1)
    echo "[$(date +%H:%M:%S)] PR #${pr}: ${state}"
    [ "$state" = "MERGED" ] || [ "$state" = "CLOSED" ] && break
    sleep 15
  done
}

# 5. Interactive ticket
interactive_ticket() {
  echo "Your repos:"
  gh repo list --limit 10 --json nameWithOwner --jq '.[].nameWithOwner'
  echo ""
  read -p "Repo (owner/repo): " repo
  read -p "Title: " title
  read -p "Type (feature/bugfix): " type
  read -p "Description: " desc
  ticket_autopr "$title" "$repo" "${type:-feature}" "${desc:-$title}"
}

# 6. List PRs
list_prs() {
  local repo=$1
  [ -z "$repo" ] && read -p "Repo: " repo
  gh pr list --repo ${repo} --state open --json number,title,author --jq '.[] | "  #\(.number): \(.title) (\(.author.login))"'
}

# 7. Issue + ticket
issue_and_ticket() {
  local repo=$1 title=$2
  local issue_url=$(gh issue create --repo ${repo} --title "${title}" --body "Auto-created from Semcod CLI" --label "bug" --json url --jq '.url' 2>&1)
  echo "GitHub issue: ${issue_url}"
  ticket_autopr "${title}" "${repo}" "bugfix" "GitHub issue: ${issue_url}"
}

# 8. ReDSL preview
redsl_preview() {
  local repo=$1
  [ -z "$repo" ] && read -p "Repo: " repo
  semcod "POST" "/api/redsl/refactor" "{
    \"project_path\": \"/mnt/project/${repo//\//-}\",
    \"max_actions\": 5, \"dry_run\": true
  }" | python3 -m json.tool 2>/dev/null
}

# Menu
show_menu() {
  echo ""
  echo "========================================="
  echo "Semcod Auto-PR CLI (gh + reDSL)"
  echo "========================================="
  echo "GitHub: ${GH_USER}"
  [ -n "$SEMCOD_SESSION" ] && echo "Semcod: authenticated ✓" || echo "Semcod: no session (gh only)"
  echo "========================================="
  echo "1. Quick Auto-PR (gh only)"
  echo "2. Ticket + reDSL Auto-PR"
  echo "3. Health check repos"
  echo "4. Monitor PR status"
  echo "5. Interactive ticket"
  echo "6. List open PRs"
  echo "7. GitHub Issue + Semcod ticket"
  echo "8. ReDSL dry-run preview"
  echo "9. Exit"
  echo "========================================="
}

main() {
  while true; do
    show_menu
    read -p "Select: " choice
    case $choice in
      1) read -p "Repo: " r; quick_autopr "$r" ;;
      2) read -p "Title: " t; read -p "Repo: " r; ticket_autopr "$t" "$r" ;;
      3) health_check ;;
      4) read -p "Repo: " r; read -p "PR #: " n; monitor_pr "$r" "$n" ;;
      5) interactive_ticket ;;
      6) list_prs ;;
      7) read -p "Repo: " r; read -p "Title: " t; issue_and_ticket "$r" "$t" ;;
      8) redsl_preview ;;
      9) exit 0 ;;
      *) echo "Invalid" ;;
    esac
  done
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main
