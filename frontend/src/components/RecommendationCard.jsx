import { useState } from "react";
import { C } from "../constants";

export function RecommendationCard({ rec, index }) {
  const [expanded, setExpanded] = useState(false);
  const prioColor = { high: C.red, medium: C.amber, low: C.green }[rec.priority] || C.fg3;
  const prioLabel = { high: "CRITICAL", medium: "IMPORTANT", low: "LOW" }[rec.priority] || rec.priority;

  return (
    <div
      style={{
        background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
        padding: 20, borderLeft: `3px solid ${prioColor}`, cursor: "pointer",
        animation: `fadeUp 0.4s ease-out ${index * 0.08}s both`,
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <span style={{ fontSize: 14, fontWeight: 600, color: C.fg, lineHeight: 1.4 }}>{rec.title}</span>
        <span style={{
          fontSize: 10, fontWeight: 700, color: prioColor, textTransform: "uppercase",
          background: `${prioColor}15`, padding: "3px 8px", borderRadius: 4,
          fontFamily: "'JetBrains Mono', monospace", whiteSpace: "nowrap", flexShrink: 0,
        }}>{prioLabel}</span>
      </div>
      {expanded && (
        <div style={{ marginTop: 12 }}>
          <p style={{ fontSize: 13, color: C.fg2, margin: "0 0 14px", lineHeight: 1.6 }}>{rec.description}</p>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{
              fontSize: 10, color: C.violet, background: `${C.violet}15`, padding: "2px 6px",
              borderRadius: 4, fontFamily: "'JetBrains Mono', monospace", fontWeight: 600,
            }}>{rec.tool}</span>
            <code style={{
              flex: 1, fontSize: 12, color: C.cyan, background: C.bg,
              padding: "8px 12px", borderRadius: 6, fontFamily: "'JetBrains Mono', monospace",
            }}>$ {rec.action}</code>
          </div>
        </div>
      )}
      {!expanded && (
        <div style={{ fontSize: 11, color: C.fg3, marginTop: 8, fontFamily: "'JetBrains Mono', monospace" }}>
          ↳ {rec.tool}: click to see command
        </div>
      )}
    </div>
  );
}
