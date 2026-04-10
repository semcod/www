import { test, expect } from '@playwright/test';

test.describe('Demo Mode', () => {
  test('Demo Login button visible on landing page', async ({ page }) => {
    await page.goto('/');
    
    // Demo Login button should be visible
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible();
  });

  test('Demo flow from landing page', async ({ page }) => {
    await page.goto('/');
    
    // Click Demo Login
    await page.getByRole('button', { name: /Demo Login/i }).click();
    
    // Should proceed to repos phase (demo mode skips OAuth)
    await expect(page.getByText('Select repository')).toBeVisible({ timeout: 5000 });
    
    // Demo repos should be listed
    const repoButtons = page.getByRole('button').filter({ hasText: /acme\/backend-api|demo/i });
    const count = await repoButtons.count();
    expect(count).toBeGreaterThan(0);
  });

  test('Demo flow from auth page', async ({ page }) => {
    // Navigate to auth page
    await page.goto('/');
    await page.getByRole('button', { name: /Connect GitHub/i }).click();
    
    // Should be on auth page with demo option
    await expect(page.getByText('Authorize GitHub')).toBeVisible();
    await expect(page.getByRole('button', { name: /Demo Mode/i })).toBeVisible();
    
    // Click demo mode
    await page.getByRole('button', { name: /Demo Mode/i }).click();
    
    // Should proceed to repos
    await expect(page.getByText('Select repository')).toBeVisible({ timeout: 5000 });
  });

  test('demo login completes full audit flow', async ({ page }) => {
    await page.goto('/');
    
    // Start demo
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText('Select repository')).toBeVisible();
    
    // Select first demo repo
    await page.getByText(/acme\/backend-api/i).first().click();
    
    // Should show scanning
    await expect(page.getByText(/Analyzing/i)).toBeVisible();
    
    // Wait for results
    await expect(page.getByText('Report:', { exact: false })).toBeVisible({ timeout: 10000 });
    
    // Verify result elements
    await expect(page.getByText('Recommendations')).toBeVisible();
    await expect(page.getByRole('button', { name: 'New audit' })).toBeVisible();
  });
});
