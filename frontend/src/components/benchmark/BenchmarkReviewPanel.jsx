import { useState } from "react";
import { createBenchmarkCase, trackBenchmarkEvent } from "../../api";
import RecommendationFeedbackForm from "./RecommendationFeedbackForm";
import BenchmarkDecisionPanel from "./BenchmarkDecisionPanel";

const SOURCE_TYPES = ["repo", "pr", "ticket"];
const CHANGE_TYPES = ["", "bugfix", "feature", "refactor", "maintenance"];

export default function BenchmarkReviewPanel({ auditId, repo, recommendations = [], benchmarkCaseId: extCaseId, setBenchmarkCaseId: extSetCaseId, trackRecommendationOpened, trackDecision }) {
  const [expanded, setExpanded] = useState(false);
  const [localCaseId, setLocalCaseId] = useState(extCaseId || "");
  const caseId = extCaseId || localCaseId;
  const setCaseId = (v) => { setLocalCaseId(v); if (extSetCaseId) extSetCaseId(v); };
  const [sourceType, setSourceType] = useState("repo");
  const [changeType, setChangeType] = useState("");
  const [baselineDetected, setBaselineDetected] = useState(false);
  const [creating, setCreating] = useState(false);
  const [created, setCreated] = useState(false);
  const [openFeedback, setOpenFeedback] = useState(null);

  const handleCreate = async () => {
    if (!caseId.trim()) return;
    setCreating(true);
    try {
      await createBenchmarkCase({
        case_id: caseId.trim(),
        audit_id: auditId,
        repo,
        source_type: sourceType,
        change_type: changeType,
        baseline_detected: baselineDetected,
        benchmark_mode: true,
      });
      await trackBenchmarkEvent(caseId.trim(), {
        event_name: "audit_completed",
        audit_id: auditId,
        metadata: { repo },
      });
      setCreated(true);
    } catch {
      /* ignore */
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="mt-6 border-t pt-4">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-2 text-sm font-semibold text-blue-700 hover:text-blue-900"
      >
        <span>{expanded ? "▼" : "►"}</span>
        <span>Benchmark Review {created && <span className="text-green-600 ml-1">● {caseId}</span>}</span>
      </button>

      {expanded && (
        <div className="mt-3 space-y-4">
          {!created ? (
            <div className="border rounded-lg p-4 bg-yellow-50 space-y-3">
              <div className="text-sm font-medium text-yellow-800">Utwórz przypadek benchmarkowy</div>

              <div className="flex gap-2 items-center">
                <input
                  value={caseId}
                  onChange={(e) => setCaseId(e.target.value)}
                  placeholder="case_id (np. BM-001)"
                  className="border rounded px-2 py-1 text-sm flex-1"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-600">Source type</label>
                  <select
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                    className="w-full border rounded px-2 py-1 text-sm mt-0.5"
                  >
                    {SOURCE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-600">Change type</label>
                  <select
                    value={changeType}
                    onChange={(e) => setChangeType(e.target.value)}
                    className="w-full border rounded px-2 py-1 text-sm mt-0.5"
                  >
                    {CHANGE_TYPES.map((t) => <option key={t} value={t}>{t || "— opcjonalnie —"}</option>)}
                  </select>
                </div>
              </div>

              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={baselineDetected}
                  onChange={(e) => setBaselineDetected(e.target.checked)}
                />
                Baseline wcześniej wykryty
              </label>

              <button
                onClick={handleCreate}
                disabled={creating || !caseId.trim()}
                className="w-full py-1.5 rounded bg-yellow-600 text-white text-sm font-medium disabled:opacity-50"
              >
                {creating ? "Tworzę…" : "Utwórz przypadek"}
              </button>
            </div>
          ) : (
            <>
              <div className="text-sm text-gray-600">
                Przypadek <strong>{caseId}</strong> — oceń rekomendacje:
              </div>

              {recommendations.map((rec) => (
                <div key={rec.recommendation_id} className="border rounded p-2">
                  <button
                    className="text-sm font-medium text-gray-800 flex justify-between w-full"
                    onClick={() => {
                      setOpenFeedback(openFeedback === rec.recommendation_id ? null : rec.recommendation_id);
                      if (openFeedback !== rec.recommendation_id && trackRecommendationOpened) {
                        trackRecommendationOpened(rec.recommendation_id);
                      }
                    }}
                  >
                    <span>{rec.title}</span>
                    <span className="text-gray-400 text-xs">{rec.recommendation_id}</span>
                  </button>
                  {openFeedback === rec.recommendation_id && (
                    <RecommendationFeedbackForm
                      caseId={caseId}
                      recommendation={rec}
                      onSaved={() => setOpenFeedback(null)}
                    />
                  )}
                </div>
              ))}

              <BenchmarkDecisionPanel caseId={caseId} trackDecision={trackDecision} />
            </>
          )}
        </div>
      )}
    </div>
  );
}
