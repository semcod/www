# GitHub OAuth Login Simulation

Complete GitHub OAuth simulation for testing the `tom-sapletta-com` user login flow without requiring real GitHub credentials.

## 🏗️ Architecture

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   Frontend     │────▶│   Backend      │────▶│  Mock GitHub    │
│  :3000         │     │  :8003         │     │  :4010          │
│                │     │                │     │                 │
│  Click Login   │     │  /auth/github  │     │  /login/oauth/* │
│  ← session ──  │◀────│  /auth/callback│◀────│  /user, /repos  │
└────────────────┘     └────────────────┘     └─────────────────┘
```

# Start the full stack with simulation
docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d

# Check if mock server is running
curl http://localhost:4010/health

# Open frontend
open http://localhost:3000
```

# Or manually:
cd mock-github
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 4010
```

# Test OAuth flow with mock server
npx playwright test frontend/e2e/github-login-sim.spec.js --grep "mock server"
```

# Complete end-to-end test with browser
npx playwright test frontend/e2e/github-login-sim.spec.js --headed
```

### Manual Testing

1. Navigate to `http://localhost:3000`
2. Click "Sign in with GitHub"
3. You'll be redirected to the mock GitHub login page
4. Click the "tom-sapletta-com" user button
5. You'll be redirected back to the frontend with a valid session

## 👤 Simulated User

| Field       | Value                      |
|-------------|----------------------------|
| login       | `tom-sapletta-com`         |
| name        | Tom Sapletta               |
| id          | 5669315                    |
| email       | tom@sapletta.com           |
| avatar      | https://avatars.githubusercontent.com/u/5669315?v=4 |
| repos       | semcod, letwhisper, dialogware |

### Simulated Repositories

- **semcod** - Semantic Code Analysis (Python, public)
- **letwhisper** - Speech-to-text tool (Python, public)  
- **dialogware** - Dialog platform (JavaScript, private)

## 🔧 How It Works

1. **OAuth Start**: Backend redirects to `GITHUB_OAUTH_AUTHORIZE_URL` → mock server
2. **Mock Login Page**: Simple HTML page with user selection buttons
3. **Code Generation**: Mock server generates a code and redirects to `/auth/callback`
4. **Token Exchange**: Backend exchanges code for access token via mock
5. **Profile Fetch**: Backend fetches user profile from mock `/user` endpoint
6. **Session Creation**: Backend creates JWT session and redirects to frontend

### Environment Variables (Backend Override)

The simulation overrides these environment variables in `docker-compose.sim.yml`:

```env
# OAuth URLs point to mock server
GITHUB_OAUTH_AUTHORIZE_URL=http://mock-github:4010/login/oauth/authorize
GITHUB_OAUTH_TOKEN_URL=http://mock-github:4010/login/oauth/access_token
GITHUB_API_BASE_URL=http://mock-github:4010

# Mock credentials (accepted by mock server)
GITHUB_CLIENT_ID=Iv1.mock_test_client
GITHUB_CLIENT_SECRET=mock_secret_for_testing
GITHUB_APP_ID=999999
GITHUB_WEBHOOK_SECRET=whsec_mock_test

# Frontend URL for redirects
FRONTEND_URL=http://localhost:3000
APP_URL=http://localhost:8003
```

### Mock Server Endpoints

- `GET /login/oauth/authorize` - Mock OAuth authorization page
- `POST /login/oauth/access_token` - Exchange code for access token
- `GET /user` - Get user profile (requires Bearer token)
- `GET /user/repos` - Get user repositories (requires Bearer token)
- `POST /api/_sim/issue-code` - Internal: register an auth code
- `GET /health` - Health check with server status

## 📁 File Structure

```
├── mock-github/
│   ├── Dockerfile              # Container definition
│   ├── requirements.txt        # Python dependencies
│   └── server.py              # FastAPI mock server
├── docker-compose.sim.yml     # Docker Compose overlay for simulation
├── run-sim.sh                 # Standalone mock server script
└── frontend/e2e/github-login-sim.spec.js  # Playwright tests
```

### Adding New Test Users

Edit `mock-github/server.py` and add to `MOCK_USERS` and `MOCK_REPOS`:

```python
MOCK_USERS = {
    "new-user": {
        "id": 1234567,
        "login": "new-user",
        "name": "New User",
        "email": "new@example.com",
        # ... other fields
    }
}

MOCK_REPOS = {
    "new-user": [
        {"id": 1, "name": "test-repo", "full_name": "new-user/test-repo", ...}
    ]
}
```

### Custom OAuth Flow

The mock server supports standard OAuth parameters:
- `client_id` - Required but any value accepted
- `redirect_uri` - Optional, defaults to backend callback URL
- `scope` - Optional, defaults to "read:user,repo"
- `state` - Optional, passed through to callback

# Check Docker logs
docker compose logs mock-github

# Or run standalone for debugging
cd mock-github && python server.py
```

### OAuth Flow Failing

1. Verify mock server health: `curl http://localhost:4010/health`
2. Check backend environment variables: `docker compose exec backend env | grep GITHUB`
3. Verify frontend URL configuration matches `FRONTEND_URL`

# Install Playwright browsers
npx playwright install

# Run tests with debug output
DEBUG=pw:api npx playwright test frontend/e2e/github-login-sim.spec.js
```

## 🧪 Test Scenarios

The test suite covers:

1. **Code → Token Exchange**: Verify mock server issues valid tokens
2. **Profile Fetch**: Confirm user profile is returned correctly
3. **Repository List**: Test repository endpoint returns expected repos
4. **Error Handling**: Invalid codes/tokens return proper errors
5. **Full Browser Flow**: Complete OAuth login via browser interface

## 🚨 Security Notes

- **Never use in production**: This is a testing mock server only
- **No real credentials**: All OAuth tokens are mock tokens
- **Open endpoints**: Mock server accepts any client_id/client_secret
- **Local only**: Designed for localhost testing only

## 📚 Related Documentation

- [Backend OAuth Implementation](backend/routers/auth.py)
- [Frontend Login Flow](frontend/src/components/)
- [Docker Compose Configuration](docker-compose.yml)
