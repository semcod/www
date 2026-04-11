import { useState } from "react";
import { useBenchmarkTracking } from "./useBenchmarkTracking.js";

export function useBenchmarkState(phase, auditId, selectedRepo) {
  const [benchmarkMode, setBenchmarkMode] = useState(false);
  const [benchmarkCaseId, setBenchmarkCaseId] = useState("");

  useBenchmarkTracking({
    phase,
    auditId,
    caseId: benchmarkCaseId,
    repo: selectedRepo?.full_name || "",
  });

  return { benchmarkMode, setBenchmarkMode, benchmarkCaseId, setBenchmarkCaseId };
}
