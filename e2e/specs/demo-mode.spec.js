import { test, expect } from '@playwright/test';

test.describe('Demo Mode', () => {
  test('Demo Login button visible on landing page', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Demo Login button should be visible
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible({ timeout: 15000 });
  });

  test('Demo flow from landing page', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Click Demo Login
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Demo Login/i }).click();

    // Should proceed to repos phase (demo mode skips OAuth)
    await expect(page.getByText('Select repository')).toBeVisible({ timeout: 30000 });

    // Demo repos should be listed
    const repoButtons = page.getByRole('button').filter({ hasText: /acme\/|demo/i });
    const count = await repoButtons.count();
    expect(count).toBeGreaterThan(0);
  });

  test('Demo flow from auth page', async ({ page }) => {
    // Navigate to auth page
    await page.goto('/', { timeout: 30000 });
    await expect(page.getByRole('button', { name: /Connect GitHub/i })).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Connect GitHub/i }).click();

    // Click demo mode if available
    const demoButton = page.getByRole('button', { name: /Demo Mode/i });
    const isVisible = await demoButton.isVisible().catch(() => false);
    
    if (isVisible) {
      await demoButton.click();
      await expect(page.getByText('Select repository')).toBeVisible({ timeout: 20000 });
    } else {
      test.skip();
    }
  });

  test('demo login completes full audit flow', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Start demo
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText('Select repository')).toBeVisible({ timeout: 20000 });

    // Select first demo repo
    await page.getByText(/acme\/backend-api/i).first().click();

    // Should show scanning
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 15000 });

    // Wait for results
    await expect(page.getByText('Report:', { exact: false })).toBeVisible({ timeout: 30000 });

    // Verify result elements
    await expect(page.getByText('Recommendations')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: 'New audit' })).toBeVisible({ timeout: 10000 });
  });
});
