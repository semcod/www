# E2E Tests

This directory contains multiple E2E testing approaches for Semcod:

1. **Playwright** - UI E2E tests (existing)
2. **Curl Script** - Quick API endpoint tests (new)
3. **Karate DSL** - Comprehensive API tests (new)

---

## Playwright UI Tests (Existing)

### Setup

```bash
cd e2e
npm install
npx playwright install
```

## Run Tests

```bash
# Run all tests (auto-starts frontend dev server)
cd e2e && npm test

# Run specific test file
npx playwright test smoke.spec.js

# Run with UI mode
npx playwright test --ui

# Run headed (visible browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug
```

## Test Structure

- `specs/smoke.spec.js` - Basic smoke tests (homepage, navigation, scan flow)
- `specs/audit.spec.js` - Audit flow tests (GitHub OAuth requires backend)
- `specs/badge.spec.js` - Badge generator tests
- `specs/demo-mode.spec.js` - Demo login flow tests (no backend required)
- `specs/metrics.spec.js` - Metrics display tests
- `specs/recent-scans.spec.js` - Recent scans tab tests
- `specs/scan-workflow.spec.js` - Multi-provider scan tests (GitHub, GitLab, Bitbucket)
- `specs/social-sharing.spec.js` - Social share buttons tests

## Configuration

See `playwright.config.js` for test configuration:
- Base URL: http://localhost:5173
- Browser: Chromium only
- Screenshot on failure
- WebServer auto-starts Vite dev server from `../frontend`

---

## Curl API Tests (New)

Quick bash script to test all major API endpoints via curl.

**Usage:**
```bash
# Run with default URLs (localhost:8003 backend, localhost:3000 frontend)
./test-api-curl.sh

# Run with custom URLs
BASE_URL=http://staging.example.com FRONTEND_URL=http://staging.example.com ./test-api-curl.sh
```

**Test Coverage (20 tests):**
- Frontend health check
- Backend health check (`/api/health`, `/api/config/domain`)
- Authentication (`/auth/demo`)
- Marketplace (`/api/apps`)
- Repositories (`/api/repos`)
- Audit (`/api/audit`)
- Metrics (`/api/metrics/standard`)
- Trend (`/api/trend/{owner}/{repo}`, `/api/scan/diff/{owner}/{repo}`)
- Badge (`/badge/{repo_slug}.svg`)
- MCP (`/mcp/info`, `/mcp/resources`, `/mcp/tools`, `/mcp/tools/invoke`)
- Billing (`/api/billing/plans`, `/api/billing/status`)
- Mirror (`/api/mirror/list`)
- Scheduler (`/api/schedules`)
- Webhook (`/webhook/github`)

**Latest Results (2026-04-10):**
- ✅ 20/20 tests passed
- All major API endpoints working
- Duration: ~5 seconds

---

## Karate DSL Tests (New)

Comprehensive API tests using Karate DSL for integration testing and CI/CD pipelines.

**Structure:**
```
karate/
├── karate-config.js    # Karate configuration
├── pom.xml             # Maven configuration for running tests
└── semcod-api.feature  # Test scenarios
```

**Usage:**

Option 1: Using Maven (recommended for CI/CD)
```bash
cd karate
mvn test
```

Option 2: Using Karate standalone JAR
```bash
# Download Karate standalone
wget https://github.com/karatelabs/karate/releases/download/v1.4.1/karate-1.4.1.jar

# Run tests
java -jar karate-1.4.1.jar semcod-api.feature
```

**Test Scenarios (20 scenarios):**
- Health check endpoint validation
- Domain configuration
- Demo authentication flow
- Marketplace apps listing
- Repository listing (authenticated)
- Audit initiation
- Metrics retrieval
- Trend analysis
- Scan diff comparison
- Badge SVG generation
- MCP server info
- MCP resources listing
- MCP tools listing
- MCP tool invocation
- Billing plans
- Billing status
- Mirror operations
- Scheduler operations
- Webhook handling

**Configuration:**
Edit `karate-config.js` to change base URL for different environments.
