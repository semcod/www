import { C } from "../../../constants";
import { DownloadButtons } from "./DownloadButtons";

export function ResultHeader({ selectedRepo, isSandbox, data, reset, activeTab, setActiveTab }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
      <div>
        <h2 style={{ fontSize: 22, fontWeight: 700 }}>
          <span style={{ color: C.fg3 }}>Report:</span> {selectedRepo?.full_name || selectedRepo?.name || "unknown/repo"}
          {isSandbox && (
            <span style={{
              display: "inline-block",
              marginLeft: 12,
              fontSize: 11,
              color: C.amber,
              background: `${C.amber}15`,
              padding: "2px 8px",
              borderRadius: 4,
              fontWeight: 500,
            }}>🔒 Sandbox</span>
          )}
        </h2>
        {isSandbox && !data.error && (
          <p style={{ fontSize: 13, color: C.fg3, marginTop: 4 }}>
            Public repository analyzed without authentication.
            <a href="#" onClick={(e) => { e.preventDefault(); reset(); }} style={{ color: C.cyan, marginLeft: 8 }}>Install GitHub App for PR reviews →</a>
          </p>
        )}
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <DownloadButtons activeTab={activeTab} setActiveTab={setActiveTab} />
        <button onClick={reset} style={{
          background: C.bg3, border: `1px solid ${C.border}`, color: C.fg2,
          cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
          fontFamily: "inherit",
        }}>New audit</button>
      </div>
    </div>
  );
}
