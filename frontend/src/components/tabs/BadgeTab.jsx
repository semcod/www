import { useState } from "react";
import { C, gradeColor } from "../../lib/config";

function BadgeSVG({ grade, score, width = 152 }) {
  const color = gradeColor(grade);
  const labelW = 82;
  const valueText = score != null ? `${grade} · ${score}%` : grade;
  const valueW = width - labelW;

  return (
    <svg width={width} height="20" role="img" style={{ display: "block" }}>
      <defs>
        <linearGradient id="bg" x2="0" y2="100%">
          <stop offset="0" stopColor="#bbb" stopOpacity=".1" />
          <stop offset="1" stopOpacity=".1" />
        </linearGradient>
        <clipPath id="cr"><rect width={width} height="20" rx="3" /></clipPath>
      </defs>
      <g clipPath="url(#cr)">
        <rect width={labelW} height="20" fill="#555" />
        <rect x={labelW} width={valueW} height="20" fill={color} />
        <rect width={width} height="20" fill="url(#bg)" />
      </g>
      <g fill="#fff" textAnchor="middle" fontFamily="Verdana,Geneva,sans-serif" fontSize="11">
        <text x={labelW / 2} y="15" fillOpacity=".3" fill="#010101">code health</text>
        <text x={labelW / 2} y="14">code health</text>
        <text x={labelW + valueW / 2} y="15" fillOpacity=".3" fill="#010101">{valueText}</text>
        <text x={labelW + valueW / 2} y="14">{valueText}</text>
      </g>
    </svg>
  );
}

export function BadgeTab() {
  const [badgeRepo, setBadgeRepo] = useState("owner/repo");

  const badgeUrl = `https://semcod.dev/badge/${badgeRepo.replace("/", "-")}.svg`;
  const markdown = `![Code Health](${badgeUrl})`;

  return (
    <div style={{ maxWidth: 600, margin: "60px auto" }}>
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <BadgeSVG grade="A+" score={92} width={160} />
      </div>

      <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 16, textAlign: "center" }}>Code Health Badge</h2>
      <p style={{ fontSize: 14, color: C.fg2, textAlign: "center", marginBottom: 40 }}>
        Add a live badge to your README showing your code health score.
        Updates automatically with every PR.
      </p>

      <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 24 }}>
        <label style={{ display: "block", fontSize: 12, color: C.fg3, marginBottom: 8, fontFamily: "'JetBrains Mono', monospace" }}>
          Repository (owner/repo)
        </label>
        <input
          type="text"
          value={badgeRepo}
          onChange={(e) => setBadgeRepo(e.target.value)}
          style={{
            width: "100%", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8,
            padding: "12px 14px", fontSize: 14, color: C.fg,
            fontFamily: "'JetBrains Mono', monospace", marginBottom: 24,
          }}
        />

        <label style={{ display: "block", fontSize: 12, color: C.fg3, marginBottom: 8, fontFamily: "'JetBrains Mono', monospace" }}>
          Markdown
        </label>
        <code style={{
          display: "block", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8,
          padding: "12px 14px", fontSize: 13, color: C.cyan,
          fontFamily: "'JetBrains Mono', monospace", marginBottom: 8,
        }}>
          {markdown}
        </code>
        <button
          onClick={() => navigator.clipboard.writeText(markdown)}
          style={{
            fontSize: 12, color: C.cyan, background: "transparent", border: "none",
            cursor: "pointer", padding: 0,
          }}
        >
          Copy to clipboard
        </button>
      </div>

      <div style={{ marginTop: 32, textAlign: "center" }}>
        <h3 style={{ fontSize: 14, color: C.fg2, marginBottom: 16 }}>Grade Scale</h3>
        <div style={{ display: "flex", justifyContent: "center", gap: 16, flexWrap: "wrap" }}>
          {["A+", "A", "B+", "B", "C", "D", "F"].map(g => (
            <div key={g} style={{ textAlign: "center" }}>
              <div style={{
                width: 40, height: 40, borderRadius: "50%",
                background: gradeColor(g),
                display: "flex", alignItems: "center", justifyContent: "center",
                fontWeight: 700, color: C.bg, fontSize: 14, marginBottom: 4,
              }}>{g}</div>
              <div style={{ fontSize: 11, color: C.fg3 }}>
                {g === "A+" ? "90+" : g === "A" ? "80-89" : g === "B+" ? "70-79" : g === "B" ? "60-69" : g === "C" ? "50-59" : g === "D" ? "40-49" : "<40"}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
