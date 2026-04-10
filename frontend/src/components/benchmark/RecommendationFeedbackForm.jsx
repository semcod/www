import { useState } from "react";
import { submitRecommendationFeedback } from "../../api";

const SCORE_LABELS = ["N/A", "0", "1", "2", "3"];

function ScoreSelect({ label, value, onChange }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="w-32 text-gray-600">{label}</span>
      <select
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value === "" ? null : Number(e.target.value))}
        className="border rounded px-2 py-0.5 text-sm"
      >
        {SCORE_LABELS.map((l, i) => (
          <option key={i} value={i === 0 ? "" : i - 1}>
            {l}
          </option>
        ))}
      </select>
    </div>
  );
}

export default function RecommendationFeedbackForm({ caseId, recommendation, onSaved }) {
  const [accepted, setAccepted] = useState(null);
  const [scores, setScores] = useState({
    novelty_score: null,
    usefulness_score: null,
    accuracy_score: null,
    actionability_score: null,
    business_value_score: null,
  });
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSubmit = async () => {
    setSaving(true);
    try {
      await submitRecommendationFeedback(caseId, recommendation.recommendation_id, {
        accepted,
        ...scores,
        notes,
      });
      setSaved(true);
      if (onSaved) onSaved();
    } catch {
      /* ignore */
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="border rounded-lg p-3 mt-2 bg-gray-50 space-y-2">
      <div className="flex items-center gap-3 text-sm font-medium text-gray-700">
        <span>Feedback dla: <em>{recommendation.title}</em></span>
        <span className="text-xs text-gray-400 font-mono">{recommendation.recommendation_id}</span>
      </div>

      <div className="flex gap-3 items-center">
        <span className="text-sm text-gray-600">Decyzja:</span>
        {[true, false].map((v) => (
          <button
            key={String(v)}
            onClick={() => setAccepted(v)}
            className={`px-3 py-1 rounded text-sm font-medium border ${
              accepted === v
                ? v ? "bg-green-100 border-green-500 text-green-800" : "bg-red-100 border-red-500 text-red-800"
                : "bg-white border-gray-300 text-gray-600"
            }`}
          >
            {v ? "Akceptuj" : "Odrzuć"}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-1">
        {Object.keys(scores).map((key) => (
          <ScoreSelect
            key={key}
            label={key.replace("_score", "").replace(/_/g, " ")}
            value={scores[key]}
            onChange={(v) => setScores((s) => ({ ...s, [key]: v }))}
          />
        ))}
      </div>

      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Notatki (opcjonalne)"
        className="w-full border rounded px-2 py-1 text-sm resize-none"
        rows={2}
      />

      <button
        onClick={handleSubmit}
        disabled={saving || saved}
        className="px-3 py-1 rounded bg-blue-600 text-white text-sm disabled:opacity-50"
      >
        {saved ? "Zapisano ✓" : saving ? "Zapisuję…" : "Zapisz feedback"}
      </button>
    </div>
  );
}
