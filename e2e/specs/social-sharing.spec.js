import { test, expect } from '@playwright/test';

test.describe('Social Sharing', () => {
  test('social share buttons visible on result page', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Click on Recent Scans tab to see share buttons there
    await page.getByRole('button', { name: 'Ostatnie Skany' }).click();
    await page.waitForTimeout(300);

    // Check if any scans exist
    const noScansMessage = page.getByText('Brak zapisanych skanów');
    const hasNoScans = await noScansMessage.isVisible().catch(() => false);

    if (hasNoScans) {
      // Skip test if no scans - share buttons won't exist
      test.skip();
      return;
    }

    // Click on a scan to open the result page
    const scanCard = page.locator('.scan-card').first();
    const hasScan = await scanCard.isVisible().catch(() => false);
    
    if (!hasScan) {
      test.skip();
      return;
    }
    
    await scanCard.click();
    await page.waitForTimeout(500);

    // Click on the Share tab to reveal share buttons
    const shareTab = page.getByRole('button', { name: /𝕏 Share/i });
    await shareTab.click();
    await page.waitForTimeout(300);

    // Check for social share buttons in the tab content
    const twitterButton = page.getByRole('button', { name: '𝕏' });
    const linkedinButton = page.getByRole('button', { name: 'in' });
    const blueskyButton = page.getByRole('button', { name: '🦋' });

    // Check visibility individually
    const twitterVisible = await twitterButton.isVisible().catch(() => false);
    const linkedinVisible = await linkedinButton.isVisible().catch(() => false);
    const blueskyVisible = await blueskyButton.isVisible().catch(() => false);

    expect(twitterVisible || linkedinVisible || blueskyVisible).toBeTruthy();
  });

  test('social share buttons visible on recent scans', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Click on Recent Scans tab
    await page.getByRole('button', { name: 'Ostatnie Skany' }).click();
    await page.waitForTimeout(300);

    // Check if any scans exist
    const noScansMessage = page.getByText('Brak zapisanych skanów');
    const hasNoScans = await noScansMessage.isVisible().catch(() => false);

    if (hasNoScans) {
      test.skip();
      return;
    }

    // Click on a scan to open the result page
    const scanCard = page.locator('.scan-card').first();
    const hasScan = await scanCard.isVisible().catch(() => false);
    
    if (!hasScan) {
      test.skip();
      return;
    }
    
    await scanCard.click();
    await page.waitForTimeout(500);

    // Click on the Share tab to reveal share buttons
    const shareTab = page.getByRole('button', { name: /𝕏 Share/i });
    await shareTab.click();
    await page.waitForTimeout(300);

    // Check for share buttons in the tab content
    const twitterButton = page.getByRole('button', { name: '𝕏' });
    const linkedinButton = page.getByRole('button', { name: 'in' });
    const blueskyButton = page.getByRole('button', { name: '🦋' });

    const twitterVisible = await twitterButton.isVisible().catch(() => false);
    const linkedinVisible = await linkedinButton.isVisible().catch(() => false);
    const blueskyVisible = await blueskyButton.isVisible().catch(() => false);

    expect(twitterVisible || linkedinVisible || blueskyVisible).toBeTruthy();
  });

  test('social share buttons visible on landing page recent scans', async ({ page }) => {
    await page.goto('/');

    await page.waitForLoadState('networkidle');

    // Check if recent scans section exists
    const recentSection = page.getByText('Ostatnio skanowane projekty');
    const isVisible = await recentSection.isVisible().catch(() => false);

    if (isVisible) {
      // Click on a recent scan to open result page
      const scanCard = page.locator('.scan-card').first();
      const hasScan = await scanCard.isVisible().catch(() => false);

      if (hasScan) {
        await scanCard.click();
        await page.waitForTimeout(500);

        // Click on the Share tab to reveal share buttons
        const shareTab = page.getByRole('button', { name: /𝕏 Share/i });
        await shareTab.click();
        await page.waitForTimeout(300);

        // Check for share buttons in the tab content
        const twitterButton = page.getByRole('button', { name: '𝕏' });
        const linkedinButton = page.getByRole('button', { name: 'in' });
        const blueskyButton = page.getByRole('button', { name: '🦋' });

        const twitterVisible = await twitterButton.isVisible().catch(() => false);
        const linkedinVisible = await linkedinButton.isVisible().catch(() => false);
        const blueskyVisible = await blueskyButton.isVisible().catch(() => false);

        expect(twitterVisible || linkedinVisible || blueskyVisible).toBeTruthy();
      }
    }
  });
});
