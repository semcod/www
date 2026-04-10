import { API } from "../../constants";

export async function fetchRecentScans(limit = 100) {
  const response = await fetch(`${API}/api/scans/recent?limit=${limit}`);
  const data = await response.json();
  return data.scans || [];
}

export function formatRecentScanDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString("pl-PL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getPrimaryLanguage(languages) {
  if (!languages || Object.keys(languages).length === 0) {
    return null;
  }
  return Object.entries(languages)[0][0];
}

export function openRecentScanRepository(repo) {
  window.open(`https://github.com/${repo}`, "_blank");
}

export function openRecentScanAudit(repo) {
  window.location.hash = `tab=audit&phase=scanning&repo=${encodeURIComponent(`https://github.com/${repo}`)}&sandbox=1`;
  window.location.reload();
}
