import { useState, useEffect } from "react";
import { C, gradeColor } from "../constants";
import { redslHealth, redslRefactor, getRedslStatus } from "../api";
import { GradeCircle } from "./GradeCircle";

function MetricRow({ label, value, target }) {
  const ok = target != null && value != null && value <= target;
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "4px 0" }}>
      <span style={{ fontSize: 13, color: C.fg2 }}>{label}</span>
      <span style={{ fontSize: 13, fontFamily: "'JetBrains Mono', monospace", color: ok ? C.green : C.fg }}>
        {value ?? "—"}{target != null && <span style={{ fontSize: 11, color: C.fg3 }}> / {target}</span>}
      </span>
    </div>
  );
}

export function RedslHealthCard({ projectPath, repo }) {
  const [health, setHealth] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refactorLoading, setRefactorLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getRedslStatus()
      .then(s => setStatus(s))
      .catch(() => setStatus({ available: false }));
  }, []);

  useEffect(() => {
    if (!projectPath || !status?.available) return;
    setLoading(true);
    redslHealth(projectPath)
      .then(h => { setHealth(h); setError(null); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [projectPath, status?.available]);

  async function handleRefactor() {
    setRefactorLoading(true);
    try {
      const result = await redslRefactor(projectPath, 5, true);
      if (result.status === "preview" && window.confirm("Apply these refactorings?")) {
        await redslRefactor(projectPath, 5, false);
        const h = await redslHealth(projectPath);
        setHealth(h);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setRefactorLoading(false);
    }
  }

  if (!status) {
    return (
      <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 20 }}>
        <div style={{ fontSize: 14, color: C.fg3 }}>Checking reDSL engine…</div>
      </div>
    );
  }

  if (!status.available) {
    return (
      <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 20 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, color: C.fg, margin: 0 }}>Code Health</h3>
        <div style={{ fontSize: 13, color: C.fg3, marginTop: 8 }}>
          reDSL engine unavailable — start with <code>docker-compose up agent</code>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 20 }}>
        <div style={{ fontSize: 14, color: C.fg3 }}>Analyzing code health…</div>
      </div>
    );
  }

  if (error && !health) {
    return (
      <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 20 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, color: C.fg, margin: 0 }}>Code Health</h3>
        <div style={{ fontSize: 13, color: C.red, marginTop: 8 }}>{error}</div>
      </div>
    );
  }

  const grade = health?.grade ?? "?";
  const score = health?.score ?? 0;

  return (
    <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 20 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 20, marginBottom: 16 }}>
        <GradeCircle grade={grade} score={score} size={90} />
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: C.fg, margin: 0 }}>Code Health</h3>
          <div style={{ fontSize: 12, color: C.fg3, marginTop: 4 }}>Powered by reDSL</div>
        </div>
      </div>

      <div style={{ borderTop: `1px solid ${C.border}`, paddingTop: 12 }}>
        <MetricRow label="CC mean" value={health?.cc_mean?.toFixed(1)} target={3.0} />
        <MetricRow label="Critical" value={health?.critical} target={0} />
        <MetricRow label="God modules" value={health?.god_modules} target={0} />
        <MetricRow label="Max CC" value={health?.max_cc} target={15} />
      </div>

      <button
        onClick={handleRefactor}
        disabled={refactorLoading}
        style={{
          marginTop: 16, width: "100%", padding: "10px 0",
          background: refactorLoading ? C.bg3 : C.accent,
          color: "#fff", border: "none", borderRadius: 8,
          fontSize: 14, fontWeight: 600, cursor: refactorLoading ? "wait" : "pointer",
          opacity: refactorLoading ? 0.6 : 1,
        }}
      >
        {refactorLoading ? "Refactoring…" : "Auto-refactor"}
      </button>

      {repo && (
        <div style={{ marginTop: 12, fontSize: 11, color: C.fg3, textAlign: "center" }}>
          Badge: <code>{`![Health](https://semcod.dev/api/redsl/badge/${repo})`}</code>
        </div>
      )}
    </div>
  );
}
