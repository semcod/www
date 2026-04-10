import { useState, useCallback } from "react";
import { startAudit as startAuditRequest, analyzePublicRepo } from "../api.js";
import { createSelectedRepo } from "./useUrlState.js";

export function useAuditActions(sessionToken, repoUrl, checkScanAllowed, setSelectedRepo, setIsSandbox, setPhase) {
  const [scanProgress, setScanProgress] = useState(0);
  const [scanLabel, setScanLabel] = useState("");
  const [audit, setAudit] = useState(null);
  const [auditId, setAuditId] = useState(null);

  const startAudit = useCallback(async (repo) => {
    if (!checkScanAllowed()) return;

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
  }, [checkScanAllowed, sessionToken, setSelectedRepo, setPhase, setIsSandbox, setAudit, setAuditId]);

  const startSandbox = useCallback(async () => {
    if (!checkScanAllowed()) return false;

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
  }, [checkScanAllowed, repoUrl, setSelectedRepo, setIsSandbox, setPhase, setAudit, setAuditId]);

  const resetAudit = useCallback(() => {
    setAudit(null);
    setAuditId(null);
    setScanProgress(0);
    setScanLabel("");
  }, [setAudit, setAuditId, setScanProgress, setScanLabel]);

  return {
    scanProgress, setScanProgress,
    scanLabel, setScanLabel,
    audit, setAudit,
    auditId, setAuditId,
    startAudit,
    startSandbox,
    resetAudit,
  };
}
