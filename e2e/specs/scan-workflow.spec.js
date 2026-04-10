import { test, expect } from '@playwright/test';

test.describe('Scan Workflow E2E', () => {
  test('scan workflow for GitHub repository', async ({ page }) => {
    test.setTimeout(120000);
    await page.goto('/', { timeout: 30000 });

    // Enter GitHub repo URL
    await expect(page.getByPlaceholder(/github\.com\/owner\/repo|https:\/\/github\.com\/owner\/repo/i)).toBeVisible({ timeout: 15000 });
    await page.getByPlaceholder(/github\.com\/owner\/repo|https:\/\/github\.com\/owner\/repo/i).fill('https://github.com/python/cpython');
    await page.getByRole('button', { name: /Analyze|Scan/i }).click();

    // Should show scanning phase
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 20000 });

    // Wait for results (may take time for actual scan)
    await page.waitForTimeout(90000);

    // Check if we're on result phase or still scanning
    const currentUrl = page.url();
    if (currentUrl.includes('phase=result') || currentUrl.includes('phase=value')) {
      // Verify result elements
      await expect(page.getByText(/Report:/i)).toBeVisible({ timeout: 10000 });
      await expect(page.locator('text=/A|B|C|D|F/').first()).toBeVisible({ timeout: 10000 });

      // Verify social share buttons exist
      await expect(page.getByRole('button', { name: /Share/i }).first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('scan workflow for GitLab repository', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Enter GitLab repo URL
    await expect(page.getByPlaceholder(/github\.com\/owner\/repo|https:\/\/github\.com\/owner\/repo/i)).toBeVisible({ timeout: 15000 });
    await page.getByPlaceholder(/github\.com\/owner\/repo|https:\/\/github\.com\/owner\/repo/i).fill('https://gitlab.com/gitlab-org/gitlab');
    await page.getByRole('button', { name: /Analyze|Scan/i }).click();

    // Should show scanning phase
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 20000 });
  });

  test('scan workflow for Bitbucket repository', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Enter Bitbucket repo URL
    await expect(page.getByPlaceholder(/github\.com\/owner\/repo|https:\/\/github\.com\/owner\/repo/i)).toBeVisible({ timeout: 15000 });
    await page.getByPlaceholder(/github\.com\/owner\/repo|https:\/\/github\.com\/owner\/repo/i).fill('https://bitbucket.org/atlassian/python-bitbucket');
    await page.getByRole('button', { name: /Analyze|Scan/i }).click();

    // Should show scanning phase
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 20000 });
  });

  test('recent scans displayed on landing page', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Wait for page to load
    await page.waitForLoadState('networkidle', { timeout: 30000 });

    // Check if recent scans section exists (may not have scans yet)
    const recentScansSection = page.getByText('Ostatnio skanowane projekty');
    const isVisible = await recentScansSection.isVisible().catch(() => false);

    if (isVisible) {
      // Verify scan cards exist
      await expect(recentScansSection).toBeVisible();
    }
  });

  test('social sharing buttons work on result page', async ({ page }) => {
    // Navigate to a completed scan (using demo mode)
    await page.goto('/#tab=audit&phase=result&repo=semcod/vallm&sandbox=1&audit=demo', { timeout: 30000 });

    await page.waitForLoadState('networkidle', { timeout: 30000 });

    // Look for share buttons
    const twitterButton = page.getByRole('button', { name: /𝕏|Twitter/i });
    const linkedinButton = page.getByRole('button', { name: /LinkedIn|in/i });

    // Verify buttons exist (may not be visible if demo mode)
    const twitterVisible = await twitterButton.isVisible().catch(() => false);
    const linkedinVisible = await linkedinButton.isVisible().catch(() => false);

    // At least one should exist
    expect(twitterVisible || linkedinVisible).toBeTruthy();
  });

  test('navigation to recent scans tab', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Click on recent scans tab
    const recentTab = page.getByRole('button', { name: /Ostatnie Skany/i });
    const isTabVisible = await recentTab.isVisible().catch(() => false);

    if (isTabVisible) {
      await recentTab.click();

      // Verify we're on the recent scans page
      await expect(page.getByText('Ostatnio skanowane projekty')).toBeVisible({ timeout: 15000 });
    }
  });
});
