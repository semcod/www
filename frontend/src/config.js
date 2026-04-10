const PUBLIC_URL = import.meta.env.VITE_PUBLIC_URL || window.location.origin;

export const config = {
  PUBLIC_URL,
  getBadgeUrl: (repo) => `${PUBLIC_URL}/badge/${repo.replace("/", "-")}.svg`,
  getShareUrl: (repo) => `${PUBLIC_URL}/?repo=${repo}`,
  getReportUrl: (owner, repo) => `${PUBLIC_URL}/report/${owner}/${repo}`,
};
