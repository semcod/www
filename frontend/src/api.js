import { API } from "./constants";

export async function fetchRepos(token) {
  const res = await fetch(`${API}/api/repos?token=${token}`);
  if (!res.ok) throw new Error("Failed to fetch repos");
  return res.json();
}

export async function startAudit(repo, token) {
  const res = await fetch(`${API}/api/audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo, token }),
  });
  if (!res.ok) throw new Error("Failed to start audit");
  return res.json();
}

export async function fetchAudit(auditId) {
  const res = await fetch(`${API}/api/audit/${auditId}`);
  if (!res.ok) throw new Error("Failed to fetch audit");
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
