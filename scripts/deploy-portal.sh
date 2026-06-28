#!/usr/bin/env bash
#
# deploy-portal.sh — deploy the dynamic PHP project portal to the Plesk server.
#
# The portal lives in web/ and renders, live from the GitHub API, the catalogue
# of every public repo in the `semcod` org plus a README subpage per project.
# This script syncs web/ into the domain httpdocs over SSH/rsync, preserving the
# server-side cache/ and any config.local.php (never overwritten or deleted).
#
# Usage:
#   scripts/deploy-portal.sh            # deploy
#   DRY_RUN=1 scripts/deploy-portal.sh  # preview, copy nothing
#
# Env overrides: SSH_HOST, SSH_USER, SSH_PORT, REMOTE_DIR (see defaults below).

set -euo pipefail

SSH_HOST="${SSH_HOST:-semcod.com}"
SSH_USER="${SSH_USER:-semcod}"
SSH_PORT="${SSH_PORT:-22}"
REMOTE_DIR="${REMOTE_DIR:-/var/www/vhosts/semcod.com/httpdocs}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/web"

RSYNC_OPTS=(
  -avz
  --exclude='cache/'             # server-side runtime cache — keep it
  --exclude='config.local.php'   # server-side secret — never push/delete
  --exclude='.gitignore'
  -e "ssh -p ${SSH_PORT}"
)

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  RSYNC_OPTS+=(--dry-run)
  echo "== DRY RUN (no files will be copied) =="
fi

echo "Deploying PHP portal to ${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}"
rsync "${RSYNC_OPTS[@]}" ./ "${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}/"

# Make sure the runtime cache dir exists and is writable by PHP-FPM.
if [[ "${DRY_RUN:-0}" != "1" ]]; then
  ssh -p "${SSH_PORT}" "${SSH_USER}@${SSH_HOST}" \
    "mkdir -p '${REMOTE_DIR}/cache' && chmod 775 '${REMOTE_DIR}/cache'"
fi

echo
echo "Done. Live at: https://${SSH_HOST}/"
echo "Tip: set GITHUB_TOKEN (Plesk > PHP settings) to raise the API rate limit to 5000/h."
