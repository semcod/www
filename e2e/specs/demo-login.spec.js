import { test, expect } from '@playwright/test';

test.describe('Demo Login Flow', () => {
  test('demo login button creates session and shows repos', async ({ page }) => {
    await page.goto('/');

    // Should see Demo Login button
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible();

    // Click Demo Login
    await page.getByRole('button', { name: /Demo Login/i }).click();

    // Should advance to repos phase (with demo repos)
    await expect(page.getByText(/Select repository/i)).toBeVisible({ timeout: 10000 });

    // Should show demo repos (acme/* from DEMO_REPOS)
    await expect(page.getByText(/acme\/backend-api/i)).toBeVisible();
  });

  test('demo user avatar appears in header after login', async ({ page }) => {
    await page.goto('/');

    // Login via demo
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText(/Select repository/i)).toBeVisible({ timeout: 10000 });

    // Header should show user login
    await expect(page.getByText('demo-user')).toBeVisible({ timeout: 5000 });

    // Logout button should be visible
    await expect(page.getByRole('button', { name: /Logout/i })).toBeVisible();
  });

  test('logout clears session and returns to landing', async ({ page }) => {
    await page.goto('/');

    // Login via demo
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText(/Select repository/i)).toBeVisible({ timeout: 10000 });

    // Click Logout
    await page.getByRole('button', { name: /Logout/i }).click();

    // Should return to landing
    await expect(page.getByText('One-click code audit')).toBeVisible({ timeout: 5000 });

    // Demo Login button should be visible again
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible();
  });

  test('session persists after page reload', async ({ page }) => {
    await page.goto('/');

    // Login via demo
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText(/Select repository/i)).toBeVisible({ timeout: 10000 });

    // Reload page
    await page.reload();

    // Should still show user (session from localStorage)
    await expect(page.getByText('demo-user')).toBeVisible({ timeout: 10000 });
  });
});
