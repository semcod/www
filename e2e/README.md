# E2E Tests

## Setup

```bash
npm install
npx playwright install
```

## Run Tests

```bash
# Run all tests
npx playwright test

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

- `specs/smoke.spec.js` - Basic smoke tests
- `specs/audit.spec.js` - Audit flow tests
- `specs/badge.spec.js` - Badge generator tests

## Configuration

See `playwright.config.js` for test configuration including:
- Base URL: http://localhost:5173
- Browsers: Chromium, Firefox
- Screenshot on failure
- HTML reporter
