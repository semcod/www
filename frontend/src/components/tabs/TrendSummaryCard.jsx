import { C } from "../../constants";

export function TrendSummaryCard({ label, value, delta, color }) {
  const sign = delta > 0 ? "+" : "";
  const deltaColor = delta > 0 ? "#10B981" : delta < 0 ? "#EF4444" : C.fg3;
  return (
    <div style={{
      background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
      padding: "16px 20px", minWidth: 140, flex: 1,
    }}>
      <div style={{ fontSize: 11, color: C.fg3, marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color: color || C.fg1 }}>{value}</div>
      {delta !== undefined && (
        <div style={{ fontSize: 12, color: deltaColor, marginTop: 4 }}>
          {sign}{delta} vs prev
        </div>
      )}
    </div>
  );
}
