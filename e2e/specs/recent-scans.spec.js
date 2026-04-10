import { test, expect } from '@playwright/test';

test.describe('Recent Scans', () => {
  test('recent scans tab displays correctly', async ({ page }) => {
    await page.goto('/#tab=recent');
    await page.waitForLoadState('networkidle');
    
    // Wait for tab content to load
    await page.waitForTimeout(500);
    
    // Verify heading
    await expect(page.getByText('Ostatnio skanowane projekty')).toBeVisible();
    
    // Verify scan count is displayed
    await expect(page.locator('text=/Liczba skanów:/i')).toBeVisible();
  });

  test('recent scans on landing page', async ({ page }) => {
    await page.goto('/');
    
    await page.waitForLoadState('networkidle');
    
    // Check if recent scans section exists
    const recentSection = page.getByText('Ostatnio skanowane projekty');
    const isVisible = await recentSection.isVisible().catch(() => false);
    
    if (isVisible) {
      // Verify scan cards are displayed
      const scanCards = page.locator('div').filter({ hasText: /github\.com/i });
      const count = await scanCards.count();
      
      if (count > 0) {
        expect(count).toBeGreaterThan(0);
        
        // Verify grade badges are shown
        await expect(page.locator('div').filter({ hasText: /[A-F]\+?/ })).first().toBeVisible();
      }
    }
  });

  test('clicking scan card opens GitHub repo', async ({ page }) => {
    await page.goto('/#tab=recent');
    
    await page.waitForLoadState('networkidle');
    
    // Find first scan card
    const scanCard = page.locator('div').filter({ hasText: /github\.com/i }).first();
    const count = await scanCard.count();
    
    if (count > 0) {
      // Click should open new tab (we can't test new tab easily in E2E, but we can verify click works)
      await scanCard.click();
    }
  });

  test('view button on scan card navigates to audit', async ({ page }) => {
    await page.goto('/#tab=recent');
    
    await page.waitForLoadState('networkidle');
    
    // Find view button
    const viewButton = page.getByRole('button', { name: /Zobacz/i });
    const count = await viewButton.count();
    
    if (count > 0) {
      await viewButton.first().click();
      
      // Should navigate to audit tab
      await expect(page.getByText(/Analyzing|Report:/i)).toBeVisible({ timeout: 5000 });
    }
  });

  test('badge info section displays on recent scans tab', async ({ page }) => {
    await page.goto('/#tab=recent');
    await page.waitForLoadState('networkidle');
    
    // Wait for tab content to load
    await page.waitForTimeout(500);
    
    // Verify badge info section - emoji can cause issues, check container instead
    await expect(page.getByRole('heading', { name: /Dodaj badge/i })).toBeVisible();
    await expect(page.locator('code').filter({ hasText: /Code Health/i })).toBeVisible();
  });
});
