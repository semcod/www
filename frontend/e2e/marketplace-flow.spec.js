import { test, expect } from '@playwright/test';

/**
 * Multi-step E2E: Marketplace tab flow.
 *
 * Validates the nginx proxy fix — API calls through the frontend
 * must return JSON (not index.html) so the Marketplace renders data.
 */

const API = process.env.API_URL || 'http://localhost:8003';

// ─── API-level checks (via Playwright request context) ──────────────────────

test.describe('Marketplace API via frontend proxy', () => {
  test('GET /api/apps returns JSON array, not HTML', async ({ request }) => {
    const res = await request.get(`${API}/api/apps`);
    expect(res.status()).toBe(200);
    const ct = res.headers()['content-type'] || '';
    expect(ct).toContain('json');
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThanOrEqual(3);

    // Each app has required fields
    for (const app of body) {
      expect(app).toHaveProperty('name');
      expect(app).toHaveProperty('version');
      expect(app).toHaveProperty('pricing');
      expect(app).toHaveProperty('triggers');
      expect(app).toHaveProperty('actions');
    }
  });

  test('GET /api/billing/plans returns plan data', async ({ request }) => {
    const res = await request.get(`${API}/api/billing/plans`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('free');
    expect(body).toHaveProperty('pro');
  });

  test('GET /api/health returns JSON health status', async ({ request }) => {
    const res = await request.get(`${API}/api/health`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('status');
    expect(body.status).toBe('ok');
  });
});

// ─── GUI-level marketplace tab tests ────────────────────────────────────────

test.describe('Marketplace Tab UI', () => {
  test('marketplace tab loads without JSON parse error', async ({ page }) => {
    // Navigate to marketplace tab
    await page.goto('/#tab=marketplace&phase=landing');
    await page.waitForLoadState('networkidle');

    // Must NOT show the JSON parse error that was the original bug
    const errorText = page.getByText('Unexpected token');
    await expect(errorText).not.toBeVisible();

    // Should see marketplace content (apps list)
    const marketplaceContent = page.locator('#root');
    await expect(marketplaceContent).not.toBeEmpty();
  });

  test('marketplace tab displays app cards', async ({ page }) => {
    await page.goto('/#tab=marketplace&phase=landing');
    await page.waitForLoadState('networkidle');

    // Look for app-related content
    const appNames = ['audit', 'security', 'performance'];
    let found = 0;
    for (const name of appNames) {
      const el = page.getByText(new RegExp(name, 'i')).first();
      if (await el.isVisible().catch(() => false)) found++;
    }
    expect(found).toBeGreaterThanOrEqual(1);
  });

  test('marketplace tab shows pricing information', async ({ page }) => {
    await page.goto('/#tab=marketplace&phase=landing');
    await page.waitForLoadState('networkidle');

    // Look for pricing-related text
    const pricingText = page.getByText(/free|pro|enterprise/i).first();
    const hasPricing = await pricingText.isVisible().catch(() => false);
    // Pricing info should exist somewhere on the page
    expect(hasPricing).toBeTruthy();
  });
});

// ─── Multi-step: Login → Navigate tabs → Verify content loads ───────────────

test.describe('Multi-step navigation flow', () => {
  test('navigate through all tabs without errors', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Track console errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    // Navigate to Audit tab
    const auditTab = page.getByRole('button', { name: /Audit/i });
    if (await auditTab.isVisible().catch(() => false)) {
      await auditTab.click();
      await page.waitForTimeout(500);
    }

    // Navigate to Badge tab
    const badgeTab = page.getByRole('button', { name: /Badge/i });
    if (await badgeTab.isVisible().catch(() => false)) {
      await badgeTab.click();
      await page.waitForTimeout(500);
    }

    // Navigate to Marketplace tab
    const marketTab = page.getByRole('button', { name: /Marketplace/i });
    if (await marketTab.isVisible().catch(() => false)) {
      await marketTab.click();
      await page.waitForTimeout(1000);
    }

    // No JSON parse errors should have occurred
    const jsonErrors = consoleErrors.filter(e =>
      e.includes('Unexpected token') || e.includes('not valid JSON')
    );
    expect(jsonErrors).toHaveLength(0);
  });

  test('API responses through frontend are never HTML', async ({ page }) => {
    const htmlResponses = [];

    // Intercept API responses
    page.on('response', async response => {
      const url = response.url();
      if (url.includes('/api/') || url.includes('/auth/') || url.includes('/mcp/')) {
        const ct = response.headers()['content-type'] || '';
        if (ct.includes('text/html')) {
          htmlResponses.push({ url, contentType: ct });
        }
      }
    });

    await page.goto('/#tab=marketplace&phase=landing');
    await page.waitForLoadState('networkidle');

    // No API call should have returned HTML
    expect(htmlResponses).toHaveLength(0);
  });
});
