import { C } from "../../lib/config";

export function ScanningPhase({ scanProgress, scanLabel, selectedRepo }) {
  return (
    <div style={{ textAlign: "center", padding: "100px 0" }}>
      <div style={{
        width: 120, height: 120, borderRadius: "50%",
        background: `conic-gradient(${C.cyan} ${scanProgress * 3.6}deg, ${C.bg3} 0deg)`,
        display: "flex", alignItems: "center", justifyContent: "center",
        margin: "0 auto 40px", position: "relative",
      }}>
        <div style={{
          width: 100, height: 100, borderRadius: "50%", background: C.bg,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <span style={{ fontSize: 24, fontWeight: 700, color: C.cyan }}>{scanProgress}%</span>
        </div>
      </div>

      <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 12 }}>
        Analyzing {selectedRepo?.full_name || "repository"}...
      </h2>
      <p style={{ fontSize: 14, color: C.fg2, fontFamily: "'JetBrains Mono', monospace" }}>
        {scanLabel}
      </p>
    </div>
  );
}
