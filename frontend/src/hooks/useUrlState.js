import { useEffect } from "react";
import { fetchAudit } from "../api.js";

const VALID_TABS = new Set(["audit", "prbot", "badge", "recent", "repo"]);
const VALID_PHASES = new Set(["landing", "auth", "repos", "scanning", "value", "trial", "result"]);

export function parseRepositoryReference(repoValue) {
  if (!repoValue) {
    return null;
  }

  const trimmed = repoValue.trim().replace(/\.git$/, "");
  const urlMatch = trimmed.match(/github\.com\/([^/]+)\/([^/.?#]+)/)
    || trimmed.match(/gitlab\.com\/([^/]+)\/([^/.?#]+)/)
    || trimmed.match(/bitbucket\.org\/([^/]+)\/([^/.?#]+)/)
    || trimmed.match(/:([^/]+)\/([^/.?#]+)\.?$/);

  if (urlMatch) {
    return {
      owner: urlMatch[1],
      repo: urlMatch[2],
    };
  }

  const parts = trimmed.split("/").filter(Boolean);
  if (parts.length < 2) {
    return null;
  }

  return {
    owner: parts[parts.length - 2],
    repo: parts[parts.length - 1].replace(/\.git$/, ""),
  };
}

export function createSelectedRepo(repoValue, url = repoValue) {
  const parsed = parseRepositoryReference(repoValue);
  if (!parsed) {
    return null;
  }

  return {
    full_name: `${parsed.owner}/${parsed.repo}`,
    name: parsed.repo,
    language: "Python",
    stars: 0,
    size_kb: 1000,
    private: false,
    url,
  };
}

export function useHashBootstrap({
  setTab,
  setPhase,
  setRepoUrl,
  setIsSandbox,
  setSelectedRepo,
  setAuditId,
  setAudit,
}) {
  useEffect(() => {
    const hash = window.location.hash.slice(1);
    const params = new URLSearchParams(hash);

    const tabParam = params.get("tab");
    if (tabParam && VALID_TABS.has(tabParam)) {
      setTab(tabParam);
    }

    const phaseParam = params.get("phase");
    if (phaseParam && VALID_PHASES.has(phaseParam)) {
      setPhase(phaseParam);
    }

    const repoParam = params.get("repo");
    const sandboxMode = params.get("sandbox") === "1";
    if (repoParam) {
      setRepoUrl(repoParam);
      setIsSandbox(sandboxMode);
      const repoData = createSelectedRepo(repoParam, repoParam);
      if (repoData) {
        setSelectedRepo(repoData);
      }
    }

    const auditParam = params.get("audit");
    if (!auditParam) {
      return;
    }

    setAuditId(auditParam);
    if (!phaseParam || !["scanning", "result", "value", "trial"].includes(phaseParam)) {
      return;
    }

    fetchAudit(auditParam)
      .then((data) => {
        if (data.status === "complete" || data.status === "error") {
          setAudit(data);
          setPhase("result");
        }
      })
      .catch(() => {});
  }, [setAudit, setAuditId, setIsSandbox, setPhase, setRepoUrl, setSelectedRepo, setTab]);
}

export function useHashSync({ tab, phase, selectedRepo, isSandbox, auditId }) {
  useEffect(() => {
    const params = new URLSearchParams();
    params.set("tab", tab);
    params.set("phase", phase);
    if (selectedRepo?.full_name) {
      params.set("repo", selectedRepo.full_name);
    }
    if (isSandbox) {
      params.set("sandbox", "1");
    }
    if (auditId) {
      params.set("audit", auditId);
    }

    window.history.replaceState({}, "", `#${params.toString()}`);
  }, [auditId, isSandbox, phase, selectedRepo, tab]);
}
