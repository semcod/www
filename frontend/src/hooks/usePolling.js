import { useEffect } from "react";
import { fetchAudit } from "../api.js";
import { DEMO_AUDIT } from "../constants.js";

const SCAN_STEPS = [
  { p: 8, t: 300, l: "⏳ Cloning repository..." },
  { p: 20, t: 700, l: "🔬 code2llm: analyzing CFG, DFG, call graphs..." },
  { p: 35, t: 1300, l: "🔁 redup: detecting duplications (AST)..." },
  { p: 50, t: 1900, l: "🧹 pyqual: quality gates (ruff + mypy + bandit)..." },
  { p: 65, t: 2500, l: "📉 regix: regression index..." },
  { p: 80, t: 3100, l: "✅ vallm: validating results..." },
  { p: 92, t: 3600, l: "📊 Generating report and badge..." },
  { p: 100, t: 4000, l: "✅ Done!" },
];

export function useScanAnimation(phase, auditId, setScanProgress, setScanLabel, setAudit, setPhase) {
  useEffect(() => {
    if (phase !== "scanning") {
      return;
    }

    setScanProgress(0);
    const timers = SCAN_STEPS.map(({ p, t, l }) =>
      setTimeout(() => {
        setScanProgress(p);
        setScanLabel(l);
      }, t)
    );
    let done = null;

    if (!auditId) {
      done = setTimeout(() => {
        setAudit(DEMO_AUDIT);
        setPhase("value");
      }, 4500);
    }

    return () => {
      timers.forEach(clearTimeout);
      if (done) {
        clearTimeout(done);
      }
    };
  }, [auditId, phase, setAudit, setPhase, setScanLabel, setScanProgress]);
}

export function useAuditPolling(phase, auditId, setAudit, setPhase) {
  useEffect(() => {
    if (phase !== "scanning" || !auditId) {
      return;
    }

    let pollCount = 0;
    const MAX_POLLS = 60;

    const poll = async () => {
      try {
        const data = await fetchAudit(auditId);

        if (data.status === "complete") {
          setAudit(data);
          setPhase("result");
          return true;
        }
        if (data.status === "error") {
          setAudit({ error: data.error || "Analysis failed" });
          setPhase("result");
          return true;
        }
      } catch (error) {
      }

      pollCount += 1;
      if (pollCount >= MAX_POLLS) {
        setAudit({ error: "Analysis timed out" });
        setPhase("result");
        return true;
      }

      return false;
    };

    const interval = setInterval(async () => {
      const shouldStop = await poll();
      if (shouldStop) {
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [auditId, phase, setAudit, setPhase]);
}
