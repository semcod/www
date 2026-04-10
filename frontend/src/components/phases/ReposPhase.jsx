import { C } from "../../lib/config";

export function ReposPhase({ repos, startAudit }) {
  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 24 }}>Select repository</h2>
      <div style={{ display: "grid", gap: 12 }}>
        {repos.map((repo) => (
          <div
            key={repo.full_name}
            onClick={() => startAudit(repo)}
            style={{
              display: "flex", alignItems: "center", gap: 16,
              background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
              padding: "16px 20px", cursor: "pointer", transition: "all 0.2s",
            }}
          >
            <div style={{
              width: 40, height: 40, borderRadius: "50%", background: C.bg3,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 18, flexShrink: 0,
            }}>
              {repo.language === "Python" ? "🐍" : repo.language === "TypeScript" ? "TS" : "📁"}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>{repo.full_name}</div>
              <div style={{ fontSize: 12, color: C.fg3, fontFamily: "'JetBrains Mono', monospace" }}>
                {repo.language} • ⭐ {repo.stars} • {Math.round(repo.size_kb / 1024 * 10) / 10} MB
                {repo.private && <span style={{ marginLeft: 8, color: C.amber }}>🔒 Private</span>}
              </div>
            </div>
            <button style={{
              background: C.bg3, border: `1px solid ${C.border}`, color: C.fg,
              borderRadius: 8, padding: "8px 16px", fontSize: 13, cursor: "pointer",
            }}>Audit →</button>
          </div>
        ))}
      </div>
    </div>
  );
}
