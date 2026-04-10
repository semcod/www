# Semcod — Podman Quadlet Deployment

## Overview

Quadlet files for rootless Podman deployment on VPS with systemd integration.

## Files

| File | Purpose |
|------|---------|
| `semcod-network.network` | Bridge network for all containers |
| `semcod-data.volume` | Persistent volume for SQLite DB |
| `semcod-backend.container` | FastAPI backend (port 8000 internal) |
| `semcod-frontend.container` | Nginx frontend (port 3000 internal) |
| `semcod-traefik.container` | Reverse proxy with Let's Encrypt |
| `traefik-prod.yml` | Traefik production config |

## Deploy

### 1. Build images

```bash
cd /opt/semcod/www
podman build -t semcod-backend:latest ./backend
podman build -t semcod-frontend:latest ./frontend
```

### 2. Prepare VPS directory

```bash
sudo mkdir -p /opt/semcod/{traefik,config}
sudo cp quadlet/*.network quadlet/*.volume quadlet/*.container /etc/containers/systemd/
sudo cp quadlet/traefik-prod.yml /opt/semcod/traefik/traefik-prod.yml
sudo touch /opt/semcod/traefik/acme.json && sudo chmod 600 /opt/semcod/traefik/acme.json
sudo cp .env /opt/semcod/.env
```

### 3. Reload systemd and start

```bash
sudo systemctl daemon-reload
sudo systemctl start semcod-network.service
sudo systemctl start semcod-traefik.service
sudo systemctl start semcod-backend.service
sudo systemctl start semcod-frontend.service
```

### 4. Check status

```bash
sudo systemctl status semcod-backend semcod-frontend semcod-traefik
podman ps
curl https://semcod.com/api/health
```

## Auto-update

Images with `AutoUpdate=registry` will auto-update when new versions are pushed to the registry.

## Logs

```bash
journalctl -u semcod-backend -f
journalctl -u semcod-frontend -f
journalctl -u semcod-traefik -f
```

## Environment

Required in `/opt/semcod/.env`:

```env
GITHUB_APP_ID=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GITHUB_WEBHOOK_SECRET=...
GITHUB_PRIVATE_KEY_PATH=
GITHUB_OAUTH_SCOPE=repo,read:org
SECRET_KEY=
APP_URL=https://api.semcod.com
FRONTEND_URL=https://semcod.com
PUBLIC_URL=https://semcod.com
HOST=0.0.0.0
PORT=8000
SESSION_EXPIRE_HOURS=168
DEMO_MODE=0
DB_PATH=/app/data/scans.db
SCAN_HISTORY_LIMIT=100
REPOS_PER_PAGE=30
CORS_ORIGINS=https://semcod.com,https://api.semcod.com
LARGE_FILE_THRESHOLD=300
```
