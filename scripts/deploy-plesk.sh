#!/usr/bin/env bash
#
# deploy-plesk.sh — deploy the static semcod.com website to the Plesk server.
#
# The site is the GitHub-Pages-style static content at the repo root
# (index.html + project/ + articles/ + docs/ + README). This script syncs
# only those parts to the domain's httpdocs over SSH/rsync, leaving the
# backend, frontend build tooling, tests and node_modules behind.
#
# Usage:
#   scripts/deploy-plesk.sh            # deploy
#   DRY_RUN=1 scripts/deploy-plesk.sh  # preview what would change, copy nothing
#
# Override defaults via env:
#   SSH_HOST   (default: semcod.com)
#   SSH_USER   (default: semcod)
#   SSH_PORT   (default: 22)
#   REMOTE_DIR (default: /var/www/vhosts/semcod.com/httpdocs)

set -euo pipefail

SSH_HOST="${SSH_HOST:-semcod.com}"
SSH_USER="${SSH_USER:-semcod}"
SSH_PORT="${SSH_PORT:-22}"
REMOTE_DIR="${REMOTE_DIR:-/var/www/vhosts/semcod.com/httpdocs}"

# Repo root = parent of this script's directory.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Static-site paths to publish (relative to repo root). Edit this list to
# change what ends up on the live site.
ASSETS=(
  index.html
  .nojekyll
  README.md
  app.doql.css
  app.doql.less
  project
  articles
  docs
)

# Keep only paths that actually exist so a missing optional asset is skipped
# rather than aborting the whole deploy.
SRC=()
for a in "${ASSETS[@]}"; do
  if [[ -e "$a" ]]; then
    SRC+=("$a")
  else
    echo "skip (missing): $a" >&2
  fi
done

if [[ ${#SRC[@]} -eq 0 ]]; then
  echo "error: no static assets found to deploy" >&2
  exit 1
fi

RSYNC_OPTS=(
  -avz
  --delete                 # mirror: remove files on server no longer in repo
  --exclude='.DS_Store'
  --exclude='*.swp'
  -e "ssh -p ${SSH_PORT}"
)

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  RSYNC_OPTS+=(--dry-run)
  echo "== DRY RUN (no files will be copied) =="
fi

echo "Deploying to ${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}"
echo "Assets: ${SRC[*]}"

rsync "${RSYNC_OPTS[@]}" "${SRC[@]}" "${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}/"

echo
echo "Done. Live at: https://${SSH_HOST}/"
