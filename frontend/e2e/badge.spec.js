import { test, expect } from '@playwright/test';

test.describe('Badge Generator', () => {
  test('generates markdown for repo', async ({ page }) => {
    await page.goto('/#tab=badge');
    
    await expect(page.getByText('Code Health Badge')).toBeVisible();
    
    // Clear and enter new repo
    const input = page.locator('input[type="text"]').first();
    await input.clear();
    await input.fill('myorg/myrepo');
    
    // Markdown should update
    await expect(page.locator('code').filter({ hasText: /myorg-myrepo/ })).toBeVisible();
  });

  test('shows grade scale', async ({ page }) => {
    await page.goto('/#tab=badge');
    
    const grades = ['A+', 'A', 'B+', 'B', 'C', 'D', 'F'];
    for (const grade of grades) {
      await expect(page.getByText(grade).first()).toBeVisible();
    }
  });
});
