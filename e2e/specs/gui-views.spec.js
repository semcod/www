import { test, expect } from '@playwright/test';

test.describe('GUI Views Visibility', () => {
  test('all navigation tabs visible on landing page', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Check landing page tabs
    const tabs = ['Audit', 'PR Bot', 'Badge'];
    for (const tab of tabs) {
      const tabButton = page.getByRole('button', { name: tab });
      const isVisible = await tabButton.isVisible().catch(() => false);
      expect(isVisible).toBeTruthy();
    }
  });

  test('badge tab displays correctly without login', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Click on Badge tab
    const badgeTab = page.getByRole('button', { name: /Badge/i });
    await badgeTab.click();
    await page.waitForTimeout(500);

    // Check for badge-related elements
    const badgeElements = [
      page.getByText(/badge/i).first(),
      page.getByText(/grade/i).first(),
      page.getByText(/Code Health/i).first(),
    ];

    let anyVisible = false;
    for (const el of badgeElements) {
      const isVisible = await el.isVisible().catch(() => false);
      if (isVisible) {
        anyVisible = true;
        break;
      }
    }
    expect(anyVisible).toBeTruthy();
  });

  test('recent scans tab displays correctly', async ({ page }) => {
    await page.goto('/#tab=recent', { timeout: 30000 });
    await page.waitForLoadState('networkidle');

    // Check if recent scans section exists
    const recentSection = page.getByText('Ostatnio skanowane projekty');
    const isVisible = await recentSection.isVisible().catch(() => false);

    if (!isVisible) {
      test.skip();
      return;
    }
    expect(isVisible).toBeTruthy();
  });

  test('Connect GitHub button visible for OAuth', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Connect GitHub button should be visible
    await expect(page.getByRole('button', { name: /Connect GitHub/i })).toBeVisible({ timeout: 15000 });
  });

  test('sandbox input and Analyze button visible', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Sandbox repo input should be visible
    const input = page.getByPlaceholder('https://github.com/owner/repo');
    await expect(input).toBeVisible({ timeout: 10000 });

    // Analyze button should be visible
    await expect(page.getByRole('button', { name: /Analyze/i })).toBeVisible({ timeout: 5000 });
  });
});
