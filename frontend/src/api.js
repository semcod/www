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

export async function demoLogin() {
  const res = await fetch(`${API}/auth/demo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Demo login failed");
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
