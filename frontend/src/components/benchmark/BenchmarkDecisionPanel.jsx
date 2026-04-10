import { useState } from "react";
import { submitBenchmarkDecision, downloadBenchmarkExport } from "../../api";

const DEPLOYMENT_MODELS = [
  { value: "", label: "— nie wybrano —" },
  { value: "client_scm", label: "Client SCM" },
  { value: "semcod_managed", label: "Semcod Managed" },
  { value: "hybrid", label: "Hybrid" },
];

const VERDICTS = ["", "go", "no-go", "pending"];
const NEXT_ACTIONS = ["", "prepare_pr", "schedule_review", "escalate", "close"];

export default function BenchmarkDecisionPanel({ caseId, onSaved, trackDecision }) {
  const [prCandidate, setPrCandidate] = useState(null);
  const [deploymentCandidate, setDeploymentCandidate] = useState(null);
  const [deploymentModel, setDeploymentModel] = useState("");
  const [verdict, setVerdict] = useState("");
  const [nextAction, setNextAction] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSubmit = async () => {
    setSaving(true);
    try {
      await submitBenchmarkDecision(caseId, {
        pr_candidate: prCandidate,
        deployment_candidate: deploymentCandidate,
        deployment_model_selected: deploymentModel || undefined,
        reviewer_verdict: verdict || undefined,
        next_action: nextAction || undefined,
      });
      setSaved(true);
      if (trackDecision) trackDecision("benchmark_case");
      if (onSaved) onSaved();
    } catch {
      /* ignore */
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-blue-50 space-y-3">
      <div className="font-semibold text-blue-800 text-sm">Decyzja benchmarkowa</div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <label className="text-xs text-gray-600 font-medium">PR Candidate</label>
          <div className="flex gap-2">
            {[true, false].map((v) => (
              <button
                key={String(v)}
                onClick={() => setPrCandidate(v)}
                className={`flex-1 py-1 rounded text-sm border ${
                  prCandidate === v
                    ? "bg-blue-600 text-white border-blue-600"
                    : "bg-white border-gray-300 text-gray-700"
                }`}
              >
                {v ? "Tak" : "Nie"}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-xs text-gray-600 font-medium">Deployment Candidate</label>
          <div className="flex gap-2">
            {[true, false].map((v) => (
              <button
                key={String(v)}
                onClick={() => setDeploymentCandidate(v)}
                className={`flex-1 py-1 rounded text-sm border ${
                  deploymentCandidate === v
                    ? "bg-purple-600 text-white border-purple-600"
                    : "bg-white border-gray-300 text-gray-700"
                }`}
              >
                {v ? "Tak" : "Nie"}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-600 font-medium block mb-1">Model deploymentu</label>
          <select
            value={deploymentModel}
            onChange={(e) => setDeploymentModel(e.target.value)}
            className="w-full border rounded px-2 py-1 text-sm"
          >
            {DEPLOYMENT_MODELS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs text-gray-600 font-medium block mb-1">Verdict</label>
          <select
            value={verdict}
            onChange={(e) => setVerdict(e.target.value)}
            className="w-full border rounded px-2 py-1 text-sm"
          >
            {VERDICTS.map((v) => <option key={v} value={v}>{v || "— wybierz —"}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className="text-xs text-gray-600 font-medium block mb-1">Następna akcja</label>
        <select
          value={nextAction}
          onChange={(e) => setNextAction(e.target.value)}
          className="w-full border rounded px-2 py-1 text-sm"
        >
          {NEXT_ACTIONS.map((a) => <option key={a} value={a}>{a || "— wybierz —"}</option>)}
        </select>
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleSubmit}
          disabled={saving || saved}
          className="flex-1 py-1.5 rounded bg-blue-600 text-white text-sm font-medium disabled:opacity-50"
        >
          {saved ? "Zapisano ✓" : saving ? "Zapisuję…" : "Zapisz decyzję"}
        </button>
        <button
          onClick={() => downloadBenchmarkExport("csv")}
          className="px-3 py-1.5 rounded border border-gray-300 text-sm text-gray-700"
          title="Pobierz benchmark CSV"
        >
          ↓ CSV
        </button>
        <button
          onClick={() => downloadBenchmarkExport("json")}
          className="px-3 py-1.5 rounded border border-gray-300 text-sm text-gray-700"
          title="Pobierz benchmark JSON"
        >
          ↓ JSON
        </button>
      </div>
    </div>
  );
}
