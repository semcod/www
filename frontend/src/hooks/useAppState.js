import { useState, useCallback, useEffect } from "react";
import { useHashBootstrap, useHashSync, createSelectedRepo } from "./useUrlState.js";
import { useScanAnimation, useAuditPolling } from "./usePolling.js";
import {
  useSessionCallbackBootstrap,
  useSessionProfile,
  getOAuthStartUrl,
  confirmAuthFlow,
  startDemoSession,
  logoutSession
} from "./useAuth.js";
import { fetchRepos, startAudit as startAuditRequest, analyzePublicRepo } from "../api.js";
import { DEMO_REPOS } from "../constants.js";

const SESSION_KEY = "semcod_session";

export function useAppState() {
  const [tab, setTab] = useState("audit");
  const [phase, setPhase] = useState("landing");
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanLabel, setScanLabel] = useState("");
  const [audit, setAudit] = useState(null);
  const [badgeRepo, setBadgeRepo] = useState("acme/backend-api");
  const [sessionToken, setSessionToken] = useState(() => localStorage.getItem(SESSION_KEY) || null);
  const [user, setUser] = useState(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [isSandbox, setIsSandbox] = useState(false);
  const [auditId, setAuditId] = useState(null);

  // Read session token from URL callback (OAuth redirect) on mount
  useSessionCallbackBootstrap(setSessionToken, SESSION_KEY);

  // Fetch user profile when session token is available
  useSessionProfile(sessionToken, setSessionToken, setUser, SESSION_KEY);

  // Read state from URL hash on mount
  useHashBootstrap({
    setTab,
    setPhase,
    setRepoUrl,
    setIsSandbox,
    setSelectedRepo,
    setAuditId,
    setAudit,
  });

  // Update URL hash when state changes
  useHashSync({ tab, phase, selectedRepo, isSandbox, auditId });

  // Fetch repos when session token available and phase is repos
  useEffect(() => {
    if (!sessionToken || phase !== "repos") {
      return;
    }

    fetchRepos(sessionToken)
      .then(setRepos)
      .catch(() => setRepos(DEMO_REPOS));
  }, [phase, sessionToken, setRepos]);

  // Scan animation
  useScanAnimation(phase, auditId, setScanProgress, setScanLabel, setAudit, setPhase);

  // Poll for analysis results (real API for sandbox, demo otherwise)
  useAuditPolling(phase, auditId, setAudit, setPhase);

  const reset = useCallback(() => {
    setPhase("landing");
    setSelectedRepo(null);
    setAudit(null);
    setIsSandbox(false);
    setRepoUrl("");
    setAuditId(null);
  }, [setPhase, setSelectedRepo, setAudit, setIsSandbox, setRepoUrl, setAuditId]);

  const startOAuth = useCallback(() => {
    window.location.href = getOAuthStartUrl();
  }, []);

  const confirmAuth = useCallback(() => {
    confirmAuthFlow(sessionToken, setRepos, setPhase);
  }, [sessionToken, setRepos, setPhase]);

  const startAudit = useCallback(async (repo) => {
    setSelectedRepo(repo);
    setPhase("scanning");
    setIsSandbox(false);
    setAudit(null);
    setAuditId(null);

    if (!sessionToken) {
      return;
    }

    try {
      const data = await startAuditRequest(repo.full_name, sessionToken);
      if (data.audit_id) {
        setAuditId(data.audit_id);
      }
    } catch (error) {
    }
  }, [sessionToken, setSelectedRepo, setPhase, setIsSandbox, setAudit, setAuditId]);

  const startSandbox = useCallback(async () => {
    const url = repoUrl.trim();
    if (!url) {
      return false;
    }

    const repoData = createSelectedRepo(url, url);
    if (!repoData) {
      return false;
    }

    setSelectedRepo(repoData);
    setIsSandbox(true);
    setPhase("scanning");
    setAudit(null);
    setAuditId(null);

    try {
      const data = await analyzePublicRepo(url);
      if (data.audit_id) {
        setAuditId(data.audit_id);
      }
    } catch (error) {
    }

    return true;
  }, [repoUrl, setSelectedRepo, setIsSandbox, setPhase, setAudit, setAuditId]);

  const startDemoLogin = useCallback(() => {
    startDemoSession(setSessionToken, setRepos, setPhase, SESSION_KEY);
  }, [setSessionToken, setRepos, setPhase]);

  const doLogout = useCallback(() => {
    logoutSession(sessionToken, SESSION_KEY, setSessionToken, setUser, reset);
  }, [sessionToken, setSessionToken, setUser, reset]);

  return {
    tab, setTab,
    phase, setPhase,
    repos, setRepos,
    selectedRepo, setSelectedRepo,
    scanProgress, scanLabel,
    audit, setAudit,
    badgeRepo, setBadgeRepo,
    sessionToken, setSessionToken,
    user,
    repoUrl, setRepoUrl,
    isSandbox, setIsSandbox,
    auditId, setAuditId,
    reset, startOAuth, confirmAuth, startAudit, startSandbox, startDemoLogin, doLogout,
  };
}
