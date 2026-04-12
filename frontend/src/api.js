import { API } from "./constants";

function authHeaders(sessionToken) {
  return sessionToken
    ? { "Content-Type": "application/json", "Authorization": `Bearer ${sessionToken}` }
    : { "Content-Type": "application/json" };
}

export async function fetchMe(sessionToken) {
  const res = await fetch(`${API}/api/me`, {
    headers: { "Authorization": `Bearer ${sessionToken}` },
  });
  if (!res.ok) throw new Error("Failed to fetch user");
  return res.json();
}

export async function logout(sessionToken) {
  const res = await fetch(`${API}/api/logout`, {
    method: "POST",
    headers: authHeaders(sessionToken),
  });
  if (!res.ok) throw new Error("Failed to logout");
  return res.json();
}

export async function fetchRepos(sessionToken) {
  const res = await fetch(`${API}/api/repos`, {
    headers: { "Authorization": `Bearer ${sessionToken}` },
  });
  if (!res.ok) throw new Error("Failed to fetch repos");
  return res.json();
}

export async function startAudit(repo, sessionToken) {
  const res = await fetch(`${API}/api/audit`, {
    method: "POST",
    headers: authHeaders(sessionToken),
    body: JSON.stringify({ repo }),
  });
  if (!res.ok) throw new Error("Failed to start audit");
  return res.json();
}

export async function fetchAudit(auditId) {
  const res = await fetch(`${API}/api/audit/${auditId}`);
  if (!res.ok) throw new Error("Failed to fetch audit");
  return res.json();
}


export async function fetchBillingStatus(sessionToken) {
  const res = await fetch(`${API}/api/billing/status`, {
    headers: { "Authorization": `Bearer ${sessionToken}` },
  });
  if (!res.ok) throw new Error("Failed to fetch billing status");
  return res.json();
}

export async function createCheckoutSession(plan, billing, sessionToken) {
  const res = await fetch(`${API}/api/billing/checkout`, {
    method: "POST",
    headers: authHeaders(sessionToken),
    body: JSON.stringify({ plan, billing }),
  });
  if (!res.ok) throw new Error("Failed to create checkout session");
  return res.json();
}

export async function analyzePublicRepo(repoUrl) {
  const res = await fetch(`${API}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl, sandbox: true }),
  });
  if (!res.ok) throw new Error("Failed to analyze repo");
  return res.json();
}

// ─── Multi-platform Auth ──────────────────────────────────────────────────────

export function loginWithProvider(provider) {
  window.location.href = `${API}/auth/${provider}`;
}

// ─── PR Preview ───────────────────────────────────────────────────────────────

export async function getPreview(repo, provider, sessionToken) {
  const res = await fetch(`${API}/api/preview`, {
    method: "POST",
    headers: authHeaders(sessionToken),
    body: JSON.stringify({ repo, provider }),
  });
  if (!res.ok) throw new Error("Failed to get preview");
  return res.json();
}

// ─── App Installation ─────────────────────────────────────────────────────────

export async function installApp(repo, provider, apps, sessionToken) {
  const res = await fetch(`${API}/api/install`, {
    method: "POST",
    headers: authHeaders(sessionToken),
    body: JSON.stringify({ repo, provider, apps }),
  });
  if (!res.ok) throw new Error("Failed to install app");
  return res.json();
}

export async function getInstallations(sessionToken) {
  const res = await fetch(`${API}/api/installations`, {
    headers: { "Authorization": `Bearer ${sessionToken}` },
  });
  if (!res.ok) throw new Error("Failed to fetch installations");
  return res.json();
}

export async function uninstallApp(repo, provider, sessionToken) {
  const res = await fetch(`${API}/api/install`, {
    method: "DELETE",
    headers: authHeaders(sessionToken),
    body: JSON.stringify({ repo, provider }),
  });
  if (!res.ok) throw new Error("Failed to uninstall app");
  return res.json();
}

// ─── Trend ────────────────────────────────────────────────────────────────────

export async function fetchTrend(owner, repo, days = 30) {
  const res = await fetch(`${API}/api/trend/${owner}/${repo}?days=${days}`);
  if (!res.ok) throw new Error("Failed to fetch trend");
  return res.json();
}

// ─── Schedules ────────────────────────────────────────────────────────────────

export async function fetchSchedules(sessionToken) {
  const res = await fetch(`${API}/api/schedules`, { headers: authHeaders(sessionToken) });
  if (!res.ok) throw new Error("Failed to fetch schedules");
  return res.json();
}

export async function createSchedule(body, sessionToken) {
  const res = await fetch(`${API}/api/schedules`, {
    method: "POST",
    headers: authHeaders(sessionToken),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("Failed to create schedule");
  return res.json();
}

export async function deleteSchedule(owner, repo, sessionToken) {
  const res = await fetch(`${API}/api/schedules/${owner}/${repo}`, {
    method: "DELETE",
    headers: authHeaders(sessionToken),
  });
  if (!res.ok) throw new Error("Failed to delete schedule");
}

export async function fetchBillingPortal(sessionToken) {
  const res = await fetch(`${API}/api/billing/portal`, {
    method: "POST",
    headers: authHeaders(sessionToken),
  });
  if (!res.ok) throw new Error("Failed to open billing portal");
  return res.json();
}

// ─── Marketplace Apps ─────────────────────────────────────────────────────────

export async function getApps() {
  const res = await fetch(`${API}/api/apps`);
  if (!res.ok) throw new Error("Failed to fetch apps");
  return res.json();
}

export async function getAppStatus(repo, provider, sessionToken) {
  const res = await fetch(`${API}/api/apps/status?repo=${encodeURIComponent(repo)}&provider=${provider}`, {
    headers: { "Authorization": `Bearer ${sessionToken}` },
  });
  if (!res.ok) throw new Error("Failed to fetch app status");
  return res.json();
}


// ─── Benchmark ────────────────────────────────────────────────────────────────

export async function createBenchmarkCase(payload) {
  const res = await fetch(`${API}/api/benchmark/cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create benchmark case");
  return res.json();
}

export async function updateBenchmarkCase(caseId, updates) {
  const res = await fetch(`${API}/api/benchmark/cases/${caseId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error("Failed to update benchmark case");
  return res.json();
}

export async function submitRecommendationFeedback(caseId, recommendationId, payload) {
  const res = await fetch(
    `${API}/api/benchmark/cases/${caseId}/recommendations/${recommendationId}/feedback`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );
  if (!res.ok) throw new Error("Failed to submit recommendation feedback");
  return res.json();
}

export async function submitBenchmarkDecision(caseId, payload) {
  const res = await fetch(`${API}/api/benchmark/cases/${caseId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to submit benchmark decision");
  return res.json();
}

export async function trackBenchmarkEvent(caseId, payload) {
  const res = await fetch(`${API}/api/benchmark/cases/${caseId}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to track benchmark event");
  return res.json();
}

export async function fetchBenchmarkSummary() {
  const res = await fetch(`${API}/api/benchmark/summary`);
  if (!res.ok) throw new Error("Failed to fetch benchmark summary");
  return res.json();
}

export function downloadBenchmarkExport(format) {
  window.open(`${API}/api/benchmark/export.${format}`, "_blank");
}


// ─── ReDSL ────────────────────────────────────────────────────────────────────

export async function getRedslStatus() {
  const res = await fetch(`${API}/api/redsl/status`);
  if (!res.ok) throw new Error("Failed to check reDSL status");
  return res.json();
}

export async function redslAnalyze(projectPath, projectToon = null) {
  const res = await fetch(`${API}/api/redsl/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_path: projectPath, project_toon: projectToon }),
  });
  if (!res.ok) throw new Error("Failed to run reDSL analysis");
  return res.json();
}

export async function redslHealth(projectPath) {
  const res = await fetch(`${API}/api/redsl/health`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_path: projectPath }),
  });
  if (!res.ok) throw new Error("Failed to get reDSL health score");
  return res.json();
}

export async function redslRefactor(projectPath, maxActions = 10, dryRun = true) {
  const res = await fetch(`${API}/api/redsl/refactor`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_path: projectPath, max_actions: maxActions, dry_run: dryRun }),
  });
  if (!res.ok) throw new Error("Failed to run reDSL refactor");
  return res.json();
}

export async function redslDecide(projectPath) {
  const res = await fetch(`${API}/api/redsl/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_path: projectPath }),
  });
  if (!res.ok) throw new Error("Failed to run reDSL decide");
  return res.json();
}

export function redslBadgeUrl(owner, repo) {
  return `${API}/api/redsl/badge/${owner}/${repo}`;
}


// ─── Marketplace Auto-fix & Auto-PR ───────────────────────────────────────────

export async function triggerAutoFix(repo, provider, prId, baseBranch, sessionToken, options = {}) {
  const res = await fetch(`${API}/api/autofix`, {
    method: "POST",
    headers: authHeaders(sessionToken),
    body: JSON.stringify({
      repo,
      provider,
      pr_id: prId,
      base_branch: baseBranch || "main",
      mirror_to_gitea: options.mirrorToGitea || false,
      gitea_target_repo: options.giteaTargetRepo || null,
      auto_deploy: options.autoDeploy || false,
    }),
  });
  if (!res.ok) throw new Error("Failed to trigger auto-fix");
  return res.json();
}

export async function triggerRedslAutoPR(repo, projectPath, sessionToken, options = {}) {
  const res = await fetch(`${API}/api/autopr/redsl`, {
    method: "POST",
    headers: authHeaders(sessionToken),
    body: JSON.stringify({
      repo,
      project_path: projectPath,
      proposal_type: options.proposalType || "redsl_refactor",
      max_actions: options.maxActions || 10,
      dry_run: options.dryRun || false,
    }),
  });
  if (!res.ok) throw new Error("Failed to trigger reDSL auto-PR");
  return res.json();
}
