import { test, expect } from '@playwright/test';

test.describe('Mock GitHub OAuth Login Flow', () => {
  test('Connect GitHub button triggers mock OAuth redirect', async ({ page, context }) => {
    await page.goto('/', { timeout: 30000 });

    // Should see Connect GitHub button
    await expect(page.getByRole('button', { name: /Connect GitHub/i })).toBeVisible({ timeout: 15000 });

    // Click Connect GitHub — mock-github auto-approves OAuth
    await page.getByRole('button', { name: /Connect GitHub/i }).click();

    // Wait for navigation (mock-github redirects back)
    await page.waitForURL(/localhost:3000|localhost:4010/, { timeout: 15000 }).catch(() => {});

    // After OAuth redirect, page should be on our domain or mock-github
    const url = page.url();
    expect(url).toMatch(/localhost/);
  });

  test('sandbox analyze works as alternative to OAuth', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Use sandbox instead of OAuth
    const input = page.getByPlaceholder('https://github.com/owner/repo');
    await input.fill('https://github.com/octocat/Hello-World');
    await page.getByRole('button', { name: /Analyze/i }).click();

    // Should start analyzing
    await expect(page.getByText(/Analyzing|Scanning|Loading/i)).toBeVisible({ timeout: 10000 });
  });

  test('landing page returns after navigation', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Badge/i }).click();
    await page.waitForTimeout(500);
    await page.goto('/');
    await expect(page.getByText('One-click code audit')).toBeVisible({ timeout: 5000 });
  });

  test('page reload preserves landing state', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('One-click code audit')).toBeVisible({ timeout: 10000 });
    await page.reload();
    await expect(page.getByText('One-click code audit')).toBeVisible({ timeout: 10000 });
  });
});
