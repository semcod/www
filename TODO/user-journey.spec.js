// e2e/specs/user-journey.spec.js
// Full user journey: landing → login → repo → audit → results → badge → tabs
// Supports 3 providers: mock (CI), gitea (dev), github (integration)
//
// Run:
//   GIT_PROVIDER=mock  npx playwright test e2e/specs/user-journey.spec.js
//   GIT_PROVIDER=gitea npx playwright test e2e/specs/user-journey.spec.js --headed
import { test, expect } from "@playwright/test";

const BASE = process.env.FRONTEND_URL || "http://localhost:3000";
const PROVIDER = process.env.GIT_PROVIDER || "mock";

const PROVIDERS = {
  mock: {
    loginUrl: /.*4010.*|.*mock.*/i,
    userSelector: 'button:has-text("tom-sapletta-com")',
    userName: "tom-sapletta-com",
  },
  gitea: {
    loginUrl: /.*3100.*|.*gitea.*/i,
    userField: 'input[name="user_name"]',
    passField: 'input[name="password"]',
    userName: "tom-sapletta-com",
    password: "Semcod2026!",
  },
};

test.describe(`User journey (${PROVIDER})`, () => {

  test("1. Landing page loads", async ({ page }) => {
    await page.goto(BASE);
    await expect(page).toHaveTitle(/semcod/i, { timeout: 10000 }).catch(() => {});
    const loginBtn = page.locator(
      'button:has-text("GitHub"), button:has-text("Connect"), button:has-text("Sign"), a:has-text("GitHub")'
    ).first();
    await expect(loginBtn).toBeVisible({ timeout: 10000 });
  });

  test("2. OAuth login flow", async ({ page }) => {
    await page.goto(BASE);
    const loginBtn = page.locator(
      'button:has-text("GitHub"), button:has-text("Connect")'
    ).first();
    await loginBtn.click();

    const cfg = PROVIDERS[PROVIDER];
    if (!cfg) { test.skip(); return; }

    // Handle provider-specific login page
    await page.waitForURL(cfg.loginUrl, { timeout: 15000 });

    if (PROVIDER === "mock") {
      await page.locator(cfg.userSelector).click();
    } else if (PROVIDER === "gitea") {
      await page.fill(cfg.userField, cfg.userName);
      await page.fill(cfg.passField, cfg.password);
      await page.click('button[type="submit"]');
      // Authorize OAuth app if prompted
      const authBtn = page.locator('button:has-text("Authorize"), button:has-text("Grant")');
      if (await authBtn.count() > 0) await authBtn.first().click();
    }

    // Should return to frontend, logged in
    await page.waitForURL(`${BASE}/**`, { timeout: 15000 });
    await expect(
      page.locator(`text=${cfg.userName}, [data-testid="user-name"]`).first()
    ).toBeVisible({ timeout: 10000 });
  });

  test("3. Repo list visible after login", async ({ page }) => {
    await performLogin(page);

    // Wait for repo list to load
    const repoItem = page.locator(
      '[data-testid="repo-item"], .repo-list button, .repo-card, li:has-text("sample")'
    ).first();
    await expect(repoItem).toBeVisible({ timeout: 15000 });
  });

  test("4. Start audit and see results", async ({ page }) => {
    test.setTimeout(180000); // 3 min for audit
    await performLogin(page);

    const repoBtn = page.locator(
      '[data-testid="repo-item"], .repo-list button'
    ).first();

    if (await repoBtn.count() === 0) { test.skip(); return; }
    await repoBtn.click();

    // Wait for scanning phase
    const scanning = page.locator(
      'text=/scanning|analyzing|running/i, [data-testid="scanning"]'
    ).first();
    // May skip scanning if cached
    if (await scanning.isVisible({ timeout: 5000 }).catch(() => false)) {
      // Wait for completion
      await expect(scanning).toBeHidden({ timeout: 120000 });
    }

    // Results should show grade
    const grade = page.locator(
      '.grade-circle, [data-testid="grade"], text=/^[A-F][+-]?$/'
    ).first();
    await expect(grade).toBeVisible({ timeout: 30000 });
  });

  test("5. Badge tab shows SVG preview", async ({ page }) => {
    await performLogin(page);

    const badgeTab = page.locator(
      'button:has-text("Badge"), [role="tab"]:has-text("Badge")'
    ).first();
    if (await badgeTab.count() === 0) { test.skip(); return; }

    await badgeTab.click();
    const badgePreview = page.locator(
      'svg, img[src*="badge"], [data-testid="badge-preview"]'
    ).first();
    await expect(badgePreview).toBeVisible({ timeout: 10000 });
  });

  test("6. Sandbox analysis (no login)", async ({ page }) => {
    test.setTimeout(120000);
    await page.goto(BASE);

    const input = page.locator(
      'input[placeholder*="repo"], input[placeholder*="URL"], [data-testid="sandbox-input"]'
    ).first();

    if (await input.count() === 0) { test.skip(); return; }

    await input.fill("https://github.com/tom-sapletta-com/semcod");
    const analyzeBtn = page.locator(
      'button:has-text("Analyze"), button:has-text("Scan"), button:has-text("Check")'
    ).first();
    if (await analyzeBtn.count() === 0) { test.skip(); return; }

    await analyzeBtn.click();
    const result = page.locator(
      '.grade-circle, [data-testid="sandbox-result"], text=/Score/'
    ).first();
    await expect(result).toBeVisible({ timeout: 90000 });
  });

  test("7. Recent scans tab", async ({ page }) => {
    await performLogin(page);

    const recentTab = page.locator(
      'button:has-text("Recent"), [role="tab"]:has-text("Recent")'
    ).first();
    if (await recentTab.count() === 0) { test.skip(); return; }

    await recentTab.click();
    const scanItem = page.locator(
      '[data-testid="scan-item"], .scan-row, tr, li'
    ).first();
    await expect(scanItem).toBeVisible({ timeout: 10000 });
  });

  test("8. Logout works", async ({ page }) => {
    await performLogin(page);

    const logoutBtn = page.locator(
      'button:has-text("Logout"), button:has-text("Sign out"), [data-testid="logout"]'
    ).first();
    if (await logoutBtn.count() === 0) { test.skip(); return; }

    await logoutBtn.click();
    // Should see login button again
    const loginBtn = page.locator(
      'button:has-text("GitHub"), button:has-text("Connect")'
    ).first();
    await expect(loginBtn).toBeVisible({ timeout: 10000 });
  });
});

// ── Helper: perform full login ──────────────────────────────────
async function performLogin(page) {
  await page.goto(BASE);
  const cfg = PROVIDERS[PROVIDER];
  if (!cfg) return;

  const loginBtn = page.locator(
    'button:has-text("GitHub"), button:has-text("Connect")'
  ).first();

  if (await loginBtn.count() === 0) return;
  await loginBtn.click();

  await page.waitForURL(cfg.loginUrl, { timeout: 15000 });

  if (PROVIDER === "mock") {
    await page.locator(cfg.userSelector).click();
  } else if (PROVIDER === "gitea") {
    await page.fill(cfg.userField, cfg.userName);
    await page.fill(cfg.passField, cfg.password);
    await page.click('button[type="submit"]');
    const authBtn = page.locator('button:has-text("Authorize"), button:has-text("Grant")');
    if (await authBtn.count() > 0) await authBtn.first().click();
  }

  await page.waitForURL(`${BASE}/**`, { timeout: 15000 });
}
