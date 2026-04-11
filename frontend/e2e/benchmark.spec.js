import { test, expect } from '@playwright/test';

const CASE_ID = `BM-E2E-PW-${Date.now()}`;

test.describe('Benchmark Review Panel', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/#tab=audit&phase=result&sandbox=1&repo=acme%2Fbackend-api&audit=demo');
    await page.waitForTimeout(800);
  });

  test('panel toggle renders below recommendations', async ({ page }) => {
    const toggle = page.getByText('Benchmark Review');
    await expect(toggle).toBeVisible();
    await toggle.click();
    await expect(page.getByText('Utwórz przypadek benchmarkowy')).toBeVisible();
  });

  test('case creation form requires case_id', async ({ page }) => {
    await page.getByText('Benchmark Review').click();
    const btn = page.getByRole('button', { name: 'Utwórz przypadek' });
    await expect(btn).toBeDisabled();
    await page.getByPlaceholder('case_id (np. BM-001)').fill(CASE_ID);
    await expect(btn).not.toBeDisabled();
  });

  test('source_type and change_type selects exist', async ({ page }) => {
    await page.getByText('Benchmark Review').click();
    await expect(page.getByText('Source type')).toBeVisible();
    await expect(page.getByText('Change type')).toBeVisible();
    const sourceSelect = page.locator('select').first();
    await expect(sourceSelect).toBeVisible();
  });

  test('panel collapses on second toggle click', async ({ page }) => {
    const toggle = page.getByText('Benchmark Review');
    await toggle.click();
    await expect(page.getByText('Utwórz przypadek benchmarkowy')).toBeVisible();
    await toggle.click();
    await expect(page.getByText('Utwórz przypadek benchmarkowy')).not.toBeVisible();
  });
});

test.describe('Benchmark API integration', () => {
  const API = process.env.API_URL || 'http://localhost:8003';

  test('summary endpoint returns expected shape', async ({ request }) => {
    const res = await request.get(`${API}/api/benchmark/summary`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('total_cases');
    expect(body).toHaveProperty('pr_conversion_rate');
    expect(body).toHaveProperty('recommendation_acceptance_rate');
  });

  test('full case lifecycle: create → patch → decision → feedback → event', async ({ request }) => {
    const caseId = `BM-PW-${Date.now()}`;

    // Create
    const create = await request.post(`${API}/api/benchmark/cases`, {
      data: { case_id: caseId, repo: 'acme/test', source_type: 'pr', change_type: 'bugfix', baseline_detected: false },
    });
    expect(create.status()).toBe(201);
    expect((await create.json()).case_id).toBe(caseId);

    // Patch
    const patch = await request.patch(`${API}/api/benchmark/cases/${caseId}`, {
      data: { reviewer_verdict: 'go' },
    });
    expect(patch.status()).toBe(200);
    expect((await patch.json()).reviewer_verdict).toBe('go');

    // Decision
    const decision = await request.post(`${API}/api/benchmark/cases/${caseId}/decision`, {
      data: { pr_candidate: true, deployment_model_selected: 'hybrid' },
    });
    expect(decision.status()).toBe(200);
    expect((await decision.json()).deployment_model_selected).toBe('hybrid');

    // Feedback
    const feedback = await request.post(
      `${API}/api/benchmark/cases/${caseId}/recommendations/rec-abc123/feedback`,
      { data: { accepted: true, novelty_score: 3, usefulness_score: 2, notes: 'Playwright test' } }
    );
    expect(feedback.status()).toBe(200);
    expect((await feedback.json()).accepted).toBe(true);

    // Event
    const event = await request.post(`${API}/api/benchmark/cases/${caseId}/events`, {
      data: { event_name: 'result_viewed', audit_id: 'pw-audit-123' },
    });
    expect(event.status()).toBe(201);
    expect((await event.json()).event_name).toBe('result_viewed');

    // Verify list
    const list = await request.get(`${API}/api/benchmark/cases/${caseId}/events`);
    expect(list.status()).toBe(200);
    const events = (await list.json()).events;
    expect(events.length).toBeGreaterThanOrEqual(1);

    // Export JSON includes the new case
    const exp = await request.get(`${API}/api/benchmark/export.json`);
    expect(exp.status()).toBe(200);
    const exportBody = await exp.json();
    expect(exportBody.cases.some((c) => c.case_id === caseId)).toBe(true);
  });

  test('duplicate case returns 409', async ({ request }) => {
    const caseId = `BM-DUP-${Date.now()}`;
    await request.post(`${API}/api/benchmark/cases`, {
      data: { case_id: caseId, repo: 'acme/dup-test' },
    });
    const dup = await request.post(`${API}/api/benchmark/cases`, {
      data: { case_id: caseId, repo: 'acme/dup-test' },
    });
    expect(dup.status()).toBe(409);
  });

  test('non-existent case returns 404', async ({ request }) => {
    const res = await request.get(`${API}/api/benchmark/cases/NONEXISTENT-CASE-${Date.now()}`);
    expect(res.status()).toBe(404);
  });
});
