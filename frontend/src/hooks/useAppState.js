import { useState, useCallback, useEffect } from "react";
import { useHashBootstrap, useHashSync } from "./useUrlState.js";
import { useScanAnimation, useAuditPolling } from "./usePolling.js";
import {
  useSessionCallbackBootstrap,
  useSessionProfile,
  getOAuthStartUrl,
  confirmAuthFlow,
  startDemoSession,
  logoutSession
} from "./useAuth.js";
import { fetchRepos } from "../api.js";
import { DEMO_REPOS } from "../constants.js";
import { useBilling } from "./useBilling.js";
import { useAuditActions } from "./useAuditActions.js";
import { useBenchmarkTracking } from "./useBenchmarkTracking.js";

const SESSION_KEY = "semcod_session";

export function useAppState() {
  const [tab, setTab] = useState("audit");
  const [phase, setPhase] = useState("landing");
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [badgeRepo, setBadgeRepo] = useState("acme/backend-api");
  const [sessionToken, setSessionToken] = useState(() => localStorage.getItem(SESSION_KEY) || null);
  const [user, setUser] = useState(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [isSandbox, setIsSandbox] = useState(false);
  const [benchmarkMode, setBenchmarkMode] = useState(false);
  const [benchmarkCaseId, setBenchmarkCaseId] = useState("");

  const {
    billingStatus,
    paywallVisible,
    checkoutLoading,
    checkScanAllowed,
    openCheckout,
    dismissPaywall,
    refreshBilling,
  } = useBilling(sessionToken);

  const {
    scanProgress, setScanProgress,
    scanLabel, setScanLabel,
    audit, setAudit,
    auditId, setAuditId,
    startAudit,
    startSandbox,
    resetAudit,
  } = useAuditActions(sessionToken, repoUrl, checkScanAllowed, setSelectedRepo, setIsSandbox, setPhase);

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

    // Skip API call for demo users - use DEMO_REPOS directly
    const demoUser = localStorage.getItem("semcod_demo_user");
    if (demoUser === "1") {
      setRepos(DEMO_REPOS);
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

  useBenchmarkTracking({
    phase,
    auditId,
    caseId: benchmarkCaseId,
    repo: selectedRepo?.full_name || "",
  });

  const reset = useCallback(() => {
    setPhase("landing");
    setSelectedRepo(null);
    setIsSandbox(false);
    setRepoUrl("");
    resetAudit();
  }, [setPhase, setSelectedRepo, setIsSandbox, setRepoUrl, resetAudit]);

  const startOAuth = useCallback(() => {
    window.location.href = getOAuthStartUrl();
  }, []);

  const confirmAuth = useCallback(() => {
    confirmAuthFlow(sessionToken, setRepos, setPhase);
  }, [sessionToken, setRepos, setPhase]);

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
    billingStatus, paywallVisible, checkoutLoading, openCheckout, dismissPaywall, refreshBilling,
    benchmarkMode, setBenchmarkMode,
    benchmarkCaseId, setBenchmarkCaseId,
  };
}
