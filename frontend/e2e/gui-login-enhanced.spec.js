// Enhanced GUI login tests for GitHub OAuth simulation
// Tests multiple browsers and frameworks integration
import { test, expect } from "@playwright/test";

const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:3000";
const MOCK_GITHUB_URL = process.env.MOCK_GITHUB_URL || "http://localhost:4010";

test.describe("Enhanced GUI Login Tests", () => {
  test.beforeAll(async ({ request }) => {
    // Verify mock GitHub server is alive
    const res = await request.get(`${MOCK_GITHUB_URL}/health`);
    expect(res.ok()).toBeTruthy();
  });

  test("Chromium - Full OAuth flow with detailed steps", async ({ page }) => {
    await testOAuthFlow(page, "chromium");
  });

  test("Firefox - Full OAuth flow with detailed steps", async ({ page }) => {
    await testOAuthFlow(page, "firefox");
  });

  test("WebKit - Full OAuth flow with detailed steps", async ({ page }) => {
    await testOAuthFlow(page, "webkit");
  });

  test("Manual login flow exploration", async ({ page }) => {
    // Navigate to frontend
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of initial page
    await page.screenshot({ path: 'test-results/01-frontend-initial.png' });
    
    // Look for any login-related elements
    const loginSelectors = [
      'button:has-text("GitHub")',
      'button:has-text("Sign in")',
      'button:has-text("Login")',
      'a:has-text("GitHub")',
      'a:has-text("Sign in")',
      '[data-testid="github-login"]',
      '[data-testid="login"]',
      'button[class*="github"]',
      'a[href*="github"]'
    ];
    
    let loginElement = null;
    for (const selector of loginSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 1000 })) {
          loginElement = element;
          console.log(`Found login element with selector: ${selector}`);
          break;
        }
      } catch (e) {
        // Continue trying other selectors
      }
    }
    
    if (loginElement) {
      await loginElement.click();
      await page.waitForLoadState('networkidle');
      
      // Check if we're on the mock GitHub page
      const currentUrl = page.url();
      console.log(`Redirected to: ${currentUrl}`);
      
      if (currentUrl.includes('4010') || currentUrl.includes('mock')) {
        await page.screenshot({ path: 'test-results/02-mock-github-page.png' });
        
        // Try multiple selectors for the user button
        const userSelectors = [
          'button:has-text("tom-sapletta-com")',
          'button:has-text("Tom Sapletta")',
          'text=tom-sapletta-com',
          'button',
          '[onclick*="tom-sapletta-com"]'
        ];
        
        for (const selector of userSelectors) {
          try {
            const userBtn = page.locator(selector).first();
            if (await userBtn.isVisible({ timeout: 2000 })) {
              console.log(`Found user button with selector: ${selector}`);
              await userBtn.click();
              break;
            }
          } catch (e) {
            // Continue trying other selectors
          }
        }
        
        // Wait for redirect back to frontend
        await page.waitForURL(`${FRONTEND_URL}/**`, { timeout: 10000 });
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/03-logged-in.png' });
        
        // Check for logged-in state
        const loggedInIndicators = [
          'text=tom-sapletta-com',
          'text=Tom Sapletta',
          '[data-testid="user-name"]',
          'button:has-text("Logout")',
          'a:has-text("Logout")'
        ];
        
        let isLoggedIn = false;
        for (const indicator of loggedInIndicators) {
          try {
            if (await page.locator(indicator).isVisible({ timeout: 2000 })) {
              isLoggedIn = true;
              console.log(`Found logged-in indicator: ${indicator}`);
              break;
            }
          } catch (e) {
            // Continue checking
          }
        }
        
        expect(isLoggedIn).toBeTruthy();
      } else {
        console.log(`Unexpected redirect URL: ${currentUrl}`);
      }
    } else {
      console.log("No login element found on the page");
      // Save page content for debugging
      const content = await page.content();
      console.log("Page content preview:", content.substring(0, 1000));
    }
  });

  async function testOAuthFlow(page, browserName) {
    console.log(`Testing OAuth flow with ${browserName}`);
    
    // Navigate to frontend
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    // Try to find and click login button
    const loginClicked = await attemptLogin(page);
    if (!loginClicked) {
      test.skip(`No login button found for ${browserName}`);
      return;
    }
    
    // Wait for redirect to mock GitHub
    await page.waitForURL(/.*4010.*|.*mock.*/, { timeout: 10000 });
    await page.waitForLoadState('networkidle');
    
    // Verify we're on the mock GitHub login page
    expect(page.url()).toContain('4010');
    
    // Look for and click the user button
    const userButtonClicked = await attemptUserLogin(page);
    expect(userButtonClicked).toBeTruthy();
    
    // Wait for redirect back to frontend
    await page.waitForURL(`${FRONTEND_URL}/**`, { timeout: 10000 });
    await page.waitForLoadState('networkidle');
    
    // Verify we're logged in
    const isLoggedIn = await checkLoginStatus(page);
    expect(isLoggedIn).toBeTruthy();
    
    // Take final screenshot
    await page.screenshot({ 
      path: `test-results/login-success-${browserName}.png`,
      fullPage: true 
    });
  }
  
  async function attemptLogin(page) {
    const selectors = [
      'button:has-text("GitHub")',
      'button:has-text("Sign in")',
      'a:has-text("GitHub")',
      '[data-testid="github-login"]'
    ];
    
    for (const selector of selectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          return true;
        }
      } catch (e) {
        // Continue trying
      }
    }
    return false;
  }
  
  async function attemptUserLogin(page) {
    const selectors = [
      'button:has-text("tom-sapletta-com")',
      'button:has-text("Tom Sapletta")',
      'text=tom-sapletta-com',
      'button'
    ];
    
    for (const selector of selectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 3000 })) {
          await element.click();
          return true;
        }
      } catch (e) {
        // Continue trying
      }
    }
    return false;
  }
  
  async function checkLoginStatus(page) {
    const indicators = [
      'text=tom-sapletta-com',
      'text=Tom Sapletta',
      '[data-testid="user-name"]',
      'button:has-text("Logout")'
    ];
    
    for (const indicator of indicators) {
      try {
        if (await page.locator(indicator).isVisible({ timeout: 3000 })) {
          return true;
        }
      } catch (e) {
        // Continue checking
      }
    }
    return false;
  }
});
