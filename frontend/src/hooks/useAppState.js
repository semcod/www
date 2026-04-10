import { useState, useEffect, useCallback } from "react";
import { analyzePublicRepo, fetchAudit, fetchRepos, startAudit as startAuditRequest } from "../api";
import { DEMO_REPOS, DEMO_AUDIT } from "../constants";

export function useAppState() {
  const [tab, setTab] = useState("audit");
  const [phase, setPhase] = useState("landing");
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanLabel, setScanLabel] = useState("");
  const [audit, setAudit] = useState(null);
  const [badgeRepo, setBadgeRepo] = useState("acme/backend-api");
  const [token, setToken] = useState(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [isSandbox, setIsSandbox] = useState(false);
  const [auditId, setAuditId] = useState(null);

  // Read state from URL hash on mount
  useEffect(() => {
    const hash = window.location.hash.slice(1);
    const params = new URLSearchParams(hash);

    const t = params.get("token");
    if (t) setToken(t);

    const tabParam = params.get("tab");
    if (tabParam && ["audit", "prbot", "badge"].includes(tabParam)) {
      setTab(tabParam);
    }

    const phaseParam = params.get("phase");
    if (phaseParam && ["landing", "auth", "repos", "scanning", "value", "trial", "result"].includes(phaseParam)) {
      setPhase(phaseParam);
    }

    const repoParam = params.get("repo");
    if (repoParam) {
      setRepoUrl(repoParam);
      setIsSandbox(true);
      const parts = repoParam.split("/");
      if (parts.length >= 2) {
        const owner = parts[parts.length - 2];
        const repo = parts[parts.length - 1].replace(".git", "");
        setSelectedRepo({
          full_name: `${owner}/${repo}`,
          name: repo,
          language: "Python",
          stars: 0,
          size_kb: 1000,
          private: false,
        });
      }
    }

    const auditParam = params.get("audit");
    if (auditParam) {
      setAuditId(auditParam);
      if (phaseParam === "scanning" || phaseParam === "result") {
        fetchAudit(auditParam)
          .then(data => {
            if (data.status === "complete" || data.status === "error") {
              setAudit(data);
              setPhase("result");
            }
          })
          .catch(() => {});
      }
    }

    const searchParams = new URLSearchParams(window.location.search);
    if (searchParams.get("token")) {
      window.history.replaceState({}, "", window.location.pathname + window.location.hash);
    }
  }, []);

  // Update URL hash when state changes
  useEffect(() => {
    const params = new URLSearchParams();
    params.set("tab", tab);
    params.set("phase", phase);
    if (token) params.set("token", token);
    if (selectedRepo?.full_name) params.set("repo", selectedRepo.full_name);
    if (isSandbox) params.set("sandbox", "1");
    if (auditId) params.set("audit", auditId);

    window.history.replaceState({}, "", `#${params.toString()}`);
  }, [tab, phase, token, selectedRepo, isSandbox, auditId]);

  // Fetch repos when token available
  useEffect(() => {
    if (!token || phase !== "repos") return;
    fetchRepos(token)
      .then(setRepos)
      .catch(() => setRepos(DEMO_REPOS));
  }, [token, phase]);

  // Scan animation
  useEffect(() => {
    if (phase !== "scanning") return;
    setScanProgress(0);
    const steps = [
      { p: 8, t: 300, l: "⏳ Cloning repository..." },
      { p: 20, t: 700, l: "🔬 code2llm: analyzing CFG, DFG, call graphs..." },
      { p: 35, t: 1300, l: "🔁 redup: detecting duplications (AST)..." },
      { p: 50, t: 1900, l: "🧹 pyqual: quality gates (ruff + mypy + bandit)..." },
      { p: 65, t: 2500, l: "📉 regix: regression index..." },
      { p: 80, t: 3100, l: "✅ vallm: validating results..." },
      { p: 92, t: 3600, l: "📊 Generating report and badge..." },
      { p: 100, t: 4000, l: "✅ Done!" },
    ];
    const timers = steps.map(({ p, t, l }) =>
      setTimeout(() => { setScanProgress(p); setScanLabel(l); }, t)
    );
    const done = setTimeout(() => { setAudit(DEMO_AUDIT); setPhase("value"); }, 4500);
    return () => { timers.forEach(clearTimeout); clearTimeout(done); };
  }, [phase]);

  // Poll for analysis results (real API for sandbox, demo otherwise)
  useEffect(() => {
    if (phase !== "scanning" || !isSandbox || !auditId) return;

    let pollCount = 0;
    const maxPolls = 60;

    const poll = async () => {
      try {
        const data = await fetchAudit(auditId);

        if (data.status === "complete") {
          setAudit(data);
          setPhase("result");
          return true;
        } else if (data.status === "error") {
          setAudit({ error: data.error || "Analysis failed" });
          setPhase("result");
          return true;
        }
      } catch (e) {
        // Continue polling on network error
      }

      pollCount++;
      if (pollCount >= maxPolls) {
        setAudit({ error: "Analysis timed out" });
        setPhase("result");
        return true;
      }

      return false;
    };

    const interval = setInterval(async () => {
      const shouldStop = await poll();
      if (shouldStop) clearInterval(interval);
    }, 2000);

    return () => clearInterval(interval);
  }, [phase, isSandbox, auditId]);

  const reset = useCallback(() => {
    setPhase("landing");
    setSelectedRepo(null);
    setAudit(null);
    setIsSandbox(false);
    setRepoUrl("");
    setAuditId(null);
  }, []);

  const startOAuth = useCallback(() => {
    setPhase("auth");
  }, []);

  const confirmAuth = useCallback(() => {
    setRepos(DEMO_REPOS);
    setPhase("repos");
  }, []);

  const startAudit = useCallback((repo) => {
    setSelectedRepo(repo);
    setPhase("scanning");

    if (token) {
      startAuditRequest(repo.full_name, token)
        .then((data) => {
          if (data.audit_id) {
            setAuditId(data.audit_id);
          }
        })
        .catch(() => {});
    }
  }, [token]);

  const startSandbox = useCallback(() => {
    if (!repoUrl.trim()) return;

    const url = repoUrl.trim();
    let owner, repo;

    const match = url.match(/github\.com\/([^\/]+)\/([^\/\.]+)/) ||
                  url.match(/gitlab\.com\/([^\/]+)\/([^\/\.]+)/) ||
                  url.match(/bitbucket\.org\/([^\/]+)\/([^\/\.]+)/);

    if (match) {
      owner = match[1];
      repo = match[2];
    } else {
      const sshMatch = url.match(/:([^\/]+)\/([^\/\.]+)\.?/);
      if (sshMatch) {
        owner = sshMatch[1];
        repo = sshMatch[2];
      }
    }

    if (owner && repo) {
      const repoData = {
        full_name: `${owner}/${repo}`,
        name: repo,
        language: "Python",
        stars: 0,
        size_kb: 1000,
        private: false,
        url: url,
      };
      setSelectedRepo(repoData);
      setIsSandbox(true);
      setPhase("scanning");

      analyzePublicRepo(url)
        .then(data => {
          if (data.audit_id) {
            setAuditId(data.audit_id);
          }
        })
        .catch(() => {});
    }
  }, [repoUrl]);

  return {
    tab, setTab,
    phase, setPhase,
    repos, setRepos,
    selectedRepo, setSelectedRepo,
    scanProgress, scanLabel,
    audit, setAudit,
    badgeRepo, setBadgeRepo,
    token, setToken,
    repoUrl, setRepoUrl,
    isSandbox, setIsSandbox,
    auditId, setAuditId,
    reset, startOAuth, confirmAuth, startAudit, startSandbox,
  };
}
