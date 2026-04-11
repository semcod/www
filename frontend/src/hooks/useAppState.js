import { useState, useCallback } from "react";
import { useHashBootstrap, useHashSync } from "./useUrlState.js";
import { useScanAnimation, useAuditPolling } from "./usePolling.js";
import { useSession } from "./useSession.js";
import { useRepoList } from "./useRepoList.js";
import { useBilling } from "./useBilling.js";
import { useAuditActions } from "./useAuditActions.js";
import { useBenchmarkState } from "./useBenchmarkState.js";

const SESSION_KEY = "semcod_session";

export function useAppState() {
  const [tab, setTab] = useState("audit");
  const [phase, setPhase] = useState("landing");
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [badgeRepo, setBadgeRepo] = useState("acme/backend-api");
  const [repoUrl, setRepoUrl] = useState("");
  const [isSandbox, setIsSandbox] = useState(false);

  const session = useSession(SESSION_KEY, setPhase);
  const { repos, setRepos } = useRepoList(session.sessionToken, phase);
  const billing = useBilling(session.sessionToken);
  const audit = useAuditActions(session.sessionToken, repoUrl, billing.checkScanAllowed, setSelectedRepo, setIsSandbox, setPhase);
  const benchmark = useBenchmarkState(phase, audit.auditId, selectedRepo);

  useHashBootstrap({
    setTab, setPhase, setRepoUrl, setIsSandbox, setSelectedRepo,
    setAuditId: audit.setAuditId, setAudit: audit.setAudit,
  });
  useHashSync({ tab, phase, selectedRepo, isSandbox, auditId: audit.auditId });
  useScanAnimation(phase, audit.auditId, audit.setScanProgress, audit.setScanLabel, audit.setAudit, setPhase);
  useAuditPolling(phase, audit.auditId, audit.setAudit, setPhase);

  const reset = useCallback(() => {
    setPhase("landing");
    setSelectedRepo(null);
    setIsSandbox(false);
    setRepoUrl("");
    audit.resetAudit();
  }, [setPhase, setSelectedRepo, setIsSandbox, setRepoUrl, audit.resetAudit]);

  const doLogout = useCallback(() => {
    session.clearSession(reset);
  }, [session.clearSession, reset]);

  return {
    tab, setTab,
    phase, setPhase,
    repos, setRepos,
    selectedRepo, setSelectedRepo,
    scanProgress: audit.scanProgress, scanLabel: audit.scanLabel,
    audit: audit.audit, setAudit: audit.setAudit,
    badgeRepo, setBadgeRepo,
    sessionToken: session.sessionToken, setSessionToken: session.setSessionToken,
    user: session.user,
    repoUrl, setRepoUrl,
    isSandbox, setIsSandbox,
    auditId: audit.auditId, setAuditId: audit.setAuditId,
    reset, startOAuth: session.startOAuth, confirmAuth: session.confirmAuth,
    startAudit: audit.startAudit, startSandbox: audit.startSandbox,
    doLogout,
    billingStatus: billing.billingStatus, paywallVisible: billing.paywallVisible,
    checkoutLoading: billing.checkoutLoading, openCheckout: billing.openCheckout,
    dismissPaywall: billing.dismissPaywall, refreshBilling: billing.refreshBilling,
    benchmarkMode: benchmark.benchmarkMode, setBenchmarkMode: benchmark.setBenchmarkMode,
    benchmarkCaseId: benchmark.benchmarkCaseId, setBenchmarkCaseId: benchmark.setBenchmarkCaseId,
  };
}
