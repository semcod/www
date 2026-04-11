#!/bin/bash
# setup-gitea.sh — Provision Gitea for Semcod development cycle
# Run AFTER: docker compose -f docker-compose.yml -f docker-compose.gitea.yml up -d
#
# Creates:
#   1. Admin user (tom-sapletta-com)
#   2. API token
#   3. OAuth2 application (for Semcod login)
#   4. 3 sample repos with real Python code
#   5. Webhooks pointing to Semcod backend
set -euo pipefail

GITEA_URL="${GITEA_URL:-http://localhost:3100}"
GITEA_INTERNAL="${GITEA_INTERNAL:-http://gitea:3000}"
BACKEND_WEBHOOK="${BACKEND_WEBHOOK:-http://backend:8000/v2/webhook/gitea}"
WEBHOOK_SECRET="${GITEA_WEBHOOK_SECRET:-semcod-webhook-secret}"

USER_LOGIN="tom-sapletta-com"
USER_PASS="Semcod2026!"
USER_EMAIL="tom@sapletta.com"
USER_FULLNAME="Tom Sapletta"

ENV_FILE="${1:-.env.gitea}"

echo "🔧 Gitea provisioning → ${GITEA_URL}"
echo ""

# ── Wait for Gitea ───────────────────────────────────────────────
echo "⏳ Waiting for Gitea..."
for i in $(seq 1 30); do
  if curl -sf "${GITEA_URL}/api/v1/version" >/dev/null 2>&1; then
    echo "✅ Gitea is ready"
    break
  fi
  [ "$i" -eq 30 ] && { echo "❌ Gitea not responding"; exit 1; }
  sleep 2
done

# ── 1. Create admin user ────────────────────────────────────────
echo ""
echo "👤 Creating user: ${USER_LOGIN}..."
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" \
  "${GITEA_URL}/api/v1/admin/users" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${USER_LOGIN}\",
    \"password\": \"${USER_PASS}\",
    \"email\": \"${USER_EMAIL}\",
    \"full_name\": \"${USER_FULLNAME}\",
    \"must_change_password\": false,
    \"login_name\": \"${USER_LOGIN}\",
    \"source_id\": 0,
    \"visibility\": \"public\"
  }" 2>/dev/null || echo "000")

# If first-run install needed, try via install form
if [ "$STATUS" = "000" ] || [ "$STATUS" = "403" ]; then
  echo "   → Trying admin creation via Gitea install API..."
  curl -sf -o /dev/null "${GITEA_URL}/api/v1/version" || true
  # Use basic auth — Gitea allows first user creation without auth
  curl -sf -o /dev/null \
    -u "${USER_LOGIN}:${USER_PASS}" \
    "${GITEA_URL}/api/v1/user" 2>/dev/null || \
  curl -sf -o /dev/null \
    "${GITEA_URL}/user/sign_up" \
    -d "user_name=${USER_LOGIN}&password=${USER_PASS}&retype=${USER_PASS}&email=${USER_EMAIL}" 2>/dev/null || true
fi
echo "✅ User ready: ${USER_LOGIN}"

# ── 2. Create API token ─────────────────────────────────────────
echo ""
echo "🔑 Creating API token..."
TOKEN_RESP=$(curl -sf \
  -u "${USER_LOGIN}:${USER_PASS}" \
  "${GITEA_URL}/api/v1/users/${USER_LOGIN}/tokens" \
  -H "Content-Type: application/json" \
  -d '{"name":"semcod-dev-'$(date +%s)'","scopes":["all"]}' 2>/dev/null || echo '{}')

GITEA_TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha1',''))" 2>/dev/null || echo "")

if [ -z "$GITEA_TOKEN" ]; then
  echo "   → Token may already exist, trying with password auth..."
  GITEA_TOKEN="__basic__"
  AUTH_HEADER="-u ${USER_LOGIN}:${USER_PASS}"
else
  AUTH_HEADER="-H Authorization:\ token\ ${GITEA_TOKEN}"
  echo "✅ Token: ${GITEA_TOKEN:0:8}..."
fi

# Helper for authenticated calls
api() {
  local method=$1 path=$2
  shift 2
  if [ "$GITEA_TOKEN" = "__basic__" ]; then
    curl -sf -X "$method" -u "${USER_LOGIN}:${USER_PASS}" \
      -H "Content-Type: application/json" \
      "${GITEA_URL}/api/v1${path}" "$@"
  else
    curl -sf -X "$method" \
      -H "Authorization: token ${GITEA_TOKEN}" \
      -H "Content-Type: application/json" \
      "${GITEA_URL}/api/v1${path}" "$@"
  fi
}

# ── 3. Create OAuth2 application ────────────────────────────────
echo ""
echo "🔐 Creating OAuth2 application..."
OAUTH_RESP=$(api POST "/user/applications/oauth2" \
  -d "{
    \"name\": \"Semcod Dev\",
    \"redirect_uris\": [\"http://localhost:8003/auth/callback\", \"http://localhost:3000/callback\"],
    \"confidential_client\": true
  }" 2>/dev/null || echo '{}')

GITEA_CLIENT_ID=$(echo "$OAUTH_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('client_id',''))" 2>/dev/null || echo "")
GITEA_CLIENT_SECRET=$(echo "$OAUTH_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('client_secret',''))" 2>/dev/null || echo "")

if [ -n "$GITEA_CLIENT_ID" ]; then
  echo "✅ OAuth2 app: client_id=${GITEA_CLIENT_ID:0:12}..."
else
  echo "⚠️  OAuth2 app creation failed (may already exist)"
fi

# ── 4. Create sample repositories ───────────────────────────────
echo ""
echo "📦 Creating sample repositories..."

create_repo_with_code() {
  local repo_name=$1
  local description=$2
  local lang=$3
  local filename=$4
  local code=$5

  # Create repo
  api POST "/user/repos" \
    -d "{\"name\":\"${repo_name}\",\"description\":\"${description}\",\"auto_init\":true,\"default_branch\":\"main\"}" \
    >/dev/null 2>&1 || true

  # Add source file
  ENCODED=$(echo -n "$code" | base64 -w0 2>/dev/null || echo -n "$code" | base64)
  api POST "/repos/${USER_LOGIN}/${repo_name}/contents/${filename}" \
    -d "{\"content\":\"${ENCODED}\",\"message\":\"Add ${filename}\"}" \
    >/dev/null 2>&1 || true

  # Add README
  README_CONTENT=$(echo -n "# ${repo_name}\n\n${description}\n\n## Language: ${lang}" | base64 -w0 2>/dev/null || echo -n "# ${repo_name}" | base64)
  api PUT "/repos/${USER_LOGIN}/${repo_name}/contents/README.md" \
    -d "{\"content\":\"${README_CONTENT}\",\"message\":\"Update README\",\"sha\":\"\"}" \
    >/dev/null 2>&1 || true

  echo "   ✅ ${USER_LOGIN}/${repo_name} (${lang})"
}

# Repo 1: Python project with intentional complexity
create_repo_with_code "sample-python" "Sample Python project for Semcod testing" "Python" "app.py" \
'import os
import json
from typing import Optional

class DataProcessor:
    """Process data with configurable pipeline."""
    
    def __init__(self, config: dict):
        self.config = config
        self.results = []
    
    def process(self, data: list) -> list:
        """Main processing pipeline."""
        filtered = [x for x in data if self.validate(x)]
        transformed = [self.transform(x) for x in filtered]
        self.results = transformed
        return transformed
    
    def validate(self, item: dict) -> bool:
        if not isinstance(item, dict):
            return False
        if "id" not in item:
            return False
        if "value" not in item:
            return False
        if item["value"] < 0:
            return False
        return True
    
    def transform(self, item: dict) -> dict:
        return {
            "id": item["id"],
            "value": item["value"] * self.config.get("multiplier", 1),
            "label": item.get("label", "unknown").upper(),
        }

    def validate(self, item: dict) -> bool:
        """Duplicate method - intentional for testing dedup detection."""
        if not isinstance(item, dict):
            return False
        if "id" not in item:
            return False
        if "value" not in item:
            return False
        if item["value"] < 0:
            return False
        return True

def complex_function(data, mode, flag_a=False, flag_b=False, flag_c=False):
    """High cyclomatic complexity function for testing."""
    result = []
    for item in data:
        if mode == "strict":
            if flag_a and item.get("priority") == "high":
                if flag_b:
                    result.append({"action": "urgent", **item})
                elif flag_c:
                    result.append({"action": "review", **item})
                else:
                    result.append({"action": "queue", **item})
            elif flag_a and item.get("priority") == "low":
                if flag_b or flag_c:
                    result.append({"action": "skip", **item})
                else:
                    result.append({"action": "archive", **item})
            else:
                result.append({"action": "default", **item})
        elif mode == "relaxed":
            result.append({"action": "pass", **item})
        else:
            if flag_a:
                result.append({"action": "unknown_flagged", **item})
            else:
                result.append({"action": "unknown", **item})
    return result

if __name__ == "__main__":
    proc = DataProcessor({"multiplier": 2})
    sample = [{"id": 1, "value": 10}, {"id": 2, "value": -5}, {"id": 3, "value": 7}]
    print(json.dumps(proc.process(sample), indent=2))
'

# Repo 2: JavaScript project
create_repo_with_code "sample-js" "Sample JavaScript project for testing" "JavaScript" "index.js" \
'const http = require("http");

class ApiServer {
  constructor(port = 3000) {
    this.port = port;
    this.routes = new Map();
    this.middleware = [];
  }

  use(fn) { this.middleware.push(fn); }

  get(path, handler) { this.routes.set(\`GET:\${path}\`, handler); }
  post(path, handler) { this.routes.set(\`POST:\${path}\`, handler); }

  async handleRequest(req, res) {
    const key = \`\${req.method}:\${req.url}\`;
    const handler = this.routes.get(key);
    
    for (const mw of this.middleware) {
      await mw(req, res);
    }
    
    if (handler) {
      try {
        const result = await handler(req, res);
        res.writeHead(200, {"Content-Type": "application/json"});
        res.end(JSON.stringify(result));
      } catch (err) {
        res.writeHead(500);
        res.end(JSON.stringify({error: err.message}));
      }
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({error: "Not found"}));
    }
  }

  // Duplicate of handleRequest — intentional for dedup testing
  async processRequest(req, res) {
    const key = \`\${req.method}:\${req.url}\`;
    const handler = this.routes.get(key);
    
    for (const mw of this.middleware) {
      await mw(req, res);
    }
    
    if (handler) {
      try {
        const result = await handler(req, res);
        res.writeHead(200, {"Content-Type": "application/json"});
        res.end(JSON.stringify(result));
      } catch (err) {
        res.writeHead(500);
        res.end(JSON.stringify({error: err.message}));
      }
    } else {
      res.writeHead(404);
      res.end(JSON.stringify({error: "Not found"}));
    }
  }

  listen() {
    const server = http.createServer((req, res) => this.handleRequest(req, res));
    server.listen(this.port, () => console.log(\`Server on :\${this.port}\`));
  }
}

const app = new ApiServer(8080);
app.get("/health", () => ({status: "ok"}));
app.get("/users", () => [{id: 1, name: "Tom"}, {id: 2, name: "Alice"}]);
app.listen();
'

# Repo 3: Multi-file project (shell)
create_repo_with_code "infra-scripts" "Infrastructure automation scripts" "Shell" "deploy.sh" \
'#!/bin/bash
set -euo pipefail

ENVIRONMENT="${1:-staging}"
VERSION="${2:-latest}"
REGISTRY="registry.example.com"

deploy() {
    local env=$1 ver=$2
    echo "Deploying v${ver} to ${env}..."
    
    if [ "$env" = "production" ]; then
        echo "Running pre-flight checks..."
        run_checks "$ver"
        echo "Creating backup..."
        backup_current "$env"
    fi
    
    docker pull "${REGISTRY}/app:${ver}"
    docker compose -f "docker-compose.${env}.yml" up -d
    
    echo "Waiting for health check..."
    for i in $(seq 1 30); do
        if curl -sf "http://localhost:8080/health" >/dev/null; then
            echo "✅ Deployment successful"
            return 0
        fi
        sleep 2
    done
    
    echo "❌ Health check failed, rolling back..."
    rollback "$env"
    return 1
}

run_checks() { echo "Checks passed for $1"; }
backup_current() { echo "Backup created for $1"; }
rollback() { echo "Rolled back $1"; }

deploy "$ENVIRONMENT" "$VERSION"
'

# ── 5. Setup webhooks ────────────────────────────────────────────
echo ""
echo "🔗 Setting up webhooks..."

for repo in sample-python sample-js infra-scripts; do
  api POST "/repos/${USER_LOGIN}/${repo}/hooks" \
    -d "{
      \"type\": \"gitea\",
      \"active\": true,
      \"events\": [\"push\", \"pull_request\", \"pull_request_comment\"],
      \"config\": {
        \"url\": \"${BACKEND_WEBHOOK}\",
        \"content_type\": \"json\",
        \"secret\": \"${WEBHOOK_SECRET}\"
      }
    }" >/dev/null 2>&1 || true
  echo "   ✅ Webhook: ${repo} → ${BACKEND_WEBHOOK}"
done

# ── 6. Save environment file ────────────────────────────────────
echo ""
echo "💾 Saving ${ENV_FILE}..."

cat > "${ENV_FILE}" << EOF
# Gitea dev environment — generated $(date -Iseconds)
GITEA_URL=${GITEA_URL}
GITEA_API_BASE_URL=${GITEA_INTERNAL}
GITEA_OAUTH_AUTHORIZE_URL=${GITEA_URL}/login/oauth/authorize
GITEA_OAUTH_TOKEN_URL=${GITEA_INTERNAL}/login/oauth/access_token
GITEA_CLIENT_ID=${GITEA_CLIENT_ID}
GITEA_CLIENT_SECRET=${GITEA_CLIENT_SECRET}
GITEA_WEBHOOK_SECRET=${WEBHOOK_SECRET}
GITEA_ADMIN_TOKEN=${GITEA_TOKEN}
GITEA_USER_LOGIN=${USER_LOGIN}
GITEA_USER_PASS=${USER_PASS}
DEFAULT_GIT_PROVIDER=gitea
EOF

echo "✅ Saved to ${ENV_FILE}"

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════"
echo "  🎉 Gitea provisioning complete!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "  Gitea UI:      ${GITEA_URL}"
echo "  Login:         ${USER_LOGIN} / ${USER_PASS}"
echo "  OAuth client:  ${GITEA_CLIENT_ID:-'(check UI)'}"
echo ""
echo "  Repositories:"
echo "    ${GITEA_URL}/${USER_LOGIN}/sample-python"
echo "    ${GITEA_URL}/${USER_LOGIN}/sample-js"
echo "    ${GITEA_URL}/${USER_LOGIN}/infra-scripts"
echo ""
echo "  Webhooks → ${BACKEND_WEBHOOK}"
echo ""
echo "  Next: bash scripts/test-full-cycle.sh"
echo ""
