import { C } from "../constants";

export function LanguageBar({ languages }) {
  const total = Object.values(languages).reduce((a, b) => a + b, 0);
  const colors = [C.cyan, C.green, C.violet, C.amber, C.red];
  const entries = Object.entries(languages);

  return (
    <div style={{ marginBottom: 32 }}>
      <div style={{ fontSize: 11, color: C.fg3, marginBottom: 8, fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: 1.5 }}>Languages</div>
      <div style={{ display: "flex", gap: 2, height: 8, borderRadius: 4, overflow: "hidden" }}>
        {entries.map(([, lines], i) => (
          <div key={i} style={{ width: `${(lines / total) * 100}%`, background: colors[i % colors.length], transition: "width 1s ease-out" }} />
        ))}
      </div>
      <div style={{ display: "flex", gap: 16, marginTop: 8, flexWrap: "wrap" }}>
        {entries.map(([lang, lines], i) => (
          <span key={lang} style={{ fontSize: 12, color: C.fg2, display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: colors[i % colors.length] }} />
            {lang} <span style={{ color: C.fg3 }}>({(lines / 1000).toFixed(1)}k)</span>
          </span>
        ))}
      </div>
    </div>
  );
}
