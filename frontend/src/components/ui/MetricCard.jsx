import { C } from "../../lib/config";

export function MetricCard({ label, value, sub, icon }) {
  return (
    <div style={{
      background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
      padding: "16px 20px", flex: "1 1 140px", minWidth: 140,
    }}>
      <div style={{ fontSize: 12, color: C.fg3, marginBottom: 6, fontFamily: "'JetBrains Mono', monospace" }}>{icon} {label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color: C.fg, letterSpacing: -0.5 }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: C.fg3, marginTop: 3 }}>{sub}</div>}
    </div>
  );
}
