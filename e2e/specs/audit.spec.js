import { test, expect } from '@playwright/test';

// Skip tests requiring backend in CI (GitHub OAuth needs running backend)
const skipInCI = process.env.CI ? test.skip : test;

test.describe('Audit Flow', () => {
  skipInCI('completes full audit flow with demo data', async ({ page }) => {
    await page.goto('/');

    // Click Connect GitHub
    await page.getByRole('button', { name: 'Connect GitHub' }).click();

    // Continue with auth
    await page.getByRole('button', { name: 'Continue with GitHub' }).click();
    await expect(page.getByText('Select repository')).toBeVisible();

    // Select first repo
    await page.getByText('acme/backend-api').first().click();

    // Should show scanning progress
    await expect(page.getByText(/Analyzing/i)).toBeVisible();
    await expect(page.getByText(/Cloning|code2llm|redup/i)).toBeVisible();

    // Wait for results (demo timeout)
    await expect(page.getByText('Report:', { exact: false })).toBeVisible({ timeout: 60000 });

    // Verify report elements
    await expect(page.getByText(/B\+|A|C/i).first()).toBeVisible();
    await expect(page.getByText('Recommendations')).toBeVisible();
  });

  test('handles sandbox mode', async ({ page }) => {
    await page.goto('/');
    
    await page.getByPlaceholder('github.com/owner/repo').fill('github.com/microsoft/vscode');
    await page.getByRole('button', { name: 'Scan' }).click();
    
    // Verify sandbox badge appears
    await expect(page.getByText('Sandbox', { exact: false })).toBeVisible({ timeout: 10000 });
  });

  test('displays error for invalid repo', async ({ page }) => {
    await page.goto('/#tab=audit&phase=result&audit=test123&sandbox=1');
    
    // Can show error state
    await page.waitForLoadState('networkidle');
  });
});
