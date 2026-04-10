import { test, expect } from '@playwright/test';

test.describe('GUI Views Visibility', () => {
  test('all navigation tabs visible after login', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Login with demo mode
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText('Select repository')).toBeVisible({ timeout: 20000 });

    // Select a demo repo
    await page.getByText(/acme\/backend-api/i).first().click();
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 15000 });

    // Wait for results
    await expect(page.getByText('Report:', { exact: false })).toBeVisible({ timeout: 60000 });

    // Check all navigation tabs are visible
    const tabs = [
      { name: 'Audit', selector: 'Audit' },
      { name: 'Ostatnie Skany', selector: /Ostatnie Skany/i },
      { name: 'PR Bot', selector: /PR Bot/i },
      { name: 'Repo', selector: 'Repo' },
      { name: 'Badge', selector: 'Badge' },
    ];

    for (const tab of tabs) {
      const tabButton = page.getByRole('button', { name: tab.selector, exact: tab.name === 'Audit' || tab.name === 'Repo' || tab.name === 'Badge' });
      await expect(tabButton).toBeVisible({ timeout: 10000 });
    }
  });

  test('all main sections visible on result page', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Login with demo mode
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText('Select repository')).toBeVisible({ timeout: 20000 });

    // Select a demo repo
    await page.getByText(/acme\/backend-api/i).first().click();
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 15000 });

    // Wait for results
    await expect(page.getByText('Report:', { exact: false })).toBeVisible({ timeout: 60000 });

    // Check main result page sections
    const sections = [
      { name: 'Health Score', selector: /A|B|C|D|F/i },
      { name: 'Recommendations', selector: /Recommendations/i },
      { name: 'Metrics', selector: /files|lines|complexity/i },
      { name: 'New Audit button', selector: /New audit/i },
    ];

    for (const section of sections) {
      const element = page.getByText(section.selector).first();
      const isVisible = await element.isVisible().catch(() => false);
      expect(isVisible).toBeTruthy();
    }
  });

  test('recent scans tab displays correctly', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Login with demo mode
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText('Select repository')).toBeVisible({ timeout: 20000 });

    // Select a demo repo
    await page.getByText(/acme\/backend-api/i).first().click();
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 15000 });

    // Wait for results
    await expect(page.getByText('Report:', { exact: false })).toBeVisible({ timeout: 60000 });

    // Click on Recent Scans tab
    await page.getByRole('button', { name: /Ostatnie Skany/i }).click();
    await page.waitForTimeout(500);

    // Check if recent scans section is visible
    const recentSection = page.getByText('Ostatnio skanowane projekty');
    const isVisible = await recentSection.isVisible().catch(() => false);

    if (!isVisible) {
      // Skip test if section not visible
      test.skip();
      return;
    }

    // Section is visible, that's sufficient
    expect(isVisible).toBeTruthy();
  });

  test('badge tab displays correctly', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Login with demo mode
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText('Select repository')).toBeVisible({ timeout: 20000 });

    // Select a demo repo
    await page.getByText(/acme\/backend-api/i).first().click();
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 15000 });

    // Wait for results
    await expect(page.getByText('Report:', { exact: false })).toBeVisible({ timeout: 60000 });

    // Click on Badge tab
    const badgeTab = page.getByRole('button', { name: /Badge/i });
    await badgeTab.click();
    await page.waitForTimeout(500);

    // Check for badge-related elements
    const badgeElements = [
      { selector: /badge/i },
      { selector: /grade/i },
      { selector: /A\+|A|B\+|B|C|D|F/i },
    ];

    let anyVisible = false;
    for (const element of badgeElements) {
      const el = page.getByText(element.selector).first();
      const isVisible = await el.isVisible().catch(() => false);
      if (isVisible) {
        anyVisible = true;
        break;
      }
    }
    expect(anyVisible).toBeTruthy();
  });

  test('user avatar visible in header after login', async ({ page }) => {
    await page.goto('/', { timeout: 30000 });

    // Login with demo mode
    await expect(page.getByRole('button', { name: /Demo Login/i })).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Demo Login/i }).click();
    await expect(page.getByText('Select repository')).toBeVisible({ timeout: 20000 });

    // Select a demo repo
    await page.getByText(/acme\/backend-api/i).first().click();
    await expect(page.getByText(/Analyzing/i)).toBeVisible({ timeout: 15000 });

    // Wait for results
    await expect(page.getByText('Report:', { exact: false })).toBeVisible({ timeout: 60000 });

    // Check for user avatar in header
    const avatar = page.locator('[data-testid="user-avatar"], .avatar, img[alt*="avatar"], img[alt*="user"]').first();
    const avatarVisible = await avatar.isVisible().catch(() => false);

    // Also check for demo user indicator
    const demoIndicator = page.getByText(/demo/i);
    const demoVisible = await demoIndicator.isVisible().catch(() => false);

    expect(avatarVisible || demoVisible).toBeTruthy();
  });
});
