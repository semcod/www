import { C } from "../../lib/config";

export function LandingPhase({ startOAuth, repoUrl, setRepoUrl, startSandbox }) {
  return (
    <div style={{ textAlign: "center", padding: "80px 0 60px" }}>
      <div style={{
        display: "inline-flex", alignItems: "center", gap: 8,
        background: C.glow, border: `1px solid ${C.border}`,
        padding: "6px 16px", borderRadius: 99, fontSize: 12,
        fontFamily: "'JetBrains Mono', monospace", color: C.cyan, marginBottom: 28,
      }}>
        <span style={{ width: 6, height: 6, borderRadius: "50%", background: C.green }} />
        AI-powered code reviews
      </div>

      <h1 style={{ fontSize: 48, fontWeight: 800, marginBottom: 16, letterSpacing: -1 }}>
        One-click <span style={{ color: C.cyan }}>code audit</span>
      </h1>
      <p style={{ fontSize: 18, color: C.fg2, maxWidth: 520, margin: "0 auto 40px", lineHeight: 1.6 }}>
        Detect complexity, duplication, and security issues in seconds. <br/>
        Get a health score badge for your README.
      </p>

      <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap", marginBottom: 60 }}>
        <button onClick={startOAuth} style={{
          background: C.cyan, color: C.bg, border: "none", borderRadius: 10,
          padding: "16px 32px", fontSize: 16, fontWeight: 700, cursor: "pointer",
          fontFamily: "inherit",
        }}>
          Connect GitHub →
        </button>
        <span style={{ color: C.fg3, padding: "16px 8px" }}>or</span>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            type="text"
            placeholder="github.com/owner/repo"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && startSandbox()}
            style={{
              background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
              padding: "14px 18px", fontSize: 14, color: C.fg, width: 220,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          />
          <button onClick={startSandbox} style={{
            background: C.bg3, color: C.fg, border: `1px solid ${C.border}`, borderRadius: 10,
            padding: "14px 20px", fontSize: 14, cursor: "pointer", fontFamily: "inherit",
          }}>
            Scan
          </button>
        </div>
      </div>

      <div style={{ display: "flex", gap: 40, justifyContent: "center", flexWrap: "wrap" }}>
        {[
          { icon: "🔬", label: "Static Analysis", desc: "code2llm TOON metrics" },
          { icon: "🔁", label: "Duplication", desc: "redup AST scanning" },
          { icon: "🧹", label: "Quality Gates", desc: "ruff + mypy + bandit" },
          { icon: "📊", label: "Health Badge", desc: "shields.io style" },
        ].map(({ icon, label, desc }) => (
          <div key={label} style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>{icon}</div>
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 12, color: C.fg3, fontFamily: "'JetBrains Mono', monospace" }}>{desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
