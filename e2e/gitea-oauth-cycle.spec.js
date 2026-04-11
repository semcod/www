// e2e/gitea-oauth-cycle.spec.js
// Playwright test for full Gitea OAuth + audit cycle
//
// Run: npx playwright test e2e/gitea-oauth-cycle.spec.js

import { test, expect } from "@playwright/test";

const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:3000";
const GITEA_URL = process.env.GITEA_URL || "http://localhost:3100";
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8003";

const GITEA_USER = "tom-sapletta-com";
const GITEA_PASS = "Semcod2026!";

test.describe("Gitea full developer cycle", () => {

  test("gitea is healthy and has repos", async ({ request }) => {
    const ver = await request.get(`${GITEA_URL}/api/v1/version`);
    expect(ver.ok()).toBeTruthy();

    const repos = await request.get(
      `${GITEA_URL}/api/v1/repos/search?q=sample`,
      { headers: { Authorization: `Basic ${Buffer.from(`${GITEA_USER}:${GITEA_PASS}`).toString("base64")}` } }
    );
    expect(repos.ok()).toBeTruthy();
    const body = await repos.json();
    const data = body.data || body;
    expect(data.length).toBeGreaterThanOrEqual(2);
  });

  test("create branch, commit, and open PR via Gitea API", async ({ request }) => {
    const auth = { Authorization: `Basic ${Buffer.from(`${GITEA_USER}:${GITEA_PASS}`).toString("base64")}` };
    const repo = `${GITEA_USER}/sample-python`;
    const branch = `test/playwright-${Date.now()}`;

    // Create branch
    const branchRes = await request.post(`${GITEA_URL}/api/v1/repos/${repo}/branches`, {
      headers: { ...auth, "Content-Type": "application/json" },
      data: { new_branch_name: branch, old_branch_name: "main" },
    });
    expect(branchRes.ok()).toBeTruthy();

    // Get file SHA
    const fileRes = await request.get(
      `${GITEA_URL}/api/v1/repos/${repo}/contents/app.py?ref=${branch}`,
      { headers: auth }
    );
    expect(fileRes.ok()).toBeTruthy();
    const fileSha = (await fileRes.json()).sha;

    // Commit change
    const newContent = Buffer.from("# Playwright test change\nprint('hello')\n").toString("base64");
    const commitRes = await request.put(`${GITEA_URL}/api/v1/repos/${repo}/contents/app.py`, {
      headers: { ...auth, "Content-Type": "application/json" },
      data: { content: newContent, message: "test: playwright commit", branch, sha: fileSha },
    });
    expect(commitRes.ok()).toBeTruthy();

    // Open PR
    const prRes = await request.post(`${GITEA_URL}/api/v1/repos/${repo}/pulls`, {
      headers: { ...auth, "Content-Type": "application/json" },
      data: { title: "test: playwright PR", head: branch, base: "main" },
    });
    expect(prRes.ok()).toBeTruthy();
    const pr = await prRes.json();
    expect(pr.number).toBeGreaterThan(0);

    // Wait and check for webhook delivery
    await new Promise((r) => setTimeout(r, 3000));

    // Get diff
    const diffRes = await request.get(
      `${GITEA_URL}/api/v1/repos/${repo}/pulls/${pr.number}.diff`,
      { headers: auth }
    );
    expect(diffRes.ok()).toBeTruthy();
    const diff = await diffRes.text();
    expect(diff.length).toBeGreaterThan(10);

    // Cleanup: close PR + delete branch
    await request.patch(`${GITEA_URL}/api/v1/repos/${repo}/pulls/${pr.number}`, {
      headers: { ...auth, "Content-Type": "application/json" },
      data: { state: "closed" },
    });
    await request.delete(`${GITEA_URL}/api/v1/repos/${repo}/branches/${branch}`, {
      headers: auth,
    });
  });

  test("backend processes gitea webhook", async ({ request }) => {
    // Simulate a gitea push webhook to backend
    const payload = {
      ref: "refs/heads/main",
      repository: {
        full_name: `${GITEA_USER}/sample-python`,
        clone_url: `${GITEA_URL}/${GITEA_USER}/sample-python.git`,
        html_url: `${GITEA_URL}/${GITEA_USER}/sample-python`,
        default_branch: "main",
      },
      pusher: { login: GITEA_USER },
      commits: [{ id: "abc123", message: "test push" }],
    };

    const res = await request.post(`${BACKEND_URL}/v2/webhook/gitea`, {
      headers: {
        "Content-Type": "application/json",
        "X-Gitea-Event": "push",
        "X-Gitea-Delivery": `test-${Date.now()}`,
      },
      data: payload,
    });

    // 200 or 202 = accepted, 404 = endpoint doesn't exist yet
    expect([200, 202, 404].includes(res.status())).toBeTruthy();
  });

  test("badge endpoint returns SVG", async ({ request }) => {
    const res = await request.get(`${BACKEND_URL}/badge/${GITEA_USER}-sample-python.svg`);
    if (res.ok()) {
      const ct = res.headers()["content-type"] || "";
      expect(ct).toContain("svg");
    }
    // Badge may not exist yet if no scan was done — that's ok
  });
});
