import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test('homepage loads with correct title', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Semcod/);
  });

  test('landing page displays main CTA', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('One-click code audit')).toBeVisible();
    await expect(page.getByRole('button', { name: /Connect GitHub/i })).toBeVisible();
  });

  test('navigation tabs work', async ({ page }) => {
    await page.goto('/');
    
    await page.getByRole('button', { name: 'PR Bot' }).click();
    await expect(page.getByText('PR Comment Bot')).toBeVisible();
    
    await page.getByRole('button', { name: 'Badge' }).click();
    await expect(page.getByText('Code Health Badge')).toBeVisible();
    
    await page.getByRole('button', { name: 'Audit' }).click();
    await expect(page.getByText('One-click')).toBeVisible();
    
    await page.getByRole('button', { name: /Ostatnie Skany/i }).click();
    await expect(page.getByText('Ostatnio skanowane projekty')).toBeVisible();
  });

  test('sandbox repo input accepts URL', async ({ page }) => {
    await page.goto('/');
    
    const input = page.getByPlaceholder('github.com/owner/repo');
    await input.fill('github.com/facebook/react');
    await expect(input).toHaveValue('github.com/facebook/react');
  });

  test('clicking Scan button starts analysis flow', async ({ page }) => {
    await page.goto('/');
    
    await page.getByPlaceholder('github.com/owner/repo').fill('github.com/octocat/Hello-World');
    await page.getByRole('button', { name: 'Scan' }).click();
    
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 5000 });
  });
});
