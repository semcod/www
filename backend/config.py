import os
from pathlib import Path
from urllib.parse import urlparse

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH", "private-key.pem")
GITHUB_OAUTH_SCOPE = os.getenv("GITHUB_OAUTH_SCOPE", "repo,read:org")

# Configurable OAuth URLs (for mock/simulation support)
GITHUB_OAUTH_AUTHORIZE_URL = os.getenv("GITHUB_OAUTH_AUTHORIZE_URL", "https://github.com/login/oauth/authorize")
GITHUB_OAUTH_TOKEN_URL = os.getenv("GITHUB_OAUTH_TOKEN_URL", "https://github.com/login/oauth/access_token")
GITHUB_API_BASE_URL = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")
APP_URL = os.getenv("APP_URL", "http://localhost:9000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
PUBLIC_URL = os.getenv("PUBLIC_URL", APP_URL)
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "9000"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
SESSION_EXPIRE_HOURS = int(os.getenv("SESSION_EXPIRE_HOURS", "168"))
DEMO_MODE = os.getenv("DEMO_MODE", "0") == "1"

# Database configuration - use PostgreSQL if available, fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "")
DB_PATH = Path(os.getenv("DB_PATH", "scans.db"))
if DATABASE_URL:
    # PostgreSQL
    DB_TYPE = "postgresql"
else:
    # SQLite fallback
    DB_TYPE = "sqlite"

SCAN_HISTORY_LIMIT = int(os.getenv("SCAN_HISTORY_LIMIT", "100"))
REPOS_PER_PAGE = int(os.getenv("REPOS_PER_PAGE", "30"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", f"{FRONTEND_URL},https://semcod.com").split(",") if o.strip()]
LARGE_FILE_THRESHOLD = int(os.getenv("LARGE_FILE_THRESHOLD", "300"))
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_PRO_MONTHLY = os.getenv("STRIPE_PRICE_PRO_MONTHLY", "")
STRIPE_PRICE_PRO_ANNUAL = os.getenv("STRIPE_PRICE_PRO_ANNUAL", "")
STRIPE_PRICE_TEAM_MONTHLY = os.getenv("STRIPE_PRICE_TEAM_MONTHLY", "")

# Usage-based billing (price per unit in cents)
STRIPE_PRICE_ANALYSIS_PER_PR = int(os.getenv("STRIPE_PRICE_ANALYSIS_PER_PR", "50"))  # $0.50
STRIPE_PRICE_AUTOFIX_PER_RUN = int(os.getenv("STRIPE_PRICE_AUTOFIX_PER_RUN", "100"))  # $1.00
STRIPE_PRICE_REPO_ACTIVE_MONTHLY = int(os.getenv("STRIPE_PRICE_REPO_ACTIVE_MONTHLY", "200"))  # $2.00

# Billing tiers
FREE_TIER_LIMITS = {
    "analysis_per_month": 10,
    "autofix_per_month": 0,
    "repos_active": 1,
}
PRO_TIER_LIMITS = {
    "analysis_per_month": 1000,
    "autofix_per_month": 50,
    "repos_active": 10,
}
TEAM_TIER_LIMITS = {
    "analysis_per_month": float('inf'),
    "autofix_per_month": float('inf'),
    "repos_active": float('inf'),
}

# Multi-platform git provider tokens
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", GITHUB_CLIENT_SECRET)  # Fallback for compatibility
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "")
GITLAB_WEBHOOK_SECRET = os.getenv("GITLAB_WEBHOOK_SECRET", "")
GITEA_TOKEN = os.getenv("GITEA_TOKEN", "")
GITEA_WEBHOOK_SECRET = os.getenv("GITEA_WEBHOOK_SECRET", "")
GITEA_BASE_URL = os.getenv("GITEA_BASE_URL", "http://localhost:3000")
