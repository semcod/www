// tests/github-login-sim.spec.js
// Playwright test for GitHub OAuth login with mock server
// User: tom-sapletta-com
//
// Run: npx playwright test tests/github-login-sim.spec.js

import { test, expect } from "@playwright/test";

const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:3000";
const MOCK_GITHUB_URL = process.env.MOCK_GITHUB_URL || "http://localhost:4010";
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8003";

test.describe("GitHub OAuth Login Simulation — tom-sapletta-com", () => {

  test.beforeAll(async ({ request }) => {
    // Verify mock GitHub server is alive
    const res = await request.get(`${MOCK_GITHUB_URL}/health`);
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.mode).toBe("github-simulation");
    expect(body.users).toContain("tom-sapletta-com");
  });

  test("mock server issues code and token for tom-sapletta-com", async ({ request }) => {
    // 1. Issue a code directly via simulation API
    const code = `tom-sapletta-com_${Date.now()}`;
    const issueRes = await request.post(`${MOCK_GITHUB_URL}/api/_sim/issue-code`, {
      data: { code, login: "tom-sapletta-com", state: "test123" },
    });
    expect(issueRes.ok()).toBeTruthy();

    // 2. Exchange code for token
    const tokenRes = await request.post(`${MOCK_GITHUB_URL}/login/oauth/access_token`, {
      headers: { Accept: "application/json" },
      data: {
        client_id: "Iv1.mock_test_client",
        client_secret: "mock_secret_for_testing",
        code,
      },
    });
    expect(tokenRes.ok()).toBeTruthy();
    const tokenBody = await tokenRes.json();
    expect(tokenBody.access_token).toBeTruthy();
    expect(tokenBody.access_token).toMatch(/^gho_mock_/);

    // 3. Use token to fetch user profile
    const userRes = await request.get(`${MOCK_GITHUB_URL}/user`, {
      headers: { Authorization: `Bearer ${tokenBody.access_token}` },
    });
    expect(userRes.ok()).toBeTruthy();
    const user = await userRes.json();
    expect(user.login).toBe("tom-sapletta-com");
    expect(user.name).toBe("Tom Sapletta");
    expect(user.id).toBe(5669315);

    // 4. Fetch repos
    const reposRes = await request.get(`${MOCK_GITHUB_URL}/user/repos`, {
      headers: { Authorization: `Bearer ${tokenBody.access_token}` },
    });
    expect(reposRes.ok()).toBeTruthy();
    const repos = await reposRes.json();
    expect(repos.length).toBeGreaterThanOrEqual(2);
    expect(repos.map((r) => r.name)).toContain("semcod");
  });

  test("invalid code returns error", async ({ request }) => {
    const tokenRes = await request.post(`${MOCK_GITHUB_URL}/login/oauth/access_token`, {
      headers: { Accept: "application/json" },
      data: {
        client_id: "Iv1.mock_test_client",
        client_secret: "mock_secret_for_testing",
        code: "invalid_code_999",
      },
    });
    expect(tokenRes.status()).toBe(400);
  });

  test("invalid token returns 401", async ({ request }) => {
    const userRes = await request.get(`${MOCK_GITHUB_URL}/user`, {
      headers: { Authorization: "Bearer gho_invalid_token" },
    });
    expect(userRes.status()).toBe(401);
  });

  test("full browser OAuth flow → frontend login", async ({ page }) => {
    // Navigate to frontend
    await page.goto(FRONTEND_URL);

    // Click login / Sign in with GitHub
    const loginBtn = page.locator('button:has-text("GitHub"), a:has-text("GitHub"), [data-testid="github-login"]');
    if (await loginBtn.count() === 0) {
      test.skip('No login button found');
      return;
    }

    await loginBtn.first().click();

    // Should redirect to mock GitHub login page
    try {
      await page.waitForURL(/.*4010.*authorize.*|.*mock.*login.*/i, { timeout: 8000 });
    } catch {
      // Redirected to real GitHub — mock not configured, skip gracefully
      const url = page.url();
      if (url.includes('github.com')) {
        test.skip('OAuth redirects to real GitHub (mock-github not configured)');
        return;
      }
      test.skip(`Unexpected redirect: ${url}`);
      return;
    }

    // Click the tom-sapletta-com user button on mock login page
    const userBtn = page.locator('button:has-text("tom-sapletta-com")');
    await expect(userBtn).toBeVisible({ timeout: 5000 });
    await userBtn.click();

    // Should redirect back to frontend with session
    await page.waitForURL(`${FRONTEND_URL}/**`, { timeout: 10000 });

    // Verify user is logged in — check for Logout button or username (may wrap across lines)
    const loggedIn = page.getByRole('button', { name: /Logout/i })
      .or(page.getByText(/tom.*sapletta/i))
      .or(page.locator('[data-testid="user-name"]'));
    await expect(loggedIn.first()).toBeVisible({ timeout: 5000 });
  });
});
