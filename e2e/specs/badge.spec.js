import { test, expect } from '@playwright/test';

test.describe('Badge Generator', () => {
  test('generates markdown for repo', async ({ page }) => {
    await page.goto('/#tab=badge');
    
    await expect(page.getByText('Code Health Badge')).toBeVisible();
    
    // Clear and enter new repo
    const input = page.getByLabel(/Repository/i);
    await input.clear();
    await input.fill('myorg/myrepo');
    
    // Markdown should update
    await expect(page.getByText('![Code Health](https://semcod.dev/badge/myorg-myrepo.svg)')).toBeVisible();
  });

  test('shows grade scale', async ({ page }) => {
    await page.goto('/#tab=badge');
    
    const grades = ['A+', 'A', 'B+', 'B', 'C', 'D', 'F'];
    for (const grade of grades) {
      await expect(page.getByText(grade).first()).toBeVisible();
    }
  });
});
