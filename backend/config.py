import os
from pathlib import Path

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH", "private-key.pem")
GITHUB_OAUTH_SCOPE = os.getenv("GITHUB_OAUTH_SCOPE", "repo,read:org")
APP_URL = os.getenv("APP_URL", "http://localhost:9000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
PUBLIC_URL = os.getenv("PUBLIC_URL", APP_URL)
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "9000"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
SESSION_EXPIRE_HOURS = int(os.getenv("SESSION_EXPIRE_HOURS", "168"))
DEMO_MODE = os.getenv("DEMO_MODE", "0") == "1"
DB_PATH = Path(os.getenv("DB_PATH", "scans.db"))
SCAN_HISTORY_LIMIT = int(os.getenv("SCAN_HISTORY_LIMIT", "100"))
REPOS_PER_PAGE = int(os.getenv("REPOS_PER_PAGE", "30"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", f"{FRONTEND_URL},https://semcod.com").split(",") if o.strip()]
LARGE_FILE_THRESHOLD = int(os.getenv("LARGE_FILE_THRESHOLD", "300"))
