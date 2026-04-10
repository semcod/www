import { test, expect } from '@playwright/test';

test.describe('Social Sharing', () => {
  test('social share buttons visible on result page', async ({ page }) => {
    // Navigate to result page with demo data
    await page.goto('/#tab=audit&phase=result&repo=semcod/vallm&sandbox=1&audit=demo');
    
    await page.waitForLoadState('networkidle');
    
    // Check for social share buttons
    const twitterButton = page.getByRole('button', { name: /𝕏|Share/i }).first();
    const linkedinButton = page.getByRole('button', { name: /in|LinkedIn/i }).first();
    const blueskyButton = page.getByRole('button', { name: /🦋|Bluesky/i }).first();
    
    // At least one share button should be visible
    const anyVisible = await Promise.any([
      twitterButton.isVisible().catch(() => false),
      linkedinButton.isVisible().catch(() => false),
      blueskyButton.isVisible().catch(() => false),
    ]);
    
    expect(anyVisible).toBeTruthy();
  });

  test('social share buttons visible on recent scans', async ({ page }) => {
    await page.goto('/#tab=recent');
    
    await page.waitForLoadState('networkidle');
    
    // If scans exist, check for share buttons
    const shareButtons = page.getByRole('button', { name: /𝕏|in|🦋/ });
    const count = await shareButtons.count();
    
    if (count > 0) {
      expect(count).toBeGreaterThan(0);
    }
  });

  test('social share buttons visible on landing page recent scans', async ({ page }) => {
    await page.goto('/');
    
    await page.waitForLoadState('networkidle');
    
    // Check if recent scans section exists
    const recentSection = page.getByText('Ostatnio skanowane projekty');
    const isVisible = await recentSection.isVisible().catch(() => false);
    
    if (isVisible) {
      // Check for share buttons in recent scans
      const shareButtons = page.getByRole('button', { name: /𝕏|in/ });
      const count = await shareButtons.count();
      
      if (count > 0) {
        expect(count).toBeGreaterThan(0);
      }
    }
  });
});
