# E2E Tests

## Setup

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
