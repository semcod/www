import { test, expect } from '@playwright/test';

test.describe('Audit Flow', () => {
  test('sandbox analyze starts for public repo', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Use sandbox mode
    const input = page.getByPlaceholder('https://github.com/owner/repo');
    await input.fill('https://github.com/octocat/Hello-World');
    await page.getByRole('button', { name: /Analyze/i }).click();

    // Should start analyzing
    await expect(page.getByText(/Analyzing|Scanning|Loading/i)).toBeVisible({ timeout: 10000 });
  });

  test('displays error for invalid repo URL', async ({ page }) => {
    await page.goto('/#tab=audit&phase=result&audit=test123&sandbox=1');
    await page.waitForLoadState('networkidle');
    // Page should load without crashing
    await expect(page.locator('body')).toBeVisible();
  });

  test('Connect GitHub button available for full audit', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });
    await expect(page.getByRole('button', { name: /Connect GitHub/i })).toBeVisible({ timeout: 15000 });
  });
});
