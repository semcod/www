import { useEffect, useRef } from "react";
import { trackBenchmarkEvent } from "../api";

function safeTrack(caseId, payload) {
  if (!caseId) return;
  trackBenchmarkEvent(caseId, payload).catch(() => {});
}

export function useBenchmarkTracking({ phase, auditId, caseId, repo }) {
  const prevPhase = useRef(null);
  const trackedResultEntry = useRef(false);
  const startedAt = useRef(null);

  useEffect(() => {
    if (!caseId) return;
    if (!startedAt.current) {
      startedAt.current = Date.now();
    }
  }, [caseId]);

  useEffect(() => {
    if (!caseId || !auditId) return;

    const prev = prevPhase.current;
    prevPhase.current = phase;

    if (phase === "scanning" && prev !== "scanning") {
      safeTrack(caseId, {
        event_name: "audit_started",
        audit_id: auditId,
        metadata: { repo },
      });
    }

    if (phase === "result" && !trackedResultEntry.current) {
      trackedResultEntry.current = true;
      const elapsed = startedAt.current ? Math.round((Date.now() - startedAt.current) / 1000) : null;
      safeTrack(caseId, {
        event_name: "result_viewed",
        audit_id: auditId,
        event_value: elapsed !== null ? String(elapsed) : "",
        metadata: { repo, time_to_result_seconds: elapsed },
      });
    }
  }, [phase, auditId, caseId, repo]);

  function trackExport(format) {
    safeTrack(caseId, {
      event_name: "export_clicked",
      audit_id: auditId,
      event_value: format,
    });
  }

  function trackRecommendationOpened(recommendationId) {
    safeTrack(caseId, {
      event_name: "recommendation_opened",
      audit_id: auditId,
      event_value: recommendationId,
    });
  }

  function trackDecision(type) {
    safeTrack(caseId, {
      event_name: `decision_${type}`,
      audit_id: auditId,
    });
  }

  return { trackExport, trackRecommendationOpened, trackDecision };
}
