import { useEffect } from "react";
import { fetchAudit } from "../api.js";

const VALID_TABS = new Set(["audit", "prbot", "badge", "recent", "repo"]);
const VALID_PHASES = new Set(["landing", "auth", "repos", "scanning", "value", "trial", "result"]);
const RESULT_PHASES = ["scanning", "result", "value", "trial"];

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
    return { owner: urlMatch[1], repo: urlMatch[2] };
  }

  const parts = trimmed.split("/").filter(Boolean);
  if (parts.length < 2) {
    return null;
  }

  return { owner: parts[parts.length - 2], repo: parts[parts.length - 1].replace(/\.git$/, "") };
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

export function parseHashState(hash) {
  const params = new URLSearchParams(hash);
  const tab = params.get("tab");
  const phase = params.get("phase");
  const repo = params.get("repo");
  const sandbox = params.get("sandbox") === "1";
  const audit = params.get("audit");

  return {
    tab: tab && VALID_TABS.has(tab) ? tab : null,
    phase: phase && VALID_PHASES.has(phase) ? phase : null,
    repo,
    sandbox,
    audit,
  };
}

export function restoreAuditFromHash(auditId, tab, phase, setAudit, setPhase) {
  if (!auditId || tab !== "audit" || !phase || !RESULT_PHASES.includes(phase)) {
    return;
  }

  fetchAudit(auditId)
    .then((data) => {
      if (data.status === "complete" || data.status === "error") {
        setAudit(data);
        setPhase("result");
      }
    })
    .catch(() => {});
}

export function useHashBootstrap({
  setTab, setPhase, setRepoUrl, setIsSandbox, setSelectedRepo, setAuditId, setAudit,
}) {
  useEffect(() => {
    const state = parseHashState(window.location.hash.slice(1));

    if (state.tab) setTab(state.tab);
    if (state.phase) setPhase(state.phase);
    if (state.repo) {
      setRepoUrl(state.repo);
      setIsSandbox(state.sandbox);
      const repoData = createSelectedRepo(state.repo, state.repo);
      if (repoData) setSelectedRepo(repoData);
    }
    if (state.audit) {
      setAuditId(state.audit);
      restoreAuditFromHash(state.audit, state.tab, state.phase, setAudit, setPhase);
    }
  }, [setAudit, setAuditId, setIsSandbox, setPhase, setRepoUrl, setSelectedRepo, setTab]);
}

export function useHashSync({ tab, phase, selectedRepo, isSandbox, auditId }) {
  useEffect(() => {
    const params = new URLSearchParams();
    params.set("tab", tab);
    params.set("phase", phase);
    if (selectedRepo?.full_name) params.set("repo", selectedRepo.full_name);
    if (isSandbox) params.set("sandbox", "1");
    if (auditId) params.set("audit", auditId);
    window.history.replaceState({}, "", `#${params.toString()}`);
  }, [auditId, isSandbox, phase, selectedRepo, tab]);
}
