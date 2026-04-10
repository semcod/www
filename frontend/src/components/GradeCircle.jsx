import { useState, useEffect } from "react";
import { C, gradeColor } from "../constants";

export function GradeCircle({ grade, score, size = 130 }) {
  const [animatedOffset, setAnimatedOffset] = useState(999);
  const color = gradeColor(grade);
  const r = size / 2 - 10;
  const circ = 2 * Math.PI * r;
  const targetOffset = circ * (1 - (score || 0) / 100);

  useEffect(() => {
    const t = setTimeout(() => setAnimatedOffset(targetOffset), 100);
    return () => clearTimeout(t);
  }, [targetOffset]);

  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={C.bg3} strokeWidth="5" />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth="5"
          strokeDasharray={circ} strokeDashoffset={animatedOffset} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1.8s cubic-bezier(0.4, 0, 0.2, 1)" }} />
      </svg>
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
      }}>
        <span style={{ fontSize: size * 0.3, fontWeight: 800, color, lineHeight: 1 }}>{grade}</span>
        <span style={{ fontSize: size * 0.13, color: C.fg2, marginTop: 3, fontFamily: "'JetBrains Mono', monospace" }}>{score}/100</span>
      </div>
    </div>
  );
}
